# LattesAutomation

Coleta TCCs da Biblioteca da FURB, gera um CSV para revisão e auxilia o
preenchimento do Currículo Lattes com Playwright.

> O programa nunca aciona o botão **Salvar**. Somente registros marcados como
> revisados no CSV podem ser preenchidos.

## Instalação

Requer Python 3.14.

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
playwright install chromium
```

## Configuração

Revise `config/config.yaml` e ajuste `config/selectors.yaml` aos seletores
atuais da Biblioteca e do Lattes. Os seletores incluídos são conservadores e
servem como ponto de partida; portais institucionais podem mudar sem aviso.

## Uso

```bash
# Biblioteca → CSV
lattes-automation collect --advisor "Dalton Solano dos Reis"

# Validar o arquivo depois da revisão manual
lattes-automation validate data/exported/tccs.csv

# Preencher a primeira linha de dados revisada (sem salvar)
lattes-automation fill data/exported/tccs.csv --row 1
```

No CSV, altere `reviewed` para `true` somente após conferir o registro.
Novas coletas sobrescrevem `data/exported/tccs.csv`, permitindo que o Git
registre somente as diferenças entre as versões sucessivas dos dados.

## Testes

```bash
pytest
ruff check .
mypy
```
