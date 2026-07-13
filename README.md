# 🏗️ Plataforma de Ingeniería NSR-10 — Monorepo

**Stack:** pnpm + Turborepo | Next.js 14 | FastAPI | Supabase | N8N | GitHub Actions

## Estructura

```
monorepo/
├── apps/
│   ├── web/          → Next.js 14 (Dashboard + PWA YOLO)  → Vercel
│   └── api/          → FastAPI (Motor APU + RAG NSR-10)   → Render → Cloud Run
├── packages/
│   ├── motor-apu/    → Motor APU matemático (Python)
│   ├── construdata/  → Schema + loader Construdata 2026
│   ├── knowledge/    → Chunks NSR-10 + NTC + Seg.Ind.
│   └── ui/           → Componentes Next.js compartidos
├── infra/
│   ├── docker/       → Dockerfiles
│   └── k8s/          → Kubernetes (futuro GCP)
└── .github/
    └── workflows/    → CI/CD GitHub Actions (gratis)
```

## Coberturas de conocimiento
- ✅ NSR-10 (Títulos A–K) — 70 chunks + grafos de dependencias
- 🔄 NTC (Normas Técnicas Colombianas) — cargar desde Drive
- 🔄 Seguridad Industrial (Decreto 1072, SISO) — cargar desde Drive
- ✅ Motor APU Construdata 2026 Barranquilla

## Comandos

```bash
# Instalar
pnpm install

# Desarrollo local (todo)
docker-compose up -d
pnpm dev

# Correr motor APU
cd packages/motor-apu
python3 -c "from src.catalogue import listar_actividades; import json; print(json.dumps(listar_actividades(), indent=2, ensure_ascii=False))"

# Tests APU
cd packages/motor-apu && pytest tests/ -v

# CI/CD
git push origin main   # dispara GitHub Actions automáticamente
```

## Secrets GitHub Actions
| Secret | Descripción |
|--------|-------------|
| `SUPABASE_URL` | URL del proyecto Supabase |
| `SUPABASE_SERVICE_KEY` | service_role key |
| `ANTHROPIC_API_KEY` | Claude API |
| `OPENAI_API_KEY` | Embeddings |
| `API_SECRET` | Clave interna API |
| `VERCEL_TOKEN` | Deploy web |
| `RENDER_DEPLOY_HOOK` | Deploy API |
| `SUPABASE_ACCESS_TOKEN` | Migraciones automáticas |
