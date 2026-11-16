# Latencia por paso de las cadenas de ejecución (#221)

Medido el 2026-11-16T10:18:41 en Windows AMD64 (Python 3.12.10) con `scripts/medicion/medir_cadenas.py`. Local, sin red externa, con los efectos sustituidos: **no es latencia de producción**, es la línea base del cómputo propio de cada cadena para comparar antes y después del encapsulado (fase 2).

Tiempo «propio» = tiempo del paso sin los pasos instrumentados que llama. La primera petición (calentamiento) no se cuenta.

## `POST /orquestador/portico-integral`

- Peticiones: 10 · p50 **543.2 ms** · p95 **596.4 ms** · tasa de error 0% (pasada sin instrumentar; instrumentar añade 2% al p50)
- Etiquetas del inventario: dependiente_de_norma
- Pasos instrumentados: 23; no instrumentables (llamadas encadenadas o externas): 0

| Paso | Llamadas/petición | Propio por petición (ms) | p50 (ms) | p95 (ms) | Error |
|---|---|---|---|---|---|
| `packages/motor-concreto/src/columna.py::disenar_columna` | 99 | 410.76 | 3.86 | 6.25 | 0% |
| `packages/motor-concreto/src/diseno_viga.py::disenar` | 33 | 35.50 | 0.87 | 1.46 | 0% |
| `packages/orquestador/src/grilla_vectorizada.py::analizar_lote` | 4 | 35.00 | 9.94 | 13.19 | 0% |
| `packages/orquestador/src/diseno_portico.py::_costo_nivel` | 290 | 25.97 | 0.07 | 0.20 | 0% |
| `packages/motor-concreto/src/diseno_viga.py::_mn_nominal` | 4510 | 5.56 | 0.00 | 0.00 | 0% |
| `packages/orquestador/src/diseno_portico.py::_analizar` | 1 | 3.85 | 4.51 | 5.22 | 0% |
| `packages/orquestador/src/diseno_portico.py::_modelo` | 5 | 3.22 | 0.60 | 0.92 | 0% |
| `packages/orquestador/src/grilla_vectorizada.py::construir_plantilla` | 4 | 2.78 | 0.60 | 1.17 | 0% |
| `packages/orquestador/src/diseno_integral.py::costo_columnas` | 873 | 2.52 | 0.00 | 0.01 | 0% |
| `packages/orquestador/src/diseno_portico.py::_demanda` | 1 | 1.62 | 1.46 | 2.53 | 0% |
| `packages/orquestador/src/diseno_integral.py::_ks` | 33 | 0.87 | 0.02 | 0.04 | 0% |
| `packages/orquestador/src/grilla_vectorizada.py::_combos` | 37 | 0.81 | 0.02 | 0.03 | 0% |
| `packages/orquestador/src/diseno_portico.py::_capacidad` | 1 | 0.72 | 0.69 | 0.98 | 0% |
| `packages/motor-concreto/src/diseno_viga.py::_d` | 429 | 0.35 | 0.00 | 0.00 | 0% |
| `packages/orquestador/src/sismo_portico.py::pesos_nivel_kn` | 5 | 0.27 | 0.05 | 0.09 | 0% |
| `packages/orquestador/src/diseno_portico.py::_lote_vectorizado` | 4 | 0.21 | 11.55 | 15.08 | 0% |
| `packages/orquestador/src/sismo_portico.py::parametros_espectro` | 4 | 0.20 | 0.04 | 0.07 | 0% |
| `packages/orquestador/src/sismo_portico.py::fuerzas_vectorizadas` | 4 | 0.16 | 0.04 | 0.07 | 0% |
| `packages/orquestador/src/diseno_integral.py::_tabla_secciones` | 1 | 0.14 | 0.13 | 0.18 | 0% |
| `packages/orquestador/src/diseno_portico.py::_basal_escalar` | 1 | 0.06 | 0.09 | 0.15 | 0% |
| `packages/orquestador/src/diseno_portico.py::_derivar_basal` | 1 | 0.06 | 0.06 | 0.06 | 0% |
| `packages/orquestador/src/diseno_portico.py::_ctx_sismico` | 1 | 0.01 | 0.01 | 0.02 | 0% |
| `packages/orquestador/src/sismo_portico.py::alturas_nivel_m` | 5 | 0.01 | 0.00 | 0.00 | 0% |
| *No atribuido a ningún paso del inventario* | | 21.88 | | | |

El 4% del p50 instrumentado no cae en ningún paso declarado: es código propio del endpoint utilidades de CPU que el inventario no cuenta como paso (p. ej. leer y escribir el Excel) o llamadas que no resuelve. Si es grande, hay que revisar el inventario antes de priorizar con esta tabla.

## `POST /apu/calculate-batch`

- Peticiones: 10 · p50 **93.3 ms** · p95 **99.7 ms** · tasa de error 0% (pasada sin instrumentar; instrumentar añade -2% al p50)
- Etiquetas del inventario: con_efectos, dependiente_de_norma, dependiente_de_datos
- Pasos instrumentados: 3; no instrumentables (llamadas encadenadas o externas): 2
- Sustituidos por funciones inertes (no medidos): get_current_user (auth), _cupo_apu_mes_restante (lectura BD), registrar_apu_calculos_lote (escritura BD)

| Paso | Llamadas/petición | Propio por petición (ms) | p50 (ms) | p95 (ms) | Error |
|---|---|---|---|---|---|
| `packages/motor-apu/src/catalogue.py::get_apu` | 10 | 25.98 | 1.88 | 5.41 | 0% |
| `packages/motor-apu/src/cantidades.py::calcular_apu_dinamico` | 10 | 25.59 | 2.39 | 3.12 | 0% |
| `apps/api/main.py::registrar_apu_calculos_lote` | 1 | 0.00 | 0.00 | 0.00 | 0% |
| *No atribuido a ningún paso del inventario* | | 39.57 | | | |

El 43% del p50 instrumentado no cae en ningún paso declarado: es código propio del endpoint utilidades de CPU que el inventario no cuenta como paso (p. ej. leer y escribir el Excel) o llamadas que no resuelve. Si es grande, hay que revisar el inventario antes de priorizar con esta tabla.

## Cómo leer y repetir esta medición

- Los tiempos absolutos de una misma máquina cambiaron hasta ~1,8× entre corridas del mismo día (carga, energía). Por eso cada corrida alterna peticiones limpias e instrumentadas, y el antes/después de la fase 2 debe medirse **alternado en la misma corrida**, nunca comparando corridas de días distintos.
- El sobrecosto de instrumentar se mide en cada corrida (columna de arriba); con el plan de reemplazos precalculado queda en pocos puntos porcentuales.
- Esta medición mostró que el inventario estático no veía los módulos cargados con `importlib.import_module` ni los alias reexportados (`_dv, _viga = _dp._dv, _dp._viga`): el 83 % del pórtico quedaba sin atribuir. Se corrigió en `scripts/inventario/cadenas_ejecucion.py` y el diseño de columna apareció como el paso dominante.

## Pendiente

- `/consultar`, `/ask` y `/amenaza-sismica`: necesitan Supabase, el LLM y el SGC. Se medirán en el nocturno con el modelo local (#172/#178) y lectura controlada, nunca contra la cuota de producción.
- Fase 2: encapsular como flujo atómico y repetir esta medición; meta preregistrada ≥ 30 % menos p95 con aciertos de caché y cero diferencias de resultado.
