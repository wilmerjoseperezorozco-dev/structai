# Construdata — Arquitectura del Sistema

## Stack

| Capa | Tecnología | Deploy |
|------|-----------|--------|
| Frontend PWA | Next.js 14 + TailwindCSS | Vercel |
| Backend API | FastAPI (Python) | Render → Cloud Run |
| Base de datos | Supabase (PostgreSQL + pgvector) | Supabase Cloud |
| Auth | Supabase Auth (JWT) | Supabase Cloud |
| Pagos | Wompi (Colombia) | Wompi API |
| CI/CD | GitHub Actions | Gratis |
| Monorepo | pnpm + Turborepo | Local |

## Estructura de carpetas

```
construdata/
├── apps/
│   ├── web/                    → Next.js 14 PWA
│   │   └── src/
│   │       ├── app/
│   │       │   ├── (auth)/     → login, registro (rutas públicas)
│   │       │   ├── (app)/      → rutas protegidas con auth
│   │       │   │   ├── dashboard/
│   │       │   │   ├── proyectos/
│   │       │   │   ├── apu/
│   │       │   │   ├── nsr10/
│   │       │   │   └── perfil/
│   │       │   ├── pricing/    → pública
│   │       │   └── landing/    → pública
│   │       ├── components/
│   │       │   ├── ui/         → botones, cards, badges
│   │       │   ├── apu/        → calculadora + desglose
│   │       │   ├── nsr10/      → navegador de títulos
│   │       │   ├── trazabilidad/ → historial + UUID
│   │       │   └── layout/     → header, nav, sidebar
│   │       └── lib/
│   │           ├── api.ts      → cliente FastAPI
│   │           ├── supabase.ts → cliente Supabase
│   │           ├── freemium.ts → límites por plan
│   │           ├── nsr10.ts    → datos NSR-10 títulos A-K
│   │           └── hooks/      → useAuth, useFreemium, usePlan
│   └── api/                    → FastAPI
│       ├── main.py             → app + CORS + startup
│       ├── routers/
│       │   ├── ask.py          → RAG NSR-10/NTC
│       │   ├── apu.py          → cálculo APU
│       │   └── detect.py       → YOLO detección
│       ├── middleware/
│       │   └── auth.py         → verificar JWT Supabase
│       └── services/           → lógica de negocio
├── packages/
│   ├── motor-apu/              → motor matemático Monte Carlo
│   ├── construdata/            → schema + RAG multi-norma
│   ├── knowledge/              → chunks NSR-10, NTC, SegInd
│   │   ├── nsr10/              → PDFs/texto por título A-K
│   │   ├── ntc/                → NTC complementarias
│   │   └── seg_industrial/     → Decreto 1072, SISO
│   └── ui/                     → componentes compartidos
├── infra/
│   ├── docker/                 → Dockerfiles producción
│   └── supabase/
│       ├── migrations/         → SQL migrations versionadas
│       └── seed/               → datos semilla desarrollo
├── docs/                       → esta carpeta
└── scripts/                    → utilidades CLI
    ├── load_nsr10.py           → cargar chunks a Supabase
    └── seed_dev.py             → datos de desarrollo
```

## Modelo freemium

| Plan | Precio | APU/mes | Proyectos | PDF | Historial |
|------|--------|---------|-----------|-----|-----------|
| Gratis | $0 | 5 | 1 | No | 7 días |
| Pro | $19.900 COP/mes | ∞ | ∞ | Sí | ∞ |
| Pro Anual | $159.000 COP/año | ∞ | ∞ | Sí | ∞ |

## Flujo de trazabilidad

1. Usuario calcula APU → se guarda en `trazabilidad_apu` con UUID único
2. Usuario consulta NSR-10 → se guarda en `trazabilidad_consultas`
3. Desde un proyecto, se pueden ver todos los APU y consultas asociados
4. Export PDF incluye UUID de trazabilidad para auditoría

## Diseño UI — principios para campo

- Dark theme (#1a1a1a base) → alto contraste bajo el sol
- Fuentes mínimo 14px en mobile
- Touch targets mínimo 44px
- Colores semánticos por capítulo NSR-10
- Sin gradientes ni efectos que consuman batería
- Offline-first: catálogo APU disponible sin conexión
