# Inventario de cadenas de ejecución (#221, fase 1)

Generado por `scripts/inventario/cadenas_ejecucion.py`; no editar a mano. Análisis **estático** (AST + imports): dice qué pasos hay y de qué tipo, **no cuánto tardan**. El orden de trabajo lo da latencia × frecuencia medidas (fase 1, paso 2), nunca este conteo solo. Ver el docstring para la definición de paso, tipo y etiqueta.

- Código analizado: 699 módulos, 2,868 funciones (sin pruebas).
- Puntos de entrada: 100 endpoints y 376 pipelines fuera de línea.
- **Candidatas a flujo atómico (≥ 4 pasos secuenciales): 99** (13 endpoints, 86 pipelines).
- Cadenas futuras con ≥ 4 motores que pasan por un motor planificado o bloqueado: **36** (solo nodos declarados en `docs/coherencia_motores.json`).
- Resolución de los pasos: externo 1286, import 150, local 405, por_nombre 55 (`por_nombre` = función única en el repo con ese nombre; revisar si un paso parece fuera de lugar).

## Etiquetas de las candidatas

| Etiqueta | Candidatas | Qué permite |
|---|---|---|
| `con_efectos` | 90 | llave de idempotencia (no caché) |
| `con_LLM` | 7 | caché por hash de prompt + modelo + contexto, con aviso |
| `dependiente_de_norma` | 17 | caché con la versión de la norma en la llave (#193) |
| `dependiente_de_datos` | 93 | caché con la versión/fecha del dato (catálogo, tabla) en la llave |
| `pura` | 1 | caché directa |
| `sin_clasificar` | 0 | revisar a mano |

Con caché ya existente en la secuencia: 14 de 99.

## Por familia

| Familia | Cadenas | Candidatas | Con LLM | Con efectos |
|---|---|---|---|---|
| scripts/ingesta | 225 | 33 | 0 | 219 |
| motor | 84 | 5 | 0 | 1 |
| scripts/satelite | 48 | 19 | 0 | 44 |
| scripts/evaluacion | 27 | 10 | 9 | 20 |
| scripts/precios | 16 | 5 | 0 | 15 |
| scripts/hidro | 16 | 7 | 0 | 15 |
| scripts/regional | 9 | 0 | 0 | 6 |
| scripts/mantenimiento | 8 | 3 | 0 | 7 |
| scripts/inventario | 7 | 1 | 0 | 6 |
| orquestador | 5 | 2 | 0 | 0 |
| precios | 5 | 3 | 0 | 3 |
| scripts/secop | 4 | 3 | 0 | 4 |
| scripts/macro | 4 | 2 | 0 | 3 |
| rag | 3 | 2 | 2 | 2 |
| scripts/datos | 3 | 0 | 0 | 3 |
| sistema | 2 | 1 | 0 | 0 |
| scripts/excavacion | 2 | 2 | 0 | 2 |
| scripts/clima | 2 | 1 | 0 | 2 |
| scripts/medicion | 2 | 0 | 0 | 1 |
| scripts/surrogate_zapata | 2 | 0 | 0 | 2 |
| vision | 1 | 0 | 0 | 0 |
| scripts/respaldo | 1 | 0 | 0 | 1 |

## Endpoints candidatos (los que ve el usuario)

| Entrada | Pasos | Etiquetas | Caché | Secuencia |
|---|---|---|---|---|
| `POST /consultar` | 61 | con_efectos, con_LLM, dependiente_de_norma, dependiente_de_datos | sí | _uso_sb.table().select().eq().maybe_single().execute[bd] → _uso_sb.table().select().eq().gte().execute[bd] → _cache_consultar.get[cache] → _informe_sitio_directo[bd] → embed_query[cache] → _centroides[embeddings] → embed_query[cache] → sb.rpc().execute[bd] → buscar_precios_apu[bd] → buscar_precios_invias_vias[bd] → search[bd] → _format_precio_context[bd] → … (+49) |
| `POST /ask` | 43 | con_efectos, con_LLM, dependiente_de_norma, dependiente_de_datos | sí | _uso_sb.table().select().eq().maybe_single().execute[bd] → _uso_sb.table().select().eq().gte().execute[bd] → _cache_ask.get[cache] → _informe_sitio_directo[bd] → _cache_l1.get[cache] → sb.table().select().eq().limit().execute[bd] → _cache_l1.set[cache] → _con_plugins[bd] → groq_client.chat.completions.create[llm] → openai_client.chat.completions.create[llm] → embed_query[cache] → sb.rpc().execute[bd] → … (+31) |
| `POST /orquestador/portico-pareto` | 24 | dependiente_de_norma | no | _capacidad[motor] → _ctx_sismico[motor] → _tabla_secciones[motor] → _lote_vectorizado[motor] → disenar[motor] → _costo_nivel[motor] → demanda_columnas[motor] → _mn_viga[motor] → disenar_columna[motor] → costo_columnas[motor] → _verificar_optimo[motor] → cantidades_portico[motor] → … (+12) |
| `POST /orquestador/portico-integral` | 23 | dependiente_de_norma | no | _capacidad[motor] → _ctx_sismico[motor] → _tabla_secciones[motor] → _modelo[motor] → construir_plantilla[motor] → alturas_nivel_m[motor] → pesos_nivel_kn[motor] → parametros_espectro[motor] → fuerzas_vectorizadas[motor] → analizar_lote[motor] → disenar[motor] → _costo_nivel[motor] → … (+11) |
| `GET /aquai/hidrologia/caudal-ideam` | 9 | dependiente_de_datos | sí | _get[red] → resolver_departamento[red] → _CACHE_DEPARTAMENTOS.get[cache] → httpx.Client[red] → client.get[red] → httpx.Client[red] → client.get[red] → httpx.Client[red] → client.get[red] |
| `GET /aquai/hidrologia/estaciones-ideam` | 8 | dependiente_de_datos | sí | httpx.Client[red] → client.get[red] → resolver_departamento[red] → _CACHE_DEPARTAMENTOS.get[cache] → httpx.Client[red] → client.get[red] → httpx.Client[red] → client.get[red] |
| `GET /amenaza-sismica` | 7 | dependiente_de_norma, dependiente_de_datos | sí | create_client[bd] → sb.table().select().range().execute[bd] → _agrupar[red] → httpx.get[red] → _agrupar[red] → cache.get[cache] → consultar_movimientos_cercanos[red] |
| `GET /data-status` | 7 | dependiente_de_datos | no | _contar_filas[bd] → _ultima_fila[bd] → _contar_filas[bd] → _ultima_fila[bd] → _contar_filas[bd] → _ultima_fila[bd] → _contar_filas[bd] |
| `POST /apu/calculate` | 6 | con_efectos, dependiente_de_norma, dependiente_de_datos | no | _uso_sb.table().select().eq().maybe_single().execute[bd] → _uso_sb.table().select().eq().gte().execute[bd] → _uso_sb.table().select().eq().maybe_single().execute[bd] → _uso_sb.table().select().eq().execute[bd] → get_apu[motor] → registrar_apu_calculo[efecto] |
| `POST /apu/calculate-dinamico` | 6 | con_efectos, dependiente_de_norma, dependiente_de_datos | no | _uso_sb.table().select().eq().maybe_single().execute[bd] → _uso_sb.table().select().eq().gte().execute[bd] → _uso_sb.table().select().eq().maybe_single().execute[bd] → _uso_sb.table().select().eq().execute[bd] → calcular_apu_dinamico[motor] → registrar_apu_calculo[efecto] |
| `POST /vulnerabilidad-vivienda/evaluar` | 6 | dependiente_de_norma, dependiente_de_datos | sí | create_client[bd] → sb.table().select().range().execute[bd] → _agrupar[red] → httpx.get[red] → _agrupar[red] → cache.get[cache] |
| `POST /apu/calculate-batch` | 5 | con_efectos, dependiente_de_norma, dependiente_de_datos | no | _uso_sb.table().select().eq().maybe_single().execute[bd] → _uso_sb.table().select().eq().gte().execute[bd] → get_apu[motor] → calcular_apu_dinamico[motor] → registrar_apu_calculos_lote[efecto] |
| `GET /admin/feedback` | 4 | dependiente_de_datos | no | require_admin[bd] → _uso_sb.table().select().eq().order().limit().execute[bd] → _uso_sb.table().select().execute[bd] → _uso_sb.table().select().eq().execute[bd] |

## Pipelines recurrentes candidatos (fuera de línea)

86 pipelines recurrentes llegan al umbral; 161 scripts puntuales (prefijo `_`, fecha en el nombre, fix/parche/reintento) no cuentan como candidatos. Los 25 más largos:

| Entrada | Pasos | Etiquetas | Secuencia |
|---|---|---|---|
| `scripts/evaluacion/comparar_groq_vs_gemini_vertex.py` | 40 | con_efectos, con_LLM, dependiente_de_norma, dependiente_de_datos | _informe_sitio_directo[bd] → _cache_l1.get[cache] → sb.table().select().eq().limit().execute[bd] → _cache_l1.set[cache] → _con_plugins[bd] → groq_client.chat.completions.create[llm] → openai_client.chat.completions.create[llm] → … (+33) |
| `scripts/evaluacion/comparar_groq_vs_ollama_local.py` | 40 | con_efectos, con_LLM, dependiente_de_norma, dependiente_de_datos | _informe_sitio_directo[bd] → _cache_l1.get[cache] → sb.table().select().eq().limit().execute[bd] → _cache_l1.set[cache] → _con_plugins[bd] → groq_client.chat.completions.create[llm] → openai_client.chat.completions.create[llm] → … (+33) |
| `scripts/evaluacion/ragas_52preguntas.py` | 27 | con_efectos, con_LLM, dependiente_de_norma, dependiente_de_datos | _informe_sitio_directo[bd] → _cache_l1.get[cache] → sb.table().select().eq().limit().execute[bd] → _cache_l1.set[cache] → _con_plugins[bd] → _descomponer_pregunta[llm] → _recuperar_candidatos_normativa[bd] → … (+20) |
| `scripts/evaluacion/ragas_baseline_nsr10.py` | 27 | con_efectos, con_LLM, dependiente_de_norma, dependiente_de_datos | _informe_sitio_directo[bd] → _cache_l1.get[cache] → sb.table().select().eq().limit().execute[bd] → _cache_l1.set[cache] → _con_plugins[bd] → _descomponer_pregunta[llm] → _recuperar_candidatos_normativa[bd] → … (+20) |
| `scripts/excavacion/comparar_alternativas_sintetico.py` | 21 | con_efectos, dependiente_de_norma | factor_seguridad_requerido[motor] → angulo_maximo_seguro[motor] → perfil_talud[motor] → costo_riesgo_geotecnico[motor] → intensidad_energetica[motor] → indice_eficiencia_geometrica[motor] → perfil_talud[motor] → … (+14) |
| `scripts/precios/agregados_canteras.py` | 13 | con_efectos, dependiente_de_datos | httpx.Client[red] → client.get[red] → requests.get[red] → CACHE_ANM.write_text[efecto] → httpx.Client[red] → client.get[red] → httpx.Client[red] → … (+6) |
| `scripts/precios/geografia_precios_invias.py` | 12 | con_efectos, dependiente_de_datos | create_client[bd] → sb.table().select().range().execute[bd] → f.write_text[efecto] → sb.table().select().range().execute[bd] → f.write_text[efecto] → sb.table().select().range().execute[bd] → f.write_text[efecto] → … (+5) |
| `scripts/evaluacion/fase2b_geologia_cauces.py` | 10 | con_efectos, dependiente_de_datos | reconstruir_grupos[bd] → httpx.Client[red] → client.get[red] → resolver_departamento[red] → httpx.Client[red] → client.get[red] → resolver_departamento[red] → … (+3) |
| `scripts/secop/extraer_obras_secop.py` | 10 | con_efectos, dependiente_de_datos | urllib.request.Request[red] → urllib.request.urlopen[red] → f.write_text[efecto] → urllib.request.Request[red] → urllib.request.urlopen[red] → urllib.request.Request[red] → urllib.request.urlopen[red] → … (+3) |
| `scripts/evaluacion/fase2_elevacion_continua.py` | 9 | con_efectos, dependiente_de_datos | reconstruir_grupos[bd] → httpx.Client[red] → client.get[red] → resolver_departamento[red] → httpx.Client[red] → client.get[red] → resolver_departamento[red] → … (+2) |
| `scripts/evaluacion/ragas_precios.py` | 8 | con_efectos, con_LLM, dependiente_de_datos | buscar_precios_apu[bd] → _detectar_ubicacion_invias[bd] → sb.rpc().execute[bd] → _format_precio_context[bd] → groq_client.chat.completions.create[llm] → openai_client.chat.completions.create[llm] → df.to_csv[efecto] → … (+1) |
| `scripts/satelite/auditar_datos_caribe.py` | 8 | con_efectos, dependiente_de_datos | _sb[bd] → sb.table().select().in_().range().execute[bd] → _sb[bd] → sb.table().select().in_().range().execute[bd] → _sb[bd] → sb.table().select().in_().range().execute[bd] → fig.savefig[efecto] → … (+1) |
| `scripts/satelite/barrido_caribe.py` | 8 | con_efectos, dependiente_de_datos | _sb[bd] → sb.table().select().in_().range().execute[bd] → _sb[bd] → sb.table().select().in_().range().execute[bd] → _sb[bd] → sb.table().select().in_().range().execute[bd] → panel.to_csv[efecto] → … (+1) |
| `scripts/ingesta/ideam_caudal/cargar_caudal_historico.py` | 7 | con_efectos, dependiente_de_datos | create_client[bd] → httpx.Client[red] → client.get[red] → sb.table().upsert().execute[efecto] → httpx.Client[red] → client.get[red] → sb.table().upsert().execute[efecto] |
| `scripts/ingesta/ungrd_emergencias/cargar_ungrd_emergencias.py` | 7 | con_efectos, dependiente_de_datos | create_client[bd] → httpx.Client[red] → sb.table().delete().eq().execute[efecto] → client.get[red] → httpx.Client[red] → client.get[red] → sb.table().insert().execute[efecto] |
| `scripts/satelite/extraer_dem_piloto.py` | 7 | con_efectos, dependiente_de_datos | httpx.Client[red] → client.get[red] → httpx.Client[red] → client.get[red] → urllib.request.Request[red] → urllib.request.urlopen[red] → salida.write_text[efecto] |
| `scripts/clima/extraer_temperatura_caribe.py` | 6 | con_efectos, dependiente_de_datos | urllib.request.Request[red] → urllib.request.urlopen().read[red] → tna.write_bytes[efecto] → urllib.request.Request[red] → urllib.request.urlopen().read[red] → sal.write_text[efecto] |
| `scripts/evaluacion/fase67_deforestacion_movimiento_masa.py` | 6 | con_efectos, dependiente_de_datos | _paginar[bd] → httpx.Client[red] → client.get[red] → resolver_departamento[red] → httpx.get[red] → json.dump[efecto] |
| `scripts/excavacion/balance_tierras_sintetico.py` | 6 | con_efectos, dependiente_de_norma | resolver_balance[motor] → combustible_gal_por_m3_km[motor] → resolver_balance[motor] → combustible_gal_por_m3_km[motor] → destino.write_text[efecto] → tasa_reutilizacion[motor] |
| `scripts/hidro/regimen_termico.py` | 6 | con_efectos, dependiente_de_datos | requests.get().json[red] → d.to_csv[efecto] → _sb[bd] → sb.table().select().range().execute[bd] → d[].to_csv[efecto] → ?.write_text[efecto] |
| `scripts/ingesta/apu_barranquilla/enriquecer_ubicacion_proveedores_rues.py` | 6 | con_efectos, dependiente_de_datos | create_client[bd] → sb.table().select().is_().execute[bd] → sb.table().select().range().execute[bd] → httpx.Client[red] → _buscar_en_rues[red] → sb.table().update().eq().execute[efecto] |
| `scripts/ingesta/normativa_general/ingest_decreto_1072_sgsst.py` | 6 | con_efectos, dependiente_de_datos | create_client[bd] → sb.table().select().eq().execute[bd] → sb.table().insert().execute[efecto] → model.encode[embeddings] → sb.table().delete().eq().execute[efecto] → sb.table().insert().execute[efecto] |
| `scripts/ingesta/normativa_general/ingest_normativa.py` | 6 | con_efectos, dependiente_de_datos | create_client[bd] → model.encode[embeddings] → sb.table().upsert().execute[efecto] → model.encode[embeddings] → sb.table().delete().eq().execute[efecto] → sb.table().insert().execute[efecto] |
| `scripts/ingesta/sisben_vulnerabilidad/cargar_vulnerabilidad_vivienda.py` | 6 | con_efectos, dependiente_de_datos | create_client[bd] → httpx.Client[red] → _agregado_por_municipio[red] → httpx.Client[red] → client.get[red] → sb.table().upsert().execute[efecto] |
| `scripts/precios/costo_parametrico_pavimentos.py` | 6 | con_efectos, dependiente_de_datos | _sb[bd] → sb.table().select().in_().order().order().range().execute[bd] → CACHE.write_text[efecto] → _sb[bd] → sb.table().select().execute[bd] → ?.write_text[efecto] |

| Carpeta | Pipelines candidatos | Con efectos | Con LLM |
|---|---|---|---|
| `scripts/ingesta` | 33 | 33 | 0 |
| `scripts/satelite` | 19 | 19 | 0 |
| `scripts/evaluacion` | 10 | 9 | 5 |
| `scripts/hidro` | 7 | 7 | 0 |
| `scripts/precios` | 5 | 5 | 0 |
| `scripts/secop` | 3 | 3 | 0 |
| `scripts/mantenimiento` | 3 | 3 | 0 |
| `scripts/excavacion` | 2 | 2 | 0 |
| `scripts/macro` | 2 | 2 | 0 |
| `scripts/clima` | 1 | 1 | 0 |
| `scripts/inventario` | 1 | 1 | 0 |

## Cadenas futuras (motores planificados o bloqueados)

Inventario estricto: caminos simples entre nodos **declarados** (con evidencia) en `docs/coherencia_motores.json`, enlazados por magnitudes que uno produce y otro consume. Ningún motor futuro se cuenta como funcionando. Todas son cálculo de motores: al implementarse nacen como flujo atómico `dependiente_de_norma` con artefactos direccionados por contenido (#150).

| Motor futuro | Estado | Cadenas futuras en las que aparece | Máximo de nodos |
|---|---|---|---|
| `futuro-sustituto-seccion-portico` | planificado | 30 | 6 |
| `futuro-columna-circular` | planificado | 8 | 5 |
| `futuro-pilotes` | bloqueado | 8 | 5 |

Un motor futuro que aparece en muchas cadenas desbloquea más flujos al implementarse; es una señal de prioridad, no la única (falta el costo de construirlo y la demanda medida).

| Nodos | Cadena | Motores futuros | Magnitudes que pasan |
|---|---|---|---|
| 6 | dato-microzonificacion-local → futuro-sustituto-seccion-portico → motor-analisis → motor-concreto → motor-geotecnia → optimizador-portico | futuro-sustituto-seccion-portico | coef_espectro_local / seccion_columna_mm,seccion_viga_mm / reaccion_vertical_kn / presion_contacto_kpa / razon_demanda_capacidad |
| 6 | motor-geopot → futuro-sustituto-seccion-portico → motor-analisis → motor-concreto → motor-geotecnia → optimizador-portico | futuro-sustituto-seccion-portico | coef_aceleracion_aa,coef_velocidad_av / seccion_columna_mm,seccion_viga_mm / reaccion_vertical_kn / presion_contacto_kpa / razon_demanda_capacidad |
| 5 | dato-microzonificacion-local → futuro-sustituto-seccion-portico → motor-analisis → futuro-columna-circular → optimizador-portico | futuro-sustituto-seccion-portico, futuro-columna-circular | coef_espectro_local / seccion_columna_mm,seccion_viga_mm / momento_flector_knm,reaccion_vertical_kn / masa_acero_kg,razon_demanda_capacidad,volumen_concreto_m3 |
| 5 | dato-microzonificacion-local → futuro-sustituto-seccion-portico → motor-analisis → futuro-pilotes → optimizador-portico | futuro-sustituto-seccion-portico, futuro-pilotes | coef_espectro_local / seccion_columna_mm,seccion_viga_mm / reaccion_vertical_kn / razon_demanda_capacidad |
| 5 | dato-microzonificacion-local → futuro-sustituto-seccion-portico → motor-analisis → motor-concreto → motor-geotecnia | futuro-sustituto-seccion-portico | coef_espectro_local / seccion_columna_mm,seccion_viga_mm / reaccion_vertical_kn / presion_contacto_kpa |
| 5 | dato-microzonificacion-local → futuro-sustituto-seccion-portico → motor-analisis → motor-concreto → optimizador-portico | futuro-sustituto-seccion-portico | coef_espectro_local / seccion_columna_mm,seccion_viga_mm / reaccion_vertical_kn / co2e_kg,costo_directo_cop,masa_acero_kg,razon_demanda_capacidad,volumen_concreto_m3 |
| 5 | dato-microzonificacion-local → futuro-sustituto-seccion-portico → motor-concreto → motor-geotecnia → optimizador-portico | futuro-sustituto-seccion-portico | coef_espectro_local / seccion_columna_mm / presion_contacto_kpa / razon_demanda_capacidad |
| 5 | futuro-sustituto-seccion-portico → motor-analisis → motor-concreto → motor-geotecnia → optimizador-portico | futuro-sustituto-seccion-portico | seccion_columna_mm,seccion_viga_mm / reaccion_vertical_kn / presion_contacto_kpa / razon_demanda_capacidad |
| 5 | motor-geopot → futuro-sustituto-seccion-portico → motor-analisis → futuro-columna-circular → optimizador-portico | futuro-sustituto-seccion-portico, futuro-columna-circular | coef_aceleracion_aa,coef_velocidad_av / seccion_columna_mm,seccion_viga_mm / momento_flector_knm,reaccion_vertical_kn / masa_acero_kg,razon_demanda_capacidad,volumen_concreto_m3 |
| 5 | motor-geopot → futuro-sustituto-seccion-portico → motor-analisis → futuro-pilotes → optimizador-portico | futuro-sustituto-seccion-portico, futuro-pilotes | coef_aceleracion_aa,coef_velocidad_av / seccion_columna_mm,seccion_viga_mm / reaccion_vertical_kn / razon_demanda_capacidad |
| 5 | motor-geopot → futuro-sustituto-seccion-portico → motor-analisis → motor-concreto → motor-geotecnia | futuro-sustituto-seccion-portico | coef_aceleracion_aa,coef_velocidad_av / seccion_columna_mm,seccion_viga_mm / reaccion_vertical_kn / presion_contacto_kpa |
| 5 | motor-geopot → futuro-sustituto-seccion-portico → motor-analisis → motor-concreto → optimizador-portico | futuro-sustituto-seccion-portico | coef_aceleracion_aa,coef_velocidad_av / seccion_columna_mm,seccion_viga_mm / reaccion_vertical_kn / co2e_kg,costo_directo_cop,masa_acero_kg,razon_demanda_capacidad,volumen_concreto_m3 |
| 5 | motor-geopot → futuro-sustituto-seccion-portico → motor-concreto → motor-geotecnia → optimizador-portico | futuro-sustituto-seccion-portico | coef_aceleracion_aa,coef_velocidad_av / seccion_columna_mm / presion_contacto_kpa / razon_demanda_capacidad |
| 5 | motor-geopot → orquestador → motor-analisis → futuro-columna-circular → optimizador-portico | futuro-columna-circular | coef_aceleracion_aa,coef_velocidad_av / seccion_columna_mm,seccion_viga_mm / momento_flector_knm,reaccion_vertical_kn / masa_acero_kg,razon_demanda_capacidad,volumen_concreto_m3 |
| 5 | motor-geopot → orquestador → motor-analisis → futuro-pilotes → optimizador-portico | futuro-pilotes | coef_aceleracion_aa,coef_velocidad_av / seccion_columna_mm,seccion_viga_mm / reaccion_vertical_kn / razon_demanda_capacidad |
| 4 | dato-microzonificacion-local → futuro-sustituto-seccion-portico → motor-analisis → futuro-columna-circular | futuro-sustituto-seccion-portico, futuro-columna-circular | coef_espectro_local / seccion_columna_mm,seccion_viga_mm / momento_flector_knm,reaccion_vertical_kn |
| 4 | dato-microzonificacion-local → futuro-sustituto-seccion-portico → motor-analisis → futuro-pilotes | futuro-sustituto-seccion-portico, futuro-pilotes | coef_espectro_local / seccion_columna_mm,seccion_viga_mm / reaccion_vertical_kn |
| 4 | dato-microzonificacion-local → futuro-sustituto-seccion-portico → motor-analisis → motor-concreto | futuro-sustituto-seccion-portico | coef_espectro_local / seccion_columna_mm,seccion_viga_mm / reaccion_vertical_kn |
| 4 | dato-microzonificacion-local → futuro-sustituto-seccion-portico → motor-apu → optimizador-portico | futuro-sustituto-seccion-portico | coef_espectro_local / seccion_columna_mm,seccion_viga_mm / costo_directo_cop |
| 4 | dato-microzonificacion-local → futuro-sustituto-seccion-portico → motor-concreto → motor-geotecnia | futuro-sustituto-seccion-portico | coef_espectro_local / seccion_columna_mm / presion_contacto_kpa |
| 4 | dato-microzonificacion-local → futuro-sustituto-seccion-portico → motor-concreto → optimizador-portico | futuro-sustituto-seccion-portico | coef_espectro_local / seccion_columna_mm / co2e_kg,costo_directo_cop,masa_acero_kg,razon_demanda_capacidad,volumen_concreto_m3 |
| 4 | futuro-sustituto-seccion-portico → motor-analisis → futuro-columna-circular → optimizador-portico | futuro-sustituto-seccion-portico, futuro-columna-circular | seccion_columna_mm,seccion_viga_mm / momento_flector_knm,reaccion_vertical_kn / masa_acero_kg,razon_demanda_capacidad,volumen_concreto_m3 |
| 4 | futuro-sustituto-seccion-portico → motor-analisis → futuro-pilotes → optimizador-portico | futuro-sustituto-seccion-portico, futuro-pilotes | seccion_columna_mm,seccion_viga_mm / reaccion_vertical_kn / razon_demanda_capacidad |
| 4 | futuro-sustituto-seccion-portico → motor-analisis → motor-concreto → motor-geotecnia | futuro-sustituto-seccion-portico | seccion_columna_mm,seccion_viga_mm / reaccion_vertical_kn / presion_contacto_kpa |
| 4 | futuro-sustituto-seccion-portico → motor-analisis → motor-concreto → optimizador-portico | futuro-sustituto-seccion-portico | seccion_columna_mm,seccion_viga_mm / reaccion_vertical_kn / co2e_kg,costo_directo_cop,masa_acero_kg,razon_demanda_capacidad,volumen_concreto_m3 |
| 4 | futuro-sustituto-seccion-portico → motor-concreto → motor-geotecnia → optimizador-portico | futuro-sustituto-seccion-portico | seccion_columna_mm / presion_contacto_kpa / razon_demanda_capacidad |
| 4 | motor-geopot → futuro-sustituto-seccion-portico → motor-analisis → futuro-columna-circular | futuro-sustituto-seccion-portico, futuro-columna-circular | coef_aceleracion_aa,coef_velocidad_av / seccion_columna_mm,seccion_viga_mm / momento_flector_knm,reaccion_vertical_kn |
| 4 | motor-geopot → futuro-sustituto-seccion-portico → motor-analisis → futuro-pilotes | futuro-sustituto-seccion-portico, futuro-pilotes | coef_aceleracion_aa,coef_velocidad_av / seccion_columna_mm,seccion_viga_mm / reaccion_vertical_kn |
| 4 | motor-geopot → futuro-sustituto-seccion-portico → motor-analisis → motor-concreto | futuro-sustituto-seccion-portico | coef_aceleracion_aa,coef_velocidad_av / seccion_columna_mm,seccion_viga_mm / reaccion_vertical_kn |
| 4 | motor-geopot → futuro-sustituto-seccion-portico → motor-apu → optimizador-portico | futuro-sustituto-seccion-portico | coef_aceleracion_aa,coef_velocidad_av / seccion_columna_mm,seccion_viga_mm / costo_directo_cop |
| 4 | motor-geopot → futuro-sustituto-seccion-portico → motor-concreto → motor-geotecnia | futuro-sustituto-seccion-portico | coef_aceleracion_aa,coef_velocidad_av / seccion_columna_mm / presion_contacto_kpa |
| 4 | motor-geopot → futuro-sustituto-seccion-portico → motor-concreto → optimizador-portico | futuro-sustituto-seccion-portico | coef_aceleracion_aa,coef_velocidad_av / seccion_columna_mm / co2e_kg,costo_directo_cop,masa_acero_kg,razon_demanda_capacidad,volumen_concreto_m3 |
| 4 | motor-geopot → orquestador → motor-analisis → futuro-columna-circular | futuro-columna-circular | coef_aceleracion_aa,coef_velocidad_av / seccion_columna_mm,seccion_viga_mm / momento_flector_knm,reaccion_vertical_kn |
| 4 | motor-geopot → orquestador → motor-analisis → futuro-pilotes | futuro-pilotes | coef_aceleracion_aa,coef_velocidad_av / seccion_columna_mm,seccion_viga_mm / reaccion_vertical_kn |
| 4 | orquestador → motor-analisis → futuro-columna-circular → optimizador-portico | futuro-columna-circular | seccion_columna_mm,seccion_viga_mm / momento_flector_knm,reaccion_vertical_kn / masa_acero_kg,razon_demanda_capacidad,volumen_concreto_m3 |
| 4 | orquestador → motor-analisis → futuro-pilotes → optimizador-portico | futuro-pilotes | seccion_columna_mm,seccion_viga_mm / reaccion_vertical_kn / razon_demanda_capacidad |

## Cadenas cortas (< 4 pasos)

377 cadenas no llegan al umbral. No se descartan: una de 3 pasos con un LLM puede pesar más que una de 6 en CPU. Están completas en el JSON.
