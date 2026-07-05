"""Persistência do arquivo intermediário em CSV."""

from __future__ import annotations

import csv
import unicodedata
from collections.abc import Iterable
from pathlib import Path

from .models import TccRecord

CSV_COLUMNS = {
    "student_name": "nome_aluno",
    "title": "titulo",
    "year": "ano",
    "course": "curso",
    "institution": "instituicao",
    "work_type": "tipo_trabalho",
    "advisor": "orientador",
    "source_url": "url_origem",
    "reviewed": "revisado",
    "registered_in_lattes": "cadastrado",
}


def sort_records(records: Iterable[TccRecord]) -> list[TccRecord]:
    """Ordena por ano e nome do aluno, ignorando caixa e acentuação."""

    def normalized_name(record: TccRecord) -> str:
        value = unicodedata.normalize("NFKD", record.student_name)
        return value.encode("ascii", "ignore").decode().casefold()

    return sorted(records, key=lambda record: (record.year, normalized_name(record)))


def _csv_row(record: TccRecord) -> dict[str, str | int]:
    values = record.to_dict()
    return {
        csv_name: (
            str(values[internal_name]).lower()
            if isinstance(values[internal_name], bool)
            else values[internal_name]
        )
        for internal_name, csv_name in CSV_COLUMNS.items()
    }


def write_records(records: Iterable[TccRecord], path: Path) -> int:
    """Grava registros em UTF-8 com BOM, adequado ao Excel em português."""
    items = list(records)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=CSV_COLUMNS.values(),
            delimiter=";",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(_csv_row(record) for record in items)
    return len(items)


def read_records(path: Path) -> list[TccRecord]:
    """Lê e valida registros de um CSV intermediário."""
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter=";")
        available = set(reader.fieldnames or ())
        required = set(TccRecord.csv_fields()) - {"registered_in_lattes"}
        missing = {
            CSV_COLUMNS[field]
            for field in required
            if CSV_COLUMNS[field] not in available and field not in available
        }
        if missing:
            raise ValueError(f"Colunas ausentes no CSV: {', '.join(sorted(missing))}.")
        records: list[TccRecord] = []
        for row in reader:
            internal_row = {
                internal_name: row.get(csv_name, row.get(internal_name, ""))
                for internal_name, csv_name in CSV_COLUMNS.items()
            }
            records.append(TccRecord.from_dict(internal_row))
        return records
