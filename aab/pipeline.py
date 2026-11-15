"""Runs the steps in dependency order:

  sources  ->  datasets  ->  analyses  ->  infographics  ->  catalogue  ->  validation

A targeted build (for example --analysis X) rebuilds only what X needs, and anything
that depends on the rebuilt items. Raw data is fetched only if it is missing, unless
--refresh is given.
"""
from dataclasses import dataclass, field

from . import ProjectError
from . import analyses as analyses_mod
from . import catalog, datasets as datasets_mod, infographics as infographics_mod, sources as sources_mod, validate
from .config import rel


@dataclass
class Plan:
    sources: set = field(default_factory=set)
    datasets: set = field(default_factory=set)
    analyses: set = field(default_factory=set)
    infographics: set = field(default_factory=set)


def make_plan(kind: str | None, target: str | None) -> Plan:
    """Work out which items a targeted build touches. kind is dataset, analysis, infographic or None."""
    all_sources = sources_mod.load_all()
    all_datasets = datasets_mod.load_all()
    all_analyses = analyses_mod.load_all()
    all_infos = infographics_mod.load_all()
    if kind is None:
        return Plan(set(all_sources), set(all_datasets), set(all_analyses), set(all_infos))

    plan = Plan()
    if kind == "dataset":
        plan.datasets.add(target)
    elif kind == "analysis":
        plan.analyses.add(target)
    elif kind == "infographic":
        plan.infographics.add(target)
    else:
        raise ProjectError(f"unknown kind {kind}")

    # Upstream: what the target needs
    changed = True
    while changed:
        changed = False
        for ds_id in list(plan.datasets):
            for sid in all_datasets[ds_id].source_ids:
                if sid not in plan.sources:
                    plan.sources.add(sid); changed = True
        for a_id in list(plan.analyses):
            for ds_id in all_analyses[a_id].dataset_ids:
                if ds_id not in plan.datasets:
                    plan.datasets.add(ds_id); changed = True
        for i_id in list(plan.infographics):
            for ds_id in all_infos[i_id].datasets:
                if ds_id not in plan.datasets:
                    plan.datasets.add(ds_id); changed = True
            for a_id in all_infos[i_id].analyses:
                if a_id not in plan.analyses:
                    plan.analyses.add(a_id); changed = True

    # Downstream: what depends on the rebuilt items
    for a in all_analyses.values():
        if set(a.dataset_ids) & plan.datasets:
            plan.analyses.add(a.id)
    for i in all_infos.values():
        if set(i.datasets) & plan.datasets or set(i.analyses) & plan.analyses:
            plan.infographics.add(i.id)
    return plan


def execute(plan: Plan, refresh: bool = False) -> None:
    all_sources = sources_mod.load_all()
    all_datasets = datasets_mod.load_all()
    all_analyses = analyses_mod.load_all()
    all_infos = infographics_mod.load_all()

    print("\n== Sources")
    for sid in sorted(plan.sources):
        print(f"-- {sid}")
        sources_mod.fetch(sources_mod.get(all_sources, sid), refresh=refresh)

    print("\n== Datasets")
    for ds_id in sorted(plan.datasets):
        ds = datasets_mod.get(all_datasets, ds_id)
        print(f"-- {ds_id}")
        df = datasets_mod.build(ds, all_sources)
        datasets_mod.write(ds, df, all_sources)
        print(f"  wrote {rel(ds.processed_csv)} ({len(df)} rows) and datapackage.json")

    print("\n== Analyses")
    for a_id in sorted(plan.analyses):
        print(f"-- {a_id}")
        analyses_mod.run(all_analyses[a_id], all_datasets)
        print("  wrote figure, table, summary and results")

    print("\n== Infographics")
    for i_id in sorted(plan.infographics):
        print(f"-- {i_id}")
        infographics_mod.run(all_infos[i_id])

    print("\n== Catalogue")
    catalog.write()
    print("  wrote CATALOG.md")


def build(kind: str | None = None, target: str | None = None, refresh: bool = False) -> int:
    plan = make_plan(kind, target)
    execute(plan, refresh=refresh)
    print("\n== Validation")
    report = validate.run()
    validate.print_report(report)
    return 0 if report.ok else 1
