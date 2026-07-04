# Estrutura CSV

O arquivo usa UTF-8 com BOM e `;` como separador.

| Coluna | Obrigatória | Descrição |
|---|---:|---|
| `student_name` | sim | Nome do aluno |
| `title` | sim | Título do trabalho |
| `year` | sim | Ano entre 1900 e 2100 |
| `course` | não | Curso |
| `institution` | sim | Instituição |
| `work_type` | sim | Tipo da orientação |
| `advisor` | não | Orientador |
| `source_url` | não | URL usada na coleta |
| `reviewed` | sim | Deve ser `true` para permitir preenchimento |

O CSV é o contrato entre a coleta e o Lattes. O módulo de coleta nunca acessa
o Lattes, e o módulo do Lattes nunca coleta dados da Biblioteca.
