# Prerregistro HE5 (#274): diafragma rígido frente a semirrígido en cortantes de columna

Fijado el 2026-11-19, **antes** de comparar cortantes. Código: `he5_diafragma.py`.

## Pregunta

En pórticos de concreto con losas típicas y relación de aspecto en planta < 3, ¿suponer el diafragma rígido (A.3.6.7.2) cambia los cortantes de columna menos de un 5 % frente al modelo semirrígido?

## Por qué importa

Si la respuesta es sí, el motor puede usar el diafragma rígido por defecto en ese rango y advertir fuera de él. Si no, la F3 tiene que ofrecer el semirrígido como modelo normal.

## Modelo semirrígido (F3)

- **Elemento:** la losa se modela con membranas QM6, cuadriláteros de 4 nodos con modos incompatibles, uno por vano, conectadas a los nodos del pórtico.
- **Validación del elemento** (`tests/test_membrana.py`):
  - no absorbe energía en movimientos de cuerpo rígido;
  - pasa la prueba de parche;
  - da exacta la flexión pura con un solo elemento en el canto;
  - un voladizo con carga de cortante queda dentro del 3 % de Timoshenko;
  - con una losa muy rígida reproduce el diafragma rígido.

## Edificios (malla paramétrica)

**Malla:** 189 edificios.
- Planta: 3 vanos en X y NY ∈ {3, …, 9} en Y, con luz L igual en ambas direcciones (aspecto 1 a 3).
- Luces: L ∈ {4, 6, 8} m.
- Pisos: N ∈ {3, 6, 10}, de 3 m.
- Espesor de losa en su plano: t ∈ {0,05 (torta de una losa aligerada); 0,10; 0,15} m.

**Elementos y materiales:**
- Columnas y vigas con el prediseño de HE6 (carga axial y L/12), sin iterar la deriva.
- Inercias fisuradas: columnas 0,70·Ig y vigas 0,35·Ig.
- Membrana con E_losa = **0,5·Ec** (principal) y ν = 0,2.
- **Sensibilidad:** E_losa = 0,25·Ec y 1,0·Ec.

**Cargas:**
- Fuerza horizontal equivalente con la distribución A.4.3 (T = Cu·Ta, Aa = 0,25, perfil D). La magnitud no importa porque el análisis es lineal.
- **Rígido:** la fuerza de cada piso va en el centro de masa, sin torsión accidental.
- **Semirrígido:** la misma fuerza, repartida en los nodos por área tributaria (masa uniforme).
- Dirección X y dirección Y por separado.

## Medida y criterio

**Error de un edificio:** el máximo entre pisos y direcciones de máx_col |V_semi − V_rígido| / máx_col |V_rígido|, dentro de cada piso. Se normaliza por el mayor cortante de columna del piso, para que las columnas que casi no reciben cortante no inflen el error.

**Población principal:** aspecto < 3 (NY = 3…8, 162 edificios). Los edificios de aspecto = 3 se reportan aparte.

**Proporción:** edificios con error ≥ 5 %, con IC95 de Wilson. El veredicto sale del E_losa principal.

| Veredicto | Condición |
|---|---|
| **CONFIRMADA** | límite superior < 0,10 |
| **REFUTADA** | límite inferior > 0,10 |
| **NO CONCLUYENTE** | en otro caso |

**Descriptivo:** resultados por espesor, aspecto y número de pisos.

## Limitaciones declaradas

- **Solo pórticos.** No hay muros ni núcleos. Con muros, el diafragma trabaja más y la diferencia sería mayor, así que el resultado **no** se extiende a sistemas con muros.
- **Planta.** Es rectangular y regular, sin aberturas ni retrocesos.
- **Malla de la losa.** Hay una membrana por vano, sin refinar. Se justifica porque QM6 representa la flexión pura de forma exacta, pero no hay estudio de convergencia en esta malla.
- **Rigidez de la losa.** E_losa = 0,5·Ec es una suposición de fisuración en el plano. Por eso se reporta la sensibilidad.
