"""Modelos de dados do domínio."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields


@dataclass(frozen=True, slots=True)
class TccRecord:
    """Representa um TCC coletado e revisável antes do Lattes."""

    student_name: str
    title: str
    year: int
    course: str = ""
    institution: str = "Universidade Regional de Blumenau"
    work_type: str = "Trabalho de conclusão de curso de graduação"
    advisor: str = ""
    source_url: str = ""
    reviewed: bool = False

    def __post_init__(self) -> None:
        """Normaliza strings e rejeita registros obviamente inválidos."""
        for field_name in (
            "student_name",
            "title",
            "course",
            "institution",
            "work_type",
            "advisor",
            "source_url",
        ):
            value = getattr(self, field_name)
            object.__setattr__(self, field_name, " ".join(value.split()))
        if not self.student_name:
            raise ValueError("Nome do aluno é obrigatório.")
        if not self.title:
            raise ValueError("Título é obrigatório.")
        if not 1900 <= self.year <= 2100:
            raise ValueError(f"Ano inválido: {self.year}.")

    @classmethod
    def csv_fields(cls) -> tuple[str, ...]:
        """Retorna a ordem estável das colunas do CSV."""
        return tuple(field.name for field in fields(cls))

    def to_dict(self) -> dict[str, str | int | bool]:
        """Converte o registro para serialização."""
        return asdict(self)

    @classmethod
    def from_dict(cls, row: dict[str, str]) -> TccRecord:
        """Cria um registro a partir de uma linha do CSV."""
        return cls(
            student_name=row["student_name"],
            title=row["title"],
            year=int(row["year"]),
            course=row.get("course", ""),
            institution=row.get("institution", ""),
            work_type=row.get("work_type", ""),
            advisor=row.get("advisor", ""),
            source_url=row.get("source_url", ""),
            reviewed=row.get("reviewed", "").strip().lower() in {"1", "true", "sim", "yes"},
        )
