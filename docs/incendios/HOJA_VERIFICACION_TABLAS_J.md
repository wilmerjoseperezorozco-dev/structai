# Hoja de verificación (#336 F0): números del Título J transcritos al motor

**Para Wilmer.** Abre el PDF oficial (`dev/descargas/nsr10/3871-10684.pdf`). Las tablas están en las páginas 1542 y 1547–1550 del PDF (J-12 a J-20 impresas).
- Marca ✔ cada fila que coincida.
- En las filas **PENDIENTE**, escribe los valores tal como se ven: con celdas combinadas o vacías, indica a qué columnas de pisos corresponden.

El motor **no clasifica** con las filas pendientes hasta que estén verificadas. Los valores viven en `packages/motor-incendios/src/tablas_j.py`.

Verifica también la **versión**: ¿el PDF incluye las modificaciones a los Títulos J y K posteriores al Decreto 926 de 2010? Anota el decreto, si lo indica.

## Tabla J.3.3-1 (pisos 1 · 2 · 3 · 4 · 5 · 6 · ≥7)

| Subgrupo | AT (m²) | Transcrito | ✔ / corrección |
|---|---|---|---|
| C-1 | > 1500 | III III II II II I I | |
| C-1 | < 1500 | III III III II II II I | |
| C-2 | > 500 | II I I I I I I | |
| C-2 | < 500 | **PENDIENTE**: la extracción da "II I I I I" (5 valores) | |
| E | sin límite | III III III II II II I | |
| I-2, I-4 | > 1000 | III II II I I I I | |
| I-2, I-4 | 500–1000 | III III II II I I I | |
| I-2, I-4 | < 500 | III III III II II II I | |
| I-3 | > 1000 | II II I I I I I | |
| I-3 | < 1000 | **PENDIENTE**: "III II II I I I" (6 valores) | |
| L-1…L-5, I-1, I-5 | > 1000 | II I I I I I I | |
| L-1…L-5, I-1, I-5 | 500–1000 | II II I I I I I | |
| L-1…L-5, I-1, I-5 | < 500 | III III II II I I I | |
| R-1, R-2 | unidades > 140 m² | **PENDIENTE**: "II I I I" (4 valores) | |
| R-1, R-2 | unidades ≤ 140 m² | **PENDIENTE**: "III II II I" (4 valores) | |
| R-3 | > 5000 | III II I I I I I | |
| R-3 | < 5000 | III II II II I I I | |

Confirma también que los subgrupos de cada bloque (C-1, C-2, E, …) quedaron bien asignados a sus filas.

## Tabla J.3.3-2 (pisos 1 · 2 · 3 · 4 · ≥5)

| Grupo | Cc (MJ/m²) | Transcrito | ✔ |
|---|---|---|---|
| A-1, A-2 | > 8000 | II II I I I | |
| A-1, A-2 | 4000–8000 | III II II I I | |
| A-1, A-2 | < 4000 | III III III II I | |
| F-1, F-2 | > 8000 | I I I I I | |
| F-1, F-2 | 4000–8000 | II II I I I | |
| F-1, F-2 | 2000–4000 | III II II I I | |
| F-1, F-2 | < 2000 | III III II II I | |
| P | > 8000 | I I I I I | |
| P | 4000–8000 | II I I I I | |
| P | < 4000 | III II II I I | |

## Tabla J.3.4-3 (horas; categorías I · II · III)

| Elemento | Transcrito | ✔ |
|---|---|---|
| Muros cortafuego | 3 · 2½ · 2 | |
| Cerramiento de escaleras, ascensores, buitrones, ductos de basura y corredores de evacuación | 2 · 2 · 1½ | |
| Muros divisorios entre unidades | 2 · 1½ · 1 | |
| Muros interiores no portantes | ½ · ¼ · — | |
| Columnas, vigas, viguetas, losas, muros portantes, celosías | 2 · 1½ · 1 | |
| Cubiertas | **PENDIENTE**: leído como 1 · 1 · ½ | |
| Escaleras interiores no encerradas | 2 · 1½ · 1 | |

## Tablas J.3.5 (horas 1 · 1½ · 2 · 3 · 4; mm)

