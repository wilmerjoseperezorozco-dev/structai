# Resultados HE1, HE2 y HE3 (#274)

Prerregistro: `PRERREGISTRO_HE1_HE3.md`, commit 6a3552f, fijado antes de correr. Corridas del 2026-11-19, de 17:23 a 17:28. Datos: `he1_he2_resultados.json` y `he3_resultados.json`.

## HE1: el periodo del pórtico desnudo supera Cu·Ta → **CONFIRMADA con inercias fisuradas; REFUTADA con brutas**

| Inercias | T > Cu·Ta | IC95 de Wilson | T/Cu·Ta mediano | Veredicto |
|---|---|---|---|---|
| **Fisuradas, 0,70/0,35 (principal)** | 487 de 500 (97,4 %) | [95,6 %; 98,5 %] | 1,23 | **CONFIRMADA** |
| Brutas (sensibilidad) | 46 de 500 (9,2 %) | [7,0 %; 12,1 %] | 0,80 | REFUTADA |

- **La hipótesis depende por completo de la inercia** con la que se calcula T. Con inercias fisuradas, en la FHE casi siempre gobierna el tope Cu·Ta. Con brutas casi nunca, salvo en 3 pisos (35 de 50).
- **Dónde falla con fisuradas:** los 13 casos están todos en Aa = 0,30 y perfil D, donde Cu = 1,2 es el mínimo. Allí T/Cu·Ta queda entre 0,89 y 0,99.
- **Por pisos (fisuradas):** la mediana es 1,48 en 3 pisos y se mantiene entre 1,18 y 1,21 desde 5 pisos.
- **Consecuencia para el motor:** el periodo que reporte debe decir con qué inercias se calculó. El cortante de la FHE con T = mín(T_modelo, Cu·Ta) casi no depende del modelo cuando se usan inercias fisuradas.

## HE2: gobierna el ajuste A.5.4.5 → **CONFIRMADA**

| | Resultado |
|---|---|
| Vt/Vs < 0,80 | 433 de 500 (86,6 %), IC95 [83,3 %; 89,3 %] |
| Vt/Vs mediano | 0,70 |
| Factor de ajuste mediano | 1,14 |

- **Cuándo no gobierna:** sobre todo en edificios de 3 pisos, donde solo 14 de 50 quedan por debajo de 0,80 (mediana 0,85). También es menos frecuente con Aa = 0,30 (71 de 100) y en perfil D.
- **De 6 a 12 pisos** el ajuste gobierna en 344 de 350 casos.
- **Consecuencia para el motor:** el análisis espectral casi nunca reduce las fuerzas por debajo del 80 % de la FHE. Su valor está en la distribución en altura y en planta, no en la magnitud. El motor debe mostrar siempre Vt, Vs y el factor de ajuste aplicado (ya lo entrega).

## HE3: omitir la torsión accidental → **CONFIRMADA, pero no es exclusivo de las plantas flexibles**

| Población, Aa = 0,25 | n | Subestiman > 10 % | IC95 de Wilson | Mediana [IC95 bootstrap] | Rango |
|---|---|---|---|---|---|
| **Flexibles, Ω < 1 (principal)** | 72 | 58 (80,6 %) | [70,0 %; 88,0 %] | 15,1 % [13,4 %; 16,3 %] | 1,7 %–20,6 % |
| Rígidas, Ω ≥ 1 (contraste) | 328 | 235 (71,6 %) | [66,5 %; 76,3 %] | 13,6 % [12,7 %; 14,4 %] | 2,2 %–26,0 % |

- **Sensibilidad Aa = 0,10:** prácticamente el mismo resultado (58 de 72; mediana 15,1 %). La razón casi no depende del nivel del espectro.
- **Descriptivo por Ω (todas las plantas, Aa = 0,25):**

| Ω | n | Subestiman > 10 % | Mediana |
|---|---|---|---|
| < 1 | 72 | 58 | 15,0 % |
| 1,0–1,2 | 139 | 135 | 17,1 % |
| 1,2–1,5 | 143 | 100 | 12,0 % |
| ≥ 1,5 | 46 | 0 | 4,7 % |

- **El efecto es máximo cerca de Ω ≈ 1, no en las plantas más flexibles.** Esto lo vi después de correr, así que es exploratorio. La lectura física es que, cuando los periodos de traslación y torsión se acercan, una excentricidad pequeña (5 %) acopla mucho los modos. Solo con Ω ≥ 1,5 la omisión es inofensiva.
- **Confusión con la altura:** 51 de las 72 plantas flexibles son de 3 pisos, y la subestimación baja con N (en las rígidas, la mediana pasa de 19 % en 3 pisos a 10 % en 12). Con estos datos no se puede separar el efecto de Ω del efecto de N.
- **Consecuencia para el motor:**
  - mantener `torsion_accidental=True` por defecto en el análisis espectral, aunque A.3.6.7 permita omitirla;
  - si el usuario la desactiva, advertir cuando Ω < 1,5;
  - reportar Ω, que ya sale de los modos.

## Limitaciones

- **Representatividad.** Las mallas tienen pesos iguales, no los del inventario de Colombia.
- **Geometría.** Las plantas son cuadradas y simétricas, sin mampostería. El núcleo de HE3 son columnas grandes, no muros (eso queda para la F3). No hay excentricidad propia, así que solo se estudió la accidental.
- **HE3 sin diseñar.** Las secciones no se iteraron para cumplir la deriva, y Ω < 1 se consiguió sobre todo con voladizos de 2–3 m.
- **El hallazgo de Ω ≈ 1 es posterior al análisis** y necesita su propio prerregistro: una malla que varíe Ω con N fijo.
