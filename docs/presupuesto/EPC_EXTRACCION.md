# Extracción de las cartillas de precios de EPC (2021–2026)

Generado por `scripts/ingesta/epc/extraer_cartillas_epc.py`. Fuente pública: Empresas Públicas de Cundinamarca (EPC), listas de precios de referencia por provincia, adoptadas por Decisión Empresarial anual. PDF en `scripts/ingesta/epc/raw/` (gitignored); salida en `scripts/ingesta/epc/salida/`.

- Cartillas: **90** (15 provincias × 6 años). Filas (actividad × municipio × año): **237,335**.
- Municipios: **118**. Actividades distintas (descripción + unidad): **564**.
- Filas por año: 2021: 46,981, 2022: 44,572, 2024: 47,223, 2025: 47,520, 2026: 51,039
- Filas sin capítulo asignado: 0.

| Cartilla | Ítems | Municipios | Filas | Ítems sin precio |
|---|---|---|---|---|
| CARTILLA-ALMEIDAS-2021.pdf | 440 | 7 | 3,080 | 0 |
| CARTILLA-ALMEIDAS-2022.pdf | 356 | 7 | 2,492 | 0 |
| CARTILLA-ALMEIDAS-2023.pdf | 0 | 0 | 0 | 0 |
| CARTILLA-ALMEIDAS-2024.pdf | 440 | 7 | 3,080 | 0 |
| CARTILLA-ALMEIDAS-2025.pdf | 440 | 7 | 3,080 | 0 |
| CARTILLA-ALMEIDAS-2026.pdf | 440 | 7 | 3,080 | 0 |
| CARTILLA-ALTO-MAGDALENA-2021.pdf | 440 | 8 | 3,520 | 0 |
| CARTILLA-ALTO-MAGDALENA-2022.pdf | 440 | 8 | 3,520 | 0 |
| CARTILLA-ALTO-MAGDALENA-2023.pdf | 0 | 0 | 0 | 0 |
| CARTILLA-ALTO-MAGDALENA-2024.pdf | 440 | 8 | 3,520 | 0 |
| CARTILLA-ALTO-MAGDALENA-2025.pdf | 440 | 8 | 3,520 | 0 |
| CARTILLA-ALTO-MAGDALENA-2026.pdf | 440 | 8 | 3,520 | 0 |
| CARTILLA-BAJO-MAGDALENA-2021.pdf | 440 | 3 | 1,320 | 0 |
| CARTILLA-BAJO-MAGDALENA-2022.pdf | 440 | 3 | 1,320 | 0 |
| CARTILLA-BAJO-MAGDALENA-2023.pdf | 0 | 0 | 0 | 0 |
| CARTILLA-BAJO-MAGDALENA-2024.pdf | 440 | 3 | 1,320 | 0 |
| CARTILLA-BAJO-MAGDALENA-2025.pdf | 440 | 3 | 1,320 | 0 |
| CARTILLA-BAJO-MAGDALENA-2026.pdf | 440 | 3 | 1,320 | 0 |
| CARTILLA-GUALIVA-2021.pdf | 440 | 12 | 5,280 | 0 |
| CARTILLA-GUALIVA-2022.pdf | 440 | 12 | 5,280 | 0 |
| CARTILLA-GUALIVA-2023.pdf | 0 | 0 | 0 | 0 |
| CARTILLA-GUALIVA-2024.pdf | 440 | 12 | 5,280 | 0 |
| CARTILLA-GUALIVA-2025.pdf | 440 | 12 | 5,280 | 0 |
| CARTILLA-GUALIVA-2026.pdf | 440 | 12 | 5,280 | 0 |
| CARTILLA-GUAVIO-2021.pdf | 440 | 8 | 3,520 | 0 |
| CARTILLA-GUAVIO-2022.pdf | 440 | 8 | 3,520 | 0 |
| CARTILLA-GUAVIO-2023.pdf | 0 | 0 | 0 | 0 |
| CARTILLA-GUAVIO-2024.pdf | 440 | 8 | 3,520 | 0 |
| CARTILLA-GUAVIO-2025.pdf | 440 | 8 | 3,520 | 0 |
| CARTILLA-GUAVIO-2026.pdf | 440 | 8 | 3,520 | 0 |
| CARTILLA-MAGDALENA-CENTRO-2021.pdf | 440 | 7 | 3,080 | 0 |
| CARTILLA-MAGDALENA-CENTRO-2022.pdf | 440 | 7 | 3,080 | 0 |
| CARTILLA-MAGDALENA-CENTRO-2023.pdf | 0 | 0 | 0 | 0 |
| CARTILLA-MAGDALENA-CENTRO-2024.pdf | 440 | 7 | 3,080 | 0 |
| CARTILLA-MAGDALENA-CENTRO-2025.pdf | 440 | 7 | 3,080 | 0 |
| CARTILLA-MAGDALENA-CENTRO-2026.pdf | 440 | 7 | 3,080 | 0 |
| CARTILLA-MEDINA-2021.pdf | 440 | 2 | 880 | 0 |
| CARTILLA-MEDINA-2022.pdf | 440 | 2 | 880 | 0 |
| CARTILLA-MEDINA-2023.pdf | 0 | 0 | 0 | 0 |
| CARTILLA-MEDINA-2024.pdf | 440 | 2 | 880 | 0 |
| CARTILLA-MEDINA-2025.pdf | 440 | 2 | 880 | 0 |
| CARTILLA-MEDINA-2026.pdf | 440 | 2 | 880 | 0 |
| CARTILLA-ORIENTE-2021.pdf | 440 | 10 | 4,400 | 0 |
| CARTILLA-ORIENTE-2022.pdf | 440 | 10 | 4,400 | 0 |
| CARTILLA-ORIENTE-2023.pdf | 0 | 0 | 0 | 0 |
| CARTILLA-ORIENTE-2024.pdf | 440 | 10 | 4,400 | 0 |
| CARTILLA-ORIENTE-2025.pdf | 440 | 10 | 4,400 | 0 |
| CARTILLA-ORIENTE-2026.pdf | 440 | 10 | 4,399 | 0 |
| CARTILLA-RIONEGRO-2021.pdf | 0 | 0 | 0 | 0 |
| CARTILLA-RIONEGRO-2022.pdf | 0 | 0 | 0 | 0 |
| CARTILLA-RIONEGRO-2023.pdf | 0 | 0 | 0 | 0 |
| CARTILLA-RIONEGRO-2024.pdf | 0 | 0 | 0 | 0 |
| CARTILLA-RIONEGRO-2025.pdf | 0 | 0 | 0 | 0 |
| CARTILLA-RIONEGRO-2026.pdf | 440 | 8 | 3,520 | 0 |
| CARTILLA-SABANA-CENTRO-2021.pdf | 391 | 11 | 4,301 | 0 |
| CARTILLA-SABANA-CENTRO-2022.pdf | 440 | 11 | 4,265 | 52 |
| CARTILLA-SABANA-CENTRO-2023.pdf | 0 | 0 | 0 | 0 |
| CARTILLA-SABANA-CENTRO-2024.pdf | 440 | 9 | 4,831 | 0 |
| CARTILLA-SABANA-CENTRO-2025.pdf | 440 | 11 | 4,840 | 0 |
| CARTILLA-SABANA-CENTRO-2026.pdf | 440 | 11 | 4,840 | 0 |
| CARTILLA-SABANA-OCCIDENTE-2021.pdf | 440 | 8 | 3,520 | 0 |
| CARTILLA-SABANA-OCCIDENTE-2022.pdf | 440 | 8 | 3,520 | 0 |
| CARTILLA-SABANA-OCCIDENTE-2023.pdf | 0 | 0 | 0 | 0 |
| CARTILLA-SABANA-OCCIDENTE-2024.pdf | 404 | 8 | 3,232 | 0 |
| CARTILLA-SABANA-OCCIDENTE-2025.pdf | 440 | 8 | 3,520 | 0 |
| CARTILLA-SABANA-OCCIDENTE-2026.pdf | 440 | 8 | 3,520 | 0 |
| CARTILLA-SOACHA-2021.pdf | 440 | 2 | 880 | 0 |
| CARTILLA-SOACHA-2022.pdf | 440 | 2 | 880 | 0 |
| CARTILLA-SOACHA-2023.pdf | 0 | 0 | 0 | 0 |
| CARTILLA-SOACHA-2024.pdf | 440 | 2 | 880 | 0 |
| CARTILLA-SOACHA-2025.pdf | 440 | 2 | 880 | 0 |
| CARTILLA-SOACHA-2026.pdf | 440 | 2 | 880 | 0 |
| CARTILLA-SUMAPAZ-2021.pdf | 440 | 10 | 4,400 | 0 |
| CARTILLA-SUMAPAZ-2022.pdf | 440 | 10 | 4,400 | 0 |
| CARTILLA-SUMAPAZ-2023.pdf | 0 | 0 | 0 | 0 |
| CARTILLA-SUMAPAZ-2024.pdf | 440 | 10 | 4,400 | 0 |
| CARTILLA-SUMAPAZ-2025.pdf | 440 | 10 | 4,400 | 0 |
| CARTILLA-SUMAPAZ-2026.pdf | 440 | 10 | 4,400 | 0 |
| CARTILLA-TEQUENDAMA-2021.pdf | 440 | 10 | 4,400 | 0 |
| CARTILLA-TEQUENDAMA-2022.pdf | 272 | 10 | 2,668 | 0 |
| CARTILLA-TEQUENDAMA-2023.pdf | 0 | 0 | 0 | 0 |
| CARTILLA-TEQUENDAMA-2024.pdf | 440 | 10 | 4,400 | 0 |
| CARTILLA-TEQUENDAMA-2025.pdf | 440 | 10 | 4,400 | 0 |
| CARTILLA-TEQUENDAMA-2026.pdf | 440 | 10 | 4,400 | 0 |
| CARTILLA-UBATE-2021.pdf | 440 | 10 | 4,400 | 0 |
| CARTILLA-UBATE-2022.pdf | 440 | 10 | 4,347 | 0 |
| CARTILLA-UBATE-2023.pdf | 0 | 0 | 0 | 0 |
| CARTILLA-UBATE-2024.pdf | 440 | 10 | 4,400 | 0 |
| CARTILLA-UBATE-2025.pdf | 440 | 10 | 4,400 | 0 |
| CARTILLA-UBATE-2026.pdf | 440 | 10 | 4,400 | 0 |
