#!/bin/bash
# Cola de bloques de analisis, secuencial y reanudable. Cada etapa espera a que termine la anterior.
# Uso: bash cola_bloques.sh <carpeta_logs> <pid_chirps_mensual>
cd "$(dirname "$0")"
LOG="$1"; PID="$2"
export PYTHONIOENCODING=utf-8
while tasklist //FI "PID eq $PID" 2>/dev/null | grep -q "$PID"; do sleep 60; done   # espera la extraccion mensual en curso
# 1) CHIRPS mensual 1981-2018 (reintenta hasta completar) -> mapa ENSO
until [ -f chirps_mensual_colombia_1981_2018.json ]; do
  python -u extraer_chirps_colombia.py 1981 2018 >> "$LOG/chirps_1981_cola.log" 2>&1 || sleep 600
done
python -u mapa_enso_lluvia.py > "$LOG/res_mapa_enso.txt" 2>&1
# 2) DEM nacional -> contraste SGC nacional
until grep -q Guardado "$LOG/dem_nacional.log"; do sleep 120; done
python -u contraste_sgc_nacional.py > "$LOG/res_contraste_nacional.txt" 2>&1
# 3) CHIRPS diario 2019-2024 -> umbrales E-D
until [ -f chirps_diario_colombia.json ]; do
  python -u extraer_chirps_diario_colombia.py 2019 2024 >> "$LOG/chirps_diario_cola.log" 2>&1 || sleep 600
done
python -u umbrales_lluvia_movimientos.py > "$LOG/res_umbrales.txt" 2>&1
echo COLA_COMPLETA > "$LOG/cola_estado.txt"
