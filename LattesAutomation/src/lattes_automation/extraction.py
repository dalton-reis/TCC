"""Extração tolerante a variações de páginas bibliográficas."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping

from bs4 import BeautifulSoup

from .models import TccRecord

_LABEL_ALIASES = {
    "student_name": ("autor", "aluno", "discente"),
    "title": ("titulo",),
    "year": ("ano", "data", "publicacao"),
    "course": ("curso",),
    "institution": ("instituicao", "universidade"),
    "work_type": ("tipo", "natureza"),
    "advisor": ("orientador", "orientacao"),
}


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return " ".join(
        normalized.encode("ascii", "ignore").decode().lower().replace(":", " ").split()
    )


def extract_labeled_values(html: str) -> dict[str, str]:
    """Extrai pares rótulo/valor de tabelas, listas de definição e metadados."""
    soup = BeautifulSoup(html, "html.parser")
    pairs: dict[str, str] = {}
    for row in soup.select("tr"):
        cells = row.find_all(["th", "td"])
        if len(cells) >= 2:
            pairs[_normalize(cells[0].get_text(" ", strip=True))] = cells[1].get_text(
                " ", strip=True
            )
    for term in soup.select("dt"):
        description = term.find_next_sibling("dd")
        if description:
            pairs[_normalize(term.get_text(" ", strip=True))] = description.get_text(
                " ", strip=True
            )
    for meta in soup.select("meta[name][content]"):
        name = str(meta.get("name", ""))
        content = str(meta.get("content", ""))
        pairs[_normalize(name)] = content
    return pairs


def _find_value(values: Mapping[str, str], field: str) -> str:
    aliases = _LABEL_ALIASES[field]
    for label, value in values.items():
        if any(alias in label for alias in aliases):
            return value
    return ""


def extract_record(html: str, source_url: str = "") -> TccRecord:
    """Converte uma página de detalhes em :class:`TccRecord`."""
    soup = BeautifulSoup(html, "html.parser")
    values = extract_labeled_values(html)
    title = _find_value(values, "title")
    if not title:
        heading = soup.select_one("h1")
        title = heading.get_text(" ", strip=True) if heading else ""
    raw_year = _find_value(values, "year")
    year_match = re.search(r"\b(19|20)\d{2}\b", raw_year)
    if year_match is None:
        year_match = re.search(r"\b(19|20)\d{2}\b", soup.get_text(" ", strip=True))
    if year_match is None:
        raise ValueError("Ano não encontrado na página do trabalho.")
    return TccRecord(
        student_name=_find_value(values, "student_name"),
        title=title,
        year=int(year_match.group()),
        course=_find_value(values, "course"),
        institution=_find_value(values, "institution")
        or "Universidade Regional de Blumenau",
        work_type=_find_value(values, "work_type")
        or "Trabalho de conclusão de curso de graduação",
        advisor=_find_value(values, "advisor"),
        source_url=source_url,
    )
