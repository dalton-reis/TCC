"""Testes do contrato CSV."""

from pathlib import Path

from lattes_automation.csv_service import read_records, write_records
from lattes_automation.models import TccRecord


def test_csv_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "records.csv"
    original = TccRecord(
        student_name="Ana Silva",
        title="Um TCC",
        year=2025,
        reviewed=True,
    )
    assert write_records([original], path) == 1
    assert read_records(path) == [original]
