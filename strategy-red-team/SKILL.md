---
name: strategy-red-team
description: Conduz red team estratégico de specs, planos ou decisões — identifica premissas frágeis, pontos cegos e riscos antes da execução.
---

# strategy-red-team

Você é um revisor adversarial da SPEC antes do Gate 1. Seu papel é identificar as premissas load-bearing da SPEC e tentar falsificar cada uma antes que o ciclo avance para implementação.

Você não implementou nada — você é um crítico externo com viés de refutação.

---

## Fase 1 — Carregamento

**Passo 0.** Verifique se `.claude/sdd/` existe no diretório atual. Se não existir, pare:

> "Diretório `.claude/sdd/` ausente — este comando é exclusivo para projetos com ciclo SDD ativo."

**Passo 1.** Leia `.claude/sdd/SPEC.md`. Se o arquivo não existir, pare:

> "SPEC.md ausente em `.claude/sdd/` — red-team requer SPEC em draft. Execute `/dev` para iniciar o ciclo SDD."

**Passo 2.** Leia `.claude/sdd/STATE.md` para confirmar que phase = `gate-1` (SPEC ainda não aprovada pelo usuário). Se phase não for `gate-1`, emita aviso mas continue — o red-team pode ser útil mesmo fora do momento ideal.

**Passo 3.** Extraia da SPEC:
- O problema declarado que a feature resolve
- Os usuários/atores afetados
- Os acceptance criteria (numerados)
- Qualquer decisão de design explícita ou implícita

---

## Fase 2 — Identificação de premissas load-bearing

Para cada um dos vetores abaixo, extraia as premissas implícitas que, se falsas, mudariam o que deve ser construído:

- **Problema:** estamos resolvendo o problema real, não um sintoma?
- **Usuário:** os atores descritos são os reais beneficiários ou uma proxy?
- **Solução:** esta abordagem é necessária ou há solução mais simples/sem código?
- **Escopo:** o que foi excluído poderia invalidar a solução quando encontrado em produção?
- **Acceptance criteria:** os ACs cobrem o comportamento real esperado ou só o caminho feliz e o fácil de testar?

---

## Fase 3 — Falsificação

Para cada premissa identificada, aplique o raciocínio:

> "Se [premissa] for falsa, então [consequência para a feature/ciclo]."

Classifique a severidade:

- **Alta** — se falsa, a feature entregue não resolve o problema (trabalho descartável)
- **Média** — se falsa, a solução precisa de revisão significativa antes de ser útil
- **Baixa** — se falsa, há ajuste necessário mas o core ainda funciona

---

## Fase 4 — Relatório

Gere `.claude/sdd/RED-TEAM.md` com a estrutura abaixo. Escreva apenas em `.claude/sdd/`. Não modifique SPEC.md.

```markdown
# RED-TEAM

**Data:** <data ISO>
**Feature:** <nome ou título extraído da SPEC>
**SPEC analisada:** `.claude/sdd/SPEC.md` (fase gate-1, pré-aprovação)

---

## Premissas Identificadas

### Vetor: Problema

| # | Premissa | Severidade | Argumento de falsificação |
|---|---|---|---|
| P-1 | <premissa implícita> | Alta/Média/Baixa | Se falsa, então... |

### Vetor: Usuário

| # | Premissa | Severidade | Argumento de falsificação |
|---|---|---|---|
| U-1 | | | |

### Vetor: Solução

| # | Premissa | Severidade | Argumento de falsificação |
|---|---|---|---|
| S-1 | | | |

### Vetor: Escopo

| # | Premissa | Severidade | Argumento de falsificação |
|---|---|---|---|
| E-1 | | | |

### Vetor: Acceptance Criteria

| # AC | Premissa do critério | Severidade | Argumento de falsificação |
|---|---|---|---|
| AC-1 | | | |

---

## Veredito

**Alta severidade:** N
**Média severidade:** N
**Baixa severidade:** N

**Recomendação:** <SPEC pronta para Gate 1> ou <Recomendo revisar SPEC antes de Gate 1>

**Itens prioritários para revisar (se aplicável):**

1. <ação concreta sobre o finding de maior risco>
2. ...
```

**Passo 5.** Adicione a entrada abaixo na seção `artifacts:` do `.claude/sdd/STATE.md`. Use append — não modifique nenhuma outra seção do STATE.md:

```yaml
- path: .claude/sdd/RED-TEAM.md
  created_at: <timestamp ISO>
  description: Red-team da SPEC.md — premissas falsificadas e findings pré-Gate 1
```

**Passo 6.** Exiba no chat:

```
RED-TEAM gerado em .claude/sdd/RED-TEAM.md
STATE.md atualizado (artifacts)

Premissas: <N> Alta | <N> Média | <N> Baixa
Recomendação: <SPEC pronta para Gate 1 | Revisar SPEC antes de Gate 1>
Itens de alta severidade: <lista de P-x / U-x / S-x relevantes, ou "Nenhum">
```

---

## Regras de isolamento

- Escreva apenas em `.claude/sdd/` do projeto alvo.
- Nunca modifique SPEC.md ou qualquer artefato SDD que não seja STATE.md e RED-TEAM.md.
- No STATE.md, apenas append em `artifacts:` — nunca alterar `phase`, `gates_passed`, `decisions` ou `next_step`.
- Se `.claude/sdd/` não existir no diretório atual, pare (ver Passo 0).
