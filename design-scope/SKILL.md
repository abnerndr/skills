# Skill `design-scope` — Escopo de Design para Feature

**Description:** Gera escopo de design inline para uma feature específica — layout pattern, componentes, UX checklist, anti-patterns e tokens relevantes.

**Trigger:** `[design-scope] feature: "{descrição da feature}"`

**Pré-condição:** `DESIGN.md` deve existir em `{project_path}`. Se ausente, interromper com:
```
[design-scope] ERRO: DESIGN.md não encontrado em {project_path}. Execute design-init primeiro.
```

**Output:** sempre inline — nunca persiste em arquivo por feature.

---

## Passo 1 — Detecção de desatualização

Comparar mtime de `design_tokens.json` com mtime de `DESIGN.md`. Se `design_tokens.json` for mais antigo:

```
[design-scope] AVISO: design_tokens.json desatualizado em relação a DESIGN.md.
Rodar: npx @google/design.md export --format dtcg --input {project_path}/DESIGN.md --output {project_path}/design_tokens.json
```

Não interromper o fluxo — continuar com os arquivos disponíveis.

---

## Passo 2 — Protocolo de leitura em 3 camadas (ordem obrigatória)

**Camada 1 — DESIGN.md (fonte de verdade):**
- Ler seções: Overview, Do's and Don'ts, Components
- Extrair: estilo, paleta canônica, anti-patterns bloqueantes, lista de componentes definidos

**Camada 2 — design_tokens.json:**
- Extrair tokens relevantes para a feature em escopo (cores, tipografia, espaçamento)
- Prioridade sobre qualquer outro arquivo se houver conflito

**Camada 3 — tailwind.config.js (condicional, se stack Tailwind):**
- Detectar stack: `tailwind.config.js` ou `tailwind.config.ts` presente OU `@import "tailwindcss"` no CSS
- Se detectado: ler para mapear tokens → classes Tailwind disponíveis
- Se não detectado: omitir campo `class:` no output

---

## Passo 3 — Protocolo expandido para design_tool != none (entre camadas 2 e 3)

Ler `STATE.md.design_system.design_tool`:

**Se design_tool: pencil:**
```
batch_get({ filePath: design_tool_ref, patterns: [{ reusable: true }], readDepth: 2 })
get_variables({ filePath: design_tool_ref })
```
→ Obter lista de componentes existentes no arquivo .pen e variáveis atuais

**Se design_tool: figma:**
```
search_design_system
get_design_context({ fileKey: design_tool_ref, nodeId: "0:1" })
```
→ Listar componentes e estilos existentes no arquivo Figma

Resultado: lista de componentes que já existem na ferramenta (não recriar esses — apenas referenciar).

---

## Passo 4 — Queries ao engine ui-ux-pro-max

```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "{feature}" --domain landing
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "{feature}" --domain ux
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "{feature}" --stack {stack}
```

Para cada recomendação do engine:
- Verificar contra seção **Do's and Don'ts** do DESIGN.md
- Se conflito: descartar a recomendação do engine; registrar no output como anti-pattern bloqueante com fonte "DESIGN.md Do's and Don'ts"
- **DESIGN.md é sempre autoritativo** — engine é complementar

---

## Passo 5 — Output obrigatório (inline)

```
Layout pattern: {padrão recomendado — seções e ordem}

Componentes:
  - {Nome}: token: {token_name} ({hex_value}), class: {tailwind_class ou "N/A se não-Tailwind"}
  ...

UX checklist (prioridade 1–10):
  [P1] {item mais crítico}
  [P2] {item}
  ...

Anti-patterns bloqueantes:
  - {anti-pattern} — fonte: {DESIGN.md Do's and Don'ts | engine}
  ...

Tokens DESIGN.md relevantes:
  - {nome}: {hex/rem} → class: {tailwind-class ou "N/A"}
  ...
```

Para stack não-Tailwind: omitir campos `class:`, usar apenas valores de `design_tokens.json`.

---

## Passo 6 — Seção condicional "Construção via ferramenta"

Incluída **somente** quando `design_tool != none`:

```
Construção via ferramenta:
  tool: {pencil | figma}
  ref: {design_tool_ref}
  componentes existentes: [{lista — não recriar; referenciar como base}]
  componentes a criar: [{lista — novos}]
  ação sugerida (Pencil): get_guidelines() → batch_design() com specs de cada componente novo
  ação sugerida (Figma): carregar skill /figma-use → use_figma() via Plugin API
```

Quando `design_tool: none`: não incluir esta seção.

---

## Regras de cruzamento DESIGN.md vs engine

| Situação | Comportamento |
|---|---|
| Engine recomenda algo alinhado ao DESIGN.md | Incluir no output com token de referência |
| Engine recomenda algo conflitante com Do's and Don'ts | Descartar + registrar como anti-pattern bloqueante |
| Token do DESIGN.md não tem classe Tailwind mapeada | Incluir valor hex; class: "N/A" |
| `design_tokens.json` ausente | Usar tokens lidos diretamente do YAML do DESIGN.md |
