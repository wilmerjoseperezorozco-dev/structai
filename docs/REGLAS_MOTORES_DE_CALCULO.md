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

## Hoja de ruta en issues (9 de noviembre de 2026)

Transversales: [#130](https://github.com/wilmerjoseperezorozco-dev/structai/issues/130) Fase 3 (contrato y API) · [#131](https://github.com/wilmerjoseperezorozco-dev/structai/issues/131) gobernanza de sustitutos de aprendizaje · [#132](https://github.com/wilmerjoseperezorozco-dev/structai/issues/132) kit de verificación independiente · [#133](https://github.com/wilmerjoseperezorozco-dev/structai/issues/133) fail-fast residual · [#147](https://github.com/wilmerjoseperezorozco-dev/structai/issues/147) pruebas de plataforma y paquete geoespacial · [#148](https://github.com/wilmerjoseperezorozco-dev/structai/issues/148) resiliencia de datos externos.

Datos y motores nuevos: [#134](https://github.com/wilmerjoseperezorozco-dev/structai/issues/134) IDF oficiales · [#135](https://github.com/wilmerjoseperezorozco-dev/structai/issues/135) sísmica municipal · [#136](https://github.com/wilmerjoseperezorozco-dev/structai/issues/136) asentamientos y consolidación · [#137](https://github.com/wilmerjoseperezorozco-dev/structai/issues/137) licuación · [#138](https://github.com/wilmerjoseperezorozco-dev/structai/issues/138) redes hidráulicas · [#139](https://github.com/wilmerjoseperezorozco-dev/structai/issues/139) alcantarillado y drenaje · [#140](https://github.com/wilmerjoseperezorozco-dev/structai/issues/140) puentes · [#141](https://github.com/wilmerjoseperezorozco-dev/structai/issues/141) acero, mampostería y madera · [#142](https://github.com/wilmerjoseperezorozco-dev/structai/issues/142) análisis modal 3D · [#143](https://github.com/wilmerjoseperezorozco-dev/structai/issues/143) eléctrica · [#144](https://github.com/wilmerjoseperezorozco-dev/structai/issues/144) minería e industrial · [#145](https://github.com/wilmerjoseperezorozco-dev/structai/issues/145) logística · [#146](https://github.com/wilmerjoseperezorozco-dev/structai/issues/146) impermeabilización.

Ya existentes: #118 pilotes, #119 muros de corte, #120 nudos y ménsulas, #121 cerchas, #122 escaleras y losas, #123 gaviones y suelo reforzado, #81 acero formado en frío, #44 LSTM de caudal, #124–#128 refuerzo.

## Orden de ejecución elegido

1. #133 y #132 (cierran la Fase 1 y dan el marco de verificación).
2. #130 en el orden motor-concreto → orquestador → análisis y deformación → resto.
3. #131 antes de exponer cualquier sustituto de aprendizaje.
4. #134 y #135 (datos que hoy dejan resultados no dimensionables o de resolución gruesa).
5. Motores nuevos por impacto en seguridad: #136, #137, #138, #142, luego #139, #140, #141, y por último #143–#146.
