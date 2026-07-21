# motor-estructural — wired en main.py (2026-07-21)

Ya conectado: import + registro en `/health` + `app.include_router` en
`apps/api/main.py`, mismo patrón que los demás motores (try/except +
`_AVAILABLE` flag). Verificado end-to-end vía `TestClient` (no solo
import) contra los dos endpoints, con resultados idénticos a los del
prototipo standalone.

## Endpoints disponibles

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/estructural/salud` | Health check del motor |
| POST | `/estructural/analizar-nudo` | IFC upload → PINN → NSR-10 chequeo nudo |
| POST | `/estructural/inspeccion-estribos` | Imagen → separación real → NSR-10 C.21.4.4 |

## Ejemplo curl — analizar-nudo

```bash
curl -X POST http://localhost:8000/estructural/analizar-nudo \
  -F "ifc_file=@nudo_test.ifc" \
  -F "guid_viga=<GUID_VIGA>" \
  -F "guid_columna=<GUID_COLUMNA>" \
  -F "fc=28" -F "fy=420" -F "b=300" -F "h=300" -F "d=265" \
  -F "Av=56.5" -F "s=75" -F "num_pisos=3"
```

## Ejemplo curl — inspeccion-estribos

```bash
curl -X POST http://localhost:8000/estructural/inspeccion-estribos \
  -F "imagen=@foto_obra.jpg" \
  -F "posiciones_y_csv=60,130,200,280,390,460" \
  -F "s_max_diseno_mm=75" \
  -F "escala_mm_por_px=1.0"
```
