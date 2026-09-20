---
name: publish-skill
description: Cria e publica skills pessoais de desenvolvimento no repositório git@github.com:abnerndr/skills.git. Use when creating a new skill, adding a skill, publishing a skill, saving a skill to GitHub, or when the user asks to criar uma skill, nova skill, publicar skill, or mandar skill para o GitHub.
---

# Publicar skill no GitHub

Fonte da verdade das skills pessoais: `/home/abner/www/abnerndr/skills`
Remote: `git@github.com:abnerndr/skills.git`

Nunca crie skill pessoal só em `~/.claude/skills/` ou `~/.cursor/skills/`. Sempre escreva neste repositório e publique.

## Quando criar uma skill nova

1. Crie a pasta no repositório (não em `~/.cursor/skills-cursor/`):

```text
/home/abner/www/abnerndr/skills/<skill-name>/SKILL.md
```

2. `skill-name`: minúsculas, hífens, no máximo 64 caracteres.
3. `SKILL.md` com frontmatter `name` + `description` (o quê + quando).
4. Arquivos de apoio (scripts, examples, references) ficam na mesma pasta, um nível abaixo.

5. Instale os symlinks locais:

```bash
bash /home/abner/www/abnerndr/skills/scripts/install.sh
```

6. Publique no GitHub:

```bash
bash /home/abner/www/abnerndr/skills/scripts/publish.sh <skill-name>
```

Se o usuário ainda não pediu commit/push, pare depois do `install.sh` e pergunte se deve publicar. Se o pedido já incluir "criar e mandar pro GitHub", "publicar skill" ou equivalente, rode o `publish.sh`.

## Skill já existente

- Edite o arquivo **neste repositório**.
- Rode `scripts/publish.sh <skill-name>` para mandar a alteração.
- Não edite cópias soltas em `~/.claude/skills` se elas forem symlink para este repo.

## O que não entra neste repositório

- Skills built-in do Cursor (`~/.cursor/skills-cursor/`)
- Plugins de terceiros (SEO AgriciDaniel, superpowers, caveman, Stripe, Figma, shadcn)
- Skills oficiais Anthropic/Codex (`pdf`, `docx`, `pptx`, `xlsx`, `morning`, `skill-creator`)
- `ui-ux-pro-max` (pacote do harness SDD, não autoria pessoal)
