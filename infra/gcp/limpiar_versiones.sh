#!/usr/bin/env bash
# Deja solo lo necesario de StructAI: la revisión que sirve tráfico + las 2 anteriores (para revertir) y las
# últimas 3 imágenes. Por defecto es SIMULACRO (solo muestra); con --aplicar borra de verdad.
#   bash infra/gcp/limpiar_versiones.sh              # simulacro
#   bash infra/gcp/limpiar_versiones.sh --aplicar    # ejecuta
# No toca otros servicios: borrar servicios completos es una decisión manual tras leer auditoria_costos.sh:
#   gcloud run services delete NOMBRE --region REGION --project PROYECTO
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; . "$HERE/config.sh"
APLICAR=0; [ "${1:-}" = "--aplicar" ] && APLICAR=1
CONSERVAR_REVISIONES="${CONSERVAR_REVISIONES:-3}"

echo "== Revisiones de $SERVICIO (se conservan las $CONSERVAR_REVISIONES más recientes y siempre las que tienen tráfico) =="
EN_TRAFICO="$(gcloud run services describe "$SERVICIO" --region "$REGION" --project "$PROJECT" --format=json \
  | python -c "import sys,json; print(' '.join(t['revisionName'] for t in json.load(sys.stdin)['status']['traffic'] if t.get('percent',0)>0 or t.get('tag')))")"
mapfile -t TODAS < <(gcloud run revisions list --service "$SERVICIO" --region "$REGION" --project "$PROJECT" \
  --sort-by="~metadata.creationTimestamp" --format="value(metadata.name)")
i=0
for rev in "${TODAS[@]}"; do
  i=$((i+1))
  if [ "$i" -le "$CONSERVAR_REVISIONES" ] || [[ " $EN_TRAFICO " == *" $rev "* ]]; then echo "  conserva  $rev"; continue; fi
  if [ "$APLICAR" -eq 1 ]; then echo "  BORRA     $rev"; gcloud run revisions delete "$rev" --region "$REGION" --project "$PROJECT" --quiet
  else echo "  (borraría) $rev"; fi
done

echo; echo "== Política de limpieza de imágenes (conserva las 3 más recientes) =="
ACTUAL="$(gcloud run services describe "$SERVICIO" --region "$REGION" --project "$PROJECT" --format='value(spec.template.spec.containers[0].image)')"
case "$ACTUAL" in
  *-docker.pkg.dev/*)
    REPO_RUTA="${ACTUAL%/*}"; REPO="${REPO_RUTA##*/}"
    echo "  repositorio: $REPO (Artifact Registry)"
    if [ "$APLICAR" -eq 1 ]; then
      gcloud artifacts repositories set-cleanup-policies "$REPO" --project "$PROJECT" --location "$REGION" \
        --policy="$HERE/politica_limpieza.json" --no-dry-run
    else
      gcloud artifacts repositories set-cleanup-policies "$REPO" --project "$PROJECT" --location "$REGION" \
        --policy="$HERE/politica_limpieza.json" --dry-run
    fi ;;
  *) echo "  La imagen no está en Artifact Registry ($ACTUAL): revisa 'gcloud container images list' y borra por digest lo que no use." ;;
esac
[ "$APLICAR" -eq 1 ] || echo; [ "$APLICAR" -eq 1 ] || echo "Simulacro terminado: no se cambió nada. Repite con --aplicar para ejecutar."
