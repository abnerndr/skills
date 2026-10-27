# Rotas e testes

Preserve idioma, base path, locale, slugs e arquitetura existentes. Em projeto novo, sugira /terms-of-service e /privacy-policy; /termos-de-uso e /politica-de-privacidade também são válidos. Não crie duplicatas apenas para traduzir slugs. Mudança necessária/autorizada de URL deve preservar links por redirecionamento. Nenhum slug garante aprovação Google.

| Stack | Implementação |
| --- | --- |
| Next App Router | app/(legal)/terms-of-service/page.tsx e app/(legal)/privacy-policy/page.tsx, sob src/app/locale se existente. (legal) não entra na URL. Use layout público sem conflito, autenticação ou dependência client desnecessária; metadata conforme versão. |
| Next Pages Router | pages/terms-of-service.tsx e pages/privacy-policy.tsx ou src/pages; não migrar só para estas páginas. |
| HTML | terms-of-service/index.html e privacy-policy/index.html se o host resolve índices; senão .html com links reais. Reuse CSS/navegação. |
| Angular | Componentes/rotas públicos fora de guards; respeite standalone/NgModule da versão. Verifique fallback para deep links. |
| Vue/Nuxt | Views/router existente ou file-based routing do Nuxt da versão instalada. Verifique history/base/fallback. Não adicione router pesado a site estático só para duas páginas. |

Consulte documentação oficial da versão se necessário. Não force SSR: avalie acessibilidade e produto Google pertinente. Use título/descrição únicos, idioma, heading principal, links descritivos, foco/contraste e mobile. Datas refletem edição real, não cada render. Canonical exige domínio conhecido; reutilize sitemap quando pertinente.

## Verificação observável

- Lint/typecheck/build pertinentes e disponíveis; diferencie falhas preexistentes e limitações.
- Abra URL direta e recarregue sem login: conteúdo correto, HTTP adequado, sem loops/404/guards/overlays bloqueantes. SPA com 200 não comprova conteúdo.
- Navegue home/rodapé/documentos; confira links, contato, teclado e mobile.
- Verifique robots/meta/canonical/sitemap conforme intenção. Preview pode ser noindex; não remova proteção privada para simular produção.
- Quando autorizado/viável, observe rede/cookies antes da decisão, após recusar, aceitar e revogar; compare terceiros ao texto. Registre limites de acesso.
- Confira aceite/versionamento nos fluxos pertinentes. Não transforme ciência da política em consentimento publicitário obrigatório.
- Teste direitos/cancelamento só com conta de teste no escopo autorizado, nunca excluindo dados reais.
- Separe evidência local de produção. Produção sem URL/acesso é não verificada.

