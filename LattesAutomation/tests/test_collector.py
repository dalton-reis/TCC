"""Testes das regras de seleção do cabeçalho de autoridade."""

from lattes_automation.collector import person_name_key


def test_person_name_key_accepts_catalog_order() -> None:
    assert person_name_key("Miguel Alexandre Wisintainer") == person_name_key(
        "Wisintainer, Miguel Alexandre"
    )


def test_person_name_key_ignores_accents_and_dates() -> None:
    assert person_name_key("Dalton Solano dos Reis") == person_name_key(
        "Reis, Dalton Solano dos, 1969-"
    )
