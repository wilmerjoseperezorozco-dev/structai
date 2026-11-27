# motor-pilotes (#118)

Capacidad axial a compresión de pilotes y grupos según la NSR-10 Título H (H.4.4 y H.4.7) y el CCP-14 (SPT), y
asentamiento de grupos por zapata equivalente (NSR-10 H.4.4.2 con el método del CCP-14 §10.7.2.3). Los textos de la
NSR-10 se cotejaron con la impresa (H-15) y los del CCP-14 con la Sección 10 oficial de INVIAS (copias locales fuera
del repositorio).

| Función (`src/contrato_api.py`) | Endpoint | Qué calcula | Norma |
|---|---|---|---|
| `pilotes_contrato` | `POST /pilotes/capacidad` | Capacidad admisible del pilote y del grupo contra la reacción de la columna | NSR-10 H.4.4.1, H.4.7, Tablas H.4.7-1 y H.2.4-1; CCP-14 §10.7.3.8.6g, §10.8.3.5.2 |
| `asentamiento_pilotes_contrato` | `POST /pilotes/asentamiento` | Acortamiento del fuste + asentamiento bajo la zapata equivalente, contra 30 / 15 cm | NSR-10 H.4.4.2, H.4.9.2; CCP-14 §10.7.2.3 |

Ambas devuelven `ResultadoMotor` con supuestos, advertencias y `en_borde_dominio`. Los endpoints tienen límite de tasa
y responden 422 con la norma citada.

## Métodos

| Módulo | Contenido |
|---|---|
| `axial.py` | Fricción τL = 2/3·τF (drenado, H.4.7-2) o α·Su (H.4.7-3); punta 9·Su en arcilla; FS separados de fricción y punta |
| `arena_spt.py` | SPT del CCP-14: Meyerhof en hincados y método β en excavados, con CN de 10.4.6.2.4-1 |
| `mixto.py` | Perfil arcilla + arena en un mismo pilote, cada estrato con su método y su FS |
| `grupo.py` | Mínimo de Σ individuales, bloque (Terzaghi y Peck, Nc de Skempton) y eficiencia de Converse-Labarre (si se pide) |
| `asentamiento.py` | Zapata equivalente (Fig. 10.7.2.3.1-1), 2V:1H, consolidación primaria de motor-geotecnia o Meyerhof con SPT (Ec. 10.7.2.3.2-1) |

### Asentamiento

- **Zapata equivalente:** a z = (L − Db) + f·Db, con Db el empotramiento en la capa de soporte y f = 1 (a, punta),
  2/3 (b, fricción en arcilla), 8/9 (c, fricción en arena sobre arcilla) o 2/3 (d, perfil por capas). La planta es el
  perímetro exterior del grupo, sin reducción B' = B − 2e (§10.7.2.3.1).
- **Cohesivo:** consolidación primaria última con Cc, Cr, e0, σ'0 y σ'p del estudio, con Δσ 2V:1H en el punto medio de
  cada estrato. Se reutiliza `motor-geotecnia` (`consolidacion.py`, `esfuerzos.py`).
- **Granular:** ρ = 30·q·I·√B / N1_60 (mm, MPa), I = 1 − 0,125·D'/B ≥ 0,5, D' = 2/3·Db. El CCP-14 advierte que tiende a
  sobrepredecir (C10.7.2.3.2).
- **Acortamiento del fuste:** Q·L/(A·Ep) con la carga completa en toda la longitud, cota superior. Ep no tiene valor
  por defecto.

## Validación con datos reales (prerregistrada en #118)

| Prueba | n | λ = medido / predicho | Veredicto | Detalle |
|---|---|---|---|---|
| El Dorado 2008 (CAPWAP, arcilla blanda) | 5 | 1,39 | No pasa el criterio de banda (1/5) | `validacion/RESULTADOS_ELDORADO_2008.md` |
| CYCU 2025, arcilla | 71 | 1,48 [1,24; 1,78] | Conservador | `validacion/RESULTADOS_CYCU_2025.md` |
| CYCU 2025, arena (SPT) | 81 | 0,96 [0,78; 1,17], COV 0,63 | Calibrado en promedio, dispersión alta | `validacion/RESULTADOS_CYCU_ARENA_2025.md` |

La base CYCU (Chen et al., 2025, CC BY 4.0) no se versiona. El asentamiento todavía no tiene validación con pruebas de
carga: solo pruebas calculadas a mano.

## Lo que NO verifica

- La resistencia estructural del fuste, la carga lateral, la tracción y la excentricidad entre pilotes (H.4.4.1).
- La fricción negativa, el asentamiento por sismo y la consolidación secundaria (H.4.4.2): próximamente.
- La roca (H.4.7-4), Nordlund/Thurman y geomateriales intermedios.
- Las tablestacas del alcance original de #118: próximamente.
- La consolidación se calcula última, no a 20 años, así que queda del lado conservador frente a H.4.9.2.

## Verificación

```powershell
python -m pytest packages/motor-pilotes/tests -q
```

55 pruebas del paquete y 8 del router (`apps/api/tests/test_router_pilotes.py`).
