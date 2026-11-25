# Resultados #242: viento B.6 (método general) en los edificios de zona baja que no son "edificios bajos"

- **Prerregistro:** [`PRERREGISTRO_242_VIENTO_ALTURA.md`](PRERREGISTRO_242_VIENTO_ALTURA.md), commit `6da0af1`, publicado en [#242](https://github.com/wilmerjoseperezorozco-dev/structai/issues/242#issuecomment-7148671299) antes de correr.
- **Corrida:** `scripts/memorias_sinteticas/viento_242.py` sin cambios.
  - 816 diseños (272 edificios × 3 brazos), 0 errores, 161 s.
  - El piloto de 2 está incluido y no hizo falta corregir nada.
- **Salida:** `data/memorias_sinteticas/f1_242/`.
- **Estado del motor:** G y Gf solo **verificados** a mano, sin validación independiente. En 245 de los 272 edificios, n1 < 1 Hz y se usa Gf con β = 0,02 (HIPÓTESIS).

## Decisión: en edificios altos de zona baja el viento SÍ cambia diseños; debe evaluarse por defecto

| Id | Métrica | W28C | W36D | Criterio (W36D) | Veredicto |
|---|---|---|---|---|---|
| **H-A1** (primaria) | Edificios con refuerzo cambiado | 3/272, IC95 [0,4; 3,2 %] | **24/272 (8,8 %), IC95 [6,0; 12,8 %]** | IC95 sup. ≤ 10 % | **NO CUMPLE** |
| **R-A** | Dejan de cumplir | 0 | **10** | 0 | **NO CUMPLE** |
| **C-A** | Sobrecosto, p90 (máx.) | 0 % (3,1 %) | 0 % (2,8 %) | ≤ 1 % | cumple |

La regla prerregistrada da: **el viento debe evaluarse por defecto en los edificios altos de zona baja**, lo que exige V por municipio (issue aparte). En W28C, que se informa sin regla, el efecto es marginal: 3 edificios, ninguno deja de cumplir.

**Quiénes cambian (W36D, descriptivo):**
- Los 24 tienen h ≥ 20 m y ρ = 1,6W/E ≥ 1,21.
- En los 10 que dejan de cumplir, la falla es siempre en columnas de pisos bajos con la sección fija del corpus. Ninguna combinación de refuerzo cumple la flexocompresión biaxial con viento: hace falta una sección mayor, no solo más acero.
- Esos 10 tienen h entre 30 y 40 m, T entre 1,75 y 2,29 s y ρ entre 1,6 y 3,0.

## Hipótesis físicas

| Id | Predicción | Resultado (W36D; W28C) | Veredicto |
|---|---|---|---|
| **H-A2** | Spearman(h, ρ) > 0 y pendiente log-log > 0, con IC95 que excluye 0 | Spearman 0,47 [0,37; 0,56]; pendiente **0,90 [0,70; 1,11]**. W28C: 0,48 y 0,91 | **CONFIRMADA**. La pendiente teórica ≈ 1,1 queda dentro del IC |
| H-A2' | ρ > 1 en ≤ 10 % (mía) | **47/272 = 17 %**, IC95 [13; 22 %]. W28C: 7/272 (2,6 %) | **REFUTADA** |
| H-A2b | ρ(W36D)/ρ(W28C) con mediana entre 1,6 y 2,4 | Mediana 2,00 (rango 1,95–2,04) | **CONFIRMADA**: ρ escala con V²·Kz·G. La afirmación de que no depende de V queda descartada |
| **H-A3** | Wilmer: > 50 % de los edificios con T > 1,5 s tienen deriva de viento en servicio (frente a h/400) mayor que la sísmica, con el máximo en el tercio superior. Mía: < 10 % | 49/134 = **36,6 %, IC95 [28,9; 45,0 %]**. El máximo está en el tercio **inferior** en 133 de 134. W28C: 5,2 % | **REFUTADA** la de Wilmer (IC sup. < 50 %). La mía también falla: 36,6 % ≫ 10 % |
| H-A4 | Fracción de combinaciones con levantamiento neto en la correa. Wilmer: 100 %. Mía: < 100 % con D = 0,30 | D = 0,15: 45/45. **D = 0,30: 41/45 (91 %)**; sin levantamiento: 1-B-1, 1-B-2, 1-B-3 y 1-C-1. D = 0,50: 32/45 (71 %) | **Mía confirmada, la de Wilmer refutada** en D ≥ 0,30 |

**Altura de transición H\*** (donde el ajuste mediano da ρ = 1):
- **≈ 49 m** en W36D, por encima del corpus (máximo 42 m). La dispersión hace que el 17 % ya supere ρ = 1.
- ≈ 103 m en W28C.

**Notas sobre H-A4:**
- La condición "succión neta > 5D" no ocurre en ninguna combinación con D ≥ 0,30 para la correa (área efectiva de 8,3 m²). La tabla se calculó con ese área; las fijaciones (área de 1 m² o menos) y los aleros tienen succiones mayores.
- Es demanda: los anclajes siguen **SIN VALIDAR** (#319).

## Lectura física

1. **La competencia sismo–viento la gobierna la altura, como proponía Wilmer.** ρ crece aproximadamente con H^0,9: el sismo de diseño crece poco con H (T largo, rama descendente) y el viento crece con el área expuesta y Kz.
2. **La velocidad sí importa:** pasar de W28C a W36D duplica ρ. La transición depende de V y de la exposición, no solo de la masa y de R.
3. **Deriva:**
   - En pórticos, el máximo de la deriva de viento está abajo, donde el cortante acumulado es mayor. No está en el tercio superior.
   - Con V = 36 m/s en exposición D, un tercio de los edificios de periodo largo tiene la deriva de viento en servicio más exigida que la sísmica, con el criterio declarado h/400.
   - El uso máximo de viento es 1,19: un edificio excede h/400 y ninguno excede el límite sísmico.

## Limitaciones

- **Gf sin validación independiente**, con β = 0,02 declarado. Un β mayor bajaría Gf y ρ. No se corrió sensibilidad: haría falta prerregistrarla.
- **Sin** los casos torsionales y de carga parcial de la Fig. B.6.5-6. Esos casos aumentarían la demanda en columnas de esquina.
- **T_modelo** sale de inercias fisuradas (0,70 Ig y 0,35 Ig). Un T más corto con inercias brutas daría un G menor.
- **Deriva de viento:** se mide en el centro del diafragma, con el criterio h/400, que NO es NSR-10.
- **Secciones fijas del corpus:** "deja de cumplir" significa que hace falta redimensionar. No se evaluó el costo de una sección mayor.
- **Corpus:** solo pórticos DMI con losa, de planta regular y en zona baja.

## Consecuencias

- **El viento pasa a ser obligatorio por defecto** en el diseño 3D de edificios de zona baja con h > 20 m. Con h ≤ 18 m sigue siendo opcional (#292-W). Para hacerlo bien falta V por municipio o por región, que va en un issue aparte. Mientras tanto, la memoria debe advertir cuando h > 20 m, zona baja y viento = None.
- Este cambio de comportamiento no se hace sin la aprobación de Wilmer.
