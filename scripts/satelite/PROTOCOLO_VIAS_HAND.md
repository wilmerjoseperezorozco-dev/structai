# Protocolo C1: exposición de la red vial principal a terreno bajo (HAND), Caribe (preregistrado 2026-11-08, antes de calcular ninguna cifra)

**Pregunta.** ¿La red vial principal (troncales, primarias y secundarias) está sobre terreno bajo respecto al cauce más que el territorio en general? Y, descriptivamente, ¿cuántos puentes hay en esa red y cuántos cruzan cauces grandes?

**Qué NO se puede hacer, y por qué.** La tabla de emergencias de la UNGRD que usamos (`ungrd_emergencias`) trae evento, personas, familias, viviendas y hectáreas, pero no daños a vías ni a puentes. Por eso esta hipótesis **no se valida contra daños**: mide exposición, no daño, y no dice que un puente vaya a fallar.

**Datos.** (1) OpenStreetMap vía Overpass (marca de tiempo de la base que se registrará en el resultado): ways con `highway` ∈ {trunk, primary, secondary} y sus puentes (`bridge=yes`) en los siete departamentos del Caribe continental ya procesados (08, 13, 20, 23, 44, 47, 70). (2) HAND con la misma tubería de `calcular_hand_caribe.py` (Copernicus DEM ~90 m, red de 5 km²), recalculado por departamento para muestrear en líneas y puntos. (3) Polígonos municipales IGAC.

**Definiciones (fijadas ahora).**
- *Exposición vial de un municipio* = fracción de la longitud de vía (sin contar segmentos marcados como puente) cuyos puntos, muestreados cada ≈ 90 m, tienen HAND < 10 m.
- *Exposición del territorio* = fracción de las celdas del municipio con HAND < 10 m (la misma de `hand_caribe.json`).
- Solo municipios con al menos 5 km de vía principal y 30 celdas válidas.
- Un puente «cruza un cauce grande» si su celda cae en una red de ≥ 25 km² aguas arriba.

**Hipótesis.**
- **C1a (confirmatoria, única).** La mediana, entre municipios, de (exposición vial − exposición del territorio) es mayor que 0. IC95 % por remuestreo de **departamentos** (7 bloques); se cumple si el límite inferior supera 0.
- **C1a′ (sensibilidad).** Lo mismo excluyendo municipios con exposición del territorio > 90 % (en llanuras de inundación casi todo es HAND < 10 m y el techo impide ver diferencias).
- **C1b (descriptiva, sin contraste).** Puentes por 100 km de vía principal, por departamento, y fracción de puentes sobre cauces ≥ 25 km².

**Límites declarados de antemano.** HAND de 90 m promediada no resuelve diques ni terraplenes: una vía elevada puede estar protegida aunque su celda tenga HAND bajo. HAND < 10 m es una condición de terreno, no una probabilidad de inundación. OpenStreetMap es voluntario: la cobertura y el etiquetado de puentes varían. Los puentes están sobre cauces por construcción, por eso no se comparan con el territorio. Exposición no es vulnerabilidad: no se evalúa el estado de ninguna estructura ni se nombra ninguna.
