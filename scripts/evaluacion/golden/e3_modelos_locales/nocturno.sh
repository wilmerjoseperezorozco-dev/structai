#!/usr/bin/env bash
# Corrida nocturna local de modelos (#172, #178). Solo en este PC: GitHub nunca llama a un LLM.
#
# Qué hace, en orden:
#   1. Corre la batería completa (138 casos) con cada modelo, ventana 16384 (default del harness).
#      El harness mantiene WSL despierto por sí mismo y nunca graba un caso con Ollama caído.
#   2. Si una corrida se corta (código 4 = Ollama no volvió), espera y la relanza: retoma de la caché.
#   3. Al final compara los modelos con el criterio prerregistrado (comparar_modelos.py).
#
# Uso (Git Bash, desde cualquier carpeta):
#   bash scripts/evaluacion/golden/e3_modelos_locales/nocturno.sh                 # llama3:8b y hermes3
#   bash scripts/evaluacion/golden/e3_modelos_locales/nocturno.sh qwen2.5:7b      # los que se indiquen
# Registro: resultados/nocturno_<fecha>.log
set -u
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$AQUI/../../../../apps/api/.venv/Scripts/python"
[ -x "$PY" ] || PY="$AQUI/../../../../apps/api/.venv/bin/python"
MODELOS=("$@")
[ ${#MODELOS[@]} -eq 0 ] && MODELOS=("llama3:8b" "hermes3:latest")
REINTENTOS=3
LOG="$AQUI/resultados/nocturno_$(date +%Y-%m-%d_%H%M).log"
mkdir -p "$AQUI/resultados"
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 HF_HUB_DISABLE_SYMLINKS_WARNING=1

registrar() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

cd "$AQUI" || exit 1
registrar "inicio: modelos=${MODELOS[*]} num_ctx=${STRUCTAI_NUM_CTX:-16384}"
for m in "${MODELOS[@]}"; do
  for intento in $(seq 1 $REINTENTOS); do
    registrar "$m: corrida (intento $intento/$REINTENTOS)"
    "$PY" -u correr_bateria.py --modelo "$m" --bateria todo 2>&1 | grep -v "^No se pudo descomponer" >> "$LOG"
    codigo=${PIPESTATUS[0]}
    if [ "$codigo" -eq 0 ]; then registrar "$m: terminado"; break; fi
    registrar "$m: salió con código $codigo; espero 5 min y retomo"
    sleep 300
  done
done
registrar "comparación"
"$PY" comparar_modelos.py --modelos qwen2.5:7b "${MODELOS[@]}" 2>&1 | tee -a "$LOG"
registrar "fin"
