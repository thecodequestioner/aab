# CCKP CRU TS 4.10 precipitation source

This source record covers the World Bank Climate Change Knowledge Portal (CCKP) API response for Afghanistan's annual country-average precipitation, 1901-2025. The underlying climate product is CRU TS 4.10.

- **Producer:** Climatic Research Unit (CRU), University of East Anglia
- **Distributor:** World Bank Climate Change Knowledge Portal (CCKP)
- **Data:** annual precipitation, country average, millimetres per year
- **Endpoint:** [`source.yaml`](source.yaml)
- **Retrieval record:** [`RETRIEVAL_LOG.csv`](RETRIEVAL_LOG.csv)
- **Raw response:** `cckp_cru_pr_annual_AFG.json`

## Licence and attribution

This repository applies **CC BY 4.0 under the World Bank Dataset Terms**, including the terms' additional conditions, to the CCKP API response. The World Bank states that CCKP data is disseminated under its Open Data policy and that CC BY 4.0 applies unless a dataset is specifically labeled otherwise. Its terms also note that some third-party data may have different terms. This repository has not identified a CCKP-specific exception for this API response and records this as its working licence determination.

The World Bank requires attribution in this form: **The World Bank: Dataset name: Data source (if known).** For this dataset, cite the World Bank CCKP annual precipitation series for Afghanistan and identify CRU TS v4.10 as the data source. Include the World Bank Dataset Terms link when sharing or facilitating access to the data. Do not imply that the World Bank endorses the project.

CRU's own CRU TS 4.10 page states that the dataset is under the Open Database License and that rights in individual contents are under the Database Contents License, with attribution to the Climatic Research Unit, University of East Anglia. This repository's determination applies to the CCKP-distributed API response; it does not claim that the World Bank changed CRU's upstream licence. Revisit this determination if CCKP metadata or written clarification identifies a different licence or a third-party exception.

- [World Bank Terms of Use for Datasets](https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets)
- [CRU TS 4.10: licence, attribution and dataset information](https://crudata.uea.ac.uk/cru/data/hrg/cru_ts_4.10/)
- [World Bank Data Access and Licensing](https://datacatalog.worldbank.org/public-licenses)

## Access and limitations

The source is accessed through the CCKP Data Catalog API. See `source.yaml` for the exact endpoint and [`RETRIEVAL_LOG.csv`](RETRIEVAL_LOG.csv) for the local file checksum. The original API request timestamp was not available when the supplied response was recorded.

The response contains country-average values, not precipitation measurements at every location in Afghanistan. CRU describes its data as gridded climate estimates; station coverage and data quality vary over time.
