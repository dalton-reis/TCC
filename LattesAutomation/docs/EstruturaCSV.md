# Estrutura CSV

O arquivo usa UTF-8 com BOM e `;` como separador.
O caminho padrão é `data/exported/tccs.csv`. O nome é estável para que novas
coletas sejam registradas pelo Git como alterações do mesmo arquivo.

| Coluna | Obrigatória | Descrição |
|---|---:|---|
| `nome_aluno` | sim | Nome do aluno |
| `titulo` | sim | Título do trabalho |
| `ano` | sim | Ano entre 1900 e 2100 |
| `curso` | não | Curso |
| `instituicao` | sim | Instituição |
| `tipo_trabalho` | sim | Tipo da orientação |
| `orientador` | não | Orientador |
| `url_origem` | não | URL usada na coleta |
| `revisado` | sim | Deve ser `true` para permitir preenchimento |
| `cadastrado` | sim | `true` quando consta no XML do Lattes |

O CSV é o contrato entre a coleta e o Lattes. O módulo de coleta nunca acessa
o Lattes, e o módulo do Lattes nunca coleta dados da Biblioteca.
