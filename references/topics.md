# DHS Topics, Indicators, and Country Codes

## Country Codes

All 92 DHS countries. Note: DHS uses non-standard codes for some countries.

| Code | Country | Code | Country |
|------|---------|------|---------|
| AF | Afghanistan | MW | Malawi |
| AL | Albania | MV | Maldives |
| AO | Angola | ML | Mali |
| AM | Armenia | MR | Mauritania |
| AZ | Azerbaijan | MX | Mexico |
| BD | Bangladesh | MB | Moldova |
| BJ | Benin | MA | Morocco |
| BO | Bolivia | MZ | Mozambique |
| BT | Botswana | MM | Myanmar |
| BR | Brazil | NM | Namibia |
| BF | Burkina Faso | NP | Nepal |
| BU | Burundi | NC | Nicaragua |
| KH | Cambodia | NI | Niger |
| CM | Cameroon | NG | Nigeria |
| CV | Cape Verde | OS | Nigeria (Ondo State) |
| CF | Central African Republic | PK | Pakistan |
| TD | Chad | PG | Papua New Guinea |
| CO | Colombia | PY | Paraguay |
| KM | Comoros | PE | Peru |
| CG | Congo | PH | Philippines |
| CD | Congo Democratic Republic | RW | Rwanda |
| CI | Cote d'Ivoire | WS | Samoa |
| DR | Dominican Republic | ST | Sao Tome and Principe |
| EC | Ecuador | SN | Senegal |
| EG | Egypt | SL | Sierra Leone |
| ES | El Salvador | ZA | South Africa |
| EK | Equatorial Guinea | LK | Sri Lanka |
| ER | Eritrea | SD | Sudan |
| SZ | Eswatini | TJ | Tajikistan |
| ET | Ethiopia | TZ | Tanzania |
| GA | Gabon | TH | Thailand |
| GM | Gambia | TL | Timor-Leste |
| GH | Ghana | TG | Togo |
| GU | Guatemala | TT | Trinidad and Tobago |
| GN | Guinea | TN | Tunisia |
| GY | Guyana | TR | Turkey |
| HT | Haiti | TM | Turkmenistan |
| HN | Honduras | UG | Uganda |
| IA | India | UA | Ukraine |
| ID | Indonesia | UZ | Uzbekistan |
| JO | Jordan | VN | Vietnam |
| KK | Kazakhstan | YE | Yemen |
| KE | Kenya | ZM | Zambia |
| KY | Kyrgyz Republic | ZW | Zimbabwe |
| LA | Lao PDR | | |
| LS | Lesotho | | |
| LB | Liberia | | |
| MD | Madagascar | | |

**Common aliases:**
- DRC / Congo = CD
- Ivory Coast = CI
- Laos = LA
- Swaziland = SZ (now Eswatini)

## Survey Discovery

