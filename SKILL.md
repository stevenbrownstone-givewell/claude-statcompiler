---
name: dhs-data
description: "Pull DHS STATcompiler data into CSV tables and charts using natural language. Use when the user wants DHS indicator data as a table, asks about DHS statistics for a country, wants to compare indicators across regions/time/demographics, or mentions STATcompiler, DHS data, DHS indicators, or asks for health or demographic statistics from DHS surveys. Handles requests like show me ITN coverage by province, malnutrition trends in Ghana, or vaccination by wealth quintile in Nigeria."
argument-hint: "<natural language query describing what data you want>"
---

# DHS Data Tables

Translate natural language requests into DHS STATcompiler API queries, fetch data,
output CSV tables, and auto-generate visualizations.

## Step 1: Interpret the Request

Parse the user's query to extract these 5 dimensions:

### Country
Map country names to DHS country codes. See [references/topics.md](references/topics.md)
for the full 92-country code table. Common ones:
- DRC/Congo = CD, Ghana = GH, Nigeria = NG, Kenya = KE, Uganda = UG
- Tanzania = TZ, Malawi = MW, Mali = ML, Niger = NI, Ethiopia = ET
- India = IA (not IN), Burkina Faso = BF, Mozambique = MZ

If the country is ambiguous, ask.

### Topic / Indicators
Match against topic mappings in [references/topics.md](references/topics.md):
- "ITN" / "bed nets" / "mosquito nets" → malaria_nets topic
- "stunting" / "wasting" / "malnutrition" → child_nutrition topic
- "vaccination" / "immunization" → child_vaccination topic
- "family planning" / "contraceptive" → family_planning topic
- "child mortality" / "under-5 mortality" → child_mortality topic

If the user provides exact indicator IDs (e.g., ML_NETP_H_ITN), use those directly.
If the topic is ambiguous, search for indicators:
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/dhs_tables.py search "<keyword>"
```

### Time
- "most recent" / "latest" → `--survey latest`
- "over time" / "trends" / "changes" → `--survey all`
- Specific year (e.g., "2018") → resolve to survey ID
- Specific survey (e.g., "DHS 2023-24") → use survey ID directly

If unsure what surveys exist, discover them:
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/dhs_tables.py surveys <country_code>
```

### Breakdown
- "by province" / "by region" / "subnational" → `--breakdown subnational`
- "by wealth" / "by quintile" → `--breakdown wealth`
- "urban vs rural" / "by residence" → `--breakdown residence`
- "by age" / "by age group" → `--breakdown age`
- No breakdown specified → `--breakdown national` (default)

### Output
- Default: CSV file + auto-generated chart
- If user says "markdown table" → `--format markdown`
- Always pass `--plot` to auto-generate a visualization

## Step 2: Fetch Data

Run the table command:
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/dhs_tables.py table \
  --country <CC> \
  --survey <survey_ids_or_latest_or_all> \
  --indicators <indicator_ids> \
  --breakdown <level> \
  --output <path.csv> \
  --plot
```

The script handles API querying, filtering, pivoting, CSV writing, and chart generation.

## Step 3: Present Results

1. Display a preview of the first ~15 rows as a markdown table
2. Report the CSV and PNG file paths
3. Note any indicators that returned no data
4. If trends, note which survey years had data

## Common Query Patterns

| User says | Country | Indicators | Survey | Breakdown |
|-----------|---------|-----------|--------|-----------|
| "ITN coverage by province in DRC" | CD | ML_NETP_H_ITN,ML_NETC_C_ITN,ML_NETP_H_IT2 | latest | subnational |
| "malnutrition trends in Ghana" | GH | CN_NUTS_C_HA2,CN_NUTS_C_WH2,CN_NUTS_C_WA2 | all | national |
| "vaccination by wealth in Nigeria 2018" | NG | CH_VACC_C_BAS,CH_VACC_C_DP3,CH_VACC_C_MSL | NG2018DHS | wealth |
| "bed net use urban vs rural DRC" | CD | ML_NETU_P_ITN,ML_NETC_C_ITN | latest | residence |
| "family planning in Kenya over time" | KE | FP_CUSA_W_MOD,FP_CUSA_W_ANY,FP_NADM_W_ANY | all | national |
| "child mortality rates in DRC" | CD | CM_ECMR_C_NNR,CM_ECMR_C_IMR,CM_ECMR_C_U5M | all | national |
| "ANC coverage trends in Tanzania" | TZ | RH_ANCN_W_N4P | all | national |
| "stunting by wealth in Ethiopia" | ET | NT_CH_NUT_SN2 | latest | wealth |

## Chart Type Selection

The `--plot` flag auto-generates the best chart for the data shape:
- **Trends** (multiple surveys, national) → line chart, year on x-axis
- **Subnational** (provinces/regions) → horizontal bar chart, sorted by value
- **Demographic breakdown** (wealth/residence/age) → grouped bar chart
- **Single value** → skip chart, just show the number

## Reference Materials

- [references/topics.md](references/topics.md) — Full topic→indicator mapping, country codes, survey discovery
