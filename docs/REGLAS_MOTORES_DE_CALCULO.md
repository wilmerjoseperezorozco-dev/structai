# Reglas obligatorias para los motores de cálculo

Vigente desde el 9 de noviembre de 2026. Aplica a los 12 motores existentes y a todo motor nuevo. Origen: los seis pilares de `motor-concreto`, elevados a regla, más las reglas de la Fase 1 de la auditoría técnica ([AUDITORIA_TECNICA_MOTORES_2026-11-09.md](AUDITORIA_TECNICA_MOTORES_2026-11-09.md)).

## Reglas

1. **Fallo explícito.** Prohibido `.get(clave, valor_por_defecto)` y cualquier sustitución silenciosa en parámetros físicos, materiales, zonas sísmicas, espesores o coeficientes normativos. Un dato ausente o fuera de dominio lanza `ValueError` que cita la norma (NSR-10, INVIAS, RAS 2000). Utilidad: `contrato_motor.exigir`.
2. **Contrato de salida uniforme.** Toda función pública devuelve `contrato_motor.ResultadoMotor`: `valor`, `unidad_si`, `ecuacion`, `referencia_normativa`, `supuestos`, `en_borde_dominio` (obligatorio, sin valor por defecto) y `aviso_responsabilidad_profesional` (no puede quedar vacío).
3. **Solvers críticos sin código artesanal.** Raíces, optimización y álgebra lineal con `scipy`/`numpy` (brentq, HiGHS, `linalg.solve`), nunca iteraciones con paso fijo. Un solver que no converge lanza error; no devuelve el último valor.
4. **Densidad y calidad de pruebas.** Cada corrección entra con la prueba que demuestra el fallo previo (rojo) y luego el parche (verde). Al menos tres casos con respuesta independiente (solución cerrada o fuente externa) por motor. Una prueba que consagra un fallback es un defecto de la prueba.
5. **Limitaciones y borde de dominio declarados.** Toda salida informa `en_borde_dominio=True` cuando un parámetro toca el límite de validez física o normativa o cuando el resultado depende de una cota de búsqueda.
6. **Optimización real.** Las búsquedas en tablas estáticas se reemplazan por optimización continua o entera sujeta a restricciones normativas explícitas, siempre que la norma admita valores continuos.
7. **Doble ronda de enmienda y revisión adversaria.** Antes de dar por terminado un motor: pruebas de monotonicidad (más carga ⇒ más sección o acero) y de homogeneidad dimensional, y una revisión adversaria independiente.

## Estado por motor (9 de noviembre de 2026)

| Motor | Regla 1 | Regla 2 | Pendiente principal |
|---|---|---|---|
| motor-aquai | Corregido (material, IDF, TR) | No | Contrato en funciones públicas; IDF oficiales |
| motor-geopot | Corregido (zona sísmica, 2 sitios) | No | Constructores con zona por defecto `"ALTA"`; sísmica municipal |
| motor-vias | Corregido (ancho de carril) | No | Drenaje "bueno" asumido en el diseño asfáltico; `.get(edad, 0.0)` en NTC 121 (falla conservadora, sin mensaje de "no ensayado") |
| motor-topovia | Corregido (AASHTO-93) | Parcial: `sn_flexible_con_contrato` | Resto de funciones públicas |
| motor-concreto, motor-analisis, motor-deformacion, motor-estructural, motor-apu, motor-gerencia, motor-vulnerabilidad-vivienda, motor-acero-frio | Sin hallazgos de `.get` numérico en el barrido; resto no auditado | No | Contrato; pruebas de monotonicidad y dimensional |

El contrato vive en `packages/contrato-motor`. La adopción completa en las funciones públicas de los 12 motores es la Fase 3 y no está hecha.
