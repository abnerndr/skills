# Termos de uso e política de privacidade

Este conjunto tem dois comandos: `create-terms-and-polices` cria as páginas; `validate-terms-and-polices` verifica documentos, implementação e requisitos aplicáveis. Instale **as duas skills juntas**: a validação lê as referências da criação.

## Instalar globalmente

Requer Node.js/npm com `npx`. Dentro desta pasta (`create-terms-and-polices`), execute:

```bash
npx skills add .. --skill create-terms-and-polices validate-terms-and-polices --global --agent codex claude-code --copy
```

O comando usa o repositório local e instala somente estas duas skills para Codex e Claude Code. `--global` permite uso em diferentes projetos; `--copy` evita depender de symlinks.

Se estiver na raiz do repositório `skills`, use:

```bash
npx skills add . --skill create-terms-and-polices validate-terms-and-polices --global --agent codex claude-code --copy
```

Para instalar em apenas um deles, use `--agent codex` ou `--agent claude-code`. Para outros agentes, confira se suportam instalação global antes de acrescentá-los. Veja a [lista atual de agentes compatíveis](https://github.com/vercel-labs/skills/blob/main/docs/agents.md).

Windows e WSL têm diretórios de usuário diferentes: execute no ambiente em que sua CLI de IA funciona. No PowerShell, se houver bloqueio de `npx.ps1`, use `npx.cmd`.

## Instalar pelo GitHub

Execute de qualquer pasta, sem clonar o repositório:

```bash
npx skills add https://github.com/abnerndr/skills --skill create-terms-and-polices validate-terms-and-polices --global --agent codex claude-code --copy
```

Repositório público: [github.com/abnerndr/skills](https://github.com/abnerndr/skills). O instalador baixa as duas skills e suas referências. Para usar alterações locais ainda não publicadas, utilize os comandos locais acima.

## Usar em um projeto

Abra sua CLI na pasta do projeto e peça:

```text
Use a skill create-terms-and-polices para criar os termos de uso e a política de privacidade deste projeto.
```

Ou:

```text
Use a skill validate-terms-and-polices para auditar os termos e a política de privacidade deste projeto.
```

A sintaxe de atalhos depende da CLI: algumas oferecem `/create-terms-and-polices` e `/validate-terms-and-polices`; outras usam seleção de skill ou menção pelo nome. A instalação não cria um comando executável de shell com esses nomes.

Não existe instalação automática garantida para **qualquer** CLI. Em uma CLI sem suporte ao formato Agent Skills, mantenha as duas pastas lado a lado e peça ao agente para ler o caminho absoluto do `SKILL.md` desejado e suas referências. Isso exige que a ferramenta consiga ler arquivos locais; sem esse recurso, forneça os conteúdos como contexto.

As páginas geradas devem refletir a operação real do projeto. A skill pesquisa fontes atuais, identifica pendências e não garante aprovação de plataformas ou ausência de processos.

Referência dos comandos: [Skills CLI](https://github.com/vercel-labs/skills/blob/main/docs/commands.md).


## Erro com Eve e PromptScript

Não use `--agent '*'` junto com `--global`: na versão 1.7.4, Eve e PromptScript não suportam instalação global. Se o instalador listar somente essas quatro falhas, elas se referem às duas skills nesses dois agentes; confira o resultado dos demais com:

```bash
npx skills list --global
```

Para Eve ou PromptScript, use instalação por projeto, sem `--global`. Na raiz do projeto de destino, substitua o caminho abaixo pelo caminho absoluto do repositório local que contém as duas skills:

```bash
npx skills add /caminho/absoluto/skills --skill create-terms-and-polices validate-terms-and-polices --copy
```

Selecione o agente desejado no instalador. O prompt “Need to install ... skills” solicita instalar o utilitário npm; ele é separado da instalação das suas skills. A mensagem “One-time prompt” isolada não informa qual é a pergunta — leia o texto completo antes de responder.
