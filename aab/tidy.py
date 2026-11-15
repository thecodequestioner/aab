"""The standard long (tidy) table used by every dataset.

One row = one country x year x indicator. A dataset may add columns through
`extra_fields` in dataset.yaml, but the standard fields below are always present.
Field descriptions are copied into each dataset's datapackage.json.
"""
import pandas as pd

STANDARD_FIELDS = [
    {"name": "iso3", "type": "string", "title": "ISO 3166-1 alpha-3 country code",
     "description": "Three-letter country code. Matches the project registry in aab/countries.csv.",
     "constraints": {"required": True, "pattern": "^[A-Z]{3}$"}},
    {"name": "country_name", "type": "string", "title": "Country name",
     "description": "Short English country name from the project registry.",
     "constraints": {"required": True}},
    {"name": "region", "type": "string", "title": "Sub-region",
     "description": "Project sub-region: Central Asia or South Asia.",
     "constraints": {"required": True}},
    {"name": "year", "type": "integer", "title": "Reference year",
     "description": "Calendar year the value refers to.",
     "constraints": {"required": True, "minimum": 1900, "maximum": 2100}},
    {"name": "indicator_code", "type": "string", "title": "Indicator code",
     "description": "Code of the indicator as published by the source, or a project code where the source has none.",
     "constraints": {"required": True}},
    {"name": "indicator_name", "type": "string", "title": "Indicator name",
     "description": "Plain-language name of the indicator.",
     "constraints": {"required": True}},
    {"name": "value", "type": "number", "title": "Observed value",
     "description": "Value in the unit given in the unit column. Missing values are not stored as rows.",
     "constraints": {"required": True}},
    {"name": "unit", "type": "string", "title": "Unit of measure",
     "description": "Unit of the value, for example 'percent of population' or 'mm per year'.",
     "constraints": {"required": True}},
    {"name": "attribution", "type": "string", "title": "Attribution",
     "description": "How to credit the source of this row. Source details are in the source's source.yaml.",
     "constraints": {"required": True}},
]
STANDARD_COLUMNS = [f["name"] for f in STANDARD_FIELDS]
PRIMARY_KEY = ["iso3", "year", "indicator_code"]


def write_csv(df: pd.DataFrame, path) -> None:
    """Write UTF-8 CSV with Unix line endings, so the file is identical on every machine."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8", lineterminator="\n")
