"""aab: shared code for the Central and South Asia water data repository.

Modules
-------
config      paths, YAML loading, discovery of sources, datasets, analyses and infographics
countries   country registry (ISO 3166-1 alpha-3) and country groups
tidy        the standard long (tidy) table every dataset uses
provenance  download logs with SHA-256 checksums
sources     upstream sources: fetching and reading raw files
datasets    cleaned, documented tables built from one or more sources
stats       trend statistics (Mann-Kendall test, Sen's slope)
analyses    question-driven analyses that read one or more datasets
validate    checks on sources, datasets, analyses, infographics and generated files
pipeline    runs the steps in dependency order
catalog     writes CATALOG.md, the showcase index
"""

__version__ = "0.1.0"


class ProjectError(Exception):
    """A problem in the repository's content or configuration, with a message a contributor can act on."""
