# Annual precipitation in Afghanistan, 1901-2025: trend

**Question:** How has annual precipitation in Afghanistan changed across the full available record?

**Reads:** dataset [`afghanistan-precipitation`](../../data/datasets/afghanistan-precipitation/README.md)  
**Method:** Sen's slope (95% interval), the conventional Mann-Kendall test, and a 10-year rolling mean. The analysis covers 1901-2025 only.

## Findings

- Across 1901-2025, Sen's slope is about **+2.55 mm per decade** (95% interval: +0.48 to +4.64). The conventional Mann-Kendall test gives p = 0.020, nominally significant at 5%.
- The full-period mean is about 324.4 mm per year. The wettest year is 1957 (443.9 mm) and the driest is 1917 (198.0 mm).
- This result describes the full historical series; it does not establish why rainfall changed or predict future rainfall.
- The p-value is exploratory: the conventional Mann-Kendall implementation does not adjust for serial correlation, and data quality varies over time.

## Figure

![Bar chart of annual country-average precipitation in Afghanistan from 1901 to 2025, with a 10-year rolling mean and a full-period trend line. The full-period slope is upward at about 2.55 mm per decade. The wettest year is 1957 at 443.9 mm and the driest is 1917 at 198.0 mm. Early-record data quality and serial correlation limit interpretation.](outputs/figures/trend_pr_annual_mm.png)

## Read carefully

- The series is a gridded national average, not a rain-gauge measurement at every location. Station coverage and data quality can vary over time, especially in the early record.
- The conventional Mann-Kendall p-value does not adjust for serial correlation. Treat statistical significance as exploratory, not as a definitive climate attribution.
- This repository applies CC BY 4.0 under the World Bank Dataset Terms, including their additional conditions, to the CCKP response and data-derived tables and figures. Credit the World Bank and identify CRU TS v4.10 as the source; do not imply World Bank endorsement. See the [dataset documentation](../../data/datasets/afghanistan-precipitation/README.md) and [source terms](../../data/sources/cru-ts-precipitation/README.md).

## Outputs

- [Generated results, table, and input checksums](outputs/results.md)
- [Data behind the chart](outputs/table.csv)
- [Machine-readable summary](outputs/summary.json), also used by the [infographic](../../infographics/afghanistan-rainfall-trend/README.md)
