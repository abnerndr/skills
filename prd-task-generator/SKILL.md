---
name: prd-task-generator
description: >
  Gera task lists detalhadas em Markdown a partir de um PRD (Product Requirements Document).
  Use esta skill sempre que o usuário mencionar PRD, task list, lista de tarefas, backlog técnico,
  breakdown de features, ou pedir para "transformar um PRD em tarefas", "gerar tasks de um PRD",
  ou "decompor requisitos em sub-tarefas". Também deve disparar quando o usuário compartilhar um
  documento de requisitos e perguntar o que precisa ser implementado.
---

# PRD Task Generator

Gera task lists estruturadas em Markdown a partir de um PRD, guiando desenvolvedores através da implementação de forma incremental e validada.

## Processo em 2 Fases

### Fase 1 — Parent Tasks

1. Leia e analise o PRD: requisitos funcionais, user stories e restrições técnicas
2. Crie o arquivo `/tasks/tasks-[prd-file-name].md`
3. Gere **~5 parent tasks** de alto nível que cubram toda a implementação
4. Apresente apenas as parent tasks ao usuário (sem sub-tasks ainda)
5. Informe: *"Tarefas de alto nível geradas. Responda **'Go'** para gerar as sub-tasks."*
6. **Aguarde confirmação antes de continuar**

### Fase 2 — Sub-Tasks (após "Go")

1. Decomponha cada parent task em sub-tasks acionáveis
2. Sub-tasks devem ser granulares o suficiente para um **dev júnior** implementar
3. Identifique arquivos relevantes (criados ou modificados), incluindo arquivos de teste
4. Produza o output final no formato abaixo e salve em `/tasks/`

## Output Format

```markdown
## Relevant Files

- `path/to/file.ts` - Descrição do papel do arquivo na feature.
- `path/to/file.test.ts` - Testes unitários para `file.ts`.

### Notes

- Testes devem ficar no mesmo diretório do arquivo testado.
- Para rodar testes: `npx jest [caminho/opcional]`

## Tasks

- [ ] 1.0 Parent Task Title
  - [ ] 1.1 Sub-task description
  - [ ] 1.2 Sub-task description
- [ ] 2.0 Parent Task Title
  - [ ] 2.1 Sub-task description
```

## Regras

- **Público-alvo:** developer júnior — sub-tasks devem ser explícitas e sem ambiguidade
- **Nomenclatura do arquivo:** `tasks-[prd-file-name].md` espelhando o nome do PRD de entrada
- **Não pule a pausa:** a confirmação "Go" é obrigatória entre Fase 1 e Fase 2
- **Arquivos de teste:** sempre liste o arquivo de teste correspondente para cada arquivo de produção identificado
