# Prerregistro #333 (H8 y H7): qué explica que las zapatas no quepan

Fijado el 2026-11-26, **antes** de correr. Solo hubo una prueba de humo sobre el edificio 544, que está fuera de la población.

- **Hipótesis:** H7 y H8 son de Wilmer (#333) y van con su formulación operativa. Al lado van mis contrapredicciones.
- **Código:**
  - `scripts/memorias_sinteticas/viento_333.py`;
  - `cimentacion_edificio_3d` de #324-C, sin cambios;
  - `optimizar_edificio_3d.optimizar(..., alturas_viga=...)`, una opción nueva que restringe la rejilla de h. Por defecto no cambia nada. Tiene prueba.
- **Suelo:** q_adm = 200 kPa (estrato medio declarado, el primario de #324-C).

## Transparencia sobre lo ya visto

- `data/memorias_sinteticas/f1_324c/crudo.json` (#324-C) ya contiene, por edificio, cuántas zapatas no caben con 200 kPa.
- Lo publicado fue solo el total (5/11), sin ids y sin cruzarlo con N ni con P.
- Wilmer formuló H8 sin ver los ids.
- La corrida recalcula todo, es determinista y debe reproducir 5/11 en el diseño W36D. Si no lo reproduce, se reporta como discrepancia antes de dar cualquier veredicto.

## H8: ¿N ≥ 11 o P_serv > 3.500 kN explican que la zapata no quepa?

- **Población:** los 11 edificios del grupo falla de #324.
  - **Primario:** el diseño W36D (secciones con viento, combinaciones con W).
  - **Sensibilidad:** sin_viento.
- **Variables por edificio:**
  - *no cabe*: al menos una zapata aislada con L > espacio entre columnas vecinas − 0,30 m (#324-C);
  - N;
  - P_serv,máx: máximo de P sobre todas las columnas y todas las combinaciones de servicio B.2.3.
- **Regla:** N ≥ 11 **o** P_serv,máx > 3.500 kN.
- **Predicción de Wilmer:** todo edificio que no cabe cumple la regla (k = n). Los demás se resuelven con zapatas aisladas.
- **Veredicto:** *se cumple* si todos los que no caben cumplen la regla. *Refutada* si al menos uno no la cumple.
- **Contrapredicción de Claude:** se cumple la implicación. En estos pórticos la carga axial crece con N, y lo que define L es P/q_adm (H2 de #324-C dio 0/11 por excentricidad). Pero la recíproca falla: algún edificio cumple la regla y aun así cabe, porque 6 de los 11 tienen N ≥ 11.
- **Se reporta también, sin que decida:**
  - la recíproca;
  - la regla con solo N;
  - el umbral de P que mejor separaría, marcado como **post hoc**.

## H7: ¿peraltar la viga evita el traslape frente a engrosar la columna?

- **Población:** 1290, 1729 y 1762, los resueltos con viga peraltada en #324. n = 3: exploratoria, sin IC.
- **Dos diseños con W36D:**
  - *viga*: las secciones de #324 con W36D;
  - *solo columna*: el optimizador de #324 con W36D y h de viga **fija** en la del diseño sin viento (1290: 550; 1729: 600; 1762: 600). Solo recorre c y Δ.
- **Momento en la base:**
  - por columna exterior (perímetro), el máximo de √(Mx² + My²) en las combinaciones de servicio con W;
  - se compara el máximo entre columnas exteriores;
  - la mediana y las combinaciones con sismo se reportan aparte.
- **Traslape:** al menos una zapata que no cabe con 200 kPa.
- **Predicción de Wilmer:** con la viga, el momento es menor **y** se evita el traslape (sin traslape con la viga, con traslape solo con columna) en **al menos 2 de 3**.
- **Veredicto:**
  - *se cumple* si k ≥ 2;
  - *refutada* si k ≤ 1 y algún diseño tiene traslape;
  - **inconclusa** si ninguno de los 3 tiene traslape en ninguno de los dos diseños, porque no hay traslape que evitar.
  - Si el optimizador no encuentra diseño solo-columna, ese edificio sale del denominador y se reporta.
- **Contrapredicción de Claude:** **no se cumple** (inconclusa o refutada).
  - El momento de servicio en la base sí podría ser menor con la viga.
  - Pero L la define P de servicio, no el momento, y P casi no cambia entre los dos diseños. Así que el traslape debería coincidir en ambos.

## Reglas

- Los criterios no cambian después de ver los resultados.
- Errores por id.
- Nada de esto diseña cimentaciones reales. El estudio de suelos (Título H) y la firma del ingeniero son insustituibles.
