---
name: git-commit-template
description: Use when user asks for a copyable commit message, PR description, COMMIT RULE template, or text to paste on GitHub pull request or commit.
---

# GitHub — commit copiável (COMMIT RULE)

## Quando usar

- commit ou descrição **copiável** para colar no GitHub
- preencher o **template COMMIT RULE**
- corpo de **PR** ou mensagem de commit no padrão do time

## Fluxo

1. Analise o contexto disponível (`git diff`, arquivos alterados, conversa).
2. Preencha **todos** os campos do template abaixo.
3. Entregue **um único bloco markdown** pronto para copiar.

Se faltar informação para algum campo:
- mantenha a seção no template
- use `TODO: <o que falta>` de forma objetiva
- faça no máximo 1–3 perguntas curtas só para destravar `TODO`s críticos

## Template (usar verbatim)

Não altere títulos, ordem, checkboxes nem o bloco de observação final.

```markdown
## O que foi feito
<!-- Mudança objetiva. -->

## Por que
<!-- Problema real ou ganho claro. -->

## Onde revisar
<!-- Ponto crítico do código. -->

## Impacto
- [ ] Nenhum
- [ ] Backend
- [ ] Frontend
- [ ] DB
- [ ] Performance
- [ ] Segurança

## Risco / Atenção
<!-- Algo que merece cuidado especial -->

## Como validar
<!-- Passos mínimos ou "coberto por testes". -->

---

> **Observação**  
> O preenchimento deste template é **obrigatório**.  
> Pull Requests sem essas informações **não serão avaliados**.
```

## Regras de preenchimento

- **Impacto**: marque **exatamente uma** opção (`- [x]` na correta, demais `- [ ]`).
- **O que foi feito**: frases objetivas no passado; sem jargão vazio.
- **Por que**: problema resolvido ou ganho de negócio/técnico.
- **Onde revisar**: caminhos de arquivo e trecho crítico (função, componente, rota).
- **Risco / Atenção**: `Nenhum` só se for verdade; senão riscos concretos (regressão, migração, flag, etc.).
- **Como validar**: passos mínimos reproduzíveis (comandos, URLs, fluxo) ou `coberto por testes` quando aplicável.

## Formato de entrega

1. Uma linha curta (ex.: "Corpo pronto para colar no GitHub:").
2. **Apenas um** fenced code block com linguagem `markdown` contendo o template **já preenchido** (sem comentários HTML `<!-- -->` — substitua pelo texto real).
3. Não envolva o bloco em listas ou citações.
4. Não duplique o template fora do bloco.

**Título do PR / primeira linha do commit** (quando pedido): sugira **antes** do bloco, em linha separada, no estilo `tipo(escopo): resumo imperativo` (máx. ~72 caracteres).

## Exemplo de saída

Sugestão de título: `fix(checkout): corrige cálculo do frete`

```markdown
## O que foi feito
Corrigido o cálculo de frete quando o CEP tem hífen.

## Por que
Pedidos exibiam valor R$ 0,00 para CEPs formatados com traço.

## Onde revisar
`src/services/shipping.ts` — função `normalizeCep` e chamada em `calculateShipping`.

## Impacto
- [ ] Nenhum
- [ ] Backend
- [x] Frontend
- [ ] DB
- [ ] Performance
- [ ] Segurança

## Risco / Atenção
Validar CEPs internacionais ou vazios; comportamento anterior mantido para 8 dígitos sem máscara.

## Como validar
1. Abrir checkout com CEP `01310-100`
2. Confirmar frete > R$ 0
3. `npm test -- shipping`

---

> **Observação**  
> O preenchimento deste template é **obrigatório**.  
> Pull Requests sem essas informações **não serão avaliados**.
```
