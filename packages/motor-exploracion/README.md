# motor-exploracion (#273)

Pre-diseño del estudio geotécnico: antes de contratar el estudio de suelos, dice qué explorar y qué medir, con su evidencia.

| Salida | Qué es | Fuente |
|---|---|---|
| `categoria` | Categoría de la unidad de construcción: la más desfavorable entre la de niveles y la de carga | NSR-10 H.3.1.1, Tabla H.3.1-1 |
| `exploracion_minima` | Número mínimo de sondeos y profundidad | Tabla H.3.2-1 y H.3.2.5, con Δσ = 10 % por Boussinesq (`motor-geotecnia`) |
| `nivel_freatico` | Alarma de nivel somero: solo con el punto del lote y en llanura de Hammond | H2, H2b, H2c y H8 de #273, validados en la Orinoquía |
| `recomendaciones` | Piezómetro, prueba de carga estática, licuación y estabilidad de taludes | H1 y H7 de #273; NSR-10 H.4.7.3, H.10.2.1 y A.2.4 |

**Privacidad:**
- El motor **no recibe coordenadas**. Solo recibe métricas de terreno ya calculadas: relieve a 1 km, pendiente y relieve a 5 km, y eventos de remoción en masa a 5 km.
- Con `ubicacion="municipio"` rechaza esas métricas, porque serían de la cabecera (H8).

**Fuera de lo validado** la salida dice "no aplica" o "sin dato". No hay valores por defecto: una entrada inválida falla.

**Pendiente:**
- Criterios adicionales de H.3.2.5 que no están transcritos en el corpus.
- Socavación (H3).
- Exposición en la API.

```powershell
python -m pytest packages/motor-exploracion/tests -q
```
