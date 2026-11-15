# Drinking water access in Central and South Asia, 2000-2024

Share of the population using safely managed and at least basic drinking water services, for 13 countries in Central and South Asia.

## Data

- Table: [`drinking-water-access.csv`](drinking-water-access.csv). Column definitions and types: [`datapackage.json`](datapackage.json).
- Indicators: `SH.H2O.SMDW.ZS` (safely managed, SDG 6.1.1) and `SH.H2O.BASW.ZS` (at least basic).
- Coverage: 13 countries, 2000-2024. One row per country, year and indicator. Not every country has every year.
- Missing values are not stored as rows. Maldives has values for at least basic water but none for safely managed water in this release.

## Source

- **Original data:** WHO/UNICEF Joint Monitoring Programme (JMP), household estimates, 2025 update.
- **Obtained through:** [`data/sources/jmp-household-water`](../../sources/jmp-household-water/README.md), via the World Bank World Development Indicators.
- **Licence:** CC BY 4.0. Credit the JMP and the World Bank.

## Method

- Countries come from the project group `central_and_south_asia` in [`aab/countries.csv`](../../../aab/countries.csv). Iran is not included, because the World Bank places it with the Middle East and North Africa. To add it, tag it in that file.
- Values are used as published, rounded to two decimals. Nothing is recalculated.

## Caveats

- These are modelled national estimates, not census counts. Countries with limited survey data have more uncertainty.
- Latest years can differ between countries. Each value in an analysis shows its year.
- Compare values within one JMP release. Estimates can be revised between releases.
- Sub-region averages in the analyses are unweighted means of countries, not population-weighted.

## How to cite

Cite the original source (WHO/UNICEF JMP 2025 update, accessed via World Bank WDI), this dataset (version in `dataset.yaml`) and the repository (`CITATION.cff`).

## Used by

- [Drinking water access ranking, latest year](../../../analysis/water-access-ranking/README.md)
