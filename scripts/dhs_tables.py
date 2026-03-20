#!/usr/bin/env python3
"""
dhs_tables.py — Fetch DHS STATcompiler data and output CSV tables + charts.

Subcommands:
  surveys <country_code>              List available surveys
  search <keyword>                    Search indicators by keyword
  table --country CC --survey S ...   Fetch data and output CSV + optional chart

Uses only Python stdlib for API calls. matplotlib for charts (optional).
"""

import argparse
import csv
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse
from collections import OrderedDict

BASE_URL = "https://api.dhsprogram.com/rest/dhs"
TIMEOUT = 30


# ── API helpers ───────────────────────────────────────────────────────────────

def api_get(endpoint, params=None):
    """Make a GET request to the DHS API."""
    url = f"{BASE_URL}/{endpoint}"
    if params:
        params["f"] = "json"
        url += "?" + urllib.parse.urlencode(params)
    else:
        url += "?f=json"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "dhs-tables/1.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        print(f"URL: {url}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def get_all_surveys(country_code):
    """Get all surveys for a country, sorted by year."""
    result = api_get("surveys", {"countryIds": country_code})
    data = result.get("Data", [])
    return sorted(data, key=lambda x: str(x.get("SurveyYear", "")))


def resolve_survey_ids(country_code, survey_arg):
    """Resolve survey argument to list of survey IDs.

    survey_arg can be:
      - 'latest': most recent DHS
      - 'all': all DHS surveys
      - comma-separated IDs or years
    """
    surveys = get_all_surveys(country_code)

    if survey_arg == "latest":
        dhs = [s for s in surveys if s.get("SurveyType") == "DHS"]
        if not dhs:
            print(f"No DHS surveys found for {country_code}.", file=sys.stderr)
            sys.exit(1)
        latest = dhs[-1]
        sid = latest["SurveyId"]
        print(f"Latest DHS: {sid} ({latest.get('SurveyYearLabel', '')})", file=sys.stderr)
        return [sid]

    if survey_arg == "all":
        dhs = [s for s in surveys if s.get("SurveyType") == "DHS"]
        if not dhs:
            print(f"No DHS surveys found for {country_code}.", file=sys.stderr)
            sys.exit(1)
        ids = [s["SurveyId"] for s in dhs]
        print(f"All DHS surveys: {', '.join(ids)}", file=sys.stderr)
        return ids

    # Comma-separated IDs or years
    parts = [p.strip() for p in survey_arg.split(",")]
    resolved = []
    for p in parts:
        if any(c.isalpha() for c in p):
            resolved.append(p)
        else:
            year = int(p)
            matches = []
            for s in surveys:
                try:
                    sy = int(s.get("SurveyYear", 0))
                except (ValueError, TypeError):
                    continue
                if sy == year or sy == year - 1:
                    matches.append(s)
            dhs = [m for m in matches if m.get("SurveyType") == "DHS"]
            if dhs:
                resolved.append(dhs[0]["SurveyId"])
                print(f"Resolved {p} -> {dhs[0]['SurveyId']}", file=sys.stderr)
            elif matches:
                resolved.append(matches[0]["SurveyId"])
                print(f"Resolved {p} -> {matches[0]['SurveyId']}", file=sys.stderr)
            else:
                print(f"Warning: no survey found for year {p}", file=sys.stderr)
    return resolved


# ── Breakdown filtering ──────────────────────────────────────────────────────

BREAKDOWN_FILTERS = {
    "national": lambda d: d.get("CharacteristicCategory") == "Total",
    "subnational": lambda d: (
        d.get("CharacteristicCategory") == "Region"
        and d.get("IsPreferred", 0) == 1
        and not str(d.get("CharacteristicLabel", "")).startswith("..")
    ),
    "subnational_detail": lambda d: (
        d.get("CharacteristicCategory") == "Region"
        and d.get("IsPreferred", 0) == 1
        and str(d.get("CharacteristicLabel", "")).startswith("..")
    ),
    "residence": lambda d: d.get("CharacteristicCategory") in ("Total", "Residence"),
    "wealth": lambda d: d.get("CharacteristicCategory") in ("Total", "Wealth quintile"),
    "age": lambda d: d.get("CharacteristicCategory") in ("Total", "Age"),
    "all": lambda d: d.get("IsPreferred", 0) == 1 or d.get("CharacteristicCategory") == "Total",
}


