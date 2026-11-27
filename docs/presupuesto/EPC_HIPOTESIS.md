# Precios de referencia de EPC (Cundinamarca, 2021–2026): cruces e hipótesis

Generado por `scripts/ingesta/epc/analizar_epc.py`. Hipótesis formuladas antes de ver los resultados (docstring del script); se reportan aunque no se confirmen.

Datos: 237,335 precios (actividad × municipio × año), 561 actividades, 117 municipios, años [2021, 2022, 2024, 2025, 2026].

## H1. Variación anual (misma actividad, mismo municipio)

| Año | Pares | Mediana precio(t)/precio(t−1) | P10–P90 | Actividades que bajaron |
|---|---|---|---|---|
| 2022 | 43,606 | 1.096 | 1.005–1.310 | 9% |
| 2025 | 37,359 | 1.035 | 0.845–1.123 | 35% |
| 2026 | 42,930 | 1.322 | 1.050–1.497 | 9% |

Índice encadenado 2021→2026: **×1.50** (mediana de razones de la misma actividad).

Por capítulo (mediana de la razón anual, años disponibles):

| Capítulo | 2022 | 2024 | 2025 | 2026 |
|---|---|---|---|---|
| CONDUCCIONES Y REDES DE ACUEDUCTO | 1.064 | — | 1.053 | 1.330 |
| CONCRETOS MORTEROS ACERO DE REFUERZO Y A | 1.146 | — | 1.020 | 1.368 |
| REDES DE ALCANTARILLADO DE AGUAS RESIDUA | 1.088 | — | 1.042 | 1.338 |
| PLANTAS DE TRATAMIENTO DE AGUA POTABLE Y | 1.122 | — | 1.040 | 1.180 |
| RECONSTRUCCION DE PAVIMENTOS ANDENES Y S | 1.127 | — | 0.979 | 1.138 |
| EXCAVACIONES NO INCLUYE CARGUE NI TRANSP | 1.096 | — | 1.102 | 1.276 |
| RELLENOS | 1.073 | — | 0.892 | 2.064 |
| DEMOLICIONES DESMONTE Y DESCAPOTE | 1.065 | — | 1.180 | 1.217 |
| OBRAS PRELIMINARES | 1.061 | — | 0.872 | 1.367 |
| IMPACTO URBANO | 1.091 | — | 1.040 | 1.050 |
| CARGUE Y RETIRO DE SOBRANTES | 1.058 | — | 0.861 | 1.156 |

Saltos ×2 o más (o caídas a la mitad) de un año al siguiente, que sugieren cambio de especificación o de alcance más que inflación: 2022: 820, 2025: 340, 2026: 1,199.
Ejemplos: 2022: LOCALIZACION Y REPLANTEO REDES [ML] 2,325→12,308; 2025: EXCAVACION MECANICA EN ROCA EN SECO SIN EXPLOSIVOS [M3] 145,641→305,154; 2026: ARENA DE PENA PARA SOPORTE DE TUBERIA [M3] 117,906→462,082

## H2. Variación entre municipios de una misma provincia (2026)

| Capítulo | Actividades | Mediana del CV entre municipios | Actividades con CV > 5 % |
|---|---|---|---|
| RELLENOS | 156 | 1.7% | 32% |
| CONCRETOS MORTEROS ACERO DE REFUERZO Y A | 910 | 1.4% | 15% |
| RECONSTRUCCION DE PAVIMENTOS ANDENES Y S | 234 | 1.3% | 7% |
| REDES DE ALCANTARILLADO DE AGUAS RESIDUA | 936 | 0.1% | 2% |
| IMPACTO URBANO | 52 | 0.0% | 2% |
| OBRAS PRELIMINARES | 65 | 0.0% | 3% |
| DEMOLICIONES DESMONTE Y DESCAPOTE | 91 | 0.0% | 0% |
| EXCAVACIONES NO INCLUYE CARGUE NI TRANSP | 156 | 0.0% | 3% |
| CARGUE Y RETIRO DE SOBRANTES | 26 | 0.0% | 0% |
| CONDUCCIONES Y REDES DE ACUEDUCTO | 2483 | 0.0% | 2% |
| PLANTAS DE TRATAMIENTO DE AGUA POTABLE Y | 611 | 0.0% | 1% |

