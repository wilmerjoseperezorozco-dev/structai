# Registro de costos de datos (P0)

Generado por `registro_costos.py`. Mide lo que existe hoy; no estima ahorros.

## Almacenamiento local (sin `node_modules` ni `.git`)

| Carpeta | Tamaño | Archivos |
|---|---:|---:|
| `scripts/precios (total)` | 581.3 MB | 69 |
| `scripts/precios/_cache` | 580.8 MB | 39 |
| `scripts/satelite (total)` | 340.3 MB | 6,114 |
| `scripts/satelite/_cache` | 307.5 MB | 6,028 |
| `scripts/ingesta (total)` | 97.4 MB | 471 |
| `scripts/secop (total)` | 96.1 MB | 16 |
| `scripts/secop/_cache` | 96.1 MB | 8 |
| `packages` | 54.6 MB | 446 |
| `scripts/ingesta/nsr10` | 32.2 MB | 269 |
| `scripts/ingesta/sgsst_raw` | 21.4 MB | 26 |
| `scripts/evaluacion (total)` | 20.8 MB | 86 |
| `scripts/ingesta/microzonificacion_cali` | 14.9 MB | 22 |
| `scripts/evaluacion/qlora_export` | 10.0 MB | 8 |
| `scripts/ingesta/microzonificacion_medellin` | 8.9 MB | 1 |
| `scripts/ingesta/microzonificacion_pereira` | 8.4 MB | 19 |
| `scripts/hidro (total)` | 6.6 MB | 13 |
| `scripts/hidro/_cache` | 6.4 MB | 2 |
| `scripts/macro (total)` | 3.8 MB | 1,303 |
| `scripts/macro/_cache` | 3.2 MB | 1,293 |
| `scripts/ingesta/ccp14` | 2.9 MB | 17 |
| `scripts/ingesta/microzonificacion_bogota` | 2.2 MB | 2 |
| `apps` | 2.1 MB | 141 |

## Almacenamiento en producción (Supabase, tablas principales)

| Tabla | Filas (estimadas) | Total | Datos | Índices |
|---|---:|---:|---:|---:|
| `invias_actividad_insumos` | 577,709 | 115 MB | 92 MB | 24 MB |
| `ideam_caudal_historico` | 351,578 | 63 MB | 26 MB | 38 MB |
| `nsr10_chunks` | 9,914 | 52 MB | 12 MB | 29 MB |
| `igac_suelos_ufh` | 169,088 | 39 MB | 35 MB | 4952 kB |
| `apu_precios_nacional_detalle` | 114,616 | 39 MB | 28 MB | 11 MB |
| `motor_chunks` | 4,060 | 22 MB | 5600 kB | 10120 kB |
| `invias_insumos_precios` | 84,305 | 21 MB | 8176 kB | 13 MB |
| `invias_actividad_costos` | 69,958 | 19 MB | 8136 kB | 11 MB |
| `noticias_relevantes` | 9,498 | 18 MB | 9464 kB | 9320 kB |
| `apu_insumos_referencia` | 10,281 | 12 MB | 5720 kB | 7016 kB |
| `ungrd_emergencias` | 41,893 | 10 MB | 8056 kB | 2144 kB |
| `apu_precios_referencia` | 4,521 | 4680 kB | 1832 kB | 2808 kB |
| `ecuador_nec_se_ds_chunks` | 395 | 1832 kB | 360 kB | 856 kB |
| `ntc_chunks` | 294 | 1624 kB | 504 kB | 816 kB |

Suma de estas tablas: 441.3 MB.

## Tiempo de procesamiento registrado

- Descarga diaria de CHIRPS para Colombia: 1,890 de 2,192 días en 3.0 h (5.7 s por día).
