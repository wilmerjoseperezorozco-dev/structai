# SECOP II y regalías: limpieza, calidad y qué sirve a StructAI

Generado por `scripts/ingesta/secop_sgr/perfil_secop_sgr.py` sobre la descarga acotada (≤ 1 GB, sin datos personales). Solo agregados: **ninguna entidad ni proveedor se nombra**. Una señal de riesgo es una característica estadística del proceso, **no evidencia de irregularidad**.

## 1. SECOP II, contratos de obra

Filas descargadas: **50,328**. Después de limpieza (sin duplicados, valor válido entre 0 y 5 billones, fechas coherentes): **49,023** (97%).

| Problema de calidad | Contratos | % |
|---|---|---|
| id de contrato duplicado | 0 | 0.0% |
| valor nulo, ≤ 0 o > 5 billones | 142 | 0.3% |
| sin fecha de firma o fin antes del inicio | 1,172 | 2.3% |
| ciudad 'No definido' | 8,510 | 16.9% |
| valor pagado mayor que el del contrato | 12 | 0.0% |

Valores > 5 billones: 1 (el mayor: 6.45e+15 COP), seguramente errores de digitación; son los que inflaban la suma de 2024.

| Año de firma | Contratos | Valor total (billones) | Mediana por contrato (millones) |
|---|---|---|---|
| 2016 | 7 | 0.02 | 71 |
| 2017 | 235 | 0.44 | 193 |
| 2018 | 1,280 | 3.82 | 176 |
| 2019 | 2,291 | 5.29 | 207 |
| 2020 | 2,751 | 11.68 | 407 |
| 2021 | 5,385 | 20.49 | 240 |
| 2022 | 5,954 | 16.80 | 285 |
| 2023 | 7,947 | 21.93 | 194 |
| 2024 | 6,483 | 13.16 | 177 |
| 2025 | 9,691 | 22.88 | 198 |
| 2026 | 6,999 | 25.52 | 245 |

Tipo de obra (por palabras clave en el objeto; línea base):

| Tipo | Contratos | Valor (billones) |
|---|---|---|
| otro / sin clasificar | 17,568 | 38.62 |
| pavimentación urbana / vías | 13,744 | 71.46 |
| edificación institucional / otra | 3,889 | 4.00 |
| edificación educativa | 3,238 | 4.28 |
| deportivo / espacio público | 3,190 | 8.43 |
| acueducto / alcantarillado / saneamiento | 2,468 | 5.09 |
| vía terciaria / placa huella | 2,297 | 1.75 |
| vivienda | 1,061 | 2.80 |
| salud | 989 | 3.83 |
| puente | 579 | 1.77 |

### Qué se puede aprovechar

