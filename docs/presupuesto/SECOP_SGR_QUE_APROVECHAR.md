# SECOP II y regalías: qué aprovecha StructAI y qué no

Fecha: 2026-11-12. Cifras: [`SECOP_SGR_PERFIL.md`](SECOP_SGR_PERFIL.md) (regenerable con `scripts/ingesta/secop_sgr/perfil_secop_sgr.py`).

**Descarga:** 283 MB de un tope de 1 GB. Incluye 50.328 contratos de obra de SECOP II, 151.359 procesos de obra, 35.010 proyectos del SGR y 112.458 proyectos de inversión del DNP (transporte y educación).

**Datos personales:** no se descargó ningún dato personal. No están los nombres ni los documentos de representantes legales, ordenadores del gasto o supervisores, ni las cuentas bancarias. Los proveedores que son personas naturales quedaron con un seudónimo HMAC, cuya clave local está en `_privado/` y no se sube al repositorio.

## Sobre la corrupción: qué hacemos y qué no

SECOP sí permite medir **señales de riesgo** que la literatura de contratación abierta usa como banderas: un solo oferente, contratación directa, poca rebaja frente al presupuesto oficial, adiciones de tiempo. StructAI las usa **solo de forma agregada**, por tipo de obra, modalidad, departamento y año, con tres fines:

1. calibrar el **revisor de presupuestos** (#196): cuánto se rebaja normalmente un presupuesto oficial según la competencia;
2. alimentar el **riesgo de proyecto** del motor de gerencia, para predecir adiciones y prórrogas;
3. avisar al usuario, por ejemplo: "en este tipo de obra y modalidad, el 45 % de los procesos tiene un solo oferente".

**No hacemos:** listas de entidades o empresas "sospechosas", ni rankings con nombre, ni conclusiones sobre casos concretos. Una señal estadística no es evidencia de una irregularidad, y señalar a alguien sin pruebas tiene consecuencias legales y éticas. Para casos concretos están los órganos de control (Contraloría, Procuraduría, Fiscalía) y las veedurías ciudadanas.

## Lo que sí sirve (con evidencia de la descarga)

| Hallazgo | Cifra | Para qué le sirve a StructAI |
|---|---|---|
| **A más ofertas, más rebaja frente al presupuesto oficial** | Spearman ρ = 0,46 (n = 34.406 procesos adjudicados) | El "precio de mercado" de una obra no es su presupuesto oficial. El revisor (#196) puede estimar la rebaja esperada según la modalidad y la competencia |
| **Un solo oferente es frecuente en ciertas obras** | acueducto y saneamiento 49 %, salud 54 %, vivienda 44 %, vía terciaria / placa huella 45 %; contratación directa 91 % | Señal agregada de baja competencia por tipo de obra. Contexto para la gerencia y la interventoría, no para acusar a nadie |
| **Rebaja típica por modalidad** | mínima cuantía 9,1 %; licitación de obra pública 2,8 %; selección abreviada 0,8 %; directa 0 % | Rango de referencia para comparar ofertas |
| **Contratos enlazados con su proceso** | 34.704 tienen presupuesto oficial, número de ofertas y días adicionados | **Dataset real para el modelo de riesgo de adiciones** del motor de gerencia (`/gerencia/ml/riesgo`): variables de tipo de obra, modalidad, valor, ofertas, duración y región |
| **Qué se contrata y dónde** | 49.023 contratos limpios, 2017–2026; vías 13.744 (71 billones), educación 3.238, acueducto 2.468, puentes 579 | Priorizar en qué regiones y tipos de obra conseguir precios (#200, #201) |
| **Ejecución de regalías** | 35.010 proyectos con ejecución física y financiera | Línea base de cumplimiento por sector: la mediana es 100 % y solo el 3 % tiene la ejecución financiera más de 20 puntos por encima de la física |

## Lo que no sirve (o casi)

| Idea | Por qué no |
|---|---|
| **Costo por km o por m² desde el objeto del contrato** | Solo el **0,7 %** (367) de los contratos menciona una cantidad en el texto. Con 10 a 14 contratos de vías por tipo, el rango es enorme (259 M/km de mediana en vías urbanas, años mezclados). Para costos paramétricos hacen falta los documentos del proceso (piloto en #203) o los anexos de regalías (#202) |
| **Enlazar SECOP con regalías por BPIN** | Solo 121 contratos citan un BPIN válido en el texto. El enlace confiable exige otra llave (código del proceso en SUIFP-SGR), por explorar |
| **Precios unitarios por ítem** | No están en los datasets abiertos. Viven en los documentos de cada proceso |

## Calidad: qué se limpió

- **Valores imposibles:** 1 contrato de 6,45 × 10¹⁵ COP, el que inflaba 2024; 142 en total con valor nulo, ≤ 0 o mayor de 5 billones.
- **Fechas:** 1.172 contratos (2,3 %) sin firma o con el fin antes del inicio.
- **Ciudad:** el 16,9 % dice "No definido". El análisis por municipio pierde una sexta parte.
- **BPIN duplicados en el SGR:** 1.754.
- **Tipo de obra:** el 35 % queda "sin clasificar" con palabras clave. El clasificador de #196 (entrenado con APU de vivienda) no aplica directo a objetos contractuales; haría falta un clasificador propio.
- **Seudonimización amplia en procesos:** 130.753 de 151.359 filas, porque los NIT no tienen formato uniforme. Protege a las personas, pero limita medir concentración de proveedores en procesos.
- **DNP:** solo coincidieron los sectores Transporte y Educación. Los nombres de los demás sectores no son exactos en el filtro, así que hay que corregirlo si se necesitan.

## Siguientes pasos propuestos

1. **Modelo de riesgo de adiciones** con los 34.704 contratos enlazados: validación temporal (entrenar hasta 2023, probar 2024–2026), métricas calibradas y sin variables de identidad. Va en el issue de gerencia ML.
2. **Rebaja esperada** según modalidad, ofertas y tipo de obra para el revisor (#196).
3. **Piloto de documentos** (#203) solo para los tipos de obra con más contratos (vías, edificación educativa, acueducto), buscando el Formulario 1 en Excel.