# ── Short labels for indicators ──────────────────────────────────────────────

def short_label(indicator_str):
    """Generate a short column name from an indicator description."""
    s = indicator_str
    # Remove common prefixes
    for prefix in ["Households with at least one ", "Children under 5 who ",
                   "Population who ", "Percentage of ", "Percent of "]:
        if s.startswith(prefix):
            s = s[len(prefix):]
    # Truncate
    if len(s) > 50:
        s = s[:47] + "..."
    return s


# ── Subcommands ───────────────────────────────────────────────────────────────

def cmd_surveys(args):
    """List available surveys for a country."""
    surveys = get_all_surveys(args.country_code)
    if not surveys:
        print(f"No surveys found for '{args.country_code}'.")
        return

    print(f"{'SurveyId':<16} {'Year':<12} {'Type':<8} {'HHs':>8} {'Women':>8} {'Men':>8}")
    print("-" * 72)
    for s in surveys:
        print(f"{s['SurveyId']:<16} "
              f"{s.get('SurveyYearLabel', str(s.get('SurveyYear', ''))):<12} "
              f"{s.get('SurveyType', ''):<8} "
              f"{s.get('NumberOfHouseholdsListed', ''):>8} "
              f"{s.get('NumberOfWomenEligibleInterviewed', ''):>8} "
              f"{s.get('NumberOfMenEligibleInterviewed', ''):>8}")


def cmd_search(args):
    """Search indicators by keyword."""
    result = api_get("indicators", {"returnFields": "IndicatorId,Label,ShortName"})
    data = result.get("Data", [])

    term = args.keyword.lower()
    matches = [
        ind for ind in data
        if term in f"{ind.get('IndicatorId', '')} {ind.get('Label', '')} {ind.get('ShortName', '')}".lower()
    ]

    if not matches:
        print(f"No indicators matching '{args.keyword}'.")
        return

    # Group by prefix
    groups = {}
    for ind in sorted(matches, key=lambda x: x.get("IndicatorId", "")):
        prefix = ind.get("IndicatorId", "")[:2]
        groups.setdefault(prefix, []).append(ind)

    print(f"Found {len(matches)} indicators matching '{args.keyword}':\n")
    for prefix, inds in sorted(groups.items()):
        print(f"  [{prefix}]")
        for ind in inds:
            iid = ind.get("IndicatorId", "")
            label = ind.get("Label", "")[:65]
            print(f"    {iid:<22} {label}")
        print()


