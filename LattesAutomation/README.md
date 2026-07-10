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

# Atualizar a coluna cadastrado usando o XML do Lattes
lattes-automation sync-lattes data/exported/tccs.csv

# Gerar XML para importar manualmente a primeira linha revisada
lattes-automation import-lattes data/exported/tccs.csv --row 1

# Preencher a primeira linha de dados revisada (sem salvar)
lattes-automation fill data/exported/tccs.csv --row 1
```

No CSV, altere `revisado` para `true` somente após conferir o registro.
A coluna `cadastrado` é atualizada pela comparação com o XML configurado em
`lattes.export_xml`. Registros já cadastrados são bloqueados pelo comando `fill`.
O comando `import-lattes` gera uma cópia completa do currículo XML com um novo
registro, mas nunca envia o arquivo ao site.
Novas coletas sobrescrevem `data/exported/tccs.csv`, permitindo que o Git
registre somente as diferenças entre as versões sucessivas dos dados.

## Testes

```bash
pytest
ruff check .
mypy
```
