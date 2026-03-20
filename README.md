# claude-statcompiler

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that pulls [DHS STATcompiler](https://www.statcompiler.com/) data into CSV tables and auto-generated charts using natural language.

Ask for DHS indicators in plain English — the skill figures out the right API calls, fetches the data, and gives you a formatted table and visualization.

## Examples

```
/dhs-data ITN coverage by province in DRC from the latest survey
/dhs-data malnutrition trends in Ghana
/dhs-data vaccination coverage by wealth quintile in Nigeria 2018
/dhs-data compare bed net use urban vs rural in DRC
/dhs-data child mortality rates in DRC over time
/dhs-data family planning in Kenya over time
```

### Sample outputs

**Subnational** — ITN ownership and child net use by province (DRC 2023-24):

![Subnational bar chart](https://github.com/user-attachments/assets/placeholder-subnational.png)

| Region | HH with ITN (%) | Children <5 under ITN (%) | Sample Size |
|--------|-----------------|---------------------------|-------------|
| Equateur | 88.8 | 74.2 | 4,652 |
| Katanga | 87.8 | 78.2 | 4,210 |
| Bandundu | 77.2 | 66.5 | 2,973 |
| ... | ... | ... | ... |

**Trends** — ITN coverage across three DRC DHS surveys:

![Trend line chart](https://github.com/user-attachments/assets/placeholder-trends.png)

| Survey | HH with ITN (%) | Children <5 under ITN (%) |
|--------|-----------------|---------------------------|
| 2007 | 9.2 | 5.8 |
| 2013-14 | 70.0 | 55.8 |
| 2023-24 | 69.4 | 57.0 |

**Demographic breakdown** — Stunting and wasting by wealth quintile (DRC 2023-24):

![Wealth grouped bar chart](https://github.com/user-attachments/assets/placeholder-wealth.png)

| Category | Children stunted (%) | Children wasted (%) |
|----------|---------------------|---------------------|
| Lowest | 52.2 | 10.0 |
| Second | 50.9 | 7.5 |
| Middle | 52.5 | 7.6 |
| Fourth | 39.9 | 4.9 |
| Highest | 18.2 | 4.4 |

## Installation

Copy the skill into your Claude Code skills directory:

```bash
git clone https://github.com/stevenbrownstone-givewell/claude-statcompiler.git \
  ~/.claude/skills/dhs-data
```

### Requirements

- **Claude Code** — the skill runs inside Claude Code's skill system
- **Python 3.6+** — the API script uses only the standard library (no pip installs)
- **matplotlib** (optional) — needed for auto-generated charts. Install with `pip install matplotlib` if you want visualizations

## What it does

1. **Parses your request** into 5 dimensions: country, topic, time period, breakdown level, and output format
2. **Maps topics to DHS indicator IDs** using a built-in reference covering 15 health domains (malaria, vaccination, nutrition, family planning, mortality, maternal health, HIV, WASH, etc.)
3. **Queries the DHS STATcompiler REST API** to fetch official published indicator values
4. **Pivots the data** into a readable CSV table with short column labels and sample sizes
5. **Auto-generates a chart** — line chart for trends, horizontal bars for subnational, grouped bars for demographic breakdowns

## Supported topics

| Topic | Example query | Key indicators |
|-------|--------------|----------------|
| Malaria / Bed Nets | "ITN coverage" | HH with ITN, children under ITN, ITN access |
| Malaria Treatment | "fever treatment" | ACT use, IPTp coverage |
| Child Vaccination | "vaccination coverage" | DPT3, measles, basic vaccination |
| Child Illness | "diarrhea treatment" | ORS, zinc, ARI care-seeking |
| Child Nutrition | "stunting trends" | Stunting, wasting, underweight |
| Breastfeeding | "exclusive breastfeeding" | EBF, early initiation |
| Anemia | "anemia prevalence" | Child anemia, women's anemia |
| Family Planning | "contraceptive use" | Modern method CPR, unmet need |
| Fertility | "total fertility rate" | TFR, teenage birth rate |
| Child Mortality | "under-5 mortality" | NMR, IMR, U5MR |
| Maternal Health | "ANC coverage" | 4+ ANC visits, skilled delivery |
| HIV/AIDS | "HIV testing" | Ever tested, comprehensive knowledge |
| Water/Sanitation | "WASH indicators" | Improved water, improved sanitation |
| Household | "electricity access" | Electricity, flooring, mobile phone |

See [references/topics.md](references/topics.md) for the full indicator mapping.

## Supported breakdowns

| Breakdown | Trigger phrases |
|-----------|----------------|
| National total (default) | "in DRC", "for Ghana" |
| Subnational / by region | "by province", "by region", "subnational" |
| Urban vs rural | "urban vs rural", "by residence" |
| Wealth quintile | "by wealth", "by quintile" |
| Age group | "by age", "by age group" |

## Country coverage

All 92 countries in the DHS Program are supported. Common codes:

| Code | Country | Code | Country | Code | Country |
|------|---------|------|---------|------|---------|
| CD | DRC | GH | Ghana | NG | Nigeria |
| KE | Kenya | UG | Uganda | TZ | Tanzania |
| MW | Malawi | ET | Ethiopia | BF | Burkina Faso |
| ML | Mali | NI | Niger | MZ | Mozambique |
| IA | India | BD | Bangladesh | PK | Pakistan |

Note: DHS uses some non-standard country codes (e.g., `IA` for India, `BU` for Burundi, `NM` for Namibia). The full list is in [references/topics.md](references/topics.md).

## Standalone script usage

The Python script can also be used directly without Claude Code:

```bash
# List available surveys for a country
python3 scripts/dhs_tables.py surveys GH

# Search for indicators by keyword
python3 scripts/dhs_tables.py search "stunting"

# Fetch a table
python3 scripts/dhs_tables.py table \
  --country CD \
  --survey latest \
  --indicators ML_NETP_H_ITN,ML_NETC_C_ITN \
  --breakdown subnational \
  --output itn_by_province.csv \
  --plot

# Fetch trends across all surveys
python3 scripts/dhs_tables.py table \
  --country GH \
  --survey all \
  --indicators CN_NUTS_C_HA2,CN_NUTS_C_WH2,CN_NUTS_C_WA2 \
  --breakdown national \
  --output gh_nutrition_trends.csv \
  --plot
```

## Data source

All data comes from the [DHS Program STATcompiler API](https://api.dhsprogram.com/). The DHS Program is funded by USAID and implemented by ICF. Data is from nationally representative household surveys conducted across 90+ countries.

## Related

- [validate-dhs](https://github.com/stevenbrownstone-givewell/validate-dhs) — Claude Code skill for validating DHS microdata computations against STATcompiler
- [DHS_DRC_Malaria](https://github.com/stevenbrownstone-givewell/DHS_DRC_Malaria) — DRC bed net usage analysis pipeline using DHS 2023-24 + AMF data
