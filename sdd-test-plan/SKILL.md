---
name: sdd-test-plan
description: Gera TEST-PLAN.md para o projeto alvo a partir de SPEC.md e DISCOVERY.md. Deve ser invocada pelo agent sdd após o Gate 1 (spec aprovada) e antes de Tasks. Output vive em .claude/sdd/TEST-PLAN.md do projeto alvo. Trigger: /sdd-test-plan
---

Você é a skill de planejamento de testes do harness SDD (Spec-Driven Development). Sua função é transformar uma spec aprovada e o relatório de discovery em um plano de testes preciso, acionável e sem ambiguidade — que servirá como contrato entre o implementador e o avaliador.

**Pré-condição**: esta skill é invocada pelo agent `sdd` após o Gate 1 (spec aprovada pelo usuário). Nunca invoque diretamente em um projeto sem SPEC.md e DISCOVERY.md presentes.

---

## Passo 1 — Ler insumos

Leia os dois arquivos do projeto alvo (cwd da sessão):

> **Resolução de `{cwd}`**: ao contrário do sub-agent `sdd-discovery` (que recebe `project_path` via Task), esta skill recebe `project_path` explicitamente no contexto de invocação — use esse valor para todos os paths abaixo. Se `project_path` não estiver presente no contexto, use o diretório da sessão Claude Code como fallback e avise o orquestrador.

1. `{cwd}/.claude/sdd/SPEC.md` — a especificação aprovada
2. `{cwd}/.claude/sdd/DISCOVERY.md` — o relatório de discovery

Se qualquer um dos dois não existir, interrompa com a mensagem:
```
[sdd-test-plan] ERRO: {arquivo ausente} não encontrado em {cwd}/.claude/sdd/. Execute o ciclo SDD na ordem correta: discovery → spec → test-plan.
```

---

## Passo 2 — Analisar e planejar

Antes de gerar o TEST-PLAN.md, raciocine internamente sobre:

**Da SPEC.md, extraia:**
- Lista completa de acceptance criteria (cada critério vira pelo menos um caso de teste)
- Entidades e operações mencionadas (ex: "criar usuário", "validar email", "retornar 404")
- Dependências externas mencionadas (APIs, bancos, serviços de terceiros)
- Edge cases explícitos ou implícitos nos critérios
- `verification_mode` de cada AC: classifique como `runtime` se o critério verifica output de execução de agents, comportamento em runtime, ou integração com serviço externo. Classifique como `static` para os demais (estrutura de código, configurações, presença de arquivos).

**Do DISCOVERY.md, extraia:**
- Tipo de projeto e framework (determina a estratégia de teste)
- Framework de teste disponível (Jest, Vitest, pytest, go test etc.)
- Número de arquivos de teste existentes (determina se há baseline ou ponto zero)
- Padrões de código (determina como gerar os stubs)

**Determine a divisão por camada:**

Priorize pela superfície de risco da SPEC: camadas com mais lógica nova e mais dependências externas recebem mais testes. E2E é justificável apenas quando a SPEC descreve fluxos de usuário end-to-end que não são cobertos por integration tests. Documente o racional da divisão escolhida no TEST-PLAN.md.

---

## Passo 3 — Gerar TEST-PLAN.md

Escreva `{cwd}/.claude/sdd/TEST-PLAN.md` com o seguinte formato:

```markdown
# SDD Test Plan

**Gerado em:** {data e hora ISO 8601}
**Baseado em:** SPEC.md (Gate 1 aprovado) + DISCOVERY.md
**Framework de teste:** {framework identificado no DISCOVERY}

---

## Test Strategy

### Divisão por camada

| Camada | % esperado | Justificativa |
|--------|-----------|---------------|
| Unit | {X}% | {1 frase baseada no tipo de projeto} |
| Integration | {Y}% | {1 frase} |
| E2E | {Z}% | {1 frase ou "Não aplicável para este tipo de projeto"} |

**Racional**: {parágrafo curto explicando por que essa divisão faz sentido para este projeto específico, referenciando o tipo e stack do DISCOVERY}

---

## Test Files to Create

Para cada acceptance criterion da SPEC, mapeie para um ou mais arquivos de teste.

{Para cada arquivo, use o bloco abaixo:}

### `{path/relativo/do/arquivo.test.ts}`

**Cobre**: {acceptance criterion(s) da SPEC que este arquivo valida}
**Camada**: Unit | Integration | E2E

```{linguagem}
// {framework}: {jest/vitest/pytest/go test}
describe('{nome da feature ou módulo}', () => {
  it('{descrição do caso de teste 1 — deve/should}', () => {
    // TODO: implementar
  });

  it('{descrição do caso de teste 2}', () => {
    // TODO: implementar
  });

  // Edge cases
  it('{descrição do edge case}', () => {
    // TODO: implementar
  });
});
```

{repita para cada arquivo necessário}

---

## Mocking Strategy

### O que mockar

| Dependência | Motivo | Como mockar ({framework}) |
|------------|--------|--------------------------|
| {ex: API externa X} | {ex: evitar chamadas reais em CI} | {ex: `jest.mock('./services/api')`} |
| {ex: banco de dados} | {ex: isolar lógica de negócio} | {ex: `pytest-mock` / `mongomemoryserver`} |
| {ex: filesystem} | {ex: testes determinísticos} | {ex: `vol` / `tmp_path` fixture`} |

