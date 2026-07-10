"""Testes da geração de XML para importação manual."""

from pathlib import Path
from xml.etree import ElementTree

import pytest

from lattes_automation.lattes_import import generate_import_xml
from lattes_automation.models import TccRecord


def _base_xml(path: Path) -> None:
    path.write_text(
        """<?xml version="1.0" encoding="ISO-8859-1"?>
        <CURRICULO-VITAE SISTEMA-ORIGEM-XML="LATTES_OFFLINE">
          <DADOS-GERAIS NOME-COMPLETO="Pessoa"/>
          <OUTRA-PRODUCAO>
            <ORIENTACOES-CONCLUIDAS>
              <OUTRAS-ORIENTACOES-CONCLUIDAS SEQUENCIA-PRODUCAO="4"/>
            </ORIENTACOES-CONCLUIDAS>
          </OUTRA-PRODUCAO>
        </CURRICULO-VITAE>""",
        encoding="iso-8859-1",
    )


def test_generate_import_xml_adds_one_guidance(tmp_path: Path) -> None:
    base = tmp_path / "base.xml"
    output = tmp_path / "import.xml"
    _base_xml(base)
    record = TccRecord(
        student_name="João da Silva",
        title="Aplicação gráfica",
        year=2025,
        course="Ciência da Computação",
        reviewed=True,
    )
    generate_import_xml(record, base, output)
    root = ElementTree.parse(output).getroot()
    items = root.findall(".//OUTRAS-ORIENTACOES-CONCLUIDAS")
    assert len(items) == 2
    assert items[-1].get("SEQUENCIA-PRODUCAO") == "5"
    assert items[-1].find(_basic_tag()).get("TITULO") == "Aplicação gráfica"


def _basic_tag() -> str:
    return "DADOS-BASICOS-DE-OUTRAS-ORIENTACOES-CONCLUIDAS"


def test_generate_import_xml_rejects_unreviewed_record(tmp_path: Path) -> None:
    record = TccRecord(student_name="Aluno", title="TCC", year=2025)
    with pytest.raises(ValueError, match="revisado"):
        generate_import_xml(record, tmp_path / "base.xml", tmp_path / "out.xml")
