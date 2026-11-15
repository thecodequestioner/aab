# Project decisions

This page explains decisions that shape the repository and the reasoning behind them. Record choices that help contributors understand or maintain the project, including significant changes to earlier decisions and their consequences. Use the changelog for release-by-release updates; this page focuses on rationale rather than a complete development history.

## Organize content by purpose

- **Sources** hold provider files and document their origin and terms.
- **Datasets** are cleaned, documented tables derived from sources.
- **Analyses** answer questions using datasets and explain the methods and limitations.
- **Infographics** communicate findings to a specific audience.

## Keep source and generated files distinct

- Preserve downloaded source files unchanged; record their provenance in the source documentation and retrieval log.
- Regenerate processed tables, catalogues, and analysis outputs with the project's tools rather than editing generated files by hand.
- Keep interpretation, methods, and limitations in the relevant item README.

## Define regional coverage consistently

Use the country group in `aab/countries.csv` as the shared definition of the project's Central and South Asia coverage. Document any exceptions in the relevant dataset or analysis.

## Check source terms

Document the source, attribution, and reuse terms for each provider. Check those terms before adding or redistributing third-party data or material derived from it.
