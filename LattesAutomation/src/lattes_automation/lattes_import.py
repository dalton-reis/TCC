"""Geração de XML para importação manual no Currículo Lattes."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree

from .models import TccRecord

_BASIC_TAG = "DADOS-BASICOS-DE-OUTRAS-ORIENTACOES-CONCLUIDAS"
_DETAIL_TAG = "DETALHAMENTO-DE-OUTRAS-ORIENTACOES-CONCLUIDAS"
_GUIDANCE_TAG = "OUTRAS-ORIENTACOES-CONCLUIDAS"


def _completed_guidance_container(root: ElementTree.Element) -> ElementTree.Element:
    other_production = root.find("OUTRA-PRODUCAO")
    if other_production is None:
        other_production = ElementTree.Element("OUTRA-PRODUCAO")
        complementary = root.find("DADOS-COMPLEMENTARES")
        if complementary is None:
            root.append(other_production)
        else:
            root.insert(list(root).index(complementary), other_production)

    completed = other_production.find("ORIENTACOES-CONCLUIDAS")
    if completed is None:
        completed = ElementTree.SubElement(other_production, "ORIENTACOES-CONCLUIDAS")
    return completed


def _next_sequence(container: ElementTree.Element) -> str:
    sequences = [
        int(value)
        for child in container
        if (value := child.get("SEQUENCIA-PRODUCAO", "")).isdigit()
    ]
    return str(max(sequences, default=0) + 1)


def _guidance_element(
    record: TccRecord,
    sequence: str,
) -> ElementTree.Element:
    guidance = ElementTree.Element(
        _GUIDANCE_TAG,
        {"SEQUENCIA-PRODUCAO": sequence},
    )
    ElementTree.SubElement(
        guidance,
        _BASIC_TAG,
        {
            "NATUREZA": "TRABALHO_DE_CONCLUSAO_DE_CURSO_GRADUACAO",
            "TIPO": "",
            "TITULO": record.title,
            "ANO": str(record.year),
            "PAIS": "Brasil",
            "IDIOMA": "Português",
            "HOME-PAGE": "",
            "FLAG-RELEVANCIA": "NAO",
            "DOI": "",
            "TITULO-INGLES": "",
            "TIPO-INGLES": "",
        },
    )
    ElementTree.SubElement(
        guidance,
        _DETAIL_TAG,
        {
            "NOME-DO-ORIENTADO": record.student_name,
            "CODIGO-INSTITUICAO": "",
            "NOME-DA-INSTITUICAO": record.institution,
            "CODIGO-CURSO": "",
            "NOME-DO-CURSO": record.course,
            "FLAG-BOLSA": "NAO",
            "CODIGO-AGENCIA-FINANCIADORA": "",
            "NOME-DA-AGENCIA": "",
            "TIPO-DE-ORIENTACAO-CONCLUIDA": "",
            "NUMERO-DE-PAGINAS": "",
            "NUMERO-ID-ORIENTADO": "",
            "NOME-DO-CURSO-INGLES": "",
        },
    )
    return guidance


def generate_import_xml(
    record: TccRecord,
    base_xml: Path,
    output: Path,
) -> Path:
    """Copia o currículo exportado e acrescenta uma orientação concluída."""
    if not record.reviewed:
        raise ValueError("O registro precisa estar marcado como revisado.")
    if record.registered_in_lattes:
        raise ValueError("O trabalho já está cadastrado no Lattes.")
    try:
        tree = ElementTree.parse(base_xml)
    except (OSError, ElementTree.ParseError) as exc:
        raise ValueError(f"Não foi possível ler o XML-base do Lattes: {exc}") from exc

    root = deepcopy(tree.getroot())
    container = _completed_guidance_container(root)
    container.append(_guidance_element(record, _next_sequence(container)))

    output.parent.mkdir(parents=True, exist_ok=True)
    ElementTree.ElementTree(root).write(
        output,
        encoding="ISO-8859-1",
        xml_declaration=True,
        short_empty_elements=True,
    )
    return output
