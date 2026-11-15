# World Bank WDI: total population, via UN World Population Prospects

Total population for the 13 countries in the project's Central and South Asia group, as estimated and projected by the World Bank from UN and national sources.

## Obtaining the data

Automatic. The pipeline downloads the indicator `SP.POP.TOTL` for the countries in `source.yaml` and logs each download in `RETRIEVAL_LOG.csv`. Run `python -m aab build --refresh` to download it again.

## Definitions

Total population is the de facto count of all residents, regardless of legal status or citizenship. Values are mid-year estimates. Years after the last estimate are projections.

## Licence and credit

- Original: United Nations Population Division, World Population Prospects 2024 revision. https://population.un.org/wpp/
- Distributed by: World Bank, World Development Indicators. https://data.worldbank.org/indicator/SP.POP.TOTL
- Licence: CC BY 4.0. Credit the UN Population Division and the World Bank.

## Known gaps

- Figures are model-based estimates, not census counts. Afghanistan has not had a modern census, so its figures are estimates.
- National statistics for Afghanistan differ from UN estimates. The UN World Population Prospects 2024 figure for 1 July 2025 is 43.8 million, as used in this dataset. The National Statistics and Information Authority (NSIA) announced 36.4 million for 2025 (Solar year 1404) in July 2025, as reported by [TOLOnews](https://tolonews.com/afghanistan-194934) and [Xinhua](https://english.news.cn/asiapacific/20250708/2ed413b2e73c4b47b0b54334a0edd588/c.html). The NSIA figure has not been independently verified.
