# Configuración común de los scripts de infra/gcp. Todo se puede sobrescribir con variables de entorno.
export PROJECT="${PROJECT:-structai-507113}"
export REGION="${REGION:-us-east1}"
export SERVICIO="${SERVICIO:-structai-api}"
# Etapa de evaluación: una instancia siempre tibia (el modelo de embeddings tarda en cargar en frío) y tope bajo
# para que un pico de tráfico o un bucle no dispare la factura.
export MIN_INSTANCIAS="${MIN_INSTANCIAS:-1}"
export MAX_INSTANCIAS="${MAX_INSTANCIAS:-3}"
export CONCURRENCIA="${CONCURRENCIA:-20}"
export TIMEOUT="${TIMEOUT:-120}"
