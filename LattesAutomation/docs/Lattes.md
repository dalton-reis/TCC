# Lattes

## Importação por XML

```bash
lattes-automation import-lattes data/exported/tccs.csv --row 1
```

O comando usa o currículo indicado por `lattes.export_xml` como base e gera
`data/exported/import_lattes.xml`. A linha precisa estar com `revisado=true` e
`cadastrado=false`.

O arquivo gerado contém uma cópia completa do currículo e uma nova
`OUTRAS-ORIENTACOES-CONCLUIDAS`, conforme o DTD do CNPq. O programa não abre a
tela de importação, não envia o arquivo e não confirma alterações no Lattes.
Revise o XML e faça a importação manualmente.
