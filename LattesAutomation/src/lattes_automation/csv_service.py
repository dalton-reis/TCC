"""Persistência do arquivo intermediário em CSV."""

from __future__ import annotations

import csv
from collections.abc import Iterable
from pathlib import Path

from .models import TccRecord


def write_records(records: Iterable[TccRecord], path: Path) -> int:
    """Grava registros em UTF-8 com BOM, adequado ao Excel em português."""
    items = list(records)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=TccRecord.csv_fields(), delimiter=";")
        writer.writeheader()
        writer.writerows(record.to_dict() for record in items)
    return len(items)


def read_records(path: Path) -> list[TccRecord]:
    """Lê e valida registros de um CSV intermediário."""
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter=";")
        expected = set(TccRecord.csv_fields())
        missing = expected - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"Colunas ausentes no CSV: {', '.join(sorted(missing))}.")
        return [TccRecord.from_dict(row) for row in reader]
