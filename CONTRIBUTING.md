# Convenciones de este repositorio

Documento vivo — refleja cómo se trabaja realmente en `construdata`/StructAI, no un ideal aspiracional. Si algo aquí deja de ser cierto, se corrige aquí primero.

## Commits

Formato: `tipo(scope): descripción corta en imperativo`.

Tipos en uso: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`.

**Scope** (recomendado para cambios de código, opcional para ingesta de contenido normativo):
- `web` — `apps/web`
- `api` — `apps/api`
- `apu`, `deform`, `aquai`, `geopot`, `vias`, `gerencia` — el motor correspondiente en `packages/motor-*`
- `infra` — `infra/`, CI/CD, configuración de deploy

Ejemplos reales de este repo:
```
fix(api): soportar HS256 legacy y ES256/JWKS en la verificación de JWT
feat(web): flujo de recuperación de contraseña
feat: cargar Titulo G real de NSR-10 (Estructuras de Madera y Guadua)
```

El último ejemplo (sin scope) es válido para commits de ingesta de contenido normativo que no pertenecen a un solo motor — no forzar un scope donde no hay uno claro.

## Paquetes Python (`packages/motor-*`)

Cada motor tiene su propio `pyproject.toml` (build backend `hatchling`) con las dependencias reales que importa su código — no una lista genérica copiada entre paquetes. Antes de agregar una dependencia nueva a un motor, verificar que efectivamente se importa en `src/`.

**El `pyproject.toml` es metadata de packaging, no un install editable funcional todavía**: los tests y el propio código de cada motor importan con `from src.X import Y` (no `from motor_apu.X import Y`), y hatchling no puede construir un wheel de `src/` sin config adicional (`[tool.hatch.build.targets.wheel]`) que además colisionaría entre motores si se instalan varios a la vez en el mismo entorno (todos declararían un paquete `src`). `pip install -e ".[dev]"` falla tal como está hoy — no lo intentes hasta que se agregue esa config.

Instalación real que funciona (deps directas, sin editable install):
```bash
cd packages/motor-<nombre>
pip install numpy scipy pydantic  # según lo que declare el pyproject.toml del motor
pytest tests/ --cov=src --cov-report=term-missing -v
```

## Cobertura real medida (`pytest --cov`, no estimada)

| Motor | Cobertura | Tests | Última medición |
|---|---|---|---|
| `motor-deformacion` | 93% | 40 pasan | 2026-07-19 |
| `motor-apu` | 75% | 6 pasan | 2026-07-19 |
| `motor-aquai` | 70% total (**91.5%** excluyendo `pdf_memoria.py` y `rag_normativo.py`, sin tests propios) | 35 pasan | 2026-07-19 |
| `motor-geopot` | — | `tests/` **vacío** — 0 tests | 2026-07-19 |
| `motor-vias` | — | `tests/` **vacío** — 0 tests | 2026-07-19 |
| `motor-gerencia` | — | no existe carpeta `tests/` | 2026-07-19 |

`motor-aquai` pasó de 0% a 70% real (2026-07-19) escribiendo `tests/test_motor_aquai.py` — 35 tests que recalculan el valor esperado con la misma fórmula documentada en el módulo (o contra las tablas normativas de `ras2000_tablas.py`), no con números supuestos. `pdf_memoria.py` (generación de PDF, 0%) y `rag_normativo.py` (módulo desconectado del flujo real, 0%) se dejaron deliberadamente sin cubrir — no aportan valor de regresión de cálculo normativo.

No hay un target de 80% fijado todavía porque solo 3 de 6 motores tienen tests reales corriendo — fijar un número ahora sería aspiracional, no una medición. Escribir tests para geopot/vias/gerencia es el trabajo pendiente real antes de prometer cualquier cobertura, no un ajuste de configuración.

## Qué NO se ha estandarizado todavía (a propósito)

- **Formato de respuesta de API** (`{ data, error?, metadata? }`): no está aplicado todavía en los routers de `apps/api` — cambiarlo requiere tocar `apps/web` en el mismo commit porque los clientes ya parsean la forma actual de cada endpoint. Pendiente, no urgente.
- **Versionado de rutas** (`/api/v1/`): las rutas actuales no están versionadas. No se adopta sin una razón concreta (aún no hay clientes externos de la API que necesiten esa garantía de compatibilidad).
