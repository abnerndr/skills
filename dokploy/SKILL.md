---
name: dokploy
description: >-
  Faz ping no MCP Dokploy, confirma que o servidor está ativo e identifica a
  sessão do ambiente autorizado, e só então executa a tarefa pedida com as
  ferramentas desse MCP. Use quando o usuário invocar /dokploy ou pedir
  deploy, logs, restart, status, projetos, aplicações ou qualquer operação
  no Dokploy.
disable-model-invocation: true
---

# Dokploy

Opera o Dokploy somente pelo MCP já conectado nesta sessão. O namespace é `user-dokploy` (servidor `dokploy` em `~/.cursor/mcp.json`, pacote `@dokploy/mcp`).

O ambiente autorizado é a instância e a conta dessa conexão. A tarefa só atinge projetos, aplicações, bancos e servidores visíveis nessa sessão.

## Quando usar

- O usuário invocou `/dokploy`, com ou sem tarefa na mesma mensagem.
- A mensagem pede uma ação no Dokploy: listar, consultar, deploy, redeploy, logs, start, stop, restart ou alteração de recurso.

Sem tarefa explícita, faça só o ping e o relatório de sessão. Pergunte qual tarefa executar.

## Ferramentas

Nesta sessão Cursor:

- Descobrir schema: `GetDynamicTools`
- Executar: `CallDynamicTool` com `namespace: "user-dokploy"`, `toolName`, `arguments` e `mcpDetails.description` (uma frase do que a chamada faz)

Não despeje o catálogo inteiro do namespace. Busque por `toolName` ou por `pattern` curto.

Antes de cada chamada, leia o schema dessa ferramenta na hora. Nomes e argumentos mudam com `@dokploy/mcp@latest`.

## Fluxo

Copie e cumpra nesta ordem:

```
- [ ] Tarefa identificada, ou ping-only se não houver tarefa
- [ ] Namespace user-dokploy utilizável
- [ ] Ping settings-health sem erro
- [ ] Sessão e organização ativa lidas
- [ ] Schema da ferramenta da tarefa lido
- [ ] Alvo único resolvido nessa conta
- [ ] Tarefa executada
- [ ] Resultado conferido e reportado
```

### 1. Tarefa

Separe o pedido em ação e alvo (projeto, aplicação, compose, banco, servidor). Se a ação muda estado e o alvo cabe em mais de um recurso, pare e pergunte. Não escolha pelo nome mais parecido.

### 2. MCP utilizável

1. `GetDynamicTools` com `namespace: "user-dokploy"` e `pattern` do ping (`settings-health`).
2. Se `namespaceStatus` for `needsAuth`, chame `mcp_auth` com arguments `{}` e leia o namespace de novo.
3. Se o namespace não existir, ou `namespaceStatus` continuar `needsAuth`, `error` ou `loading`, pare. Diga que o MCP Dokploy não está utilizável nesta sessão e que a tarefa não foi executada.

Uma tentativa de `mcp_auth`. Não peça token, cookie ou `DOKPLOY_API_KEY` no chat. Não leia nem imprima essa variável.

### 3. Ping

Chame `settings-health` com arguments `{}`.

O MCP está ativo somente quando essa chamada retorna sem `isError`, sem `success: false` e sem campo `error`.

Se o ping falhar, pare. Não chame sessão, não liste recursos e não execute a tarefa. Traduza o erro:

| Sinal | O que dizer |
|---|---|
| `Invalid URL` | O processo MCP subiu, mas `DOKPLOY_URL` está ausente ou não é uma URL absoluta (`https://…`). Ajuste a env do servidor `dokploy` e recarregue o MCP. |
| 401 ou 403 | A URL respondeu e a credencial do MCP foi recusada. Atualize `DOKPLOY_API_KEY` fora do chat e recarregue o MCP. |
| timeout ou conexão recusada | A URL não está alcançável a partir desta sessão. |
| namespace ausente | O servidor `dokploy` não está carregado no Cursor. |

Configuração esperada, sem valores reais:

```json
{
  "mcpServers": {
    "dokploy": {
      "command": "npx",
      "args": ["-y", "@dokploy/mcp@latest"],
      "env": {
        "DOKPLOY_URL": "https://<seu-dokploy>",
        "DOKPLOY_API_KEY": "<chave no ambiente, nunca no chat>"
      }
    }
  }
}
```

Não reescreva `mcp.json` por conta própria. Não chame a API Dokploy por curl, HTTP direto ou cliente paralelo.

### 4. Ambiente autorizado

Com o ping ok, chame em paralelo, arguments `{}`:

- `user-session`
- `organization-active`

Guarde usuário e organização. Daqui em diante toda busca e toda mutação usam essa conta. Se o usuário pediu outra instância, outra URL ou outra API key, pare e diga que esta skill opera só o MCP já autorizado.

`settings-checkInfrastructureHealth` não substitui o ping. Use só quando a tarefa for saúde de infraestrutura.

### 5. Executar

1. Traduza a ação para um `pattern` de ferramenta (`project-`, `application-`, `compose-`, `postgres-`, `domain-`, `deployment-`).
2. Leia o schema com `GetDynamicTools` antes do `CallDynamicTool`.
3. Resolva o alvo com ferramenta de leitura (`-search`, `-all`, `-one`). Vários resultados: pare e pergunte. Nenhum: reporte que não existe nessa conta.
4. Execute a ação pedida, com os argumentos do schema. Não acrescente deploy, restart, limpeza ou alteração vizinha.
5. Leia de novo o recurso afetado (status, detalhe ou log) e use essa leitura no relatório.

### 6. Resposta

Responda em português, neste formato:

```markdown
## Dokploy
- MCP: ativo | indisponível
- Ambiente: <organização e usuário da sessão, ou "não confirmado">
- Tarefa: <pedido, ou "nenhuma — aguardando tarefa">
- Alvo: <recurso resolvido, ou "—">
- Resultado: <o que a ferramenta retornou, sem segredos>
```

Omita tokens, chaves, headers `Authorization` e o conteúdo de `.env`.

## Confirmação antes de mudar estado

Pode executar na hora quando o usuário nomeou a ação e um alvo que a busca resolveu para um único recurso. Exemplos: deploy, redeploy, start, restart, ler logs, alterar env já descrita na mensagem.

Pare e peça confirmação quando a ação for irreversível ou o alvo for amplo, mesmo que o verbo tenha aparecido:

- remover, apagar, dropar, limpar filas, prune, kill de build
- trocar senha, desativar, cancelar deploy
- `cleanAll`, limpeza de imagens, volumes ou containers em um servidor inteiro
- qualquer mutação em que a busca não tenha um único id

A confirmação precisa repetir o nome do recurso. Até lá, entregue só o que a leitura encontrou.

## Exemplos

**`/dokploy`**

Ping e sessão. Se o ping passar, entregue o relatório com tarefa "nenhuma — aguardando tarefa".

**`/dokploy lista os projetos`**

Ping, sessão, schema de `project-all` ou `project-search`, chamada, relatório com a lista. Sem deploy e sem restart.

**`/dokploy faz deploy da aplicação api-producao`**

Ping, sessão, busca da aplicação. Um id: leia o schema de `application-deploy` e faça o deploy. Mais de um: pare e liste os nomes. Depois leia o status do deployment e reporte.

**`/dokploy apaga o banco orders`**

Ping e sessão. Busque o banco. Não chame remove. Mostre o alvo encontrado e peça confirmação com o nome exato.
