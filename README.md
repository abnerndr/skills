# skills

Skills pessoais de desenvolvimento do [abnerndr](https://github.com/abnerndr).

Repositório: `git@github.com:abnerndr/skills.git`

## O que tem aqui

| Skill | Uso |
|---|---|
| `git-commit-template` | Mensagem de commit/PR no template COMMIT RULE |
| `qa-validacao-tasks` | Plano de teste a partir de task/Slack (Playwright + API) |
| `prd-writer` | PRD curto e acionável |
| `prd-task-generator` | Task list a partir de um PRD |
| `dev` | Entry point do ciclo SDD (`/dev`) |
| `design-init` | Inicializa design system no ciclo SDD |
| `design-scope` | Escopo de design de uma feature |
| `sdd-test-plan` | Gera `TEST-PLAN.md` depois do Gate 1 |
| `strategy-red-team` | Red team da SPEC antes do Gate 1 |
| `publish-skill` | Criar skill nova neste repo e publicar no GitHub |

## Instalar no Claude e no Cursor

```bash
git clone git@github.com:abnerndr/skills.git ~/www/abnerndr/skills
bash ~/www/abnerndr/skills/scripts/install.sh
```

Isso cria symlinks em `~/.claude/skills/` e `~/.cursor/skills/`.

## Criar uma skill nova

1. Crie `/home/abner/www/abnerndr/skills/<nome>/SKILL.md`
2. `bash scripts/install.sh`
3. `bash scripts/publish.sh <nome>`

O agente deve seguir a skill `publish-skill` sempre que você pedir uma skill nova.

## Fora deste repositório

Não copiei plugins e skills de terceiros:

- SEO (`claude-seo` / AgriciDaniel)
- `ui-ux-pro-max`
- Superpowers, Caveman, Stripe, Figma, shadcn
- Skills oficiais do Cursor, Anthropic e Codex
