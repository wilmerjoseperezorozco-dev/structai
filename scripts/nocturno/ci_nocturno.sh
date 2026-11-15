#!/usr/bin/env bash
# CI nocturno local de StructAI (#178). Corre en ESTE PC con un LLM local (Ollama en WSL); GitHub nunca llama a un
# LLM (el CI de GitHub corre `pytest -m "not llm"`). El modelo local NO va a producción.
#
# Qué corre, en orden (cada paso retoma si se cortó la noche anterior):
#   1. pytest -m llm  con qwen2.5:7b y ventana 16384 (ganador de la comparación prerregistrada de #172).
#   2. sabotaje.py    sabotaje controlado del contexto (#169): ¿responde con lo recuperado o con su memoria?
#   3. Resumen en scripts/nocturno/registros/<fecha>.md
#
# Lo lanza la tarea programada de Windows "StructAI-CI-nocturno" (ver instalar_tarea.ps1). A mano:
#   bash scripts/nocturno/ci_nocturno.sh
set -u
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="$RAIZ/apps/api/.venv/Scripts/python"
[ -x "$PY" ] || PY="$RAIZ/apps/api/.venv/bin/python"
MODELO="${STRUCTAI_LLM_LOCAL:-qwen2.5:7b}"
FECHA="$(date +%Y-%m-%d)"
REG="$RAIZ/scripts/nocturno/registros"
mkdir -p "$REG"
LOG="$REG/$FECHA.log"
RES="$REG/$FECHA.md"
export STRUCTAI_LLM_LOCAL="$MODELO" STRUCTAI_NUM_CTX="${STRUCTAI_NUM_CTX:-16384}" RAG_CACHE_DISABLED=true \
       PYTHONUTF8=1 PYTHONIOENCODING=utf-8 HF_HUB_OFFLINE=1 HF_HUB_DISABLE_SYMLINKS_WARNING=1

registrar() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

# WSL puede dejar un relé de puerto "fantasma" tras reinicios (2026-11-15): Ollama responde dentro de WSL pero no
# desde Windows. Si no responde desde Windows, se reinicia WSL (a esta hora no debería haber nada corriendo en él).
if ! curl -s -m 5 http://127.0.0.1:11434/api/version >/dev/null; then
  wsl.exe -d Ubuntu -- sleep 90 >/dev/null 2>&1 &     # despierta la distro y la mantiene viva mientras se prueba
  sleep 25
  if ! curl -s -m 5 http://127.0.0.1:11434/api/version >/dev/null; then
    registrar "Ollama no responde desde Windows: reinicio WSL (wsl --shutdown)"
    wsl.exe --shutdown; sleep 10
  fi
fi
registrar "inicio CI nocturno: modelo=$MODELO rama=$(git -C "$RAIZ" branch --show-current) commit=$(git -C "$RAIZ" rev-parse --short HEAD)"

# 1. Pruebas con LLM (el conftest mantiene WSL despierto y espera a Ollama)
cd "$RAIZ/apps/api" || exit 1
"$PY" -m pytest -m llm -q -rfE -p no:cacheprovider --junitxml="$REG/$FECHA-pytest-llm.xml" >> "$LOG" 2>&1
PYTEST_CODIGO=$?
RESUMEN_PYTEST="$(grep -aE '^=+ .* in [0-9.]+s' "$LOG" | tail -1)"
registrar "pytest -m llm terminó con código $PYTEST_CODIGO: $RESUMEN_PYTEST"

# 2. Sabotaje controlado (retoma desde su caché; reintenta si Ollama se cae)
cd "$RAIZ/scripts/evaluacion/golden/e3_modelos_locales" || exit 1
for intento in 1 2 3; do
  "$PY" -u sabotaje.py --modelo "$MODELO" >> "$LOG" 2>&1 && break
  registrar "sabotaje cortado (intento $intento); espero 5 min y retomo"
  sleep 300
done
SABOTAJE_MD="SABOTAJE_${MODELO//:/_}.md"

# 3. Resumen
{
  echo "# CI nocturno local — $FECHA"
  echo
  echo "- Modelo: \`$MODELO\` (ventana ${STRUCTAI_NUM_CTX}); rama \`$(git -C "$RAIZ" branch --show-current)\`, commit \`$(git -C "$RAIZ" rev-parse --short HEAD)\`."
  echo "- **pytest -m llm:** ${RESUMEN_PYTEST:-sin resumen (ver log)} (código $PYTEST_CODIGO)."
  echo
  echo "Fallos:"
  grep -aE '^FAILED' "$LOG" | sed 's/^/- /' | tail -40
  echo
  [ -f "$SABOTAJE_MD" ] && cat "$SABOTAJE_MD"
} > "$RES"
registrar "fin; resumen en $RES"
