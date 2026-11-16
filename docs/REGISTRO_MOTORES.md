# Registro de motores medidos a producción

Generado por `scripts/inventario/registro_motores.py`; no editar a mano. Criterio: sección «Criterio de motor «medido a producción»» de [REGLAS_MOTORES_DE_CALCULO.md](REGLAS_MOTORES_DE_CALCULO.md).

1. Pruebas rojo→verde contra referencia independiente · 2. Revisión adversaria corregida · 3. Contrato, 422 y límite de tasa · 4. Desplegado en Cloud Run y verificado con llamada real.

**Cómo se llenan las celdas.** La condición 3 se deduce del código de cada router. Las condiciones 1, 2 y 4 no se pueden deducir: se atestiguan con evidencia en [registro_motores.json](registro_motores.json). «?» significa sin atestar, **no** que cumpla; «no» significa que se comprobó que no cumple.

**Estado: 2 de 10 motores cumplen las cuatro condiciones** (el DAG sigue sin conectarse).

| Motor (router) | Paquete | 1 | 2 | 3 | 4 | Pruebas paquete / router | CI | Endpoints |
|---|---|---|---|---|---|---|---|---|
| `analisis` | `motor-analisis` | ? | ? | sí | ? | 18 / 3 | sí | POST /analisis/portico |
| `aquai` | `motor-aquai` | ? | ? | no | ? | 89 / 5 | sí | POST /aquai/poblacion, POST /aquai/caudales, POST /aquai/hidraulica, POST /aquai/hidrologia, POST /aquai/verificar/res0330, GET /aquai/hidrologia/estaciones-ideam, GET /aquai/hidrologia/precipitacion-ideam, GET /aquai/hidrologia/caudal-ideam, POST /aquai/hidraulica/manning, POST /aquai/hidraulica/ariete, POST /aquai/hidraulica/bombeo, POST /aquai/saneamiento/ptap, POST /aquai/saneamiento/ptar, POST /aquai/saneamiento/lagunas, POST /aquai/tarifas/calcular, POST /aquai/sui/reporte, POST /aquai/reporte/memoria |
| `concreto` | `motor-concreto` | ? | ? | sí | ? | 287 / 5 | sí | POST /concreto/zapata, POST /concreto/talud |
| `geotecnia` | `motor-geotecnia` | sí | sí | sí | sí | 88 / 5 | sí | POST /geotecnia/asentamiento, POST /geotecnia/portante |
| `licuacion` | `motor-licuacion` | ? | ? | sí | sí | 53 / 7 | sí | POST /licuacion/spt |
| `orquestador_api` | `orquestador` | ? | ? | sí | ? | 85 / 9 | sí | POST /orquestador/portico-integral, POST /orquestador/portico-pareto |
| `redes` | `motor-redes` | sí | sí | sí | sí | 105 / 11 | sí | POST /redes/permanente, POST /redes/periodo, POST /redes/ariete |

El conteo de pruebas son funciones `test_*`; una prueba parametrizada cuenta una vez.

## Evidencia atestada

### `aquai`
- condición 3: sin límite de tasa o sin 422 explícito en POST /aquai/verificar/res0330, GET /aquai/hidrologia/estaciones-ideam, GET /aquai/hidrologia/precipitacion-ideam, GET /aquai/hidrologia/caudal-ideam, POST /aquai/reporte/memoria

### `geotecnia`
- condicion 1: docs/REGLAS_MOTORES_DE_CALCULO.md declara que motor-geotecnia cumple 1–3 en su primer corte. Atestación heredada de ese documento; no re-verificada en esta revisión.
- condicion 2: Mismo documento (cumple 1–3). Atestación heredada; no re-verificada en esta revisión.
- condicion 4: POST /geotecnia/asentamiento: Δσ 2:1 = 21,4286 kPa y S = 50,5925 mm, idénticos a Terzaghi NC a mano. Llamada real autenticada contra la revisión en producción con infra/gcp/llamadas_reales.py (tolerancia relativa 1e-9). (revisión structai-api-00015-hot, 2026-11-16)

### `licuacion`
- condicion 4: POST /licuacion/spt: CSR 0,214100, CRR 0,160058 y FS 0,747313 en la primera subcapa, idénticos a Seed-Idriss / Youd et al. (2001) a mano. Llamada real autenticada contra la revisión en producción con infra/gcp/llamadas_reales.py (tolerancia relativa 1e-9). (revisión structai-api-00015-hot, 2026-11-16)

### `redes`
- condicion 1: docs/VALIDACION_REDES_EPANET_2026-11.md y packages/motor-redes/tests/test_validacion_epanet.py: Hardy-Cross, soluciones cerradas, scipy y casos EPANET (Net1, todinitest); golpe de ariete contra Joukowsky y onda cuadrada. Es validación frente a otro solver y a casos analíticos, no contra datos medidos.
- condicion 2: Dos revisiones adversarias (solver permanente; bombas, válvulas y periodo extendido) corregidas en el commit 3160c9a; pruebas en packages/motor-redes/tests/test_revision2.py.
- condicion 4: POST /redes/permanente: carga en N = 93,571884 m, idéntica a Hazen-Williams a mano (1 km, D=0,3 m, C=130, Q=0,1 m³/s). Llamada real autenticada contra la revisión en producción con infra/gcp/llamadas_reales.py (tolerancia relativa 1e-9). (revisión structai-api-00015-hot, 2026-11-16)
