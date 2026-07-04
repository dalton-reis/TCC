# Seletores

Todos os seletores externos ficam em `config/selectors.yaml`.

Devem ser preferidos, nesta ordem:

1. papéis e nomes acessíveis;
2. atributos estáveis do domínio;
3. nomes de campos;
4. CSS específico.

Seletores posicionais ou dependentes da estrutura visual devem ser evitados.
O coletor falha de forma explícita quando um campo crítico não é encontrado.

Os seletores listados em `lattes.forbidden_save` são apenas documentação e
defesa em profundidade: o código não possui método de salvar e não consulta
esses elementos durante o preenchimento.
