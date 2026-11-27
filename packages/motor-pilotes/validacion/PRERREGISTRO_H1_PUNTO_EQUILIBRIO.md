# Prerregistro H1 (#273): punto de equilibrio entre el diseño conservador de pilotes y una prueba de carga

Fijado el 2026-11-18, **antes** de calcular ahorros. Código: `h1_punto_equilibrio.py`.

## Pregunta

Cuando se diseñan pilotes sin prueba de carga, ¿cuánto cuesta ese conservadurismo frente a hacer la prueba? ¿Llega al 18-30 % del costo de los pilotes, como se afirma (cifra de Wilmer, sin fuente todavía)? ¿Desde cuántos pilotes se paga la prueba?

## Base normativa

- **NSR-10 H.4.7.3:** la capacidad última de cimentaciones profundas se puede calcular a partir de pruebas de carga "en número suficiente" (tabla H.4.7-2). En ese caso los factores de seguridad pueden reducirse, sin bajar del **80 %** de la tabla.
- **La tabla H.4.7-2 (número de pruebas) no está en el corpus de StructAI.** Por eso el número de pruebas es un escenario (1, 2 o 3), no una exigencia transcrita. Queda pendiente verificarlo en la edición oficial.
- La PDA (ensayo dinámico) no se toma como "prueba de carga" de H.4.7.3 en el análisis principal, porque la norma no lo dice explícitamente.

## Modelo (fijo)

- **Sin prueba:** L0 es la longitud mínima con Q_adm(L) ≥ Q. Q_adm sale del motor de pilotes de StructAI con los FS de la NSR-10 (combinación CM + CV normal).
- **Con prueba:** con λ = capacidad medida / capacidad predicha por el motor, la capacidad admisible es λ·Q_adm(L)/0,8. L1(λ) es la longitud mínima que la cumple.
  - λ sale de la base CYCU (Chen et al. 2025, CC BY 4.0), la misma de la validación del motor:
    - arcilla: 71 pruebas, 36 sitios;
    - arena: 81 pruebas, 34 sitios;
    - perfil mixto: las dos.
  - Se toma un λ por proyecto: se supone que la prueba representa al sitio.
  - Si L1 supera los 40 m, se acota en 40 m y se cuenta como "no factible" (habría que rediseñar).
- **Costo:** N·L·precio por metro + n_pruebas·precio de la prueba.
  - Precios: INVIAS 2026-1, costo directo sin AIU, mediana de 140 provincias (`precios_invias_2026_1.json`).
  - Pilote in situ Ø0,5 m: 812.627 $/m. Pilote in situ Ø1,0 m: 2.386.993 $/m. Pilote prefabricado Ø0,5 m: 397.763 $/m.
  - Prueba estática: 8.850.420 $ (in situ) y 9.092.897 $ (prefabricado). Es un valor nacional único, que no depende de la carga y parece bajo para el mercado; por eso se hace sensibilidad ×3 y ×10.
- **Ahorro:** (C0 − E[C1]) / C0. Se mide sobre el costo de los pilotes; sobre el costo total de la cimentación (cabezales, vigas) sería menor.
- **Perfiles** (nivel freático a 1 m):
  - **arcilla blanda:** Su = 20 + 2z kPa;
  - **arena:** N60 = 8 + z (máximo 50);
  - **mixto:** 8 m de arcilla y luego arena con N60 = 15 + (z − 8).
- **Pilotes y cargas admisibles por pilote:**
  - in situ Ø0,5 y prefabricado Ø0,5: 300, 600 y 1.000 kN;
  - in situ Ø1,0: 1.500 y 3.000 kN.
  - En arena solo se usan los de Ø0,5.
- **Conteo previo** (`--conteo`, solo L0 y número de λ, sin ahorros):
  - L0 va de 7 a 35,5 m;
  - arcilla blanda, Ø1,0 m con 3.000 kN no es factible en 40 m y se excluye.
  - En arena, el pilote in situ sale más corto que el hincado. Es consecuencia de los métodos del CCP-14 en el motor (β y 0,057·N60 frente a Meyerhof) y no se ajusta.

## Confirmatorio

- **Escenario principal:** N = 30 pilotes, 1 prueba estática, precio INVIAS ×1 y precios p50.
- Para cada perfil se calcula el ahorro esperado (promedio de los escenarios de pilote y carga), con IC95 % por bootstrap de sitios CYCU (2.000 réplicas, semilla 1181).
- **Veredicto** sobre la afirmación "18-30 %":

  | Si el IC95… | Veredicto |
  |---|---|
  | queda en 0,18 o más | **CONFIRMADO** |
  | queda por debajo de 0,18 | **REFUTADO** |
  | en otro caso | **NO CONCLUYENTE** |

## Secundario y descriptivo

- **Solo la reducción del FS (λ = 1):** ahorro y punto de equilibrio en número de pilotes. Por construcción, este ahorro **no puede pasar del 20 %** de la longitud. Si la capacidad crece más rápido que la longitud, como en arcilla con Su creciente o en arena, es menor.
- **Punto de equilibrio empírico:** N*, el número de pilotes desde el cual la prueba se paga.
- **P(la prueba alarga):** fracción de sitios con L1 > L0. La prueba revela capacidad menor y el diseño sin prueba quedaba corto.
- **P(λ < 0,8):** el diseño sin prueba tendría un margen real menor que el mínimo que la norma acepta incluso con prueba.
- **Sensibilidad:** N = 10/30/100, pruebas 1/2/3, precio de la prueba ×1/×3/×10 y precio del pilote p10/p90.

## Lectura fijada de antemano

- **Ahorro grande en arcilla:** como el motor es conservador en arcilla (λ ≈ 1,45 en la validación), es esperable que la prueba revele capacidad de más. Eso no es "factor de seguridad inflado" por el constructor: es el sesgo del método α + 9·Su de la NSR-10.
- **Ahorro pequeño o negativo en arena:** aquí λ ≈ 1 con COV 0,63. La prueba no ahorra en promedio, pero detecta los sitios donde el diseño quedaba corto. Su valor es de **seguridad**, no de costo.
- **Qué no mide:**
  - el sobrecosto que mete un constructor en la licitación por falta de estudio (contingencias, imprevistos). Eso requiere ofertas comparables de SECOP, que no tienen ítems desagregados de prueba de carga: solo 5 contratos de SECOP II mencionan "prueba de carga pilote".
  - Por eso H1 mide el **componente normativo** del sobrecosto, no el total.

## Limitaciones declaradas

- La base CYCU es de Taiwán (suelos y prácticas distintos).
- Un λ por sitio ignora la variabilidad dentro del sitio.
- Los precios del INVIAS son referenciales para vías.
- El precio de la prueba no escala con la carga.
- Los perfiles son idealizados.
- No se incluye el costo del tiempo de la prueba ni el de un pilote de reacción adicional.
- La tabla H.4.7-2 no se verificó.
