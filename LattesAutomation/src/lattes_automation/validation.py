"""Validação dos dados coletados."""

from __future__ import annotations

from dataclasses import dataclass

from .models import TccRecord


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """Problema encontrado em um registro."""

    row: int
    severity: str
    message: str


def validate_records(records: list[TccRecord]) -> list[ValidationIssue]:
    """Detecta campos incompletos e duplicidades prováveis."""
    issues: list[ValidationIssue] = []
    seen: dict[tuple[str, str, int], int] = {}
    for row, record in enumerate(records, start=2):
        key = (record.student_name.casefold(), record.title.casefold(), record.year)
        if key in seen:
            issues.append(
                ValidationIssue(row, "erro", f"Possível duplicata da linha {seen[key]}.")
            )
        else:
            seen[key] = row
        if not record.course:
            issues.append(ValidationIssue(row, "aviso", "Curso não informado."))
        if not record.advisor:
            issues.append(ValidationIssue(row, "aviso", "Orientador não informado."))
        if not record.source_url:
            issues.append(ValidationIssue(row, "aviso", "URL de origem não informada."))
    return issues
