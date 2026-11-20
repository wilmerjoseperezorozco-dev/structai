# Flujo atómico (#221, fase 2)

La fase 1 midió dónde se va el tiempo (`docs/LATENCIA_CADENAS.md`). Esta fase encapsula las cadenas como flujos atómicos y
repite la medición. Empieza por el pórtico, la cadena más pesada entre las que corren sin red.

## Qué cambió

| Pieza | Archivo | Qué hace |
|---|---|---|
| `Flujo`, `Paso` | `packages/dag-proyecto/dag_proyecto/flujo.py` | Flujo con caché por contenido, idempotencia, atomicidad y paralelismo, sobre los artefactos de #150. |
| `AlmacenAcotado` | mismo archivo | Caché del proceso con tope LRU, segura entre hilos. Verifica el hash del artefacto al leer. |
| `huella_de_archivos` | mismo archivo | SHA-256 de fuentes y datos: la versión real de un motor o de una norma. |
| Pórtico en flujo | `apps/api/routers/orquestador_api.py` | `/orquestador/portico-integral` y `/orquestador/portico-pareto` corren como flujos sobre una caché de 128 artefactos. |
| `_scwb` vectorizado | `packages/motor-concreto/src/columna.py` | Columna fuerte–viga débil con una interpolación por curva, en vez de una por nudo. |

### Garantías del `Flujo`

- **Caché por contenido.** El id de cada artefacto es el SHA-256 de (flujo, versión, paso, versión del paso, versión de la norma,
  parámetros, ids de entrada), el mismo esquema de #150.
  - En el pórtico, la versión del paso es la huella de las fuentes de `orquestador`, `motor-concreto`, `motor-apu`,
    `motor-geopot` y `contrato-motor`.
  - La versión de la norma es la huella de los datos que la cadena lee: el Apéndice A-4 y los JSON de `motor-apu`.
  - Por eso un cambio de código o de norma nunca sirve un resultado viejo (#193). Ejemplo: el cambio de Supía por el
    Decreto 1711 (#189) habría cambiado la llave.
- **Idempotencia.** Un paso con efectos (escribir en BD, enviar correo) no se cachea por contenido, porque dos pedidos iguales
  pueden ser dos pedidos. Exige una `idempotency_key`:
  - la misma llave con las mismas entradas devuelve el resultado registrado, sin repetir el efecto;
  - la misma llave con otras entradas lanza `ConflictoIdempotencia`.
- **Atomicidad.** Los efectos corren al final, solo si todos los pasos puros terminaron bien. Un paso puro no puede depender
  de un efecto; se valida al construir el flujo.
  - Si algo falla, `ultima_completa` no cambia.
  - Los artefactos ya calculados son válidos por construcción (su id es su contenido), así que el reintento sigue desde ahí.
- **Paralelismo.** Los pasos de un mismo nivel del grafo corren en hilos. Sirve para E/S (recuperar varias normas a la vez); el
  cómputo puro en CPU no gana por el GIL, así que el pórtico corre con `max_hilos=1`.

Qué **no** se cachea: un 422 (solicitud sin solución), que se recalcula en cada petición, y nada con BD, LLM o red. Las dos
cadenas del pórtico son puras y deterministas.

## Resultado (criterio preregistrado en #221)

`python scripts/medicion/comparar_flujo.py --antes <worktree de origin/master> --rondas 8 --por-ronda 5`

Cada variante corre en su propio proceso y las variantes se turnan ronda a ronda, alternando también cuál va primero. Así la
carga de la máquina cae por igual en todas. Resultado guardado en `scripts/medicion/resultados/fase2_portico_2026-11-16.json`.

| `POST /orquestador/portico-integral` | n | p50 (ms) | p95 (ms) | p95 vs. antes |
|---|---|---|---|---|
| Antes (origin/master `7aaa7a3`) | 40 | 308,7 | 386,9 | — |
| Esta rama, petición nueva (caché vaciada antes de cada una) | 40 | 215,2 | 300,3 | **−22,4 %** |
| Esta rama, aciertos de caché | 40 | 6,1 | 8,4 | **−97,8 %** |

- **Meta ≥ 30 % menos p95 con aciertos de caché: se cumple (−97,8 %).**
- **Cero diferencias de resultado: se cumple.**
  - Las tres variantes devuelven la misma respuesta byte a byte (SHA-256 `662e465c…`).
  - Fuera del endpoint, `diseno_integral` (todos los candidatos factibles, todos sus campos, `repr` de cada float) y la
    frontera de Pareto dan la misma huella antes y después en 6 escenarios: Pereira DES con 3000 y 4000 psi, Bogotá con
    3 vanos y 3 pisos, Barranquilla DMI, Medellín DMO y Supía con suelo E y grupo II. Son 273 candidatos.
  - `test_scwb_vectorizado_identico_al_recorrido_por_nudo` lo deja vigilado en el CI con igualdad exacta, sin tolerancia.
- La mejora sin caché viene de `_scwb`. Antes era el 60 % del diseño de columna, con unas 20.800 interpolaciones por
  petición; ahora la demanda concatena sus nudos una sola vez (`DemandaColumna.nudos_concatenados`). Como dividir entre un
  ΣMnb positivo es monótono, min(aᵢ)/d = min(aᵢ/d) exactamente.

Como en la fase 1, son tiempos locales, sin red y con TestClient: **no es latencia de producción**. Sirven para comparar
antes y después en la misma máquina y en la misma corrida.

## Límites y siguiente paso

- La caché es del proceso: se pierde al reiniciar y no se comparte entre instancias. Hoy la API corre en una sola instancia
  (`apps/api/cache.py`). Una caché compartida (tabla o Redis) es otra decisión, que depende de #193.
- El `RegistroEfectos` también está en memoria. Para usar idempotencia en producción (p. ej. en `/apu/calculate-batch`, que
  escribe en Supabase) el registro debe ser durable: una tabla con restricción única sobre la llave. Esa migración toca
  producción y queda pendiente de aprobación.
- Faltan `/consultar` y `/ask`: dependen del LLM y de Supabase, y se medirán en el nocturno con el modelo local, nunca contra
  la cuota de producción. Ahí sí rinde el paralelismo (recuperar varias normas a la vez).
