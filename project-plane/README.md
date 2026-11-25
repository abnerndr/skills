# project-plane

Conduz uma entrevista curta sobre uma ideia de negócio ou software e entrega um plano de ação em Markdown, dividido em tarefas para agentes de codificação. Não escreve código de implementação.

## Instalar todas as skills com um comando

No WSL ou no Windows, da pasta que estiver:

```bash
curl -fsSL https://raw.githubusercontent.com/abnerndr/skills/main/scripts/install.sh | bash
```

O comando clona (ou atualiza) [abnerndr/skills](https://github.com/abnerndr/skills) e instala **todas** as skills pessoais nos agentes que existem nesta máquina, no CLI e no aplicativo desktop.

Entram sempre, no home do Linux e no home do Windows quando os dois existem:

- `~/.agents/skills/` (Codex, Warp e outros que compartilham esse diretório)
- `~/.claude/skills/` (Claude Code e Claude Desktop)
- `~/.codex/skills/` (Codex CLI e Codex Desktop)
- `~/.gemini/skills/` (Gemini CLI)
- `~/.cursor/skills/` (Cursor)

Se o programa estiver instalado, entra também: Antigravity (`~/.gemini/config/skills/`), OpenCode, Qwen, Kiro e GitHub Copilot.

No WSL a instalação é um symlink para o repositório. No Windows, um symlink apontando para o WSL exige administrador, então o script copia as pastas. Rode o mesmo comando de novo para atualizar as cópias. Pasta que você já tinha criado à mão não é sobrescrita.

## Só esta skill

```bash
npx skills add https://github.com/abnerndr/skills --skill project-plane --global -y --agent claude-code cursor codex gemini-cli
```

Inclua `--agent antigravity opencode qwen-code kiro-cli github-copilot` se quiser esses agentes também. O `npx skills` instala no sistema em que o comando roda (WSL ou Windows), não nos dois de uma vez. O comando `curl` acima cobre os dois.

## Usar

Abra o agente na pasta do projeto e peça:

```text
Use a skill project-plane para montar o plano de ação deste produto.
```

A sintaxe de atalho depende da CLI. Algumas aceitam `/project-plane`; outras pedem a skill pelo nome.