| Tabla | Fila | Transcrito | ✔ |
|---|---|---|---|
| J.3.5-1 columnas | silíceo | 200 230 250 310 360 | |
| J.3.5-1 | carbonato | 200 230 250 300 310 | |
| J.3.5-1 | liviano | 200 220 230 270 310 | |
| J.3.5-1, notas | con dos lados ≥ 950 mm | 2 h y 3 h → 200; 4 h → 250 | |
| J.3.5-2 muros y losas | silíceo | 90 110 130 160 180 | |
| J.3.5-2 | carbonato | 80 100 120 150 170 | |
| J.3.5-2 | finos livianos | 70 80 100 120 140 | |
| J.3.5-2 | gruesos livianos | 60 80 90 110 130 | |
| J.3.5-3 recubrimiento de losas | restringida, todos | 20 20 20 20 20 | |
| J.3.5-3 | no restringida, silíceo | 20 20 30 30 40 | |
| J.3.5-3 | no restringida, carbonato y livianos | 20 20 20 30 30 | |
| J.3.5-5 recubrimiento de vigas | restringida, ancho 130 | 20 20 20 30 30 | |
| J.3.5-5 | restringida, 180 y ≥ 250 | 20 20 20 20 20 | |
| J.3.5-5 | no restringida, 130 | 20 30 30 — — | |
| J.3.5-5 | no restringida, 180 | 20 20 20 40 80 | |
| J.3.5-5 | no restringida, ≥ 250 | 20 20 20 30 40 | |

## Interpretaciones que conviene revisar con un experto en protección contra incendios

1. "Más de N pisos o H m de altura, lo que sea mayor": el motor lo aplica como pisos > N **o** altura > H (la lectura más exigente).
2. Para A, F y P, la categoría sale de la Tabla J.3.3-2 (J.3.3.2), aunque J.3.3.1 los liste en una categoría fija. Lo mismo para R-1 con la Tabla J.3.3-1.
3. En los límites exactos de área se usa la fila más exigente.

## F8: Título A.9, B.2.4 y Apéndice C-D (soportes y anclajes)

Los valores están en `packages/motor-incendios/src/soportes.py`. Los cotejé con el PDF oficial el 2026-11-26:
- Título A: páginas A-89 a A-95; la Tabla A.9.6-1 está en la página 138 del PDF.
- Apéndice C-D: C-D.3.3 y C-D.7.

| Numeral | Transcrito | ✔ |
|---|---|---|
| A.9.4-1 | Fp = (ax·ap/Rp)·g·Mp ≥ (Aa·I/2)·g·Mp | |
| A.9.4-2 | ax = As + (Sa − As)·hx/heq (hx ≤ heq); ax = Sa·hx/heq (hx ≥ heq); heq ≈ 0,75 hn | |
| A.9.4.8 | en la base o por debajo de ella: ax = Aa·I | |
| A.9.4.4 | vertical adicional ±W/3 sin amplificar | |
| A.9.4.9 | Rp = 6 especiales/dúctiles (embebido/d > 8, sin expansión ni tiros); 1,5 no dúctiles; 0,5 húmedos | |
| A.9.1.3 | exentos los grupos I y II en zona baja | |
| Tabla A.9.2-1 | IV y III superior; II bueno; I bajo | |
| Tabla A.9.6-1 | tubería contra incendio ap 2,5: dúctil / no dúctil / no dúctil | |
| Tabla A.9.6-1 | bombas hidráulicas (equipo en general) ap 1,0: dúctil / no dúctil / no requerido | |
| Tabla A.9.6-1, nota (d) | exime solo a "otros sistemas de tuberías", no a la red contra incendio | |
| B.2.4-1, -5, -7 | 1,4D; 1,2D + 1,0E + 1,0L; 0,9D + 1,0E | |
| C-D.3.3.3 | concreto 0,75φNn y 0,75φVn en DMO y DES | |
| C-D.3.3.6 | 0,4 × resistencia de C-D.3.3.3 | |
| C-D.7 | umbrales 0,2φ; N/φN + V/φV ≤ 1,2 | |

**Interpretaciones para revisar:**
4. **As = Aa·Fa·I.** Es la ordenada en T = 0 de la figura A.2.6-1 (2,5·Aa·Fa·I·0,4). No encontré en el texto una ecuación explícita de As.
5. **Componente vertical.** La nota (b) de la Tabla A.9.6-1 sube el ap vertical un 33 %, mientras que A.9.4.4 da W/3 sin amplificar. El motor usa A.9.4.4 e informa aparte el valor que daría la nota (b).
6. **El agua dentro del tubo se toma como carga muerta D**, no como F (fluidos).
