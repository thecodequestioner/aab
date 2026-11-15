# Water in Central and South Asia

Open data, analyses and infographics on water in Central and South Asia. Every number traces back to a published source, through a cleaned table, to the result you see.

**Name:** *aab* (آب) is the Persian word for water. The Python package is `aab`.

**Author:** The{code}questioner · **Licence:** code MIT, data and text CC BY 4.0

## Start here

| If you want to... | Go to                                    |
|---|------------------------------------------|
| See the story in pictures | [Infographics](infographics/)            |
| Check how a conclusion was reached | [Analysis](analysis/)                    |
| Download or reuse the numbers | [Datasets](data/datasets/)               |
| Find out where the data came from | [Sources](data/sources/)                 |
| Browse everything in one list | [CATALOG.md](CATALOG.md)                 |
| Learn the words, standards and how to add to it | [Guide](docs/guide.md)                   |
| Check accessibility rules and the publication checklist | [Accessibility](docs/accessibility.md)   |
| Browse the question bank and ideas | [Questions and ideas](docs/questions.md) |
| See how the project is organized | [Project decisions](docs/decisions.md)   |

## Layout

```
data/
  sources/      where the data comes from: one folder per provider, raw files unchanged
  datasets/     cleaned, documented tables: one folder per table
analysis/       one question per folder: findings, method, results
infographics/   one answer per folder, for one audience
docs/           guide, accessibility, questions and ideas, decisions
aab/            the pipeline (Python package)
tests/          unit tests
```

Each item is one folder with a `README.md` (for people) and one descriptor (`source.yaml`, `dataset.yaml`, `analysis.yaml` or `infographic.yaml`, for the pipeline). Files in `outputs/` and the `*.csv` and `datapackage.json` files in dataset folders are generated. Do not edit them by hand.

## Set up and rebuild

You only need to install Python packages if you want to rebuild the project or run its tests. The CSV files can be used directly.

The project requires Python 3.10 or later. Python 3.11 is used in the automated checks. Run commands from the repository folder containing `pyproject.toml`.

### Anaconda or Miniconda

In Anaconda Prompt or the PyCharm Terminal:
```bash
conda create -n aab python=3.11
conda activate aab
python -m pip install -r requirements-dev.txt
```

If you already have an environment for this project, activate it and skip the `conda create` command.

### Standard Python environment

Create and activate a virtual environment:
```bash
python -m venv .venv
```

Activate it with the command for your system:
```text
Windows PowerShell:  .venv\Scripts\Activate.ps1
Windows Command Prompt:  .venv\Scripts\activate.bat
macOS or Linux:  source .venv/bin/activate
```

Then install the requirements:
```bash
python -m pip install -r requirements-dev.txt
```

### Build and test

These Python commands work across operating systems and don’t require Make:
```bash
python -m aab build
python -m pytest -q
```

To validate without rebuilding:
```bash
python -m aab validate
```

To rebuild one analysis and its inputs:
```bash
python -m aab build --analysis water-access-ranking
```

### Optional Make shortcuts

If GNU Make is installed, you can use these shortcuts instead:
```bash
make all
make test
make validate
make analysis ANALYSIS=water-access-ranking
```

On Windows, if `python3` is not recognized by Make, use `make PY=python` before the target, for example:
```bash
make PY=python all
```


## Using the data

1. Open a dataset's folder and read its `README.md`. It states the source, the licence, the years and the known limits.
2. Use the CSV file in that folder. Each row is one value for one country and year.
3. Cite the dataset and the original source named in it. [CITATION.cff](CITATION.cff) gives the citation for the repository.

## Accessibility

- Every infographic has alternative text in its descriptor, and the catalogue shows it under each image.
- Findings give the year and unit with each number, and state the limits.
- Charts use colour-blind-safe colours and label their key values directly.

The full rules, the colour reference and the checklist are in [docs/accessibility.md](docs/accessibility.md).

## Limits

These are summary figures from international estimates, not measurements by this project. Check the limits stated in each dataset and analysis before you use a number.

## Contribute and cite

- [CONTRIBUTING.md](CONTRIBUTING.md): how to report, add and review.
- [CHANGELOG.md](CHANGELOG.md): notable public changes to the repository.
- [LICENSE](LICENSE) (code) and [LICENSE-DATA](LICENSE-DATA) (data, text and figures). [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
