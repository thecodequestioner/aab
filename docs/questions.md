# Question bank and ideas

This page collects candidate questions and related ideas for possible additions to the repository. These entries are proposals, not findings. Confirm data sources, indicator codes, coverage, and licence terms before starting an analysis.

Before using an indicator code, confirm it in the relevant source catalogue. Codes marked *(verify)* are suggestions that still need checking.

**Statuses:**
- **Open:** not yet underway.
- **In progress:** work has started.
- **Partly done:** related work answers part of the question or implements part of the idea.
- **Done:** linked work answers the question or the idea has been implemented.

## 1. Question bank

| ID | Question | Theme | Data needed | Status | Related work |
|---|---|---|---|---|---|
| Q001 | Which countries have improved safely managed drinking water fastest since 2000? | water-access | JMP via World Bank WDI, `SH.H2O.SMDW.ZS` | Partly done: latest-year ranking exists; change since 2000 is not yet analysed | [water-access-ranking](../analysis/water-access-ranking/README.md) |
| Q002 | Are rural-urban gaps in safely managed drinking water narrowing? | water-access | JMP urban and rural series via WDI *(verify)* | Open | |
| Q003 | How does sanitation access compare with drinking water access in each country? | sanitation | JMP safely managed sanitation via WDI, e.g. `SH.STA.SMSS.ZS` *(verify)* | Open | |
| Q004 | How has annual precipitation in Afghanistan changed across the full available record? | climate | CRU TS via CCKP | Done | [afghanistan-rainfall-trend](../analysis/afghanistan-rainfall-trend/README.md) |
| Q005 | Does the choice of start year change the sign of the rainfall trend? | climate (method) | As Q004, with several start years | Open | |
| Q006 | Which countries in the region have the most variable rainfall from year to year? | climate | CRU TS via CCKP; coefficient of variation per country | Open | |
| Q007 | How much have annual mean temperatures risen in the region since 1975? | climate | CRU TS temperature via CCKP | Open | |
| Q008 | How many drought years occurred in each decade, using the bottom 10% of rainfall during 1981-2010 as the threshold? | climate | CRU TS via CCKP; percentile method | Open | |
| Q009 | Is the rainfall trend in Afghanistan consistent across provinces? | climate, subnational | Gridded data clipped to provinces (ISO 3166-2 codes) | Open | |
| Q010 | How does water stress compare across the region? | water-resources | WDI freshwater withdrawal as a share of resources, `ER.H2O.FWTL.ZS` *(verify)* | Open | |
| Q011 | Do countries with more renewable freshwater per person have less water stress? | water-resources | WDI `ER.H2O.INTR.PC` and `ER.H2O.FWTL.ZS` *(verify)* | Open | |
| Q012 | Which sector uses the most water in each country? | water-resources | WDI sectoral withdrawal shares, e.g. `ER.H2O.FWAG.ZS` for agriculture *(verify)* | Open | |
| Q013 | Do countries with higher income have higher access to safely managed drinking water? | equity | JMP via WDI, plus GDP per capita `NY.GDP.PCAP.KD` *(verify)* | Open | |
| Q014 | How much do JMP estimates change between releases? | data-quality | Two JMP releases for the same countries | Open | |
| Q015 | Where do national statistics and WDI differ for the same indicator? | data-quality | National statistical yearbooks and WDI | Open | |
| Q016 | How has the flow of the Amu Darya and Syr Darya changed? | water-resources | Station records; source availability is uncertain | Open | |
| Q017 | How can a teaching infographic present the observed rainfall trend without overstating certainty? | climate (education) | `afghanistan-precipitation` and `afghanistan-rainfall-trend` | Done | [Afghanistan rainfall infographic](../infographics/afghanistan-rainfall-trend/README.md) |

## 2. Ideas

| ID | Idea | Why | Status |
|---|---|---|---|
| I001 | Translate the rainfall infographic into local languages such as Dari and Pashto. | The contributing guide welcomes translations. Each needs a native-speaker check; Dari and Pashto also need right-to-left text shaping. | Open |

## 3. How to propose or update an entry

1. Check the bank for an existing question or idea before proposing a new one.
2. Use GitHub’s **Question or new analysis** issue template to propose an entry or discuss work on an existing one. Include the existing ID if you are picking it up. For a new entry, leave the ID blank to avoid duplicate IDs.
3. Describe the question or idea, the data needed, the countries and years of interest, and the intended audience. Mark unconfirmed indicator codes *(verify)* rather than presenting them as checked.
4. Before analysis begins, confirm the source, indicator definition, data coverage, and licence terms. Update the data-needed description if these checks change the proposal.
5. When a new entry is accepted into the bank, assign the next unused `Q` ID if it is a question, or `I` ID if it is a broader idea. Use three digits, such as `Q001` or `I001`. Keep assigned IDs stable and do not reuse retired IDs.
6. Update the status in a pull request when work begins or is completed. For a question, add the analysis or infographic link under **Related work**. Mark it **Done** only when the linked work addresses the question. For an idea, mark it **Done** only when its implementation is merged.
