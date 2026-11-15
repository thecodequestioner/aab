# Total population in Central and South Asia, 2000-2025

Total population of the 13 countries in the project's Central and South Asia group, for each year from 2000 to 2025. Each country has one row per year.

## Data

- Table: [`population-central-south-asia.csv`](population-central-south-asia.csv). Column definitions: [`datapackage.json`](datapackage.json).
- Coverage: 13 countries, years 2000 to 2025, 338 rows. No values are missing.

## Source

- **Original data:** United Nations Population Division, World Population Prospects 2024 revision, as distributed by the World Bank (indicator `SP.POP.TOTL`).
- **Obtained through:** [`data/sources/wdi-population`](../../sources/wdi-population/README.md).
- **Licence:** CC BY 4.0. Credit the UN Population Division and the World Bank.

## Method

Rows are taken from the World Bank indicator `SP.POP.TOTL` for 2000 to 2025, one per country and year. Values are rounded to whole people. The project does not estimate or adjust any value.

## Caveats

- The values are model-based. UN World Population Prospects 2024 includes estimates up to 2023, so the values for 2024 and 2025 are projections, not counts.
- National figures can differ. For example, this dataset gives 43.8 million for Afghanistan in 2025, while the National Statistics and Information Authority (NSIA) reported 36.4 million for 2025.
- The only nationwide census of Afghanistan was held in 1979, so its estimates are less certain than those for countries with recent censuses.
- Year-to-year changes reflect the model's assumptions as well as real change. Compare longer periods rather than single years.

## How to cite

Cite the original source (see `data/sources/wdi-population/README.md`) and this repository (`CITATION.cff`).