To find available surveys for any country:
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/dhs_tables.py surveys <country_code>
```

Returns all surveys with SurveyId, year, type (DHS/MIS/AIS), and sample sizes.
Use this when the user asks about "recent" or "all" surveys, or when unsure
which survey years exist for a country.

---

## Topic Mappings

### Malaria / Bed Nets
**Keywords:** ITN, bed net, mosquito net, malaria prevention, net coverage, net use, net ownership, LLIN
**Indicators:**
- ML_NETP_H_MOS: % HH with any mosquito net
- ML_NETP_H_ITN: % HH with >=1 ITN
- ML_NETP_H_MNI: Mean ITNs per HH
- ML_NETP_H_IT2: % HH with >=1 ITN per 2 people
- ML_ITNA_P_ACC: % population with ITN access
- ML_NETU_P_ITN: % population slept under ITN
- ML_NETU_P_IT1: % pop slept under ITN (in HHs with ITN)
- ML_ITNU_N_ITN: % existing ITNs used last night
- ML_NETC_C_ITN: % children <5 slept under ITN
- ML_NETC_C_IT1: % children <5 under ITN (in HHs with ITN)

**Common subsets:**
- "ITN coverage": ML_NETP_H_ITN,ML_NETP_H_IT2,ML_NETC_C_ITN
- "ITN use": ML_NETU_P_ITN,ML_NETC_C_ITN,ML_ITNU_N_ITN
- "net ownership": ML_NETP_H_MOS,ML_NETP_H_ITN,ML_NETP_H_MNI

### Malaria Treatment
**Keywords:** malaria treatment, fever treatment, ACT, artemisinin, IPTp, antimalarial
**Indicators:**
- ML_FVRP_C_AML: % children with fever given antimalarial
- ML_FVRP_C_ACT: % children with fever given ACT
- ML_AMLD_C_ADQ: % children given ACT same/next day
- ML_IPTP_W_SPF: % pregnant women receiving IPTp (SP/Fansidar)
- ML_IPTP_W_3SP: % pregnant women receiving 3+ doses IPTp

**Common subsets:**
- "malaria treatment": ML_FVRP_C_AML,ML_FVRP_C_ACT,ML_AMLD_C_ADQ
- "IPTp": ML_IPTP_W_SPF,ML_IPTP_W_3SP

### Child Vaccination
**Keywords:** vaccination, immunization, vaccine, DPT, measles, BCG, polio, pentavalent
**Indicators:**
- CH_VACC_C_BAS: % children 12-23mo with basic vaccinations
- CH_VACC_C_NON: % children 12-23mo with no vaccinations
- CH_VACC_C_DP1: % children with DPT1
- CH_VACC_C_DP3: % children with DPT3
- CH_VACC_C_MSL: % children with measles
- CH_VACC_C_BCG: % children with BCG
- CH_VACC_C_PL3: % children with polio 3

**Common subsets:**
- "vaccination coverage": CH_VACC_C_BAS,CH_VACC_C_NON,CH_VACC_C_DP3,CH_VACC_C_MSL
- "full vaccination": CH_VACC_C_BAS,CH_VACC_C_NON

### Child Illness Treatment
**Keywords:** diarrhea, ORS, zinc, ARI, pneumonia, fever, care seeking
**Indicators:**
- CH_DIAR_C_DIA: % children with diarrhea (last 2 weeks)
- CH_DIAR_C_ORT: % children with diarrhea given ORT
- CH_DIAR_C_ORS: % children with diarrhea given ORS
- CH_DIAR_C_ZNC: % children with diarrhea given zinc
- CH_ARI_C_ARI: % children with ARI symptoms
- CH_ARI_C_ARF: % children with ARI taken to health facility
- CH_FEVR_C_FEV: % children with fever (last 2 weeks)

**Common subsets:**
- "diarrhea treatment": CH_DIAR_C_DIA,CH_DIAR_C_ORT,CH_DIAR_C_ORS,CH_DIAR_C_ZNC
- "ARI": CH_ARI_C_ARI,CH_ARI_C_ARF

### Child Nutrition / Anthropometry
**Keywords:** stunting, wasting, underweight, malnutrition, nutrition, anthropometry, height-for-age, weight-for-height, stunted, wasted
**Indicators:**
- CN_NUTS_C_HA2: % children stunted (height-for-age < -2 SD)
- CN_NUTS_C_HA3: % children severely stunted (< -3 SD)
- CN_NUTS_C_WH2: % children wasted (weight-for-height < -2 SD)
- CN_NUTS_C_WH3: % children severely wasted (< -3 SD)
- CN_NUTS_C_WA2: % children underweight (weight-for-age < -2 SD)
- CN_NUTS_C_WA3: % children severely underweight (< -3 SD)
- CN_NUTS_C_OW2: % children overweight (weight-for-height > +2 SD)

**Common subsets:**
- "malnutrition": CN_NUTS_C_HA2,CN_NUTS_C_WH2,CN_NUTS_C_WA2
- "stunting": CN_NUTS_C_HA2,CN_NUTS_C_HA3
- "wasting": CN_NUTS_C_WH2,CN_NUTS_C_WH3

### Breastfeeding
**Keywords:** breastfeeding, exclusive breastfeeding, early initiation
**Indicators:**
- NT_BF_EBF: % children <6mo exclusively breastfed
- NT_BF_ERI: % children breastfed within 1 hour of birth
- NT_BF_EVR: % children ever breastfed
- NT_BF_MDF: % children 6-23mo with minimum dietary diversity

**Common subsets:**
- "breastfeeding": NT_BF_EBF,NT_BF_ERI,NT_BF_EVR

### Anemia
**Keywords:** anemia, hemoglobin, iron deficiency
**Indicators:**
- NT_ANM_C_ANY: % children 6-59mo with any anemia
- NT_ANM_W_ANY: % women 15-49 with any anemia
- NT_ANM_C_MOD: % children with moderate anemia
- NT_ANM_C_SVR: % children with severe anemia

**Common subsets:**
- "anemia": NT_ANM_C_ANY,NT_ANM_W_ANY

### Family Planning
**Keywords:** family planning, contraceptive, contraception, unmet need, modern method, CPR
**Indicators:**
- FP_CUSA_W_MOD: % currently married women using modern method
- FP_CUSA_W_ANY: % currently married women using any method
- FP_CUSA_W_TRD: % currently married women using traditional method
- FP_NADM_W_UNT: % married women with unmet need (total)
- FP_NADM_W_ANY: % demand for FP satisfied
- FP_NADM_W_MET: % demand for FP satisfied by modern methods

**Common subsets:**
- "family planning": FP_CUSA_W_MOD,FP_CUSA_W_ANY,FP_NADM_W_UNT,FP_NADM_W_ANY
- "unmet need": FP_NADM_W_UNT,FP_NADM_W_ANY,FP_NADM_W_MET

### Fertility
**Keywords:** fertility, TFR, total fertility rate, birth rate, ASFR, teenage pregnancy
**Indicators:**
- FE_FRTR_W_TFR: Total fertility rate
- FE_FRTR_W_GFR: General fertility rate
- FE_TEEN_W_TBR: Teenage birth rate (15-19)
- FE_FRTR_W_MBI: Median birth interval (months)

**Common subsets:**
- "fertility": FE_FRTR_W_TFR,FE_TEEN_W_TBR,FE_FRTR_W_MBI

### Child Mortality
**Keywords:** child mortality, infant mortality, neonatal, under-5, IMR, NMR, U5MR
**Indicators:**
- CM_ECMR_C_NNR: Neonatal mortality rate
- CM_ECMR_C_PNR: Post-neonatal mortality rate
- CM_ECMR_C_IMR: Infant mortality rate
- CM_ECMR_C_CMR: Child mortality rate (1-4)
- CM_ECMR_C_U5M: Under-5 mortality rate

**Common subsets:**
- "child mortality": CM_ECMR_C_NNR,CM_ECMR_C_IMR,CM_ECMR_C_U5M
- "infant mortality": CM_ECMR_C_NNR,CM_ECMR_C_PNR,CM_ECMR_C_IMR

### Maternal Health / ANC
**Keywords:** ANC, antenatal, prenatal, delivery, skilled birth, postnatal, maternal
**Indicators:**
- RH_ANCN_W_N4P: % women with 4+ ANC visits
- RH_ANCP_W_SKP: % with ANC from skilled provider
- RH_DELP_C_SKP: % births with skilled attendant
- RH_DELA_C_FBD: % births in health facility
- RH_PNCM_C_N2D: % mothers with PNC within 2 days

**Common subsets:**
- "ANC": RH_ANCN_W_N4P,RH_ANCP_W_SKP
- "delivery": RH_DELP_C_SKP,RH_DELA_C_FBD
- "maternal health": RH_ANCN_W_N4P,RH_DELP_C_SKP,RH_DELA_C_FBD,RH_PNCM_C_N2D

### HIV/AIDS
**Keywords:** HIV, AIDS, testing, knowledge, stigma, ARV, PMTCT
**Indicators:**
- HA_KNOW_W_K1A: % women with comprehensive HIV knowledge
- HA_TEST_W_EVR: % women ever tested for HIV
- HA_TEST_W_R12: % women tested and received results (last 12mo)
- HA_STGM_W_DIS: % women with discriminatory attitudes towards HIV

**Common subsets:**
- "HIV testing": HA_TEST_W_EVR,HA_TEST_W_R12
- "HIV knowledge": HA_KNOW_W_K1A,HA_STGM_W_DIS

### Water and Sanitation
**Keywords:** water, sanitation, drinking water, toilet, handwashing, WASH
**Indicators:**
- WS_SRCE_H_IMP: % HH with improved drinking water source
- WS_SRCE_H_PIP: % HH with piped water
- WS_TLET_H_IMP: % HH with improved sanitation
- WS_TLET_H_NFC: % HH with no sanitation facility
- WS_HNDW_H_BAS: % HH with basic handwashing facility

**Common subsets:**
- "WASH": WS_SRCE_H_IMP,WS_TLET_H_IMP,WS_HNDW_H_BAS
- "water": WS_SRCE_H_IMP,WS_SRCE_H_PIP
- "sanitation": WS_TLET_H_IMP,WS_TLET_H_NFC

### Household Characteristics
**Keywords:** electricity, housing, floor, roof, assets, wealth
**Indicators:**
- HC_ELEC_H_ELC: % HH with electricity
- HC_FLOR_H_ETH: % HH with earth/sand floor
- HC_ROOF_H_NAT: % HH with natural roofing
- HC_HEFF_H_MPH: % HH with mobile phone

**Common subsets:**
- "household": HC_ELEC_H_ELC,HC_FLOR_H_ETH,HC_HEFF_H_MPH
