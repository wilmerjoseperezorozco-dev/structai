#!/bin/bash
# Corrida final (programada el 2026-11-07): ejecuta, cuando cada insumo esté listo, los análisis pendientes de los protocolos §§19, 21, 22 y 23.
# Cada etapa espera su propio insumo; las etapas independientes avanzan en paralelo. Los resultados quedan en resultados_corrida/.
# Uso: bash corrida_final.sh <carpeta_de_registros_de_extraccion>   (donde están dem_nacional.log y crecientes.log)
cd "$(dirname "$0")"
LOGS="$1"
OUT=resultados_corrida
mkdir -p "$OUT"
export PYTHONIOENCODING=utf-8
date > "$OUT/inicio.txt"

# A) CHIRPS diario 2019-2024 (reanudable; reintenta si el servidor limita)
( until [ -f chirps_diario_colombia.json ]; do
    python -u extraer_chirps_diario_colombia.py 2019 2024 >> "$OUT/chirps_diario.log" 2>&1 || sleep 300
  done; echo "chirps diario listo" >> "$OUT/estado.txt" ) &

# B) Contraste nacional con el SGC (§17) cuando termine el DEM nacional
( until grep -q Guardado "$LOGS/dem_nacional.log" 2>/dev/null; do sleep 120; done
  python -u contraste_sgc_nacional.py > "$OUT/contraste_sgc_nacional.txt" 2>&1; echo "contraste SGC listo" >> "$OUT/estado.txt" ) &

# C) H3 (susceptibilidad en logaritmo): el insumo ya existe
( python -u hipotesis_h3_susceptibilidad_log.py > "$OUT/h3.txt" 2>&1; echo "H3 listo" >> "$OUT/estado.txt" ) &

# D) Frecuencia de crecientes (§21) ya está corriendo; al terminar se copia su resumen y se corren H4/H5
( until [ -f frecuencia_crecientes_ideam.json ]; do sleep 120; done; sleep 90
  cp "$LOGS/crecientes.log" "$OUT/frecuencia_crecientes.txt" 2>/dev/null
  python -u hipotesis_h4_h5_crecientes.py > "$OUT/h4_h5.txt" 2>&1; echo "H4/H5 listo" >> "$OUT/estado.txt" ) &

# E) Umbrales de lluvia (§19) y H1/H2 cuando estén CHIRPS diario y el DEM (pendiente municipal)
( until [ -f chirps_diario_colombia.json ] && grep -q Guardado "$LOGS/dem_nacional.log" 2>/dev/null; do sleep 120; done
  python -u umbrales_lluvia_movimientos.py > "$OUT/umbrales.txt" 2>&1
  python -u hipotesis_h1_h2_umbrales.py > "$OUT/h1_h2.txt" 2>&1; echo "umbrales y H1/H2 listos" >> "$OUT/estado.txt" ) &

wait
python -u consolidar_corrida.py > "$OUT/consolidado_holm.txt" 2>&1
date > "$OUT/fin.txt"
echo CORRIDA_COMPLETA >> "$OUT/estado.txt"
