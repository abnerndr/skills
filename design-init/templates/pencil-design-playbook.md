# Pencil MCP — Playbook Operacional

Carregado automaticamente quando Pencil ou `.pen` for mencionado na sessão (ver trigger em `CLAUDE.md`).

Gerado por `design-init` ao detectar `design_tool: pencil`. Relacionado: DESIGN.md (fonte de verdade de tokens), ADR de design (se criado na fase Memory Update).

---

## Modelo padrão

**Inicie a sessão de design em Opus 4.8.** O agente da sessão é quem executa as mutações no `.pen` via `batch_design` — e seu modelo é fixado no início da sessão.

Para spec (texto puro): use sempre `agent(prompt, {model: "opus"})` explicitamente. O override é load-bearing: sub-agents sem tipo definido herdam o modelo do pai (Opus), mas sub-agents com tipo definido (ex: `general-purpose`) resolvem o modelo pela definição do tipo primeiro — sem o override, podem não rodar em Opus.

Resumo: spec usa sub-agents com override explícito `{model: "opus"}`; mutação exige sessão iniciada em Opus.

---

## Sequência obrigatória de tools

1. `get_editor_state(include_schema: true)` — obter schema do arquivo antes de qualquer outra chamada
2. `batch_design` — aplicar mutações no `.pen` com o schema já carregado
3. `get_screenshot` — verificar resultado visual após mutação

Nunca chamar `batch_design` sem o schema. Nunca usar `Read` ou `Bash cat` em arquivos `.pen`.

---

## Estratégia de execução (2 fases)

**Fase 1 — Spec (paralelizável):** N agentes geram opções de design como texto puro. Nenhum toca o `.pen`. Revisar e escolher antes de avançar.

**Fase 2 — Mutação (sequencial):** Um único agente executa `batch_design` com a opção escolhida. Nunca paralelizar esta fase — race condition corromperia o arquivo.

---

## Veículo de execução (provisório)

A questão central é: **sub-agents conseguem alcançar o MCP local do Pencil?**

**Fase 1 (spec) — funciona sem spike:** sub-agents só produzem texto puro, sem chamar MCP. Use `{model: "opus"}` explicitamente em cada `agent()` de spec. Paralelize normalmente.

**Fase 2 (mutação) — verificar alcance MCP antes de delegar:** `batch_design` precisa do MCP local. Se sub-agent não alcançar MCP local, o agente da sessão (Opus) deve executar a mutação diretamente.

Spike recomendado: abrir sessão Opus, chamar `batch_design` de dentro de um sub-agent, confirmar alcance do MCP local. Documentar resultado em ADR.

---

## Variáveis de design em batch_design

**Referências de variável `$--{token}` não resolvem no runtime do batch_design.**

Sintoma: nós criados com `fill: "$--color-primary"` ficam transparentes/invisíveis mesmo que o modelo de dados mostre o valor correto via `batch_get`.

**Regra prática: use sempre hex hardcoded em batch_design.**

Mapeamento dos tokens deste projeto para uso direto:
| Token | Hex / Valor |
|---|---|
| `--color-primary` | `{primary_hex}` |
| `--color-secondary` | `{secondary_hex}` |
| `--color-background` | `{background_hex}` |
| `--color-surface` | `{surface_hex}` |
| `--color-text` | `{text_hex}` |
| `--font-heading` | `"{heading_font}"` |
| `--font-body` | `"{body_font}"` |

> Esta tabela foi preenchida por `design-init` com os valores extraídos de `get_variables`. Se os tokens mudarem no `.pen`, atualizar este arquivo manualmente.

---

## Constraints operacionais

- App Pencil deve estar aberto com o `.pen` ativo durante a sessão
- MCP `pencil` é local — não funciona em runs headless/cloud
- `export_nodes` não está coberto neste playbook — feature separada
- Screenshots de páginas com baixo contraste podem parecer em branco em miniatura — é artefato de escala, não erro de renderização. Use fundo escuro para verificação visual rápida.
