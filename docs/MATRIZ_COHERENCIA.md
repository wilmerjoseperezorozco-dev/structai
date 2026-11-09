# Matriz de coherencia entre motores y datos

Generado por `scripts/inventario/matriz_coherencia.py` desde [coherencia_motores.json](coherencia_motores.json); no editar a mano. Dos nodos se conectan cuando una magnitud que produce uno (con su unidad) es una que consume el otro. **Coherente no significa probado**: solo las cadenas de la sección «Cadenas probadas» tienen una prueba que las ejecuta.

- Motores implementados: 16; con declaración completa: 8; **pendientes de declarar: 8** (`motor-aquai`, `motor-vias`, `motor-gerencia`, `motor-vulnerabilidad-vivienda`, `motor-estructural`, `motor-deformacion`, `motor-acero-frio`, `motor-topovia`). Lo no declarado no genera conexiones: no se infiere nada.
- Motores futuros (planificados o bloqueados): 4. Nunca se cuentan como funcionando.
- Magnitudes del vocabulario: 43, cada una con unidad y dominio físico.

## Cuántas conexiones y cadenas cierran

Camino simple = sin repetir nodo. «Solo implementados» no incluye ningún motor futuro; «con futuros» son los adicionales que aparecerían al construirlos.

| Nodos en la cadena | Solo implementados | Adicionales con motores futuros |
|---|---|---|
| 2 (pares) | 8 | 9 |
| 3 (cadenas) | 7 | 11 |
| 4 (cadenas) | 3 | 10 |

Probadas de extremo a extremo: **1**.

## Cadenas probadas

- `orquestador -> motor-analisis -> motor-concreto` — prueba: `packages/dag-proyecto/tests/test_motores_reales.py::def test_la_cadena_produce_los_tres_artefactos_con_linaje`

## Conexiones entre nodos implementados

Vía: **endpoint** = ambos lados son campos del contrato HTTP; **adaptador** = exige una transformación escrita aparte (combinar cargas, armar la malla); **paquete** = solo desde Python.

| Origen | Destino | Magnitudes | Vía |
|---|---|---|---|
| `motor-analisis` | `motor-concreto` | reaccion_vertical_kn | adaptador |
| `orquestador` | `motor-analisis` | seccion_columna_mm, seccion_viga_mm | adaptador |
| `orquestador` | `motor-concreto` | seccion_columna_mm | endpoint |
| `orquestador` | `motor-apu` | seccion_columna_mm, seccion_viga_mm | paquete |
| `motor-concreto` | `motor-geotecnia` | presion_contacto_kpa | adaptador |
| `motor-geotecnia` | `motor-concreto` | q_adm_kpa | endpoint |
| `motor-geopot` | `orquestador` | coef_aceleracion_aa, coef_velocidad_av | paquete |
| `dato-factores-emision` | `motor-concreto` | factor_emision_kgco2e_kg | paquete |

## Conexiones que abrirían los motores futuros

| Origen | Destino | Magnitudes |
|---|---|---|
| `motor-analisis` | `futuro-columna-circular` | momento_flector_knm, reaccion_vertical_kn |
| `motor-analisis` | `futuro-pilotes` | reaccion_vertical_kn |
| `orquestador` | `futuro-optimizador-portico` | costo_directo_cop, deriva_relativa |
| `motor-concreto` | `futuro-optimizador-portico` | co2e_kg, costo_directo_cop, masa_acero_kg, razon_demanda_capacidad, volumen_concreto_m3 |
| `motor-geotecnia` | `futuro-optimizador-portico` | razon_demanda_capacidad |
| `motor-apu` | `futuro-optimizador-portico` | costo_directo_cop |
| `futuro-columna-circular` | `futuro-optimizador-portico` | masa_acero_kg, razon_demanda_capacidad, volumen_concreto_m3 |
| `futuro-losas` | `futuro-optimizador-portico` | masa_acero_kg, razon_demanda_capacidad, volumen_concreto_m3 |
| `futuro-pilotes` | `futuro-optimizador-portico` | razon_demanda_capacidad |

## Huecos

