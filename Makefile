PY ?= python3
PYM = $(PY) -m aab

.PHONY: all build dataset analysis infographic refresh validate catalog new test clean help

help:
	@echo "make all                              build and validate everything"
	@echo "make dataset DATASET=<id>             build one dataset, and what depends on it"
	@echo "make analysis ANALYSIS=<id>           run one analysis, and its inputs"
	@echo "make infographic INFOGRAPHIC=<id>     draw one infographic, and its inputs"
	@echo "make refresh                          download World Bank data again, then build"
	@echo "make validate                         check the repository without building"
	@echo "make catalog                          regenerate CATALOG.md"
	@echo "make new KIND=<kind> SLUG=<slug>      kind: source, dataset, analysis or infographic"
	@echo "make test                             run the unit tests"
	@echo "make clean                            delete generated figures and results"

all build:
	$(PYM) build

dataset:
	@test -n "$(DATASET)" || (echo "Usage: make dataset DATASET=<id>" && exit 1)
	$(PYM) build --dataset $(DATASET)

analysis:
	@test -n "$(ANALYSIS)" || (echo "Usage: make analysis ANALYSIS=<id>" && exit 1)
	$(PYM) build --analysis $(ANALYSIS)

infographic:
	@test -n "$(INFOGRAPHIC)" || (echo "Usage: make infographic INFOGRAPHIC=<id>" && exit 1)
	$(PYM) build --infographic $(INFOGRAPHIC)

refresh:
	$(PYM) build --refresh

validate:
	$(PYM) validate

catalog:
	$(PYM) catalog

new:
	@test -n "$(KIND)" -a -n "$(SLUG)" || (echo "Usage: make new KIND=<kind> SLUG=<slug>" && exit 1)
	$(PYM) new $(KIND) $(SLUG)

test:
	$(PY) -m pytest -q

clean:
	$(PYM) clean
