# WHO/UNICEF JMP household water estimates, via the World Bank WDI

National estimates of drinking water services, 2000-2024, for the 13 countries in the project's Central and South Asia group.

## Obtaining the data

Automatic. The pipeline downloads these World Bank indicators for the countries in `source.yaml`, and logs each download in `RETRIEVAL_LOG.csv`. Run `python -m aab build --refresh` to download again.

| Indicator code | Name |
|---|---|
| `SH.H2O.SMDW.ZS` | People using safely managed drinking water services (% of population). Used for SDG 6.1.1. |
| `SH.H2O.BASW.ZS` | People using at least basic drinking water services (% of population) |

## Definitions

- **Safely managed:** an improved source that is on premises, available when needed, and free from faecal and priority chemical contamination.
- **At least basic:** an improved source with a round-trip collection time of 30 minutes or less.

## Licence and credit

- Original: WHO/UNICEF Joint Monitoring Programme for Water Supply, Sanitation and Hygiene, household estimates, 2025 update. https://washdata.org/
- Distributed by: World Bank World Development Indicators. https://data.worldbank.org/indicator/SH.H2O.SMDW.ZS
- Licence: CC BY 4.0. Credit JMP and the World Bank.
