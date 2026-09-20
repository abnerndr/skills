---
name: dev
description: Entry point do harness SDD. Verifica STATE.md do projeto atual — retoma ciclo existente ou inicia novo. Invoca o agent sdd como session agent. Trigger: /dev
---

# Skill `/dev` — Entry Point do Harness SDD

Esta skill é fina por design. Ela não executa o ciclo — inicializa o estado e entrega o controle ao agent `sdd`.

---

## Passo 0 — Atualizar o harness (obrigatório, sempre)

Antes de qualquer outra coisa — inclusive antes de checar STATE.md — garantir que os agents/skills/references/templates instalados em `~/.claude/` refletem a versão mais recente do harness. **Não é opcional e não pode ser pulado**, mesmo em retomada de ciclo: nunca rodar um ciclo (novo ou retomado) com instruções desatualizadas.

```bash
if [ -d ~/.claude/harness/mzk-sdd/.git ]; then
  git -C ~/.claude/harness/mzk-sdd pull --ff-only
else
  mkdir -p ~/.claude/harness
  git clone https://github.com/pyxys-inteligencia-digital/agent-sdd-mzk.git ~/.claude/harness/mzk-sdd
fi
bash ~/.claude/harness/mzk-sdd/scripts/install.sh
```

- Se o `pull` falhar mas o clone local já existir (falha pontual de rede): aviso best-effort ("harness pode estar desatualizado") e seguir com a versão local já instalada — não bloqueia.
- Se o clone **inicial** falhar (harness ainda não existia localmente e não foi possível criá-lo) ou o `install.sh` falhar: **BLOQUEAR** — exibir o erro completo ao usuário e instruir a resolver acesso/rede antes de continuar. Não prosseguir para o Passo 1.

Só depois de concluído (ou do aviso best-effort de pull falho), seguir para o Passo 1.

---

## Passo 1 — Verificar estado do ciclo

Checar se existe `.claude/sdd/STATE.md` no diretório atual (`cwd`):

```bash
ls .claude/sdd/STATE.md 2>/dev/null && echo "EXISTE" || echo "NOVO"
```

---

## Passo 2a — Se STATE.md existir: retomada

Ler STATE.md e exibir o resumo (project_path, mode, phase, gates_passed, next_step). Perguntar ao usuário: "Retomar ciclo em `{phase}`? (s/n)".

- Se `s`: passar o STATE.md como contexto para o agent sdd (ver Passo 3) — a lógica de retomada é executada pela **Seção 2 de `~/.claude/agents/sdd.md`**.
- Se `n`: pedir confirmação antes de deletar STATE.md, então seguir para Passo 2b.

---

## Passo 2b — Se STATE.md não existir: novo ciclo

Pedir ao usuário:

> Nenhum ciclo ativo encontrado. Descreva em 1-3 frases o que você quer construir:

Aguardar a resposta. Este é o **brief** que será passado ao agent `sdd`.

---

## Passo 3 — Executar o ciclo SDD nesta sessão

Carregar as instruções do orquestrador diretamente:

```bash
cat ~/.claude/agents/sdd.md
```

Após ler o arquivo, **agir como o orquestrador `sdd` nesta mesma sessão** — sem abrir nova sessão nem redirecionar o usuário. O brief coletado no Passo 2b (ou o conteúdo do STATE.md do Passo 2a) é o contexto de partida do ciclo.

> Isolamento: o ciclo pode rodar dentro de qualquer projeto alvo, incluindo repos PYXYS/MZK — exceto o próprio repo do harness (`mzk-sdd-harness`). Os artefatos do ciclo ficam confinados em `.claude/sdd/` do projeto alvo, que o Gate 0 mantém no `.gitignore`, de modo que nunca entram no histórico git do repositório.
