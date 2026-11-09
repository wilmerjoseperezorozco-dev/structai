#!/usr/bin/env bash
# Auditoría de SOLO LECTURA: qué recursos del proyecto pueden estar generando costo.
# No modifica nada. Uso: bash infra/gcp/auditoria_costos.sh   (requiere gcloud autenticado)
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; . "$HERE/config.sh"
sec() { printf '\n== %s ==\n' "$1"; }
try() { "$@" 2>&1 || echo "(no disponible: API deshabilitada o sin permiso)"; }
echo "Proyecto: $PROJECT   Región de referencia: $REGION   $(date -u +%FT%TZ)"

sec "Cloud Run - servicios (todas las regiones)"
try gcloud run services list --project "$PROJECT"

sec "Cloud Run - revisiones de $SERVICIO (las que reciben tráfico cuestan; las demás no)"
try gcloud run revisions list --service "$SERVICIO" --region "$REGION" --project "$PROJECT"
try gcloud run services describe "$SERVICIO" --region "$REGION" --project "$PROJECT" --format="yaml(status.traffic,spec.template.spec.containers[0].resources,spec.template.metadata.annotations)"

sec "Cloud Run - jobs"
try gcloud run jobs list --project "$PROJECT"

sec "Artifact Registry - repositorios (el almacenamiento de imágenes se factura)"
try gcloud artifacts repositories list --project "$PROJECT"

sec "Container Registry heredado (gcr.io) - imágenes"
try gcloud container images list --project "$PROJECT"

sec "Compute Engine - VMs (cuestan encendidas; apagadas siguen cobrando el disco)"
try gcloud compute instances list --project "$PROJECT"
sec "Compute Engine - discos sin adjuntar e IPs reservadas sin usar (cobran aunque no se usen)"
try gcloud compute disks list --project "$PROJECT" --filter="-users:*"
try gcloud compute addresses list --project "$PROJECT" --filter="status=RESERVED"
sec "Compute Engine - balanceadores, reglas de reenvío y NAT (costo fijo por hora)"
try gcloud compute forwarding-rules list --project "$PROJECT"
try gcloud compute routers list --project "$PROJECT"

sec "Cloud SQL"
try gcloud sql instances list --project "$PROJECT"
sec "GKE"
try gcloud container clusters list --project "$PROJECT"
sec "Cloud Functions"
try gcloud functions list --project "$PROJECT"
sec "Cloud Scheduler"
try gcloud scheduler jobs list --project "$PROJECT" --location "$REGION"
sec "Pub/Sub"
try gcloud pubsub topics list --project "$PROJECT" --format="value(name)"
sec "Buckets de almacenamiento"
try gcloud storage buckets list --project "$PROJECT"
sec "Secret Manager"
try gcloud secrets list --project "$PROJECT"
sec "Cloud Build - triggers"
try gcloud builds triggers list --project "$PROJECT"
sec "Facturación"
try gcloud billing projects describe "$PROJECT"
echo; echo "Fin. Presupuesto y alertas: Consola > Facturación > Presupuestos y alertas (ver infra/gcp/README.md)."
