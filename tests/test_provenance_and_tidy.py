"""Checks for the provenance log, the country registry and the tidy-table rules."""
import pandas as pd
import pytest

from aab import ProjectError
from aab.countries import select
from aab.provenance import latest_checksum, log_existing_file, read_log, sha256_bytes
from aab.tidy import PRIMARY_KEY, STANDARD_COLUMNS, STANDARD_FIELDS


def test_log_existing_file_adds_one_row_per_checksum(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    f = raw / "data.csv"
    f.write_text("a,b\n1,2\n", encoding="utf-8")
    assert log_existing_file(raw, f, "https://example.org/data") is True
    assert log_existing_file(raw, f, "https://example.org/data") is False
    rows = read_log(raw)
    assert len(rows) == 1
    assert rows[0]["sha256"] == sha256_bytes(f.read_bytes())
    assert latest_checksum(raw, "data.csv") == rows[0]["sha256"]


def test_changed_file_is_not_matched_by_old_checksum(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    f = raw / "data.csv"
    f.write_text("v1", encoding="utf-8")
    log_existing_file(raw, f, "https://example.org/")
    f.write_text("v2", encoding="utf-8")
    assert latest_checksum(raw, "data.csv") != sha256_bytes(f.read_bytes())


def test_country_groups_select_expected_members():
    south = {r["iso3"] for r in select("south_asia")}
    central = {r["iso3"] for r in select("central_asia")}
    assert "AFG" in south and "KAZ" in central
    assert not (south & central)
    assert len(select("central_and_south_asia")) == 13


def test_unknown_group_is_a_clear_error():
    with pytest.raises(ProjectError):
        select("no_such_group")


def test_standard_fields_are_documented_and_keyed():
    assert STANDARD_COLUMNS[0] == "iso3"
    assert all(f.get("description") for f in STANDARD_FIELDS)
    assert PRIMARY_KEY == ["iso3", "year", "indicator_code"]
    assert "source" not in STANDARD_COLUMNS and "attribution" in STANDARD_COLUMNS
