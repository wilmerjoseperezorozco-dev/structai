# Re-optimización de zapata por costo y CO₂ con dosificación variable (2026-11-08)

Reproducir: `python scripts/experimentos/reoptimizar_zapata_costo_co2.py` → `reoptimizacion_zapata_costo_co2_2026-11.json`.
Variables: geometría (prisma / troncopiramidal), f'c ∈ {21, 28, 35} MPa, ceniza volante ∈ {0, 10, 20, 30 %} del ligante. 15 casos (P_serv × q_adm).
Línea base: zapata prismática de mínimo costo, sin ceniza (en los 15 casos resultó f'c = 21).

| Mediana de 15 casos (ceniza 150 COP/kg, cemento 1,010) | Efecto vs línea base |
|---|---|
| Solo geometría (mínimo costo) | −23,6 % costo |
| Solo mezcla (mínimo CO₂, prisma) | −12,6 % CO₂, +1,0 % costo |
| Geometría + mezcla (mínimo CO₂) | −32,9 % CO₂, −22,8 % costo |

Con ceniza a 300 COP/kg la mezcla sola cuesta +3,4 % y la combinación sigue en −21,0 %. Con cemento 0,892 el CO₂ baja 32,6 %. Con carga de 300 kN no hay ganancia geométrica (la mezcla sola da −12,6 % CO₂); a 2500 kN la combinación llega a −42 % CO₂.
En ningún caso hubo conflicto costo–CO₂: el punto de mínimo CO₂ también es más barato que la línea base.

## Límites (obligatorio leer)
- **El óptimo siempre cae en el borde de la rejilla** (f'c = 21, ceniza 30 %): no es un óptimo interior; con más ceniza el modelo seguiría "ahorrando". Hace falta un tope por durabilidad.
- **Modelo de mezcla sin verificar**: Abrams con constantes genéricas, f_cm = f'c + 8,5 MPa, k = 0,4 para ceniza (EN 206), resistencia a 28 d, agua 190 kg/m³. La ceniza retrasa la ganancia de resistencia y el modelo lo ignora.
- **Sin verificación de exposición** (NSR-10 C.4, ambiente marino/costero de Barranquilla): relación a/mc máxima y cemento mínimo no se aplicaron.
- **Precio de la ceniza supuesto** (150 y 300 COP/kg): el APU no la tiene. Precio de 35 MPa extrapolado; 28 MPa es el de vigas.
- Factor de CO₂ de la ceniza (0,015) es secundario; no hay CO₂ de encofrado, transporte ni de la mayor demanda de aditivo.
- Es una hipótesis de investigación con la misma salvedad que la zapata troncopiramidal: la NSR-10 no trata espesor variable.
