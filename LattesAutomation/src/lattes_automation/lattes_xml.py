"""Comparação de TCCs com um currículo Lattes exportado em XML."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, replace
from pathlib import Path
from xml.etree import ElementTree

from .models import TccRecord

_TCC_GRADUACAO = "TRABALHO_DE_CONCLUSAO_DE_CURSO_GRADUACAO"


@dataclass(frozen=True, slots=True)
class LattesGuidance:
    """Identificação mínima de uma orientação concluída."""

    student_name: str
    title: str
    year: int


def _normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    ascii_value = value.encode("ascii", "ignore").decode().casefold()
    return " ".join(re.findall(r"[a-z0-9]+", ascii_value))


def _key(student_name: str, title: str, year: int) -> tuple[str, str, int]:
    return (_normalize(student_name), _normalize(title), year)


def read_completed_tccs(path: Path) -> list[LattesGuidance]:
    """Lê somente TCCs de graduação concluídos no XML do Lattes."""
    try:
        root = ElementTree.parse(path).getroot()
    except (OSError, ElementTree.ParseError) as exc:
        raise ValueError(f"Não foi possível ler o XML do Lattes: {exc}") from exc

    guidance: list[LattesGuidance] = []
    for item in root.findall(".//OUTRAS-ORIENTACOES-CONCLUIDAS"):
        basic = item.find("DADOS-BASICOS-DE-OUTRAS-ORIENTACOES-CONCLUIDAS")
        details = item.find("DETALHAMENTO-DE-OUTRAS-ORIENTACOES-CONCLUIDAS")
        if basic is None or details is None:
            continue
        if basic.get("NATUREZA") != _TCC_GRADUACAO:
            continue
        title = basic.get("TITULO", "").strip()
        student_name = details.get("NOME-DO-ORIENTADO", "").strip()
        raw_year = basic.get("ANO", "")
        if title and student_name and raw_year.isdigit():
            guidance.append(LattesGuidance(student_name, title, int(raw_year)))
    return guidance


def mark_registered(records: list[TccRecord], xml_path: Path) -> list[TccRecord]:
    """Marca correspondências exatas normalizadas por aluno, título e ano."""
    registered_keys = {
        _key(item.student_name, item.title, item.year)
        for item in read_completed_tccs(xml_path)
    }
    return [
        replace(
            record,
            registered_in_lattes=_key(
                record.student_name, record.title, record.year
            )
            in registered_keys,
        )
        for record in records
    ]
