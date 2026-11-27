# motor-pilotes: utilidad y aplicabilidad en Colombia (#118)

Estado al 2026-11-18. Cruza los métodos del motor con los datos colombianos que ya tiene StructAI. No contiene texto de las normas, solo números y referencias.

## 1. Métodos y su respaldo

| Camino | Norma | Validación | Estado |
|---|---|---|---|
| Arcilla: fricción α·Su y punta 9·Su | NSR-10 H.4.7-3 (punta: Skempton) | CYCU λ = 1,48 [1,24; 1,78], n = 71. El Dorado λ = 1,39, n = 5 | Conservador, con COV 0,58 |
| Arena, hincado: Meyerhof SPT | CCP-14 10.7.3.8.6g | CYCU λ = 0,97 [0,76; 1,22], n = 65 | Calibrado en promedio, COV 0,66 |
| Arena o grava, excavado: β y 0,057·N60 | CCP-14 10.8.3.5.2 | CYCU λ = 0,90 [0,68; 1,18], n = 16 (7 sitios) | No concluyente |
| Arena: Nordlund/Thurman | CCP-14 10.7.3.8.6f | — | Próximamente (hay que digitalizar las figuras f-1 a f-9) |
| Geomaterial intermedio (N60 > 50) y roca | CCP-14 10.8.3.5.4 y NSR-10 H.4.7-4 | — | Próximamente |
| Perfil mixto arcilla + arena en un mismo pilote | Cada estrato con su método | Equivalencia exacta con los caminos puros y cálculo a mano | Implementado (`mixto.py`, también en el contrato) |

## 2. Qué datos colombianos tiene StructAI y para qué sirven

| Dato (Supabase o repo) | Contenido | Utilidad para pilotes |
|---|---|---|
| `microzonificacion_sismica_local` (36 zonas) | Bogotá, Cali y Pereira: descripción geológica y Fa/Fv por zona | **Tamizaje del método.** La zona dice si el perfil probable es arcilla blanda, aluvial con arenas o gravas de piedemonte. No reemplaza la exploración. |
| `sgc_amenaza_sismica_municipios` (1.121 municipios) | Aa, Av, Ae, Ad y zona de amenaza | Entra en la combinación sísmica. En sismo el FS de punta es 1,5 y el de fricción 1,10, y **la NSR-10 no permite usar Su en análisis seudo-estático**: el motor lo rechaza explícitamente. |
| `igac_suelos_ufh` (~169 mil polígonos) | Textura y drenaje agronómicos del primer metro y medio | **No sirve para diseñar pilotes.** Sirve para contexto, por ejemplo que hay ~22 Mha "franco arenosa" y ~1,5 Mha "arenosa". |
| APU INVIAS (`motor-apu`) | Ítems de pilote vaciado in situ, prefabricados (Ø 0,40, 0,50 y 1,0 m), PDA, prueba estática ASTM D1143 y crosshole | Une capacidad con costo: kN de capacidad por peso, y cuánto cuesta una prueba de carga frente al sobrecosto de diseñar conservador. |
| `motor-licuacion` (`spt.py`) | CSR, CRR, MSF y corrección por finos | Las arenas aluviales de Bogotá y Cali están marcadas como susceptibles a licuación. Ver 4.3. |
| **No hay** | Sondeos, SPT ni pruebas de carga colombianas abiertas | El único caso colombiano validado es El Dorado (arcilla). Los demás que se encontraron exigen carta o licencia. |

## 3. Aplicabilidad por tipo de suelo colombiano (según la microzonificación)

- **Bogotá lacustre (arcillas limosas blandas de 50 a 500 m):**
  - Es el camino α del motor, validado conservador, y El Dorado es de esta zona.
  - **Riesgos que el motor aún no cubre:**
    - fricción negativa por consolidación regional y por subsidencia;
    - asentamiento del grupo, porque en estas arcillas suele gobernar el servicio y no la capacidad.
- **Bogotá aluvial, con lentes de arena limpia y susceptible a licuación:**
  - Es el camino SPT del CCP-14, ya implementado.
  - Antes de usarlo en diseño hace falta:
    - la validación prerregistrada;
    - descontar el fuste en las capas que licúan.
- **Bogotá piedemonte y Cali piedemonte (bloques, cantos y gravas en matriz):**
  - El SPT es poco confiable con bloques: da rechazo o N inflado.
  - El β de grava existe, pero con N > 50 el material pasa a geomaterial intermedio, que está próximamente.
  - Hace falta exploración con otros ensayos.
- **Cali, llanura del Cauca y abanicos (depósitos aluviales de 100 a 1.700 m):**
  - El perfil alterna arcilla y arena, y **todavía no se puede calcular en un solo pilote** (ver 4.2).
- **Costa Caribe** (Cartagena, Barranquilla): no está en la microzonificación cargada. Se suelen encontrar arenas con limos y arcillas marinas, así que también requieren el perfil mixto.

## 4. Brechas y próximos pasos

### 4.1 Normativas

- **La NSR-10 (H.4) no da fórmula de punta.** El motor usa:
  - 9·Su en arcilla;
  - el CCP-14 en arena.
- **El CCP-14 rige puentes (INVIAS).** Para edificaciones, el motor lo usa como referencia técnica y lo declara en los supuestos.
- **Hay dos erratas en el CCP-14 que el motor corrige y documenta:**
  - 10.7.3.8.6g: el texto en SI repite "ocho veces N1_60 ksf". El valor correcto es 0,4·N1_60 MPa.
  - 10.8.3.5.2c-1: está impresa "Para 0,057N60 ≤ 50, qp = 1,2N60". Lo correcto es qp = 0,057·N60 MPa para N60 ≤ 50, con tope de 3 MPa.
  - Vale la pena reportarlas al INVIAS. Si un diseñador copia la versión impresa, puede sobreestimar la punta varias veces.

### 4.2 Perfil mixto (implementado el 2026-11-18)

`mixto.capacidad_mixta` evalúa cada estrato con su método y su factor de seguridad:
- arcilla con α·Su;
- suelo drenado con K;
- suelo granular con SPT.

La punta sale del estrato de apoyo. En Meyerhof, Db cuenta solo la penetración dentro del estrato granular. El grupo y el contrato ya usan esta función.

**Pendiente:** validación con datos de perfil estratificado. La CYCU trae un solo estrato por prueba, así que no sirve para esto.

**Precaución vigente:** en arena, con los FS de la NSR-10, el 14 % de las pruebas CYCU quedó con la capacidad medida por debajo de la admisible. El contrato lo advierte.

### 4.3 Licuación

Con el motor de licuación se pueden marcar las capas con FS_liq < 1. Para esas capas:
- su fuste no cuenta en sismo;
- se agrega como carga de fricción negativa (*downdrag*).

### 4.4 SPT en Colombia

- La corrección a N60 exige la relación de energía del equipo. **No se asume:** se pide en la entrada.
- `motor-licuacion/spt.py` tampoco tiene la corrección por energía.

### 4.5 Datos colombianos de validación

El objetivo es conseguir pruebas de carga con sondeo de Bogotá, Cali y la Costa, con permiso de uso. Los ítems de prueba de carga que tiene el APU INVIAS muestran que estas pruebas existen en obra pública.
