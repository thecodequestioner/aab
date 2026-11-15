# Contributing

Thank you for contributing. The repository is built so that most changes touch one folder: a source, a dataset, an analysis or an infographic. Shared code changes rarely.

## What you can add

| You want to... | Read | Usual change |
|---|---|---|
| Report an error or suggest a source | the *Data issue* template | an issue |
| Add data from a new provider | [add a source](docs/guide.md) | a folder in `data/sources/` |
| Add a cleaned table | [add a dataset](docs/guide.md) | a folder in `data/datasets/` |
| Answer a question with data | [add an analysis](docs/guide.md) | a folder in `analysis/` |
| Explain a result to an audience | [add an infographic](docs/guide.md) | a folder in `infographics/` |
| Pick up a question or idea | [questions and ideas](docs/questions.md) | an issue naming the ID |
| Improve the accessibility of a figure | [accessibility checklist](docs/accessibility.md#4-pre-publication-checklist) | the figure's descriptor or README |
| Improve docs, translations or accessibility | the file itself | a pull request |

## Ground rules

1. **Only publish data you may share.** Record the source, its licence and the retrieval date.
2. **Never include confidential, personal or security-sensitive information.** Aggregate to national or district level where needed.
3. **Keep raw data raw.** Never edit a raw file or its log by hand. Download again, or change the pipeline.
4. **Use the standard.** Tidy format, the columns in `aab/tidy.py`, and the rules in [standards](docs/guide.md#2-data-and-code-standards).
5. **Generated files come from the pipeline.** `datapackage.json`, `CATALOG.md`, `outputs/` and processed tables are regenerated, never edited.
6. **Cite sources** in each source and dataset README.
7. **Write findings in plain words.** Give the year and the unit with every number. State the limits.

## Workflow

1. Fork the repository and create a branch: `data/...`, `analysis/...`, `infographic/...`, `feat/...`, `fix/...` or `docs/...`.
2. Make the change. Run `make all` and `make test`. Fix every error. Read every warning.
3. Check the generated files, the alt text and the figure at projector size.
4. Update the question or idea status and related-work link, if applicable. Record user-visible changes in `CHANGELOG.md`.
5. Open a pull request using the template. CI rebuilds everything and fails if any generated text file differs from the committed one.

## Versioning

- **Datasets** use semantic versioning in `dataset.yaml`: patch for fixes, minor for new rows or columns, major for breaking changes.
- **Analyses and infographics** have a version too. Bump it when the question, method or claim changes.
- **The repository** has one version in `project.yaml`. `CITATION.cff` and `codemeta.json` must match. The validator checks this.

## Style

- Python 3.10 or later, PEP 8, docstrings for modules and public functions.
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/), for example `data: add sanitation access dataset` or `analysis: add trend for drinking water`.
- Text is plain English, with defined terms (see the [glossary](docs/guide.md#appendix-glossary)). Accessibility rules are in [accessibility](docs/accessibility.md). Translations are welcome: Dari, Pashto, Urdu, Russian and others.

By contributing, you agree that code is released under the MIT licence and data, text and figures under CC BY 4.0.
