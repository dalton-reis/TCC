"""Testes das regras de validação."""

from lattes_automation.models import TccRecord
from lattes_automation.validation import validate_records


def test_duplicate_is_error() -> None:
    record = TccRecord(student_name="Ana", title="TCC", year=2025)
    issues = validate_records([record, record])
    assert any(issue.severity == "erro" for issue in issues)
