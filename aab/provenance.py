"""Download logs with SHA-256 checksums: one log per source, in data/sources/<id>/RETRIEVAL_LOG.csv.

Every raw file must match the latest checksum in its log (checked by aab.validate).
The log is append-only. To correct a row, add a new row and use the note column to explain.
"""
import csv
import datetime as dt
import hashlib
from pathlib import Path

HEADER = ["retrieved_utc", "file", "source_url", "sha256", "bytes", "note"]
LOG_NAME = "RETRIEVAL_LOG.csv"


def sha256_bytes(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _append(raw_dir: Path, row: list) -> None:
    raw_dir.mkdir(parents=True, exist_ok=True)
    log = raw_dir / LOG_NAME
    is_new = not log.exists()
    with log.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        if is_new:
            writer.writerow(HEADER)
        writer.writerow(row)


def log_download(raw_dir: Path, filename: str, url: str, body: bytes, note: str = "") -> None:
    """Record a download made by the pipeline. Every download adds a row."""
    _append(raw_dir, [_now(), filename, url, sha256_bytes(body), len(body), note])


def log_existing_file(raw_dir: Path, path: Path, url: str, note: str = "") -> bool:
    """Record a file that was placed by hand. Adds a row only if its checksum is not yet logged."""
    digest = sha256_file(path)
    if digest in logged_checksums(raw_dir):
        return False
    _append(raw_dir, [_now(), path.name, url, digest, path.stat().st_size, note])
    return True


def read_log(raw_dir: Path) -> list[dict]:
    log = raw_dir / LOG_NAME
    if not log.exists():
        return []
    with log.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def logged_checksums(raw_dir: Path) -> set[str]:
    return {r["sha256"] for r in read_log(raw_dir)}


def latest_checksum(raw_dir: Path, filename: str) -> str | None:
    rows = [r for r in read_log(raw_dir) if r["file"] == filename]
    return rows[-1]["sha256"] if rows else None
