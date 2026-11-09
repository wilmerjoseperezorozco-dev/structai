# Despliegue y control de costos en Google Cloud (etapa de evaluación)

Proyecto `structai-507113`, región `us-east1`, servicio Cloud Run `structai-api`. Los scripts son `bash` (funcionan en Git Bash y en Cloud Shell) y toman sus valores de [`config.sh`](config.sh).

## Requisitos (una sola vez)

1. Instalar el SDK de Google Cloud (`gcloud`) o usar Cloud Shell en la consola.
2. `gcloud auth login` y `gcloud config set project structai-507113`.
3. Permisos sobre el proyecto: Cloud Run Admin, Cloud Build Editor, Artifact Registry Writer y Service Account User.

## Orden recomendado

| Paso | Comando | Qué hace |
|---|---|---|
| 1 | `bash infra/gcp/auditoria_costos.sh` | Solo lectura. Lista servicios, revisiones, repositorios de imágenes, VMs, discos e IPs sin usar, SQL, GKE, buckets, secretos y triggers. |
| 2 | Decidir qué sobra | Cualquier servicio o recurso que no sea `structai-api` y no se use se borra a mano, con el nombre exacto (ver abajo). |
| 3 | `bash infra/gcp/limpiar_versiones.sh` | Simulacro: muestra las revisiones e imágenes viejas que borraría. |
| 4 | `bash infra/gcp/limpiar_versiones.sh --aplicar` | Conserva la revisión con tráfico más las 2 anteriores y las 3 últimas imágenes. |
| 5 | `bash infra/gcp/desplegar.sh` | Pruebas locales, construcción, despliegue **sin tráfico**, verificación de 5 rutas y solo entonces mueve el tráfico. |

El despliegue conserva las variables de entorno y los secretos que ya tiene el servicio: no los pisa. Si la revisión candidata falla la verificación, el tráfico sigue en la revisión anterior y el script lo dice.

## Qué garantiza que la app esté viva

- `--min-instances 1`: siempre hay una instancia cargada. El modelo de embeddings y el reranker tardan en cargar en frío; sin esto, la primera consulta tras un rato de inactividad espera ese arranque.
- `--cpu-boost`: más CPU solo durante el arranque.
- `--max-instances 3`: tope de gasto ante picos o bucles.
- Verificación previa a mover tráfico (`/health` y las rutas `/salud` de cada motor).
- Reversión inmediata con un comando (lo imprime el script).

El único costo continuo que añade esta configuración es la instancia mínima. Si prefieres gastar lo mínimo y aceptar el arranque en frío: `MIN_INSTANCIAS=0 bash infra/gcp/desplegar.sh`.

## Qué cuesta y qué no

- Una **revisión** de Cloud Run sin tráfico no consume; limpiarlas es orden, no ahorro.
- Las **imágenes** en Artifact Registry sí cobran almacenamiento: la política de [`politica_limpieza.json`](politica_limpieza.json) deja las 3 últimas.
- Cuestan aunque no se usen: VMs apagadas (disco), **discos sin adjuntar**, **IPs reservadas sin asignar**, balanceadores, Cloud NAT, instancias de Cloud SQL y clústeres GKE. La auditoría los marca por separado.
- DigitalOcean está apagado por decisión propia; no hay nada que hacer en GCP por eso, pero conviene confirmar en la facturación de DigitalOcean que no queden recursos activos.

## Borrar lo que no se use

Solo después de leer la auditoría y con el nombre exacto:

```bash
gcloud run services delete NOMBRE --region REGION --project structai-507113
gcloud compute addresses delete NOMBRE --region REGION --project structai-507113
gcloud compute disks delete NOMBRE --zone ZONA --project structai-507113
```

## Presupuesto con alerta (recomendado)

```bash
gcloud billing accounts list
gcloud billing budgets create --billing-account=ID_CUENTA --display-name="StructAI evaluación" \
  --budget-amount=USD_MENSUAL --threshold-rule=percent=0.5 --threshold-rule=percent=0.9 --threshold-rule=percent=1.0
```

Las alertas llegan por correo a los administradores de facturación; no frenan el gasto por sí solas, por eso el tope de `--max-instances`.

## Rutas de verificación manual

`/health?deep=true`, `/data-status`, `/proyecto/salud`, `/orquestador/salud`, `/analisis/salud`, `/concreto/salud`.

## Limitaciones

Estos scripts se escribieron sin acceso a `gcloud` desde la máquina de desarrollo: se validó su sintaxis y la imagen se probó importando `apps/api/main.py` con todos los routers, pero no se ejecutaron contra el proyecto real. La primera corrida de `auditoria_costos.sh` es la verificación.
