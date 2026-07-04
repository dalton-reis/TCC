"""Testes da extração independente do navegador."""

from lattes_automation.extraction import extract_record


def test_extract_record_from_table() -> None:
    html = """
    <html><body><h1>Título alternativo</h1><table>
      <tr><th>Autor:</th><td>Ana da Silva</td></tr>
      <tr><th>Título:</th><td>Automação responsável</td></tr>
      <tr><th>Ano:</th><td>2025</td></tr>
      <tr><th>Curso:</th><td>Ciência da Computação</td></tr>
      <tr><th>Orientador:</th><td>Prof. Exemplo</td></tr>
    </table></body></html>
    """
    record = extract_record(html, "https://example.test/1")
    assert record.student_name == "Ana da Silva"
    assert record.title == "Automação responsável"
    assert record.year == 2025
    assert record.course == "Ciência da Computação"
    assert record.source_url == "https://example.test/1"