- **Cantidad en el objeto** (km, m², ml, m³): **367** contratos (0.7%). Con valor ÷ cantidad sale un **costo paramétrico** por tipo de obra, región y año, útil para estimar y para revisar presupuestos (#196).
- **BPIN mencionado en el texto**: **361** contratos, que se pueden enlazar con regalías (sección 3).
- **Fuente de recursos**: 1,816 contratos con aporte del SGR.

Ejemplo de costo paramétrico (vías con cantidad en km, filtrado a 50 M–20.000 M COP/km, años mezclados, sin indexar):

| Tipo | Contratos | P25 (M/km) | Mediana (M/km) | P75 (M/km) |
|---|---|---|---|---|
| pavimentación urbana / vías | 14 | 154 | 259 | 986 |
| vía terciaria / placa huella | 10 | 974 | 1,213 | 2,649 |

## 2. SECOP II, procesos de obra: competencia y descuento

Procesos descargados: **151,359**; adjudicados con presupuesto oficial y valor adjudicado válidos: **34,406**.

| Modalidad | Procesos | Mediana de descuento frente al presupuesto oficial | Un solo oferente |
|---|---|---|---|
| Contratación Directa (con ofertas) | 1,535 | 0.0% | 91% |
| Contratación régimen especial (con ofertas) | 2,071 | 0.0% | 47% |
| Licitación pública | 252 | 1.0% | 26% |
| Licitación pública Obra Publica | 7,063 | 2.8% | 18% |
| Mínima cuantía | 9,814 | 9.1% | 28% |
| Seleccion Abreviada Menor Cuantia Sin Manifestacion Interes | 262 | 0.4% | 40% |
| Selección Abreviada de Menor Cuantía | 13,409 | 0.8% | 35% |

| Tipo de obra | Procesos | Mediana de descuento | Un solo oferente | Mediana de ofertas |
|---|---|---|---|---|
| acueducto / alcantarillado / saneamiento | 1,860 | 0.2% | 49% | 1 |
| deportivo / espacio público | 2,401 | 0.9% | 35% | 2 |
| edificación educativa | 2,355 | 1.2% | 32% | 3 |
| edificación institucional / otra | 3,484 | 2.3% | 22% | 4 |
| otro / sin clasificar | 13,272 | 1.3% | 33% | 3 |
| pavimentación urbana / vías | 8,197 | 2.8% | 28% | 4 |
| puente | 384 | 1.3% | 34% | 2 |
| salud | 712 | 0.1% | 54% | 1 |
| vivienda | 830 | 0.0% | 44% | 2 |
| vía terciaria / placa huella | 911 | 0.1% | 45% | 2 |

**Hipótesis de competencia:** a más ofertas, mayor descuento frente al presupuesto oficial. Spearman ρ(ofertas, descuento) = **0.46** (n = 34,406).

Enlace contrato ↔ proceso (`proceso_de_compra` = `id_del_portafolio`): **34,704** contratos con su presupuesto oficial y su número de ofertas.

Contratos con días adicionados: 25.1% con un solo oferente frente a 28.8% con dos o más. Es una asociación, no una causa.

## 3. Regalías (SGR)

Proyectos: **35,010**; BPIN duplicados: 1,754.

| Sector | Proyectos | Valor (billones) | Mediana ejecución física | Mediana ejecución financiera | Financiera > física + 20 pp |
|---|---|---|---|---|---|
| AGRICULTURA Y DESARROLLO RURAL | 2,294 | 8.08 | 100 % | 100 % | 3% |
| AMBIENTE Y DESARROLLO SOSTENIBLE | 2,777 | 6.32 | 100 % | 100 % | 5% |
| CIENCIA, TECNOLOGÍA E INNOVACIÓN | 1,569 | 10.02 | 97 % | 94 % | 2% |
| COMERCIO, INDUSTRIA Y TURISMO | 349 | 2.26 | 100 % | 99 % | 4% |
| CULTURA | 539 | 1.54 | 100 % | 100 % | 3% |
| DEPORTE Y RECREACIÓN | 3,406 | 6.74 | 100 % | 100 % | 3% |
| EDUCACIÓN | 3,746 | 20.80 | 100 % | 99 % | 3% |
| GOBIERNO TERRITORIAL | 636 | 1.48 | 100 % | 100 % | 5% |
| INCLUSIÓN SOCIAL Y RECONCILIACIÓN | 977 | 2.44 | 100 % | 100 % | 2% |
| MINAS Y ENERGÍA | 1,342 | 6.54 | 100 % | 100 % | 3% |
| SALUD Y PROTECCIÓN SOCIAL | 892 | 4.23 | 100 % | 100 % | 1% |
| TRANSPORTE | 10,995 | 80.05 | 100 % | 100 % | 3% |
| VIVIENDA, CIUDAD Y TERRITORIO | 4,853 | 16.59 | 100 % | 100 % | 3% |

Contratos de SECOP II cuyo texto cita un BPIN que existe en el listado del SGR: **121**.

Proyectos de inversión del DNP (infraestructura): **112,458**; por sector: Transporte 65,090, Educación 47,368.

## 4. Tamaño

Descarga en `raw/`: **283 MB** (tope 1.024 MB).

