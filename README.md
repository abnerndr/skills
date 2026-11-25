# skills

Skills pessoais de desenvolvimento do [abnerndr](https://github.com/abnerndr).

Repositório: [github.com/abnerndr/skills](https://github.com/abnerndr/skills)

## O que tem aqui

| Skill | Uso |
|---|---|
| `project-plane` | Plano de ação em tarefas para agentes de codificação |
| `git-commit-template` | Mensagem de commit/PR no template COMMIT RULE |
| `qa-validacao-tasks` | Plano de teste a partir de task/Slack (Playwright + API) |
| `prd-writer` | PRD curto e acionável |
| `prd-task-generator` | Task list a partir de um PRD |
| `create-terms-and-polices` | Cria páginas de termos e privacidade por projeto |
| `validate-terms-and-polices` | Audita documentos, implementação e requisitos aplicáveis |
| `dokploy` | Operações no Dokploy via MCP (deploy, logs, status) |
| `publish-skill` | Criar skill nova neste repo e publicar no GitHub |

## Instalar todas com um comando

No WSL ou no Windows:

```bash
curl -fsSL https://raw.githubusercontent.com/abnerndr/skills/main/scripts/install.sh | bash
```

Isso clona o repositório em `~/www/skills` (se ainda não existir), atualiza com `git pull` quando a árvore está limpa, e instala todas as skills no CLI e no desktop dos agentes encontrados.

Destinos fixos, nos dois homes quando Linux e Windows estão na mesma máquina:

- `~/.agents/skills/`
- `~/.claude/skills/`
- `~/.codex/skills/`
- `~/.gemini/skills/`
- `~/.cursor/skills/`

Também instala em Antigravity, OpenCode, Qwen, Kiro e GitHub Copilot quando o programa existe. No WSL são symlinks. No Windows são cópias, porque symlink para o WSL pede administrador. Rode o comando de novo para atualizar as cópias.

Se o repositório já estiver clonado:

```bash
bash ~/www/skills/scripts/install.sh
```

## Criar uma skill nova

1. Crie `/home/abner/www/skills/<nome>/SKILL.md`
2. `bash scripts/install.sh`
3. `bash scripts/publish.sh <nome>`

O agente deve seguir a skill `publish-skill` sempre que você pedir uma skill nova.

## Fora deste repositório

Não copiei plugins e skills de terceiros:

- SEO (`claude-seo` / AgriciDaniel)
- `ui-ux-pro-max`
- Superpowers, Caveman, Stripe, Figma, shadcn
- Skills oficiais do Cursor, Anthropic e Codex