**Magnitudes que algún nodo consume y ninguno produce** (las aporta el usuario o un estudio externo): `aceleracion_pico_g`, `angulo_friccion_deg`, `asentamiento_admisible_mm`, `carga_muerta_kn_m`, `carga_viva_kn_m`, `cohesion_kpa`, `estratos_arcilla`, `geometria_portico`, `grupo_uso`, `magnitud_momento_mw`, `modulo_balasto_kn_m3`, `municipio_codigo_dane`, `nivel_freatico_m`, `perfil_spt`, `perfil_suelo_clase`, `peso_unitario_kn_m3`, `red_hidraulica`.

**Magnitudes que algún nodo produce y ninguno consume** (hoy salen de la cadena sin uso): `asentamiento_mm`, `capacidad_pilote_kn`, `caudal_m3s`, `factor_seguridad_talud`, `frontera_pareto`, `fs_licuacion_minimo`, `golpe_ariete_pico_m`, `lpi`, `presion_m`, `q_ult_kpa`, `velocidad_ms`.

## Nodos

| Nodo | Tipo | Estado | Declaración | Entradas | Salidas | En cadena probada |
|---|---|---|---|---|---|---|
| `dato-factores-emision` | dato | implementado | completa | 0 | 1 | no |
| `motor-acero-frio` | motor | implementado | **?** pendiente | 0 | 0 | no |
| `motor-analisis` | motor | implementado | completa | 5 | 2 | sí |
| `motor-apu` | motor | implementado | completa | 2 | 1 | no |
| `motor-aquai` | motor | implementado | **?** pendiente | 0 | 0 | no |
| `motor-concreto` | motor | implementado | completa | 10 | 7 | sí |
| `motor-deformacion` | motor | implementado | **?** pendiente | 0 | 0 | no |
| `motor-estructural` | motor | implementado | **?** pendiente | 0 | 0 | no |
| `motor-geopot` | motor | implementado | completa | 1 | 2 | no |
| `motor-geotecnia` | motor | implementado | completa | 6 | 4 | no |
| `motor-gerencia` | motor | implementado | **?** pendiente | 0 | 0 | no |
| `motor-licuacion` | motor | implementado | completa | 4 | 2 | no |
| `motor-redes` | motor | implementado | completa | 1 | 4 | no |
| `motor-topovia` | motor | implementado | **?** pendiente | 0 | 0 | no |
| `motor-vias` | motor | implementado | **?** pendiente | 0 | 0 | no |
| `motor-vulnerabilidad-vivienda` | motor | implementado | **?** pendiente | 0 | 0 | no |
| `orquestador` | motor | implementado | completa | 7 | 4 | sí |
| `futuro-columna-circular` | motor | planificado | completa | 2 | 3 | no |
| `futuro-losas` | motor | planificado | completa | 3 | 3 | no |
| `futuro-optimizador-portico` | motor | planificado | completa | 6 | 1 | no |
| `futuro-pilotes` | motor | bloqueado (bloqueado: El corpus no tiene norma específica de pilotes (AASHTO LRFD, FHWA); sin ella el motor tendría que inventar criterios.) | completa | 3 | 2 | no |

## Qué se valida hacia el futuro

- `--verificar` (en CI) falla si el documento está desactualizado, si una evidencia («ruta::texto») ya no existe en el código, si aparece un paquete `motor-*` sin figurar aquí, si un motor con contrato queda «pendiente» o sus endpoints difieren de los del router, o si una cadena probada pierde su prueba.
- `--validar-declaracion` revisa la declaración de un motor o dato nuevo antes de añadirlo: magnitudes del vocabulario, accesos y evidencia vigente.
- `--validar-valores` (y la función `validar_valor`) rechaza datos fuera del dominio físico de su magnitud: negativos donde no cabe, no finitos, por encima del máximo (p. ej. aceleración pico > 2 g, ángulo de fricción > 90°).

## Límites

- La coincidencia de magnitudes es condición necesaria, no suficiente: una conexión puede exigir un adaptador (columna «vía») o supuestos que el contrato de cada motor declara.
- La matriz no mide si una cadena es correcta; eso lo hacen las condiciones 1 y 2 del [registro de motores](REGISTRO_MOTORES.md).
