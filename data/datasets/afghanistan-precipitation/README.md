# Annual precipitation in Afghanistan, 1901-2025

Country-average annual precipitation for Afghanistan from the CCKP CRU TS 4.10 historical series.

## Data

- Table: [`afghanistan-precipitation.csv`](afghanistan-precipitation.csv). Column definitions and types: [`datapackage.json`](datapackage.json).
- Indicator: `PR_ANNUAL_MM`, a project code for annual precipitation in millimetres per year.
- Coverage: one country, 1901-2025, one row per year (125 annual values).
- The source is the CCKP Data Catalog API response stored in [`data/sources/cru-ts-precipitation`](../../sources/cru-ts-precipitation/README.md).

## Source and licence

- **Underlying data:** CRU TS 4.10, obtained as Afghanistan's country-average annual precipitation series through the World Bank Climate Change Knowledge Portal (CCKP).
- **Source file:** [`cckp_cru_pr_annual_AFG.json`](../../sources/cru-ts-precipitation/cckp_cru_pr_annual_AFG.json).
- **Licence applied to the CCKP response:** CC BY 4.0 under the World Bank Dataset Terms, including their additional conditions. This repository applies the World Bank's published default because no CCKP-specific exception for this response was identified in the reviewed metadata. CRU's own CRU TS 4.10 page separately states ODbL terms for the dataset and Database Contents License terms for individual contents; this repository's determination is for the CCKP-distributed response.
- **Required credit:** The World Bank: CCKP annual precipitation for Afghanistan, 1901-2025; data source: Climatic Research Unit (CRU), University of East Anglia, CRU TS v4.10. Do not imply World Bank endorsement. See the [source README](../../sources/cru-ts-precipitation/README.md) for the terms links and attribution details.

## Method

- The endpoint returns annual precipitation for the CCKP country-average product. The transformer reads the `AFG` series and its `YYYY-07` annual keys, verifies that every year from 1901 through 2025 is present, and rounds values to one decimal place.
- The table is built by [`transform.py`](transform.py). The raw JSON response is kept unchanged and its checksum is recorded in the source retrieval log.

## Caveats

- These are gridded estimates, not direct measurements at every location. The spatial product is a national average and conceals strong local differences.
- Data quality and station coverage can vary over time, particularly in the early record. A complete annual series does not mean every year's estimate is equally certain.
- The trend analysis covers the full 1901-2025 record only; it does not compare separate time periods or explain the causes of change.
- The project's conventional Mann-Kendall test does not adjust its p-value for serial correlation. Treat statistical significance as exploratory.

## How to cite

Cite the World Bank CCKP annual precipitation series for Afghanistan and identify CRU TS v4.10 as the data source. Include the World Bank Dataset Terms URL when sharing or facilitating access to the data. See the [source record](../../sources/cru-ts-precipitation/README.md) and [`CITATION.cff`](../../../CITATION.cff).

## Used by

- [Annual precipitation in Afghanistan, 1901-2025: trend](../../../analysis/afghanistan-rainfall-trend/README.md)
- [Afghanistan rainfall infographic](../../../infographics/afghanistan-rainfall-trend/README.md)
