#!/usr/bin/env bash
# CI nocturno local de StructAI (#178): pytest -m llm con un LLM local (Ollama en WSL) sobre el código de master.
# GitHub nunca llama a un LLM (su CI corre `pytest -m "not llm"`); esta corrida es la única prueba de punta a punta de
# la IA. El modelo local NO va a producción.
#
# Dónde corre: en un worktree propio (por defecto C:\Users\wilme\dev\structai-nocturno, en HEAD separado). La tarea
# programada (instalar_tarea.ps1) lo pone en origin/master ANTES de lanzar este script, así que cada noche prueba lo
# último que se mergeó y no toca el clon principal ni sus ramas.
#
# Qué usa sin copiarlo al worktree (nada de esto está en git):
#   - el venv de apps/api del clon principal (solo se ejecuta, nunca se instala nada en él);
#   - las variables de apps/api/.env del clon principal, cargadas al entorno sin imprimirlas;
#   - el índice RAG local del último despliegue (structai-deploy/apps/api/datos_indice/indice_rag.npz), el mismo de
#     producción.
#
# Horario: 23:00 con el PC prendido. Si arranca fuera de la ventana nocturna (por ejemplo, a mano de día), se salta,
# salvo con NOCTURNO_FORZAR=1. Resultado: scripts/nocturno/registros/<fecha>.md y .log.
set -u
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PRINCIPAL="${STRUCTAI_CLON_PRINCIPAL:-/c/Users/wilme/dev/structai}"
PY="${STRUCTAI_PY:-$PRINCIPAL/apps/api/.venv/Scripts/python}"
[ -x "$PY" ] || PY="$PRINCIPAL/apps/api/.venv/bin/python"
MODELO="${STRUCTAI_LLM_LOCAL:-qwen2.5:7b}"
FECHA="$(date +%Y-%m-%d)"
REG="$RAIZ/scripts/nocturno/registros"
mkdir -p "$REG"
LOG="$REG/$FECHA.log"
RES="$REG/$FECHA.md"

registrar() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

HORA=$((10#$(date +%H)))
if [ "${NOCTURNO_FORZAR:-0}" != "1" ] && [ "$HORA" -lt 22 ] && [ "$HORA" -ge 6 ]; then
  registrar "arranque a las $(date +%H:%M), fuera de la ventana nocturna: se salta (NOCTURNO_FORZAR=1 para forzar)"
  exit 0
fi

if [ -f "$PRINCIPAL/apps/api/.env" ]; then
  set -a; . "$PRINCIPAL/apps/api/.env"; set +a          # sin imprimir nada
fi
export STRUCTAI_LLM_LOCAL="$MODELO" STRUCTAI_NUM_CTX="${STRUCTAI_NUM_CTX:-16384}" RAG_CACHE_DISABLED=true \
       RAG_INDICE_LOCAL_RUTA="${RAG_INDICE_LOCAL_RUTA:-/c/Users/wilme/dev/structai-deploy/apps/api/datos_indice/indice_rag.npz}" \
       PYTHONUTF8=1 PYTHONIOENCODING=utf-8 HF_HUB_OFFLINE=1 HF_HUB_DISABLE_SYMLINKS_WARNING=1
[ -f "$RAG_INDICE_LOCAL_RUTA" ] || registrar "aviso: no existe el índice local $RAG_INDICE_LOCAL_RUTA; se usan las RPC"

# Desde el 2026-11-27 hay un solo Ollama (el de WSL). Si no responde desde Windows, se despierta la distro y, si
# sigue sin responder, se reinicia WSL (a esta hora no debería haber nada corriendo en él).
if ! curl -s -m 5 http://127.0.0.1:11434/api/version >/dev/null; then
  wsl.exe -d Ubuntu -- sleep 90 >/dev/null 2>&1 &
  sleep 25
  if ! curl -s -m 5 http://127.0.0.1:11434/api/version >/dev/null; then
    registrar "Ollama no responde desde Windows: reinicio WSL (wsl --shutdown)"
    wsl.exe --shutdown; sleep 10
  fi
fi
COMMIT="$(git -C "$RAIZ" rev-parse --short HEAD)"
registrar "inicio CI nocturno: modelo=$MODELO commit=$COMMIT ($(git -C "$RAIZ" log -1 --format=%s | cut -c1-80))"

# pytest -m llm (el conftest mantiene WSL despierto, impide la suspensión y espera a Ollama)
cd "$RAIZ/apps/api" || exit 1
"$PY" -m pytest -m llm -q -rfE -p no:cacheprovider --junitxml="$REG/$FECHA-pytest-llm.xml" >> "$LOG" 2>&1
CODIGO=$?
RESUMEN="$(grep -aE '^=+ .* in [0-9.]+s' "$LOG" | tail -1)"
registrar "pytest -m llm terminó con código $CODIGO: $RESUMEN"

{
  echo "# CI nocturno local — $FECHA"
  echo
  echo "- Modelo: \`$MODELO\` (ventana ${STRUCTAI_NUM_CTX}); master en \`$COMMIT\`."
  echo "- **pytest -m llm:** ${RESUMEN:-sin resumen (ver log)} (código $CODIGO)."
  echo
  echo "Fallos:"
  grep -aE '^FAILED' "$LOG" | sed 's/^/- /' | tail -40
} > "$RES"
registrar "fin; resumen en $RES"
