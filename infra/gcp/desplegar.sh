#!/usr/bin/env bash
# Construye, despliega y VERIFICA la API en Cloud Run. Uso: bash infra/gcp/desplegar.sh [--sin-pruebas]
# - Conserva las variables de entorno y secretos que ya tiene el servicio (no los toca).
# - La revisión nueva se despliega SIN tráfico; solo recibe tráfico si pasa la verificación.
# - Antes de construir, actualiza la instantánea del índice RAG local (apps/api/datos_indice/, gitignored pero incluida
#   en la imagen por .gcloudignore) solo si las tablas cambiaron. Lee apps/api/.env (solo lectura; la clave no se
#   imprime). SIN_INDICE_RAG=1 lo omite: la API usa entonces las RPC de Supabase, como antes.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; . "$HERE/config.sh"
RAIZ="$(cd "$HERE/../.." && pwd)"; cd "$RAIZ"
command -v gcloud >/dev/null || { echo "gcloud no está instalado o no está en el PATH"; exit 1; }

echo "[1/7] Árbol de trabajo"
if [ -n "$(git status --porcelain)" ]; then echo "Hay cambios sin confirmar: confirma antes de desplegar para que la imagen sea reproducible."; exit 1; fi
SHA="$(git rev-parse --short HEAD)"

