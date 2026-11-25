# Prerregistro #242: viento B.6 en los pórticos de zona sísmica baja que no son "edificios bajos"

Fijado el 2026-11-24, **antes** de correr. Código: `scripts/memorias_sinteticas/viento_242.py` y el método general del motor (`b6.fuerzas_por_nivel`, `b6.factor_rafaga`, `b6.cp_cubierta_general`) en la rama `feat/viento-altura-242`.

## Sesgo declarado

- **Lo que ya sé (no sale de correr viento en esta población):**
  - el resultado de #292-W en los 86 edificios bajos: 0/86 cambian refuerzo, razón 1,6W/E con mediana 0,14 y máximo 0,40 en W36D;
  - la geometría de la población: 272 edificios, N de 3 a 12, h de 8,7 a 42 m (mediana 25,6), 49 con h ≤ 18 m pero esbeltos en planta; todos DMI (R = 2,5) con losa;
  - el T_modelo del corpus (113 con T > 1,5 s, máximo 2,29 s).
- **Hipótesis propuestas por Wilmer**, ajustadas para que sean falsables (la evaluación crítica está en #242). Las predicciones de Wilmer y las mías se registran por separado cuando difieren.
- **Motor de altura sin validación independiente.** G y Gf (B.6.5.8) están verificados solo a mano en pruebas unitarias. No hay un ejemplo resuelto gratuito: los manuales con ejemplos son de pago y no se compran. Los resultados son **verificación**, no validación.

## Diseño

- **Población:** los 272 edificios de zona baja del corpus F1 (`corpus.csv`, estado ok) que no son "edificios bajos" de B.6.
- **Brazos pareados por edificio** (las mismas secciones, cargas y margen u_máx por defecto, como #292-W):
  - **control:** sin viento;
  - **W28C:** V = 28 m/s, exposición C;
  - **W36D:** V = 36 m/s, exposición D.
- **Viento:** método general B.6.5.12.2.1, cerrado (GCpi ±0,18), I = 1,00 en el grupo I, Kzt = 1.
  - Muros: barlovento con qz (Kz caso 2) y sotavento con qh, Cp de la Fig. B.6.5-3.
  - G rígido si n1 ≥ 1 Hz; Gf flexible si n1 < 1 Hz, con n1 = 1/T_modelo por dirección y **β = 0,02 (HIPÓTESIS)**.
  - Cubierta plana: Cp por distancia al borde de barlovento.
  - **Sin** los casos 2–4 de carga parcial y torsional de la Fig. B.6.5-6.

## Hipótesis y métricas

IC95 de Wilson para proporciones y bootstrap (2.000 remuestreos, semilla 2421) para correlación y pendiente.

| Id | Métrica | Predicción |
|---|---|---|
| **H-A1** (primaria) | Fracción de edificios cuyo refuerzo cambia (firma completa) en W36D | IC95 superior ≤ 10 % |
| H-A1b | Lo mismo por separado en vigas y en columnas | Wilmer: el refuerzo longitudinal de vigas no cambia. Descriptiva |
| **C-A** | Sobrecosto relativo en W36D | p90 ≤ 1 % |
| **R-A** | Edificios que cumplían y dejan de cumplir | 0 |
| **H-A2** (física) | ρ = 1,6·W_base / E_base (máximo por dirección) contra h: Spearman y pendiente log-log | Spearman > 0 y pendiente > 0, ambos con IC95 que excluye 0, en los dos brazos. Teoría: pendiente ≈ 1,1 (V_W ∝ H^1,2 y V_s ∝ H^0,1 en la rama descendente), descriptiva |
| H-A2' | Edificios con ρ > 1 en W36D | ≤ 10 % (es decir, la altura de transición H* queda por encima de la mayoría del corpus). H* del ajuste mediano: descriptivo |
| H-A2b | Razón ρ(W36D) / ρ(W28C) por edificio | Mediana entre 1,6 y 2,4: ρ **sí** depende de V (∝ V²·Kz·G). Contrasta la afirmación original de que no depende de V |
| **H-A3** (deriva) | Entre los edificios con T_max > 1,5 s: fracción donde la deriva de viento en servicio (1,0W lateral, centro del diafragma) usa más de su límite **h_piso/400** (criterio DECLARADO, no NSR-10) que la deriva sísmica de su límite A.6.4 | **Wilmer:** > 50 %, con el máximo en el tercio superior. **Mía:** < 10 % |
| H-A4 (cubierta liviana) | Correa con θ = 5°, h = 6 m, luz 5 m. Fracción de combinaciones región (5) × exposición (3) × zona (1, 2, 3) con levantamiento neto 1,6·\|p\| > 0,9·D, para D = 0,15, 0,30 y 0,50 kPa | **Wilmer:** 100 %, con tensión neta en todos los anclajes y correas cuando la succión neta supera 5D. **Mía:** < 100 % con D = 0,30 (región 1, exposición B, zona 1 sin levantamiento neto). Es demanda determinista: los anclajes siguen SIN VALIDAR (#319) |

## Reglas de decisión

- **H-A1, C-A y R-A (W36D):** si las tres se cumplen, el viento **no gobierna** el pórtico con losa en zona baja hasta 42 m. Queda opcional en todo el corpus de zona baja. Si no se cumplen, el viento debe evaluarse por defecto en edificios altos de zona baja, lo que exige V por municipio (issue aparte).
- **H-A3:**
  - IC95 inferior > 50 %: **CONFIRMADA** la de Wilmer;
  - IC95 superior < 50 %: **REFUTADA**;
  - en otro caso, **NO CONCLUYENTE**.
- **H-A2, H-A2' y H-A2b:** se informan con veredicto contra la predicción, sin regla de decisión de diseño.

## Calidad

- Errores de ejecución se reportan por id y no se reemplazan.
- Si el viento no se evalúa en un edificio, cuenta como error.
- La corrida no se hace entre las 23:00 y el fin del CI nocturno (`--hasta 22:45`).

## Piloto (declarado)

Antes de la corrida completa se corre un piloto de 2 edificios (`--piloto 2`), solo para comprobar que el script no falla. Si falla, se corrige el script, no los criterios, y la corrección se declara en los resultados. Los 2 edificios quedan incluidos.

## Fuera de alcance

- Casos torsionales y de carga parcial de viento.
- Efectos de segundo orden con viento.
- Aceleraciones de confort.
- Viento cruzado y torsional dinámico: el Método 2 no los cubre (B.6.5.1). Se asume que el corpus, con planta regular, no tiene respuesta inusual.
- Validación independiente de Gf.
