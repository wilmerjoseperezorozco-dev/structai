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
| `motor-geopot` | **82%** (`__init__.py` 100%) | 39 pasan | 2026-07-19 |
| `motor-vias` | **88%** | 46 pasan | 2026-07-20 |
| `motor-gerencia` | **96%** | 38 pasan | 2026-07-20 |
| `motor-estructural` | **86%** | 7 pasan | 2026-07-21 |

`motor-aquai` pasó de 0% a 70% real (2026-07-19) escribiendo `tests/test_motor_aquai.py` — 35 tests que recalculan el valor esperado con la misma fórmula documentada en el módulo (o contra las tablas normativas de `ras2000_tablas.py`), no con números supuestos. `pdf_memoria.py` (generación de PDF, 0%) y `rag_normativo.py` (módulo desconectado del flujo real, 0%) se dejaron deliberadamente sin cubrir — no aportan valor de regresión de cálculo normativo.

`motor-geopot` pasó de 0% a 82% real (2026-07-19), mismo patrón, `tests/test_motor_geopot.py` — 39 tests cubriendo sismica.py, lab_suelos.py (USCS/AASHTO/Atterberg/Proctor/CBR/Granulometría), lab_concreto.py y lab_agregados.py, más un bloque final que ejercita directamente `src/__init__.py` (los wrappers que consume `apps/api/routers/geopot.py`), llevándolo a 100%. Dos hallazgos reales al correr los tests por primera vez (no se asumió nada): (1) un rango de plasticidad mal citado en el propio test (18% de IP es "Media plasticidad", no "Alta" — el código estaba bien, el test estaba mal); (2) el demo del propio módulo `lab_concreto.py` (`__main__`, cargas 260/268/255 kN sobre cilindros de 152mm) en realidad da fc≈14-15 MPa, muy por debajo del fc_diseño=21 MPa del mismo demo — no ilustra un caso "conforme" como parecía a primera vista. Se corrigieron ambos tests tras verificar el comportamiento real, no el código.

`motor-vias` pasó de 0% a 88% real (2026-07-20) — es el motor más grande (1814 líneas reales), con 7 verificadores NTC en `ntc_materiales_1.py` y 8 más en `ntc_materiales_2.py` (dos patrones de serialización distintos: dict plano vs. `dataclasses.asdict()`), además de diseño geométrico INVIAS, pavimentos AASHTO-93, mantenimiento y topografía. `tests/test_motor_vias.py`, 46 tests. Un hallazgo real documentado explícitamente en el test (no corregido, solo verificado tal como es): `mantenimiento.py::_determinar_prioridad` compara `prioridad.value < "alto"` como string, no por severidad — "bajo" < "alto" es `False` lexicográficamente, así que un TPD alto nunca sube una prioridad "bajo" directo a "alto", cae a "medio" en su lugar.

`motor-gerencia` pasó de 0% a 96% real (2026-07-20) — no tenía ni carpeta `tests/`. `tests/test_motor_gerencia.py`, 38 tests, todos pasaron en la primera corrida (sin hallazgos que corregir esta vez). Cubre EVM (`models.py::Snapshot`/`Project`, `evm.py`: clasificación de KPIs, score compuesto, tendencia, forecast EAC, resumen cruzado de portafolio) y ML predictivo (`ml_engine.py`: regresión lineal, detección de anomalías por z-score, fecha de término revisada, score de riesgo, forecast de KPIs, correlación de Pearson).

`motor-estructural` (InfraCortex) pasó de 0% a 86% real (2026-07-21) — el motor más reciente, BIM (IFC) → topología del nudo → PINN → chequeo NSR-10 Títulos A/B/C. `tests/test_motor_estructural.py`, 7 tests, valores verificados contra una corrida end-to-end real vía `TestClient` de `/estructural/analizar-nudo` e `/estructural/inspeccion-estribos` antes de escribir las aserciones (no números supuestos). Un bug real encontrado y corregido antes de escribir los tests: `infracortex_core.py::extraer_topologia_nudo` calculaba la matriz de la columna pero nunca la asignaba (llamada sin guardar el resultado) — la función que por nombre extrae la topología del NUDO (viga + columna) en realidad descartaba la columna por completo, retornando solo 2 valores en vez de 3. Sin impacto en el veredicto NSR-10 actual (`chequeo_nsr10_nudo` solo usa propiedades escalares de la sección, no las matrices de rotación), pero sí en el campo `matriz_T12_columna_shape` de la respuesta y en cualquier feature futura que dependa de la rotación real de la columna. Sin cubrir deliberadamente: `MultidisciplinaryPINN` (entrenamiento, no ejercitado en estos tests) y `generar_imagen_anotada` (dibujo/side-effect, sin valor de regresión).

**Con los 7 motores medidos, el piso real hoy es 70% (motor-aquai) y el techo 96% (motor-gerencia)** — se fija **75% como target mínimo por motor** (por debajo del promedio real, con margen para que futuros motores nuevos no bloqueen CI mientras se estabilizan). `motor-aquai` queda como el único bajo ese target — subirlo pasa por escribir tests para `pdf_memoria.py` o aceptar que ese archivo se excluya explícitamente de la medición de cobertura (`--cov-report` con `omit`), no por inventar tests triviales solo para subir el número.

## Qué NO se ha estandarizado todavía (a propósito)

- **Formato de respuesta de API** (`{ data, error?, metadata? }`): no está aplicado todavía en los routers de `apps/api` — cambiarlo requiere tocar `apps/web` en el mismo commit porque los clientes ya parsean la forma actual de cada endpoint. Pendiente, no urgente.
- **Versionado de rutas** (`/api/v1/`): las rutas actuales no están versionadas. No se adopta sin una razón concreta (aún no hay clientes externos de la API que necesiten esa garantía de compatibilidad).