### Exemplo de mock para {dependência principal}

```{linguagem}
// TODO: exemplo de como mockar {dependência principal} no framework {framework}
// Baseado nas convenções identificadas no DISCOVERY
```

---

## Coverage Thresholds

| Camada | Threshold mínimo | Ferramenta de medição |
|--------|-----------------|----------------------|
| Unit | ≥ {X}% | {ex: jest --coverage / pytest-cov} |
| Integration | ≥ {Y}% | {mesmo} |
| Global (statements) | ≥ {Z}% | {mesmo} |

**Configuração recomendada** ({arquivo de config, ex: jest.config.ts}):

```{linguagem}
// TODO: adicionar configuração de threshold ao arquivo de config do projeto
// Exemplo:
// coverageThreshold: {
//   global: { statements: Z, branches: W, functions: V, lines: Z }
// }
```

---

## Definition of Done

Checklist binária — cada item é verdadeiro ou falso. Nenhum item é subjetivo.

- [ ] Todos os arquivos listados em "Test Files to Create" existem no projeto
- [ ] Todos os `// TODO` foram substituídos por implementações reais
- [ ] Nenhum teste está em estado `skip`, `xtest`, `xit` ou `pytest.mark.skip`
- [ ] Coverage de unit atinge ≥ {X}%
- [ ] Coverage de integration atinge ≥ {Y}%
- [ ] Coverage global (statements) atinge ≥ {Z}%
- [ ] Todos os acceptance criteria da SPEC.md têm ao menos um teste cobrindo o caminho feliz
- [ ] Todos os edge cases explícitos da SPEC.md têm ao menos um teste
- [ ] Nenhuma dependência externa é chamada diretamente nos testes de unit (mocks aplicados)
- [ ] `{comando de teste}` passa sem erros em ambiente limpo (sem variáveis locais)

---

## Contract for Evaluator

Esta seção é um contrato direto com o `sdd-evaluator`. O avaliador deve verificar **exatamente** os itens abaixo, sem margem de interpretação:

### Arquivos obrigatórios

{lista de paths absolutos dos arquivos de teste que devem existir}

### Comandos de verificação

```bash
# Rodar testes e gerar cobertura
{comando exato para o framework identificado, ex: npx jest --coverage}

# Verificar se todos os testes passam (exit code 0)
{comando exato}
```

### Critérios de aprovação (pass/fail)

| Critério | Valor esperado | Como verificar |
|---------|---------------|----------------|
| Exit code dos testes | 0 | `echo $?` após rodar os testes |
| Coverage unit | ≥ {X}% | output do coverage report |
| Coverage global | ≥ {Z}% | output do coverage report |
| Arquivos de teste | {número} arquivos criados | `find ... | wc -l` |
| Testes skippados | 0 | grep no output por `skip`/`pending` |

### Acceptance criteria cobertos

{para cada acceptance criterion da SPEC, uma linha:}
- **AC-{N}**: {texto do criterion} → `verification_mode: static|runtime` → coberto por `{arquivo.test.ts}` → teste `{nome do it}`
```

---

## Passo 4 — Salvar e reportar

Salve o arquivo em `{cwd}/.claude/sdd/TEST-PLAN.md`.

Em seguida, exiba obrigatoriamente o seguinte resumo:

```
[sdd-test-plan] Arquivos de teste a criar: {número} — {lista dos paths relativos, separada por vírgula}
[sdd-test-plan] Estratégia: {X}% unit / {Y}% integration / {Z}% e2e
[sdd-test-plan] Thresholds: unit ≥ {X}% | integration ≥ {Y}% | global ≥ {Z}%
[sdd-test-plan] Acceptance criteria mapeados: {número de ACs da SPEC}
[sdd-test-plan] TEST-PLAN.md salvo em: {path absoluto}
```

Este resumo é o que o agent `sdd` usará para confirmar ao usuário que o plano foi gerado e está pronto para o próximo gate.