def cmd_table(args):
    """Fetch data and output as CSV table."""
    survey_ids = resolve_survey_ids(args.country, args.survey)

    # Build the API breakdown parameter
    api_breakdown = None
    if args.breakdown in ("subnational", "subnational_detail"):
        api_breakdown = "subnational"
    elif args.breakdown in ("residence", "wealth", "age", "all"):
        api_breakdown = "all"
    # national needs no breakdown parameter

    # Fetch data for each survey
    all_records = []
    for sid in survey_ids:
        params = {
            "countryIds": args.country,
            "surveyIds": sid,
            "indicatorIds": args.indicators,
        }
        if api_breakdown:
            params["breakdown"] = api_breakdown

        result = api_get("data", params)
        records = result.get("Data", [])
        if not records:
            print(f"Warning: no data for {sid}", file=sys.stderr)
        all_records.extend(records)

    if not all_records:
        print("No data found. The indicators may not be available for these surveys.")
        print("Try: python3 dhs_tables.py search \"<keyword>\" to find valid indicator IDs.")
        return

    # Apply breakdown filter
    filt = BREAKDOWN_FILTERS.get(args.breakdown, BREAKDOWN_FILTERS["national"])
    filtered = [r for r in all_records if filt(r)]

    if not filtered:
        print(f"No records match breakdown='{args.breakdown}'. Showing all {len(all_records)} records.")
        filtered = all_records

    # Build indicator ID → short label mapping
    ind_labels = {}
    for r in filtered:
        iid = r.get("IndicatorId", "")
        if iid not in ind_labels:
            ind_labels[iid] = short_label(r.get("Indicator", iid))

    indicator_ids = list(ind_labels.keys())
    multi_survey = len(survey_ids) > 1

    # Determine row key structure
    if args.breakdown in ("subnational", "subnational_detail"):
        row_key_name = "Region"
        get_row_key = lambda r: r.get("CharacteristicLabel", "").lstrip(".")
    elif args.breakdown in ("residence", "wealth", "age", "all"):
        row_key_name = "Category"
        get_row_key = lambda r: r.get("CharacteristicLabel", "")
    else:
        row_key_name = "Survey"
        get_row_key = lambda r: r.get("SurveyYearLabel", str(r.get("SurveyYear", "")))

    # Pivot: build {(row_key, survey_label): {indicator: value}}
    pivot = OrderedDict()
    sample_sizes = {}

    for r in filtered:
        row_key = get_row_key(r)
        survey_label = r.get("SurveyYearLabel", str(r.get("SurveyYear", "")))

        if multi_survey and args.breakdown != "national":
            key = (row_key, survey_label)
        elif multi_survey:
            key = (survey_label,)
        else:
            key = (row_key,)

        if key not in pivot:
            pivot[key] = {}
        iid = r.get("IndicatorId", "")
        pivot[key][iid] = r.get("Value", "")

        # Track sample size from first indicator
        if iid == indicator_ids[0]:
            sample_sizes[key] = r.get("DenominatorUnweighted", "")

    # Sort rows
    sort_orders = {}
    for r in filtered:
        row_key = get_row_key(r)
        survey_label = r.get("SurveyYearLabel", str(r.get("SurveyYear", "")))
        if multi_survey and args.breakdown != "national":
            key = (row_key, survey_label)
        elif multi_survey:
            key = (survey_label,)
        else:
            key = (row_key,)
        sort_orders[key] = (
            r.get("CharacteristicOrder", 0),
            str(r.get("SurveyYear", "")),
        )

    sorted_keys = sorted(pivot.keys(), key=lambda k: sort_orders.get(k, (999, "")))

    # Build CSV rows
    header = []
    if multi_survey and args.breakdown != "national":
        header = [row_key_name, "Survey"]
    elif multi_survey:
        header = ["Survey"]
    else:
        header = [row_key_name]

    for iid in indicator_ids:
        header.append(ind_labels[iid])
    header.append("Sample Size (N)")

    rows = []
    for key in sorted_keys:
        row = list(key)
        for iid in indicator_ids:
            row.append(pivot[key].get(iid, ""))
        row.append(sample_sizes.get(key, ""))
        rows.append(row)

    # Output
    if args.format == "markdown":
        # Print markdown table
        print("| " + " | ".join(str(h) for h in header) + " |")
        print("| " + " | ".join("---" for _ in header) + " |")
        for row in rows:
            print("| " + " | ".join(str(v) for v in row) + " |")
    else:
        # Write CSV
        if args.output:
            os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
            with open(args.output, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(rows)
            print(f"Saved: {args.output} ({len(rows)} rows, {len(header)} columns)", file=sys.stderr)
        else:
            writer = csv.writer(sys.stdout)
            writer.writerow(header)
            writer.writerows(rows)

    # Plot if requested
    if args.plot:
        plot_path = args.output.rsplit(".", 1)[0] + ".png" if args.output else "/tmp/dhs_chart.png"
        make_chart(header, rows, sorted_keys, indicator_ids, ind_labels,
                   args.breakdown, multi_survey, survey_ids, args.country, plot_path)


# ── Charting ──────────────────────────────────────────────────────────────────

def make_chart(header, rows, sorted_keys, indicator_ids, ind_labels,
               breakdown, multi_survey, survey_ids, country, output_path):
    """Auto-generate the best chart type for the data."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed — skipping chart.", file=sys.stderr)
        return

    try:
        plt.style.use("seaborn-v0_8-whitegrid")
    except OSError:
        pass

    n_indicators = len(indicator_ids)
    n_rows = len(rows)

    if n_rows == 0:
        return

    # Extract labels and values
    row_labels = [" / ".join(str(v) for v in key) for key in sorted_keys]

    # Values per indicator: list of lists
    ind_values = []
    for i, iid in enumerate(indicator_ids):
        col_idx = len(sorted_keys[0])  # number of key columns
        vals = []
        for row in rows:
            try:
                vals.append(float(row[col_idx + i]))
            except (ValueError, TypeError, IndexError):
                vals.append(None)
        ind_values.append(vals)

    # Decide chart type
    if multi_survey and breakdown == "national":
        _plot_trend(plt, row_labels, ind_values, indicator_ids, ind_labels,
                    country, output_path)
    elif breakdown == "subnational":
        _plot_horizontal_bars(plt, row_labels, ind_values, indicator_ids, ind_labels,
                              country, survey_ids, output_path)
    elif breakdown in ("wealth", "residence", "age"):
        _plot_grouped_bars(plt, row_labels, ind_values, indicator_ids, ind_labels,
                           country, survey_ids, breakdown, output_path)
    else:
        # Fallback: horizontal bars
        _plot_horizontal_bars(plt, row_labels, ind_values, indicator_ids, ind_labels,
                              country, survey_ids, output_path)


def _plot_trend(plt, labels, ind_values, indicator_ids, ind_labels, country, path):
    """Line chart for trends over time."""
    fig, ax = plt.subplots(figsize=(10, 6))

    for i, iid in enumerate(indicator_ids):
        vals = ind_values[i]
        valid = [(l, v) for l, v in zip(labels, vals) if v is not None]
        if valid:
            xl, yl = zip(*valid)
            ax.plot(xl, yl, marker="o", linewidth=2, markersize=8, label=ind_labels[iid])

    ax.set_xlabel("Survey")
    ax.set_ylabel("Value (%)")
    ax.set_title(f"DHS Trends — {country}")
    ax.legend(loc="best", fontsize=9)
    ax.annotate("Source: DHS STATcompiler", xy=(0, 0), xycoords="figure fraction",
                fontsize=7, color="gray", va="bottom")

    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Chart saved: {path}", file=sys.stderr)


def _plot_horizontal_bars(plt, labels, ind_values, indicator_ids, ind_labels,
                          country, survey_ids, path):
    """Horizontal bar chart for subnational or categorical data."""
    n_ind = len(indicator_ids)

    if n_ind == 1:
        fig, ax = plt.subplots(figsize=(10, max(6, len(labels) * 0.35)))
        vals = ind_values[0]
        # Sort by value
        paired = sorted(zip(labels, vals), key=lambda x: x[1] if x[1] is not None else -1)
        sl, sv = zip(*paired) if paired else ([], [])
        sv_clean = [v if v is not None else 0 for v in sv]

        bars = ax.barh(sl, sv_clean, color="#2171b5", edgecolor="white")
        ax.set_xlabel("Value (%)")
        ax.set_title(f"{ind_labels[indicator_ids[0]]} — {country}")

    else:
        fig, axes = plt.subplots(1, n_ind, figsize=(5 * n_ind, max(6, len(labels) * 0.35)),
                                 sharey=True)
        if n_ind == 1:
            axes = [axes]

        for i, (iid, ax) in enumerate(zip(indicator_ids, axes)):
            vals = ind_values[i]
            paired = sorted(zip(labels, vals), key=lambda x: x[1] if x[1] is not None else -1)
            sl, sv = zip(*paired) if paired else ([], [])
            sv_clean = [v if v is not None else 0 for v in sv]

            ax.barh(sl, sv_clean, color=f"C{i}", edgecolor="white")
            ax.set_xlabel("Value (%)")
            ax.set_title(ind_labels[iid], fontsize=10)

    survey_str = ", ".join(survey_ids) if len(survey_ids) <= 3 else f"{len(survey_ids)} surveys"
    fig.suptitle(f"DHS — {country}", fontsize=13, y=1.02)
    fig.text(0, -0.02, f"Source: DHS STATcompiler ({survey_str})", fontsize=7, color="gray")

    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Chart saved: {path}", file=sys.stderr)


def _plot_grouped_bars(plt, labels, ind_values, indicator_ids, ind_labels,
                       country, survey_ids, breakdown, path):
    """Grouped bar chart for demographic breakdowns."""
    import numpy as np

    n_groups = len(labels)
    n_ind = len(indicator_ids)
    x = np.arange(n_groups)
    width = 0.8 / n_ind

    fig, ax = plt.subplots(figsize=(max(8, n_groups * 1.2), 6))

    for i, iid in enumerate(indicator_ids):
        vals = [v if v is not None else 0 for v in ind_values[i]]
        offset = (i - n_ind / 2 + 0.5) * width
        ax.bar(x + offset, vals, width, label=ind_labels[iid])

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45 if n_groups > 5 else 0, ha="right" if n_groups > 5 else "center")
    ax.set_ylabel("Value (%)")
    ax.set_title(f"DHS — {country} by {breakdown.title()}")
    ax.legend(loc="best", fontsize=9)

    survey_str = ", ".join(survey_ids) if len(survey_ids) <= 3 else f"{len(survey_ids)} surveys"
    ax.annotate(f"Source: DHS STATcompiler ({survey_str})", xy=(0, 0),
                xycoords="figure fraction", fontsize=7, color="gray", va="bottom")

    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Chart saved: {path}", file=sys.stderr)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Fetch DHS STATcompiler data into tables and charts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python3 dhs_tables.py surveys CD
  python3 dhs_tables.py search "stunting"
  python3 dhs_tables.py table --country CD --survey latest --indicators ML_NETP_H_ITN,ML_NETC_C_ITN --breakdown subnational --output itn.csv --plot
  python3 dhs_tables.py table --country GH --survey all --indicators NT_CH_NUT_SN2,NT_CH_NUT_WS2 --breakdown national --output trends.csv --plot
""")

    sub = parser.add_subparsers(dest="command", required=True)

    # surveys
    p_surv = sub.add_parser("surveys", help="List available surveys")
    p_surv.add_argument("country_code", help="DHS country code (e.g., CD)")

    # search
    p_search = sub.add_parser("search", help="Search indicators by keyword")
    p_search.add_argument("keyword", help="Keyword to search")

    # table
    p_table = sub.add_parser("table", help="Fetch data and output table")
    p_table.add_argument("--country", required=True, help="DHS country code")
    p_table.add_argument("--survey", required=True,
                         help="Survey ID(s), year(s), 'latest', or 'all'")
    p_table.add_argument("--indicators", required=True,
                         help="Comma-separated indicator IDs")
    p_table.add_argument("--breakdown",
                         choices=["national", "subnational", "subnational_detail", "residence", "wealth", "age", "all"],
                         default="national", help="Breakdown level (default: national)")
    p_table.add_argument("--output", help="Output CSV path (default: stdout)")
    p_table.add_argument("--format", choices=["csv", "markdown"], default="csv")
    p_table.add_argument("--plot", action="store_true", help="Generate chart alongside CSV")

    args = parser.parse_args()

    if args.command == "surveys":
        cmd_surveys(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "table":
        cmd_table(args)


if __name__ == "__main__":
    main()
