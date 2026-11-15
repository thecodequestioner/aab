"""Command-line entry point.

    python -m aab build [--dataset ID | --analysis ID | --infographic ID] [--refresh]
    python -m aab validate
    python -m aab catalog
    python -m aab new {source,dataset,analysis,infographic} SLUG
    python -m aab clean
"""
import argparse
import shutil
import sys

from . import ProjectError, pipeline, scaffold, validate
from . import catalog as catalog_mod
from .config import ROOT, ANALYSES_DIR, INFOGRAPHICS_DIR


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m aab", description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    b = sub.add_parser("build", help="fetch, build, analyse, draw, catalogue and validate")
    group = b.add_mutually_exclusive_group()
    group.add_argument("--dataset", metavar="ID")
    group.add_argument("--analysis", metavar="ID")
    group.add_argument("--infographic", metavar="ID")
    b.add_argument("--refresh", action="store_true", help="re-download World Bank raw data")

    sub.add_parser("validate", help="check the repository without building")
    sub.add_parser("catalog", help="regenerate CATALOG.md")
    n = sub.add_parser("new", help="create a new item from its template")
    n.add_argument("kind", choices=sorted(scaffold.KINDS))
    n.add_argument("slug")
    sub.add_parser("clean", help="delete generated figures and results (raw and processed data are kept)")

    args = parser.parse_args(argv)
    try:
        if args.command == "build":
            kind, target = None, None
            for k in ("dataset", "analysis", "infographic"):
                if getattr(args, k):
                    kind, target = k, getattr(args, k)
            return pipeline.build(kind, target, refresh=args.refresh)
        if args.command == "validate":
            report = validate.run()
            validate.print_report(report)
            return 0 if report.ok else 1
        if args.command == "catalog":
            catalog_mod.write()
            print("wrote CATALOG.md")
            return 0
        if args.command == "new":
            print(f"Created {scaffold.new(args.kind, args.slug)}/")
            print("Next: edit the descriptor and README, then run the build for that item.")
            return 0
        if args.command == "clean":
            for base in (ANALYSES_DIR, INFOGRAPHICS_DIR):
                for out in base.glob("*/outputs"):
                    shutil.rmtree(out, ignore_errors=True)
                    out.mkdir(parents=True, exist_ok=True)
                    (out / ".gitkeep").touch()
            print("removed generated outputs; raw and processed data are kept")
            return 0
    except ProjectError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
