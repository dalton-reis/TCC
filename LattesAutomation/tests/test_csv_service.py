"""Testes do contrato CSV."""

from pathlib import Path

from lattes_automation.csv_service import read_records, sort_records, write_records
from lattes_automation.models import TccRecord


def test_csv_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "records.csv"
    original = TccRecord(
        student_name="Ana Silva",
        title="Um TCC",
        year=2025,
        reviewed=True,
        registered_in_lattes=True,
    )
    assert write_records([original], path) == 1
    assert read_records(path) == [original]
    header = path.read_text(encoding="utf-8-sig").splitlines()[0]
    assert header == (
        "nome_aluno;titulo;ano;curso;instituicao;tipo_trabalho;orientador;"
        "url_origem;revisado;cadastrado"
    )


def test_sort_records_by_year_then_student_name() -> None:
    records = [
        TccRecord(student_name="Zélia", title="C", year=2024),
        TccRecord(student_name="Álvaro", title="B", year=2024),
        TccRecord(student_name="Carlos", title="A", year=2023),
    ]
    result = sort_records(records)
    assert [(record.year, record.student_name) for record in result] == [
        (2023, "Carlos"),
        (2024, "Álvaro"),
        (2024, "Zélia"),
    ]
