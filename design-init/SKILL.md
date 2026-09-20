# Skill `design-init` — Inicialização do Design System

**Description:** Inicializa o design system de um projeto — gera DESIGN.md, design_tokens.json e tailwind.config.js com base no estado detectado pela Probe 7.

**Trigger:** `design-init` (invocado pelo agent sdd durante a fase design-system)

**Pré-condições:**
- `STATE.md` presente no projeto alvo com bloco `design_system` preenchido
- `design_system.state` definido (exists | implicit | greenfield)

---

## Passo 1 — Branching inicial (inviolável)

Ler `STATE.md.design_system.state`:

```
se state == exists:
  log "[design-init] DESIGN.md já existe — skip"
  Confirmar que design_md_path está preenchido em STATE.md
  return  ← não prosseguir; próxima fase
```

Esta regra implementa o **write-once**: DESIGN.md só é escrito uma vez por projeto.

---

## Passo 2 — Fluxo greenfield (state == greenfield)

1. Ler `product_type` e `industry_keywords` do STATE.md

2. Rodar:
   ```bash
   python3 .claude/skills/design-init/scripts/run_engine.py \
     --keywords "{industry_keywords}" \
     --product-type "{product_type}" \
     --out /tmp/design_init_out.md
   ```
   `run_engine.py` importa `DesignSystemGenerator` + `csv_to_design_md_yaml` em memória e produz DESIGN.md completo (YAML front matter + 8 seções canônicas) — sem serialização JSON intermediária.

3. Validar:
   ```bash
   npx @google/design.md lint /tmp/design_init_out.md
   ```
   - Se warnings WCAG → corrigir hex para contraste AA mínimo e re-lintar (greenfield: auto-fix)
   - Se erro de sintaxe → interromper com log de erro

4. Write `{project_path}/DESIGN.md` com conteúdo de `/tmp/design_init_out.md`

5. Seguir **Passo 4 — Passos comuns de export**

---

## Passo 3 — Fluxo implicit

### 3A — design_tool: pencil

**Constraints operacionais obrigatórios (verificar antes de chamar MCP):**
- App Pencil deve estar aberto com o `.pen` ativo
- MCP `pencil` é local — não funciona headless/cloud
- Nunca chamar `batch_design` neste fluxo — design-init é read-only no Pencil
- Nunca usar `Read` ou `Bash cat` em arquivos `.pen`

**Sequência:**

1. Verificar que MCP Pencil responde:
   ```
   get_editor_state({ filePath: design_tool_ref, include_schema: true })
   ```
   - Se falhar → aviso "[design-init] MCP Pencil indisponível — fallback para design_tool: none" → executar 3C

2. Extrair variáveis:
   ```
   get_variables({ filePath: design_tool_ref })
   ```
   Mapear variáveis `--color-*`, `--font-*` → hex direto (nunca `$--token`)

3. Listar componentes existentes:
   ```
   batch_get({ filePath: design_tool_ref, patterns: [{ reusable: true }], readDepth: 2 })
   ```

4. Montar YAML front matter com valores hex diretos extraídos (sem referências `$--token`)

5. Construir DESIGN.md completo (YAML front matter + 8 seções canônicas)

6. Copiar template pencil-design-playbook.md para o projeto:
   ```bash
   cp .claude/skills/design-init/templates/pencil-design-playbook.md \
      {project_path}/.claude/memory/pencil-design-playbook.md
   ```
   Preencher a tabela de tokens com os valores hex reais extraídos no passo 2.

7. Criar ou atualizar `{project_path}/.claude/memory/MEMORY.md` com pointer:
   ```
   - [Pencil Design Playbook](.claude/memory/pencil-design-playbook.md) — regras operacionais MCP Pencil + tokens hex deste projeto
   ```

8. Seguir **Passo 4** — WCAG em modo warn-only (não auto-fix para implicit)

### 3B — design_tool: figma

1. `get_design_context({ fileKey: design_tool_ref, nodeId: "0:1" })` → extrair contexto global

2. `search_design_system` → listar componentes existentes

3. `get_metadata` → extrair estilos globais (color styles, text styles, effect styles)

