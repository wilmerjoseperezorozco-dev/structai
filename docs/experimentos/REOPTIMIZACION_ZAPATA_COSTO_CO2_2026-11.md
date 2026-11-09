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

## Actualización: durabilidad NSR-10 C.4 y tope de ceniza (2026-11-08)
Se ingestaron las tablas C.4.2.1, C.4.3.1, C.4.4.1, C.4.4.2 y C.4.5.1 (el corpus solo las citaba por nombre) y se aplicaron como restricciones. `a/mc` = agua / total de materiales cementantes (C.4.1.1).
**Hallazgo normativo:** la NSR-10 no fija tope de ceniza volante fuera de la clase F3 (25 %, congelamiento y deshielo: no aplica en Colombia). Se usa 25 % como tope de diseño **por analogía**, no por exigencia. Lo que sí limita es: costa (C2: a/mc ≤ 0,40, f'c ≥ 35 MPa) y sulfato/agua marina (S1: cemento tipo II/IP(MS)/MS; añadir ceniza exige ensayo C.4.5.1).

Datos: `reoptimizacion_zapata_durabilidad_2026-11.json` (medianas de 15 casos; línea base = prisma de mínimo costo sin ceniza, con la misma exposición).

| Escenario | Solo geometría (costo) | Mezcla sola (CO₂) | Geometría + mezcla: CO₂ / costo |
|---|---|---|---|
| Interior (C1, S0): a/mc ≤ 0,50, f'c ≥ 17, ceniza ≤ 25 % | −18,1 % | −21,0 % (+8,3 % costo) | −37,0 % / −26,9 % |
| Costa C2+S1, sin ensayo de sulfatos (ceniza = 0) | −11,3 % | 0 % | −10,5 % / −11,3 % |
| Costa C2+S1, con ensayo C.4.5.1 (ceniza ≤ 25 %) | −11,3 % | −10,4 % | −19,7 % / −10,5 % |
| Sin C.4 ni tope (corrida anterior) | −23,6 % | −12,6 % | −32,9 % / −22,8 % |

Lectura: en costa el ahorro de CO₂ cae de 33 % a 10–20 % porque C2 obliga a f'c ≥ 35 MPa (más cemento) y S1 impide la ceniza sin un ensayo de 6 meses. El óptimo ya es interior respecto a la ceniza solo en interior (25 %, el tope); en costa con ensayo también topa en 25 %: **el tope sigue siendo el que manda, no el óptimo**.
Notas: (1) con el modelo de Abrams, el 21 MPa sin ceniza da a/mc = 0,508, apenas sobre 0,50: es un artefacto del modelo sin calibrar, pero explica por qué en interior la línea base sube de f'c. (2) C.7.7.6 (recubrimiento para C2) y el cemento tipo II/MS no se verificaron en el costo; el recubrimiento extra de C2 aumentaría concreto y acero. (3) Retrieval de las tablas: la consulta con el numeral las devuelve, pero C.4.4.2 queda detrás de un fragmento viejo `C_4_4_1-sub3`.
