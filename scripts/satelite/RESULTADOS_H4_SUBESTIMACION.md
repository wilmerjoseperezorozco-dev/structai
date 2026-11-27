# Resultados H4 (#273): consulta de remoción en masa por cabecera municipal frente a consulta por GPS (2026-11-18)

- **Protocolo:** `PROTOCOLO_ANALISIS.md` §29, publicado en [#273](https://github.com/wilmerjoseperezorozco-dev/structai/issues/273#issuecomment-6994786089) antes de contar SIMMA en la malla.
- **Código:** `h4_subestimacion_remocion.py`, sin cambios después del prerregistro. **Salida:** `h4_subestimacion_resultados.json`.
- **Muestra:** 1.000 municipios de 21 departamentos, 129.603 nodos de 2 km; 885 municipios con SIMMA a ≤ 15 km de la malla o de la cabecera.
- **Intervalos:** IC95 % por bootstrap por departamento, 2.000 réplicas.

## Veredictos (radio de 15 km)

| Medida | Valor | IC95 % | Veredicto |
|---|---|---|---|
| **C1:** mediana del CV intramunicipal | **0,49** | [0,42; 0,63] | **HETEROGÉNEO** (umbral 0,30) |
| **C2 (principal):** fracción del área subestimada (≥ 2× la cabecera) | **9,7 %** | [7,1 %; 12,3 %] | **NO CONCLUYENTE** (entre 5 % y 10 %) |

- **La cabecera no representa a su municipio.** El conteo SIMMA que ve un sitio cambia típicamente un 49 % según dónde caiga dentro del mismo municipio; en el 10 % de los municipios más heterogéneos, el CV pasa de 1,8.
- **Pero el error dominante no es subestimar, es sobreestimar.** El 30 % del área tiene a lo sumo la mitad de los eventos que la cabecera, frente al 10 % que tiene el doble o más. Es coherente con el sesgo de acceso de SIMMA: se inventaría más cerca de los cascos urbanos y las vías.
- **Donde la cabecera dice "cero", el municipio no está limpio:** los 104 municipios con cero SIMMA a 15 km de la cabecera tienen SIMMA en parte de su territorio, y en 42 de ellos al menos el 10 % del área tiene 2 o más eventos.

## S1: frente al historial de emergencias UNGRD (movimiento en masa 2019-2024)

| Consulta | ρ de Spearman (15 km) | ρ (5 km) |
|---|---|---|
| Cabecera | 0,48 [0,30; 0,67] | 0,41 [0,28; 0,58] |
| Media de la malla | 0,48 [0,30; 0,67] | 0,48 [0,33; 0,66] |
| Máximo de la malla | 0,49 [0,33; 0,67] | 0,50 [0,35; 0,65] |
| **Diferencia media − cabecera** | **+0,005** [−0,018; +0,022] | **+0,069** [+0,025; +0,108] |

- A 15 km el radio es tan amplio que cabecera y malla dicen casi lo mismo sobre el historial municipal.
- A 5 km la malla se asocia mejor que la cabecera con los eventos UNGRD (IC que no cruza 0). Es un resultado de sensibilidad, no el principal, y en parte es por construcción (los dos lados son agregados municipales).
- ρ(CV, UNGRD) = −0,19: los municipios con más emergencias reportadas tienen inventario más parejo (más eventos repartidos).

## Sensibilidad a 5 km

- C1: mediana del CV 1,38 [1,25; 1,59], HETEROGÉNEO.
- C2: 6,8 % [5,3 %; 8,3 %], NO CONCLUYENTE. Sobreestimado: 38 %.
- 250 municipios tienen cero SIMMA a 5 km de la cabecera, todos con SIMMA en parte del territorio.

## Descriptivo

| Grupo | Mediana CV (15 km) | Fracción subestimada |
|---|---|---|
| Andina (628) | 0,41 | 10,3 % |
| Caribe (195) | 1,37 | 12,1 % |
| Pacífica (148) | 0,46 | 8,7 % |
| Orinoquía (29) | 1,74 | 2,8 % |
| Pendiente baja / media / alta (tercil p90) | 0,78 / 0,41 / 0,42 | 8,1 % / 12,2 % / 8,8 % |

Municipios con mayor fracción del área subestimada (15 km): Marulanda (84 %, cabecera 2 vs máximo 16), Suárez (Tolima), Mariquita, Anzá, Santa Helena del Opón, Pulí, La Gloria, Pacho, Natagaima y Nilo (74-83 %).

## Lectura (fijada de antemano)

- **Qué muestra:** la consulta por cabecera iguala lotes del mismo municipio que tienen contextos de ladera muy distintos. El error va en los dos sentidos y es mayor hacia la **sobreestimación** (30 % del área) que hacia la subestimación (10 %). El argumento a favor del GPS no es "la cabecera subestima", sino "**la cabecera no es el sitio**": en uno de cada tres lotes exagera el inventario cercano y en uno de cada diez lo minimiza.
- **Qué no muestra:** que el GPS prediga mejor los eventos futuros. SIMMA no tiene fecha y no hay prueba temporal.
- **Hipótesis tal como se formuló** ("la cabecera subestima"): **no confirmada** en el umbral prerregistrado del 10 %; el estimado (9,7 %) queda justo debajo y el IC lo cruza.
- **Para StructAI:** `/sitio` ya consulta SIMMA por la coordenada redondeada (radio de 15 km). Este resultado respalda mantenerlo así y mostrar el conteo como "inventario cercano al punto", con el aviso de sesgo de acceso, no como amenaza.

## Limitaciones

- SIMMA tiene sesgo de acceso y de cartografía; parte de la "sobreestimación" de la cabecera es justamente ese sesgo.
- El radio de 15 km suaviza; los nodos cerca del borde cuentan eventos del municipio vecino.
- La malla pesa igual zonas habitadas y despobladas.
- S1 es municipal (falacia ecológica) y en parte coincide por construcción.
- Los umbrales 0,30 y 10 % son arbitrarios.
