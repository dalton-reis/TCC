# 📘 Modelos de Prompt para Revisar Código do Workspace (VSCode + Codex)

```text
Revise todo este workspace em modo somente leitura.
Objetivo: encontrar bugs, riscos de regressão, code smells e melhorias de performance/manutenibilidade.
Restrições:
- não alterar o que o código se propõe a fazer
- não mudar API pública
- não editar arquivos sem minha autorização
Saída esperada:
- lista de achados por severidade (alto/médio/baixo)
- arquivo + linha
- explicação curta do impacto
- sugestão de correção mínima
- lacunas de testes
Ação: “primeiro só relatório; depois eu aprovo correções”.

Escopo: “Revise só CG_N2_Exemplo” ou “só CG_Biblioteca”.
Foco: “foco em matemática geométrica”, “foco em OpenGL/shaders”, “foco em arquitetura”.
```
