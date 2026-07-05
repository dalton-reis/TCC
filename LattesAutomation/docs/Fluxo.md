# Fluxo

1. Pesquisar o orientador na Biblioteca.
2. Percorrer a paginação e armazenar os HTMLs em `data/raw`.
3. Extrair e normalizar os registros.
4. Gerar CSV em `data/exported`.
5. Comparar com o XML exportado do Lattes e marcar `cadastrado`.
6. Revisar manualmente e marcar `revisado=true`.
7. Validar o CSV.
8. Abrir o Lattes e fazer login manualmente.
9. Abrir manualmente o formulário da orientação.
10. Preencher somente um registro revisado e ainda não cadastrado.
11. Conferir e salvar manualmente.
