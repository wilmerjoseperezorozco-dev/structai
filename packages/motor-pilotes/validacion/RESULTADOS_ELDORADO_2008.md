# Prueba de realidad: El Dorado, Bogotá (#118)

- **Prerregistro:** [#118, comentario 6975779859](https://github.com/wilmerjoseperezorozco-dev/structai/issues/118#issuecomment-6975779859), publicado antes de correr el motor con estos datos.
- **Motor:** `motor-pilotes`, commit `fc0b8a1`.
- **Script:** `validacion/eldorado_2008.py`.
- **Fuente:** Rodríguez, J. A., «Optimización de cimentaciones», 5.º Encuentro de Suelos y Estructuras, Escuela Colombiana de Ingeniería. Ensayos PDA/CAPWAP de GRL y Jeoprobe, 2008.

## Resultado: NO PASA el criterio prerregistrado (1/5 en banda; se pedía ≥ 4/5)

| Pilote | Medido (kN) | Banda motor bajo–alto (kN) | Central (kN) | λ total | λ fricción | ¿En banda? |
|---|---|---|---|---|---|---|
| Preexcavado 1 | 1884 | 1040–1652 | 1389 | 1.36 | 1.35 | no |
| Preexcavado 2 este | 2080 | 1040–1652 | 1389 | 1.50 | 1.37 | no |
| Preexcavado 3 | 3021 | 1258–1976 | 1670 | 1.81 | 1.63 | no |
| Hincado 1 | 1295 | 808–1260 | 1069 | 1.21 | 1.18 | no |
| Hincado 2 | 1256 | 808–1260 | 1069 | 1.17 | 1.12 | sí |

- Media geométrica de λ total en el escenario central: **1,39**.
- Por tipo, λ total:
  - preexcavados: 1,36, 1,50 y 1,81;
  - hincados: 1,21 y 1,17.

## Lectura (descriptiva, n = 5)

1. **El motor queda del lado conservador en los 5 pilotes:** predice menos de lo medido. Con el factor de seguridad, el margen real sería mayor que el nominal. No es un error del lado inseguro, pero sí una subestimación sistemática.
2. **El escenario "alto" de Su (20/40 kPa) tampoco alcanza** a los preexcavados. El artículo ya advierte que el Su de los ensayos UU está bajo por remoldeo, y los autores lo corrigieron con estado crítico (solo en figura, no digitalizada). Lo más probable es que el déficit venga del **dato de entrada (Su)** y no de la ecuación α. Con estos datos no se puede separar una cosa de la otra.
3. **El Su constante bajo 10 m no reproduce el aumento con la profundidad.**
   - El preexcavado 3 mide 6 m más que el 1 y lleva 1.137 kN más.
   - El motor solo suma unos 280 kN por esos 6 m.
   - La fricción medida implica un τ promedio que crece con la profundidad, consistente con un Su que aumenta por confinamiento (como dice el artículo).
4. **Punta:** el motor da 76 kN en los preexcavados con 9·Su, contra 118–432 kN medidos. La punta pesa poco en el total (6–14 %), pero también queda baja.
5. **Hincados contra preexcavados:** los hincados quedan más cerca de lo medido (λ ≈ 1,2), aunque llevan ganancia de capacidad con el tiempo (16 días). Los preexcavados quedan más lejos (λ ≈ 1,4–1,8). No se corrige nada con n = 5.

## Lo que no se hace

No se cambian los escenarios, las longitudes, la muestra ni el criterio. No se recalibra α con estos 5 pilotes.

Cualquier ajuste sería una versión nueva, con su propio prerregistro y validada con otros datos. Por ejemplo:
- Su creciente con la profundidad;
- el perfil de estado crítico, si se consigue digitalizado;
- el método α del CCP-14 §10.8.3.5.1b para pozos perforados.

## Limitaciones

- n = 5, así que no hay sesgo con intervalo de confianza.
- La capacidad medida es de ensayo dinámico (CAPWAP), no de carga estática.
- El Su sale de una descripción textual de rangos.
- La fuente no publica el perfil de Su usado por los autores.