if [ "${1:-}" != "--sin-pruebas" ]; then
  echo "[2/7] Pruebas locales previas"
  (cd apps/api && SUPABASE_URL=http://localhost:54321 SUPABASE_JWT_SECRET=local python -m pytest tests/test_router_proyecto.py tests/test_router_orquestador.py tests/test_router_analisis.py tests/test_router_concreto.py tests/test_router_geotecnia.py tests/test_router_pilotes.py tests/test_router_licuacion.py tests/test_router_redes.py -q) || { echo "Pruebas fallidas: no se despliega."; exit 1; }
  (cd packages/motor-redes && python -m pytest tests -q) || { echo "Pruebas de motor-redes fallidas: no se despliega."; exit 1; }
  (cd packages/dag-proyecto && python -m pytest tests -q) || { echo "Pruebas del DAG fallidas: no se despliega."; exit 1; }
  (cd apps/api && SUPABASE_URL=http://localhost:54321 SUPABASE_JWT_SECRET=local python -m pytest tests/test_indice_local.py ../../infra/gcp/test_llamadas_reales.py -q) || { echo "Pruebas del índice RAG local fallidas: no se despliega."; exit 1; }
fi

echo "[3/7] Índice RAG local (búsqueda híbrida en memoria)"
INDICE="apps/api/datos_indice/indice_rag.npz"
if [ "${SIN_INDICE_RAG:-}" = "1" ]; then
  echo "  SIN_INDICE_RAG=1: la imagen se construye sin índice local (la API usará las RPC de Supabase)."
  rm -f "$INDICE" "${INDICE%.npz}.manifiesto.json"
else
  python scripts/rag/construir_indice_local.py --si-cambio || { echo "No se pudo construir el índice RAG local: no se despliega (SIN_INDICE_RAG=1 para omitirlo)."; exit 1; }
  python - "$INDICE" <<'PY' || { echo "El índice RAG local no pasó la verificación sha256: no se despliega."; exit 1; }
import hashlib, json, sys
from pathlib import Path
r = Path(sys.argv[1]); m = json.loads(r.with_suffix(".manifiesto.json").read_text(encoding="utf-8"))
assert hashlib.sha256(r.read_bytes()).hexdigest() == m["sha256"], "sha256"
print(f"  {r.name}: {m['bytes'] / 1e6:.1f} MB, {sum(m['filas_por_corpus'].values()):,} filas, construido {m['construido_en']}")
PY
fi

echo "[4/7] Imagen actual (para conservar el repositorio y poder revertir)"
descr() { gcloud run services describe "$SERVICIO" --region "$REGION" --project "$PROJECT" "$@"; }
ACTUAL="$(descr --format='value(spec.template.spec.containers[0].image)')"
[ -n "$ACTUAL" ] || { echo "No se pudo leer la imagen actual del servicio $SERVICIO"; exit 1; }
REPO="${ACTUAL%/*}"; IMAGEN="$REPO/structai-api:$SHA"
REV_ANTERIOR="$(descr --format='value(status.latestReadyRevisionName)')"
echo "  imagen actual: $ACTUAL"; echo "  imagen nueva:  $IMAGEN"; echo "  revisión anterior: $REV_ANTERIOR"

echo "[5/7] Construcción (Cloud Build)"
gcloud builds submit --project "$PROJECT" --config infra/gcp/cloudbuild.yaml --substitutions "_IMAGEN=$IMAGEN" .

echo "[6/7] Despliegue sin tráfico y verificación de la revisión candidata"
gcloud run deploy "$SERVICIO" --project "$PROJECT" --region "$REGION" --image "$IMAGEN" \
  --min-instances "$MIN_INSTANCIAS" --max-instances "$MAX_INSTANCIAS" --concurrency "$CONCURRENCIA" --timeout "$TIMEOUT" \
  --cpu-boost --no-traffic --tag candidata
URL_CAND="$(descr --format=json | python -c "import sys,json; t=[x for x in json.load(sys.stdin)['status']['traffic'] if x.get('tag')=='candidata']; print(t[0]['url'] if t else '')")"
[ -n "$URL_CAND" ] || { echo "No se obtuvo la URL de la revisión candidata"; exit 1; }
fallo=0
for ruta in /health /proyecto/salud /orquestador/salud /analisis/salud /concreto/salud /geotecnia/salud /pilotes/salud /licuacion/salud /redes/salud; do
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 90 "$URL_CAND$ruta" || true)"
  echo "  $ruta -> ${code:-000}"; [ "${code:-000}" = "200" ] || fallo=1
done
if [ "${SIN_INDICE_RAG:-}" != "1" ]; then
  # /health?deep=true carga el índice (una vez) y dice si quedó activo; si no, la revisión usaría las RPC en silencio.
  if curl -s --max-time 120 "$URL_CAND/health?deep=true" | python -c "import sys,json; e=json.load(sys.stdin)['dependencias']['indice_rag_local']; print('  indice_rag_local ->', e); assert e.get('activo'), e"; then :; else
    echo "  El índice RAG local no quedó activo en la revisión candidata."; fallo=1
  fi
fi
if [ "$fallo" -ne 0 ]; then
  echo "X La revisión candidata NO pasó la verificación. El tráfico sigue en $REV_ANTERIOR."
  echo "  Logs: gcloud run services logs read $SERVICIO --region $REGION --project $PROJECT"
  exit 1
fi

# Llamadas reales (condición 4 de docs/REGLAS_MOTORES_DE_CALCULO.md) a redes, geotecnia y licuación, comparadas con un
# cálculo a mano independiente. Requiere un JWT válido de Supabase en TOKEN_PRUEBA; sin él no se afirma la condición 4.
REV_CAND="$(descr --format='value(status.latestCreatedRevisionName)')"
if ! PYTHONIOENCODING=utf-8 python infra/gcp/llamadas_reales.py "$URL_CAND"; then
  echo "X Una llamada real no coincide con el cálculo a mano. El tráfico sigue en $REV_ANTERIOR."; exit 1
fi
[ -n "${TOKEN_PRUEBA:-}" ] && echo "  Para registrar la condición 4: edite docs/registro_motores.json (revision=$REV_CAND, fecha=$(date +%F)) y ejecute scripts/inventario/registro_motores.py"

echo "[7/7] Se mueve el tráfico a la revisión nueva"
gcloud run services update-traffic "$SERVICIO" --project "$PROJECT" --region "$REGION" --to-latest
URL="$(descr --format='value(status.url)')"
curl -s --max-time 60 "$URL/health?deep=true"; echo
echo "OK Desplegado $IMAGEN."
echo "Para revertir: gcloud run services update-traffic $SERVICIO --region $REGION --project $PROJECT --to-revisions $REV_ANTERIOR=100"
