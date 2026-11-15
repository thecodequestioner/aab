# Natural Earth Admin 0 country boundaries

Country-boundary GeoJSON files for use as cartographic references. The population map uses the 1:50m file.

## Obtaining the data

Manual. Download these files from the `geojson` folder of the Natural Earth vector repository:

- `ne_50m_admin_0_countries.geojson` — used by the population map; contains all 13 target countries.
- `ne_110m_admin_0_countries.geojson` — retained as a lower-resolution alternative; it does not include Maldives.

Save the files in this folder with their original names. The project checks each file and records its checksum in `RETRIEVAL_LOG.csv`.

## Use in this project

The infographic uses these files only to draw country shapes. Country names, sub-regions, and population figures come from the processed population dataset.

## Licence and credit

- Original: Natural Earth, https://www.naturalearthdata.com/
- Licence: public domain. Credit Natural Earth.

## Known gaps

Boundaries are generalized cartographic references, not authoritative legal boundaries. Natural Earth depicts de facto boundaries. Maldives is present in the 1:50m file, but its islands may need a callout to be visible at this map scale.