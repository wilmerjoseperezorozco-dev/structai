# Validación con la CYCU pile load test database (#118)

- **Prerregistro:** [#118, comentario 6975967154](https://github.com/wilmerjoseperezorozco-dev/structai/issues/118#issuecomment-6975967154).
- **Código:** script `validacion/cycu_2025.py` (commit `73020ef`) y motor en el commit `fc0b8a1`, sin cambios.
- **Datos:** Chen et al. (2025), *CYCU pile load test database*, Mendeley Data V1, doi:10.17632/x6c63j8bv8.1, licencia CC BY 4.0.

## Resultado principal: el motor es CONSERVADOR en arcilla

| Grupo | n | Sitios | λ (media geométrica) | IC95 (bootstrap por sitio) | COV de λ | Veredicto |
|---|---|---|---|---|---|---|
| Todas | 71 | 36 | **1,48** | [1,24; 1,78] | 0,58 | CONSERVADOR |
| Excavadas (L2) | 45 | 18 | 1,58 | [1,24; 2,06] | 0,61 | CONSERVADOR |
| Hincadas (Davisson) | 26 | 18 | 1,31 | [1,07; 1,56] | 0,43 | CONSERVADOR |

- **Definición:** λ = capacidad medida / capacidad última del motor, con fricción α·Su de la NSR-10 H.4.7-3 y punta 9·Su.
- **Exclusiones** (reglas prerregistradas):
  - 183 filas no son arcilla y 22 no tienen Su;
  - 17 no tienen capacidad interpretada, porque la prueba no llegó a la falla (">X");
  - 2 tienen la capacidad extrapolada por encima de Qmax.
- **Cuantiles de λ:** p10 0,75, p50 1,45 y p90 3,08.
- **El motor sobreestima (λ < 1) en el 20 % de las pruebas.**

## Secundarios

- **H2 (exploratoria): ¿las excavadas quedan más subestimadas que las hincadas?**
  - La diferencia de ln λ es 0,19, con IC95 [−0,13; 0,51].
  - **No es concluyente**: va en la misma dirección que El Dorado, pero el intervalo contiene 0.
- **Sensibilidad al criterio de falla:** con Terzaghi y Peck (n = 64), λ = 1,52. La conclusión no depende del criterio.
- **Pruebas sin falla (post hoc, no prerregistrado):**
  - En las 19 excluidas, la cota inferior de λ (carga máxima o ">X" sobre el predicho) tiene media geométrica 1,81.
  - Solo el 5 % de esas cotas queda bajo 1.
  - Excluirlas hace que el motor parezca **menos** conservador de lo que es, así que el veredicto se sostiene.

## Lectura

1. **Coincide con El Dorado** (λ = 1,39 con n = 5). El método α de la NSR-10, con Su representativo y punta 9·Su, subestima de forma sistemática la capacidad última en arcilla.
2. **Conservador no es lo mismo que preciso.**
   - Con COV de 0,58, una de cada cinco pruebas queda por debajo de lo que predice el motor, y el 10 % queda por debajo de 0,75.
   - Con los factores de seguridad de la NSR-10 (1,80 en fricción y 3,0 en punta), un λ de 0,75 todavía deja un margen real de alrededor de 1,35 o más. Eso es menor que el nominal, pero sigue siendo mayor que 1.
   - Este razonamiento sobre el margen es una cuenta de orden de magnitud, no un análisis de confiabilidad.
3. **Lo que no se puede decir con estos datos:** de dónde viene el sesgo.
   - Puede venir de la ecuación α, del Su representativo de la base (sin método declarado) o de los criterios de falla.
   - Separarlo requiere datos con perfiles de Su por estrato.

## Lo que no se hace

No se recalibra α con estos datos. Una versión 2 tendría que validarse con datos distintos de estos 71, porque ya se usaron para evaluar. Las opciones a probar son:
- el α del CCP-14 §10.7.3.8.6b / §10.8.3.5.1b;
- Su creciente con la profundidad.

El motor no queda "medido a producción": eso requiere las 4 condiciones de `docs/REGLAS_MOTORES_DE_CALCULO.md`.

## Limitaciones

- Solo arcilla. Arena queda pendiente de Nordlund/Thurman y SPT del CCP-14.
- Cada prueba trae un estrato representativo, y la base no declara cómo se obtuvo Su.
- Falta la fecha del ensayo después de la instalación, así que no se controla la ganancia de capacidad con el tiempo.
- 36 sitios: el bootstrap por sitio da intervalos honestos, pero anchos.