Factor municipal (mediana de precio / mediana de su provincia, 112 municipios): más caros COTA (1.006), TENJO (1.006), CHOCONTA (1.000), MACHETA (1.000), MANTA (1.000); más baratos SIMIJACA (1.000), SUSA (1.000), SUTATAUSA (1.000), TAUSA (1.000), UBATE (1.000).

## H3. Factor municipal frente a distancia a Bogotá

Municipios con coordenadas: 108 de 112 (sin coordenadas: NARINO, QUEBRADANEGR A, SAN JUAN DE RIO SECO, UBATE).
Spearman ρ = **-0.20** (IC95 bootstrap -0.32 a -0.12). Se confirma una relación negativa.

## H4. Cundinamarca (EPC) frente a Atlántico (base de StructAI)

Pares con misma unidad y similitud ≥ 0,80: **20**.
Mediana de precio EPC 2026 / precio base: **0.79** (P25–P75 0.70–1.87). Ojo: la base mezcla años (contratos 2016–2019 ajustados por IPC, catálogos recientes); la razón no es solo regional.

Ejemplos: ENTIBADO TIPO 2 CONTINUO EN MADERA ↔ Entibado Tipo 3.  Continuo de madera (Barranquilla): ×0.78; ENTIBADO TIPO 1A DISCONTINUO EN MADERA ↔ Entibado tipo 1. Discontinuo de madera (Puerto Colombia): ×0.68; DEMOLICION DE ESTRUCTURAS EN CONCRETO ↔ DEMOLICION DE ESTRUCTURAS (Atlántico): ×1.46; ESMALTE SOBRE LAMINA LLENA 2 MANOS ↔ ESMALTE SOBRE LÁMINA LLENA (Barranquilla): ×1.50; DESMONTE Y LIMPIEZA CON RETIRO ↔ Desmonte y Limpieza (Barranquilla): ×16.31

## H5. Clasificador por etapa (#196) sobre las actividades de EPC (fuera de dominio)

Filas: capítulo según EPC. Columnas: etapa predicha (0 transversales, 1 obra negra, 2 obra gris, 3 obra blanca, 4 fase final). En obras de acueducto y alcantarillado lo esperado es la etapa 4 (redes externas) o la 1 (excavación, concretos); mucho 2 o 3 indica confusión del modelo entrenado con vivienda.

| Capítulo EPC | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| CONDUCCIONES Y REDES DE ACUE | 0 | 43 | 172 | 72 | 0 |
| REDES DE ALCANTARILLADO DE A | 0 | 35 | 35 | 10 | 0 |
| CONCRETOS MORTEROS ACERO DE  | 0 | 66 | 1 | 1 | 2 |
| PLANTAS DE TRATAMIENTO DE AG | 0 | 15 | 16 | 14 | 4 |
| RECONSTRUCCION DE PAVIMENTOS | 0 | 11 | 9 | 1 | 0 |
| RELLENOS | 0 | 17 | 0 | 0 | 1 |
| EXCAVACIONES NO INCLUYE CARG | 0 | 14 | 0 | 4 | 0 |
| DEMOLICIONES DESMONTE Y DESC | 0 | 5 | 1 | 1 | 0 |
| OBRAS PRELIMINARES | 0 | 5 | 0 | 0 | 0 |
| IMPACTO URBANO | 0 | 3 | 0 | 1 | 0 |
| CARGUE Y RETIRO DE SOBRANTES | 0 | 2 | 0 | 0 | 0 |

