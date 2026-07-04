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


def _author_name(value: str) -> str:
    """Remove datas catalográficas e converte ``Sobrenome, Nome``."""
    value = re.sub(r",?\s*\d{4}\s*-\s*(?:\d{4})?\s*$", "", value).strip(" ,")
    parts = [part.strip() for part in value.split(",") if part.strip()]
    if len(parts) == 2:
        return f"{parts[1]} {parts[0]}"
    return value


def extract_record(html: str, source_url: str = "") -> TccRecord:
    """Converte uma página de detalhes em :class:`TccRecord`."""
    soup = BeautifulSoup(html, "html.parser")
    values = extract_labeled_values(html)
    rows = [
        (
            _normalize(cells[0].get_text(" ", strip=True)),
            cells[1].get_text(" ", strip=True),
        )
        for row in soup.select("tr")
        if len(cells := row.find_all(["th", "td"])) >= 2
    ]
    title = _find_value(values, "title")
    if not title:
        heading = soup.select_one("h1")
        title = heading.get_text(" ", strip=True) if heading else ""
    bibliographic_title = title
    title = re.split(r"\s*/\s*", title, maxsplit=1)[0]
    title = re.sub(r"\s*\[recurso eletrônico\]\s*", " ", title, flags=re.IGNORECASE)
    raw_year = _find_value(values, "year")
    year_match = re.search(r"\b(19|20)\d{2}\b", raw_year)
    if year_match is None:
        year_match = re.search(r"\b(19|20)\d{2}\b", bibliographic_title)
    if year_match is None:
        raise ValueError("Ano não encontrado na página do trabalho.")
    notes = " ".join(value for label, value in rows if label == "notas")
    advisor_match = re.search(
        r"orientador(?:a)?\s*:\s*([^.;]+(?:\s+[^.;]+)*)",
        notes,
        flags=re.IGNORECASE,
    )
    secondary_authors = [
        value for label, value in rows if label == "autor secundario"
    ]
    course = ""
    for value in secondary_authors:
        course_match = re.search(r"\bCurso de (.+?)[.]?$", value, flags=re.IGNORECASE)
        if course_match:
            course = course_match.group(1)
            break
    return TccRecord(
        student_name=_author_name(_find_value(values, "student_name")),
        title=title,
        year=int(year_match.group()),
        course=course or _find_value(values, "course"),
        institution=_find_value(values, "institution")
        or "Universidade Regional de Blumenau",
        work_type=_find_value(values, "work_type")
        or "Trabalho de conclusão de curso de graduação",
        advisor=advisor_match.group(1) if advisor_match else _find_value(values, "advisor"),
        source_url=source_url,
    )
