# E3: modelos locales (Ollama en WSL) en las baterías de StructAI (#172)

Fecha: 2026-11-12. Hardware: Ryzen 5 8640HS, CPU sin GPU, WSL 16 GB / 10 núcleos, `num_ctx` 8192, temperatura 0,1.
Recuperación, enrutamiento y prompts idénticos a producción; solo cambia el generador (`_llamar_llm_con_respaldo`
parcheado). Caché de respuestas de producción desactivada (`RAG_CACHE_DISABLED`). Sin Groq ni OpenAI.
Tabla completa: `RESUMEN.md` (`python correr_bateria.py --resumen`). Respuestas: `resultados/<modelo>.jsonl`.

## Fase 3: piloto (38 casos = 13 motores + 25 NSR-10 estratificados)

| Modelo | Pasa | p50 por caso |
|---|---|---|
| qwen2.5:7b | **38/38** | ~2,5 min |
| qwen2.5:14b | 37/38 | ~3,5 min |
| llama3:8b | 34/38 | ~1,5 min |
| hermes3 | 34/38 | ~1,8 min |

McNemar exacto, qwen2.5:7b vs llama3:8b y vs hermes3: discordantes 4–0, p = 0,125 (no significativo con n = 38).
El 14B no mejora al 7B y cuesta ~2× → descartado para CI. Elegido **qwen2.5:7b**.

## Fase 4: batería completa con qwen2.5:7b (138 casos)

| Batería | Pasa | Wilson IC95 |
|---|---|---|
| Motores | 13/13 | 77–100 % |
| NSR-10 | 106/125 (84,8 %) | 77,5–90,0 % |
| **Total** | **119/138 (86,2 %)** | 79,5–91,0 % |

Fallos por título: **H 9**, F 5 (aluminio), K 2 (vidrio), B 1, NTC 174 1, H/F restantes en la lista de `resultados`.

### Alucinación numérica: 4 marcas, 1 real

| Caso | Valor marcado | Veredicto |
|---|---|---|
| D-no-reforzada-zona-baja-Aa-005 | 1.123 | Falso positivo: "1.123 municipios" viene del prompt del sistema |
| F-espesor-minimo-entregado-95porciento | 2,00 / 1,90 mm | Falso positivo: ejemplo ilustrativo del 95 %, aritmética correcta |
| F-f546-tirante-excentrico-06ao | 0,4 | Falso positivo: 1 − 0,6 derivado del dato correcto |
| H-kst-amax-macizos-rocosos-100 | 0,05 MPa | **Real**: Kst/amax es adimensional; valor y unidad inventados (caso fallido) |

→ 1/138 alucinaciones reales (0,7 %). El detector debería ignorar cifras presentes en el prompt del sistema y
aritmética derivada de cifras del contexto (mejora propuesta, no aplicada).

## Discusión

- qwen2.5:7b es viable como **generador del CI nocturno** (#178): 86 % en la batería NSR-10 sin GPU, ~2 min por caso
  → la batería completa cabe en ~4,5 h de noche. **No va a producción** (decisión del usuario).
- Los fallos se concentran en el **Título H**, que es justamente el título con huecos de corpus
  (`scripts/ingesta/nsr10/PLAN_HUECOS_GRAFO_2026-11.md`). Falta separar si fallan por recuperación o por generación:
  medir recall@k del chunk esperado en esos 9 casos (sin LLM) antes de culpar al modelo.
- No hay referencia de Groq medida en esta corrida (no se gastó cuota); la comparación con producción queda pendiente
  de una corrida de referencia autorizada.

## Incidente de la corrida

WSL se apagó por inactividad entre dos renovaciones del keepalive (una falló al lanzarse desde PowerShell). 5 casos
quedaron con `ConnectError`; se borraron de la caché y se re-corrieron. Para #178: el proceso nocturno debe verificar
`/api/version` antes de cada caso y reintentar, en vez de grabar el error.