4. Mapear estilos Figma → tokens YAML front matter:
   - Ferramenta tem precedência sobre código
   - Se conflito com tokens de código: registrar motivo no corpo do DESIGN.md

5. Construir DESIGN.md completo

6. Seguir **Passo 4** — WCAG em modo warn-only

### 3C — design_tool: none

1. Extrair tokens do código:
   ```bash
   node .claude/skills/design-init/scripts/extract-tokens.cjs {project_path}
   ```
   Output: JSON com `{ colors: {...}, typography: {...}, spacing: {...} }`

2. Usar tokens extraídos como base do YAML (não inventar valores ausentes)
   - Se token ausente: deixar campo com valor placeholder explícito; não inventar hex

3. Para lacunas: complementar com engine ui-ux-pro-max (queries por domínio)

4. Construir DESIGN.md completo

5. Seguir **Passo 4** — WCAG em modo warn-only

---

## Passo 4 — Passos comuns de export

Executados após write do DESIGN.md em todos os fluxos (exceto skip):

1. **Detectar Tailwind v4:**
   ```bash
   ls {project_path}/tailwind.config.ts 2>/dev/null || echo "NO_TS_CONFIG"
   grep -r "@import \"tailwindcss\"" {project_path}/src {project_path}/styles 2>/dev/null
   ```
   - Se `tailwind.config.ts` ausente **e** `@import "tailwindcss"` detectado → Tailwind v4:
     ```bash
     npx @google/design.md export --format css-tailwind \
       --input {project_path}/DESIGN.md \
       --output {project_path}/src/styles/design-tokens.css
     ```
   - Caso contrário (Tailwind v3 ou ausente):
     ```bash
     npx @google/design.md export --format tailwind \
       --input {project_path}/DESIGN.md \
       --output {project_path}/tailwind.config.js
     ```
     - Se `tailwind.config.js` já existir (implicit): merge das chaves em `theme.extend` — não substituir o arquivo inteiro

2. **Export DTCG (sempre):**
   ```bash
   npx @google/design.md export --format dtcg \
     --input {project_path}/DESIGN.md \
     --output {project_path}/design_tokens.json
   ```

3. **Atualizar STATE.md:**
   ```yaml
   design_system:
     design_md_path: "{project_path}/DESIGN.md"
   artifacts:
     - path: "{project_path}/DESIGN.md"
       description: "Design system — fonte de verdade de tokens"
     - path: "{project_path}/design_tokens.json"
       description: "Tokens no formato W3C DTCG"
     - path: "{project_path}/tailwind.config.js"    # ou design-tokens.css se v4
       description: "Config Tailwind gerada do DESIGN.md"
   ```
   Se `design_tool: pencil`, adicionar:
   ```yaml
     - path: "{project_path}/.claude/memory/pencil-design-playbook.md"
       description: "Playbook operacional Pencil MCP com tokens hex do projeto"
   ```

---

## Passo 5 — Gatilho de ADR (opcional)

Após gerar DESIGN.md, identificar se houve escolha estrutural (ex: "adotar estilo Minimalism para portais automotivos", "usar paleta escura para produto B2B de segurança").

Se sim, exibir ao usuário:
```
[design-init] Decisão candidata a ADR:
  Decisão: {descrição}
  Rationale: engine ui-ux-pro-max — produto "{product_type}", keywords "{industry_keywords}"
  Criar ADR? (s/n) — se s, será proposto na fase Memory Update
```

Não criar o ADR automaticamente.

---

## Degradação graciosa

| Cenário | Comportamento |
|---|---|
| Python 3 indisponível | Log de aviso + interromper (não gerar DESIGN.md corrompido via inline LLM) |
| MCP Pencil offline | Fallback para `design_tool: none` com aviso |
| MCP Figma offline | Aviso + prosseguir com tokens de código se disponíveis |
| `npx @google/design.md` ausente | Log de aviso para os passos de lint/export; DESIGN.md ainda é escrito |
| `node` ausente | Log de aviso para extract-tokens.cjs; prosseguir com engine apenas |

Em nenhum caso um erro de ferramenta deve bloquear silenciosamente o ciclo SDD. Sempre logar antes de interromper.
