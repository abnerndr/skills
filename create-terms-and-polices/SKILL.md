---
name: create-terms-and-polices
description: Cria termos de uso e política de privacidade específicos do projeto, com pesquisa jurídica atual, LGPD e requisitos Google aplicáveis. Use para /create-terms-and-polices.
---

# Criar termos e políticas

Atenda `/create-terms-and-polices` e `$create-terms-and-polices`. Preserve a grafia. Use português brasileiro salvo idioma/pedido diferente. Reduza riscos; nunca prometa impedir processos, certificação jurídica ou aprovação Google.

Leia [critérios jurídicos](references/legal-review.md) e [rotas e testes](references/routes.md).

1. Inspecione instruções locais, framework/versão, rotas, layout público, formulários, autenticação, schema, uploads, pagamentos, logs, analytics, anúncios e integrações. Não exponha segredos/dados pessoais. Dependência instalada não prova uso; ausência no código não prova ausência de tratamento externo.
2. Separe fatos com evidências, inferências e pendências. Confirme identidade do responsável, contatos, público/países e práticas não verificáveis com perguntas agrupadas; continue trabalho independente. Não invente CNPJ, endereço, encarregado, fornecedor, prazo, base legal ou funcionalidade.
3. Pesquise fontes vigentes conforme aplicabilidade, usando ctresb/leis como índice e confirmando fonte oficial. Se indisponível, produza rascunho com limitação, nunca declaração de conformidade atual.
4. Redija documentos específicos, claros, com datas reais e compromissos cumpríveis. Não copie concorrentes nem acrescente serviços hipotéticos. Implemente páginas separadas, acessíveis e responsivas, reaproveitando layout/design/URLs. Inclua links no rodapé/home pública e fluxos relevantes.
5. Com fatos essenciais faltantes, salve minuta em `docs/legal/drafts/` ou equivalente e liste pendências. Não coloque placeholders ou afirmações não confirmadas em páginas públicas prontas para implantação. Prepare o trabalho independente sem chamar a entrega de publicável. CMP, exclusão de conta e infraestrutura de consentimento só devem ser implementados se estiverem no escopo; caso contrário, registre lacunas.
6. Execute a revisão abaixo e checks pertinentes. Entregue arquivos, URLs, fontes datadas, verificações e pendências. Criação não autoriza deploy ou alteração de consoles externos.

## Revisão compartilhada pelos dois comandos

Compare documentos, código e evidências operacionais usando ambos os guias. Gere `docs/legal/validation-YYYY-MM-DD.md` ou convenção local, com sufixo incremental para não sobrescrever histórico. Inclua escopo, ambiente, data, evidências, matriz requisito → fato → conclusão e checks executados/não executados. Cada achado: gravidade, arquivo/URL/localização, evidência, impacto e correção concreta.

Classifique itens como verificado, divergente, não verificado ou não aplicável com justificativa. Resultado geral: **pendente** com fatos essenciais/fontes atuais faltantes; **com divergências** com defeitos demonstrados; **sem divergências no escopo verificado** apenas se os checks aplicáveis passarem. Nunca aprovação jurídica geral. Destaque revisão especializada para dados sensíveis, menores, setores regulados, múltiplas jurisdições ou cláusulas controversas.

