# Plantilla: 60 preguntas held-out para validar K6 (issue #171)

Para escribir **a mano** (o en el CSV `PLANTILLA_HELDOUT_K6.csv`, que abre en Excel). La versión para imprimir es `PLANTILLA_HELDOUT_K6.html`: ábrela en el navegador y usa Imprimir.

## Antes de empezar

- **No mires** `scripts/evaluacion/golden/e1_enrutador/dataset_e1.jsonl` ni los informes E1. La gracia es que las preguntas sean tuyas.
- Escribe como preguntaría de verdad un ingeniero, un maestro de obra, un estudiante o un funcionario. Mezcla formal y coloquial, con y sin tildes, con y sin siglas.
- Etiqueta cada pregunta con `docs/evaluacion/GUIA_ETIQUETADO_DOMINIO.md`:
  - **etiqueta**: el dominio que da la mejor respuesta;
  - **aceptables**: otros dominios que también servirían (opcional);
  - **tipo**: marca `N` si la pregunta tiene una **negación** ("no quiero el precio, sino…") y `C` si es **compuesta** (dos temas a la vez).
- Si no sabes qué etiqueta poner, déjala en blanco. Es mejor que adivinar.

## Reparto (60)

| Bloque | Cuántas | Etiqueta típica |
|---|---|---|
| Sísmica de un lugar (Aa, Av, zona, microzonificación) y geotecnia (suelos, capacidad portante, licuación) | 12 | `geopot` |
| Laboratorio: concreto, agregados, cemento, suelos (slump, cilindros, granulometría, Proctor, CBR…) | 6 | `geopot` |
| Vivienda existente de 1-2 pisos (¿resiste?, grietas, reforzamiento) | 6 | `vulnerabilidad_vivienda` |
| Agua: acueducto, alcantarillado, aguas lluvias, Res. 0330 | 6 | `aquai` |
| Vías, pavimentos, puentes, túneles | 6 | `vias` |
| Gerencia: valor ganado, cronograma, contratación pública, interventoría | 6 | `gerencia` |
| Precios, costos y APU | 6 | `apu_precios` |
| NSR-10 de diseño estructural, NTC, seguridad en obra, saludos o fuera de tema | 9 | `normativa_general` |
| Perú o Ecuador | 3 | `peru_e030` / `ecuador_nec_se_ds` |

Dentro de esas 60, incluye **al menos 5 negaciones (`N`) y 5 compuestas (`C`)**, repartidas en distintos bloques.

## Formato de cada renglón

| # | Pregunta | Etiqueta | Aceptables | Tipo |
|---|---|---|---|---|
| 1 | *(tu pregunta, tal cual la harías)* | | | |
| … | | | | |
| 60 | | | | |

## Qué pasa después

1. Me pasas la hoja (foto, PDF o el CSV).
2. La transcribo a `dataset_heldout_k6.jsonl` **sin cambiar palabras ni etiquetas**. Lo ilegible lo marco como `[ilegible]` y te pregunto; no lo adivino.
3. Revisas la transcripción.
4. Corro K6 frente a producción con el criterio fijado en #171, que ya no se puede cambiar.
