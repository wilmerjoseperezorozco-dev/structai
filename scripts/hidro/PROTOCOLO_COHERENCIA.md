# Protocolo: coherencia espacio-temporal de las anomalías de caudal (tercer orden)

Preregistrado el 2026-11-07, antes de calcular. Datos: caudales mensuales IDEAM en caché (`_cache/caudal_historico.pkl`, 352.022 registros), estaciones con ≥ 240 meses, región y coordenadas de `ideam_estaciones_caudal`. Descriptivo: la climatología usa todo el registro, no se predice nada.

**Pregunta.** Una anomalía de tercer orden no es el z de una estación, sino una desviación coherente en el espacio y el tiempo. ¿Cuán sincronizadas están las anomalías de caudal entre estaciones, cuánto alcanza esa dependencia en distancia y depende de la fase de ENSO?

**Definiciones.**
- z mensual robusto por estación y mes calendario: (ln Q − mediana) / (1,4826·MAD), con piso de escala 0,05. Anomalía alta: z ≥ 2; baja: z ≤ −2.
- Regiones naturales como en el §23 (Caribe, Andina, Pacífica, Orinoquía, Amazonía); se analizan las que tengan ≥ 8 estaciones. Un mes-región entra si reportan ≥ 8 estaciones.

**C1 — sincronía (confirmatoria, Holm sobre las regiones).** Para el mes t y la región r, K = número de estaciones en anomalía alta; p_s = frecuencia empírica de la estación. Razón de varianzas VR = Σ(K − Σp_s)² / Σ Σp_s(1 − p_s). VR = 1 bajo independencia. Se prueba VR > 1 con un nulo de permutación (cada estación se baraja entre años dentro del mismo mes calendario, 500 permutaciones, lo que conserva su estacionalidad y destruye el alineamiento entre estaciones) y un IC95 % por bootstrap de bloques móviles de 12 meses.

**C2 — dependencia de ENSO (confirmatoria, Holm sobre las regiones).** Fracción media mensual de estaciones en anomalía alta, La Niña (ONI ≤ −0,5) menos neutral (|ONI| < 0,5); signo esperado positivo. IC95 % por bootstrap de bloques de 12 meses. Exploratoria y rotulada: anomalía baja, El Niño menos neutral.

**C3 — alcance espacial (descriptiva).** Correlación de los z mensuales entre pares de estaciones con ≥ 120 meses comunes, mediana por rangos de distancia (km, haversine): 0-50, 50-100, 100-200, 200-400, 400-800 y > 800. Se reporta la distancia a la que la mediana cae por debajo de 0,10 y, por región, la correlación media dentro de la región y el número efectivo de estaciones n/(1 + (n − 1)·ρ̄).

**Límites.** Estaciones con huecos distintos entre sí, mezcla de cuencas con distinto tamaño y régimen, y una climatología de todo el registro que absorbe parte de la tendencia. No se infiere causalidad ni se pronostica.
