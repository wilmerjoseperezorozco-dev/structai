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

Instalación local de un motor para desarrollo:
```bash
cd packages/motor-<nombre>
pip install -e ".[dev]"
```

## Qué NO se ha estandarizado todavía (a propósito)

- **Formato de respuesta de API** (`{ data, error?, metadata? }`): no está aplicado todavía en los routers de `apps/api` — cambiarlo requiere tocar `apps/web` en el mismo commit porque los clientes ya parsean la forma actual de cada endpoint. Pendiente, no urgente.
- **Cobertura de tests por motor**: no hay un número objetivo fijado todavía — se mide antes de prometerlo, no se asume.
- **Versionado de rutas** (`/api/v1/`): las rutas actuales no están versionadas. No se adopta sin una razón concreta (aún no hay clientes externos de la API que necesiten esa garantía de compatibilidad).
