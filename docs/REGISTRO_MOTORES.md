# Registro de motores medidos a producción

Generado por `scripts/inventario/registro_motores.py`; no editar a mano. Criterio: sección «Criterio de motor «medido a producción»» de [REGLAS_MOTORES_DE_CALCULO.md](REGLAS_MOTORES_DE_CALCULO.md).

1. Pruebas rojo→verde contra referencia independiente · 2. Revisión adversaria corregida · 3. Contrato, 422 y límite de tasa · 4. Desplegado en Cloud Run y verificado con llamada real.

**Cómo se llenan las celdas.** La condición 3 se deduce del código de cada router. Las condiciones 1, 2 y 4 no se pueden deducir: se atestiguan con evidencia en [registro_motores.json](registro_motores.json). «?» significa sin atestar, **no** que cumpla; «no» significa que se comprobó que no cumple.

**Estado: 0 de 10 motores cumplen las cuatro condiciones** (el DAG sigue sin conectarse).

| Motor (router) | Paquete | 1 | 2 | 3 | 4 | Pruebas paquete / router | CI | Endpoints |
|---|---|---|---|---|---|---|---|---|
| `analisis` | `motor-analisis` | ? | ? | sí | ? | 18 / 3 | sí | POST /analisis/portico |
| `concreto` | `motor-concreto` | ? | ? | sí | ? | 285 / 5 | sí | POST /concreto/zapata, POST /concreto/talud |
| `geotecnia` | `motor-geotecnia` | sí | sí | sí | no | 88 / 5 | sí | POST /geotecnia/asentamiento, POST /geotecnia/portante |
| `licuacion` | `motor-licuacion` | ? | ? | sí | no | 53 / 7 | sí | POST /licuacion/spt |
| `orquestador_api` | `orquestador` | ? | ? | sí | ? | 75 / 4 | sí | POST /orquestador/portico-integral |
| `redes` | `motor-redes` | sí | sí | sí | no | 105 / 11 | sí | POST /redes/permanente, POST /redes/periodo, POST /redes/ariete |

El conteo de pruebas son funciones `test_*`; una prueba parametrizada cuenta una vez.

## Evidencia atestada

### `geotecnia`
- condicion 1: docs/REGLAS_MOTORES_DE_CALCULO.md declara que motor-geotecnia cumple 1–3 en su primer corte. Atestación heredada de ese documento; no re-verificada en esta revisión.
- condicion 2: Mismo documento (cumple 1–3). Atestación heredada; no re-verificada en esta revisión.
- condicion 4: Sin desplegar según el estado de la sesión del 2026-11-09 (la imagen de Cloud Run es anterior a este motor); confirmar con infra/gcp/desplegar.sh.

### `licuacion`
- condicion 4: Sin desplegar según el estado de la sesión del 2026-11-09 (la imagen de Cloud Run es anterior a este motor); confirmar con infra/gcp/desplegar.sh.

### `redes`
- condicion 1: docs/VALIDACION_REDES_EPANET_2026-11.md y packages/motor-redes/tests/test_validacion_epanet.py: Hardy-Cross, soluciones cerradas, scipy y casos EPANET (Net1, todinitest); golpe de ariete contra Joukowsky y onda cuadrada. Es validación frente a otro solver y a casos analíticos, no contra datos medidos.
- condicion 2: Dos revisiones adversarias (solver permanente; bombas, válvulas y periodo extendido) corregidas en el commit 3160c9a; pruebas en packages/motor-redes/tests/test_revision2.py.
- condicion 4: Sin desplegar: la imagen de Cloud Run es anterior a geotecnia, licuación y redes.
