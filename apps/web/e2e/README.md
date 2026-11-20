# Pruebas E2E del chat (issue #190)

Playwright contra `next dev` con la **API simulada**. Ninguna prueba toca producción, Supabase ni un LLM, y no hacen
falta secretos:

- `soporte.ts` intercepta toda petición del navegador. Las del backend falso (`constantes.ts`) se responden con
  `fixtures.ts`; cualquier otro host se aborta y queda registrado en `backend.bloqueadas`.
- La sesión es una cookie falsa de `@supabase/ssr` apuntando a un host inexistente (`getSession()` no hace red).
- Los textos fijos de los fixtures (aviso de responsabilidad, etiquetas de dominio, aviso de vigencia de Supía) se
  copian de `packages/construdata/rag_multi_norma.py`: si cambian allá, actualízalos acá.

```bash
npm run test:e2e                         # escritorio + celular (Pixel 7)
npx playwright test --project=escritorio  # solo uno
npx playwright show-trace test-results/<caso>/trace.zip
```

Primera vez: `npx playwright install chromium`.

Verificado con mutaciones, quitando a mano cada protección de `Chat.tsx`:
- sin `<AvisoResponsabilidad>`, falla la prueba de Sincelejo;
- sin `esUrlSegura`, falla la prueba del link `javascript:`.
