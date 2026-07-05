"""Testes da comparação com o XML exportado pelo Lattes."""

from pathlib import Path

from lattes_automation.lattes_xml import mark_registered, read_completed_tccs
from lattes_automation.models import TccRecord


def test_marks_normalized_exact_match(tmp_path: Path) -> None:
    xml_path = tmp_path / "lattes.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
        <CURRICULO-VITAE><ORIENTACOES-CONCLUIDAS>
          <OUTRAS-ORIENTACOES-CONCLUIDAS>
            <DADOS-BASICOS-DE-OUTRAS-ORIENTACOES-CONCLUIDAS
              NATUREZA="TRABALHO_DE_CONCLUSAO_DE_CURSO_GRADUACAO"
              TITULO="Aplicação gráfica" ANO="2025"/>
            <DETALHAMENTO-DE-OUTRAS-ORIENTACOES-CONCLUIDAS
              NOME-DO-ORIENTADO="João da Silva"/>
          </OUTRAS-ORIENTACOES-CONCLUIDAS>
        </ORIENTACOES-CONCLUIDAS></CURRICULO-VITAE>""",
        encoding="utf-8",
    )
    records = [
        TccRecord(
            student_name="Joao da Silva",
            title="APLICACAO GRAFICA",
            year=2025,
        ),
        TccRecord(student_name="Outra Pessoa", title="Outro TCC", year=2025),
    ]
    result = mark_registered(records, xml_path)
    assert len(read_completed_tccs(xml_path)) == 1
    assert result[0].registered_in_lattes is True
    assert result[1].registered_in_lattes is False
