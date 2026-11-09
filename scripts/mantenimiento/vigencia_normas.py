"""Vigilancia de vigencia normativa: avisa cuando una fuente de la cadena de modificaciones cita una norma nueva.

Es solo un aviso. No ingesta, no modifica el corpus y no decide qué norma está vigente: eso exige leer el texto
(CLAUDE.md: «verificar vigencia ANTES de escribir el primer chunk»). Qué hace:

  1. Descarga cada página listada en scripts/mantenimiento/vigilancia_normas.json.
  2. Extrae los identificadores de normas que cita («Decreto 945 de 2017», «R.M. N° 183-2026-VIVIENDA», …).
  3. Los compara con la foto de la corrida anterior (vigilancia_normas_estado.json). Lo que aparece nuevo se reporta.
  4. Reporta también los «pendientes conocidos»: normas que ya se sabe que existen y no están ingestadas.

La primera corrida solo fija la línea base (no alerta). Una fuente que no se pudo descargar se reporta como tal;
nunca se interpreta como «sin cambios».

Uso:
    python scripts/mantenimiento/vigencia_normas.py             # compara contra la foto anterior
    python scripts/mantenimiento/vigencia_normas.py --actualizar  # además guarda la foto nueva
Códigos de salida: 0 sin novedades · 3 hay normas nuevas o pendientes · 2 ninguna fuente se pudo leer
"""
import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

AQUI = Path(__file__).resolve().parent
CONFIG = AQUI / "vigilancia_normas.json"
ESTADO = AQUI / "vigilancia_normas_estado.json"
AGENTE = "Mozilla/5.0 (compatible; structai-vigencia/1.0; +https://github.com/wilmerjoseperezorozco-dev/structai)"
PLAZO_S = 30

_NUM = r"(?:n\S{0,3}\s*)?"                       # «N°», «Nº», «N.», o el carácter dañado por una mala codificación
_RM = re.compile(rf"(?:resoluci[oó]n\s+ministerial|r\.?\s?m\.?)\s*{_NUM}(\d{{1,4}})-(\d{{4}})-vivienda", re.I)
_DECRETO = re.compile(rf"decreto\s+{_NUM}(\d{{1,4}})\s+de\s+(\d{{4}})", re.I)
_RESOLUCION = re.compile(rf"resoluci[oó]n\s+{_NUM}(\d{{1,4}})\s+de\s+(\d{{4}})", re.I)


def a_texto(crudo: bytes) -> str:
    try:
        t = crudo.decode("utf-8")
    except UnicodeDecodeError:
        t = crudo.decode("latin-1")
    t = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", t, flags=re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t.replace("\xa0", " "))


def identificadores(texto: str) -> Set[str]:
    """Identificadores canónicos: decreto-926-2010, resolucion-17-2017, rm-183-2026-vivienda."""
    t = re.sub(r"\s+", " ", texto.replace("\xa0", " "))
    ids = {f"rm-{int(n)}-{a}-vivienda" for n, a in _RM.findall(t)}
    ids |= {f"decreto-{int(n)}-{a}" for n, a in _DECRETO.findall(t)}
    ids |= {f"resolucion-{int(n)}-{a}" for n, a in _RESOLUCION.findall(t)}
    return ids


_DISPARADOR = re.compile(r"(modific|deroga|adiciona|sustitu|reglament|corrige|aclara)", re.I)
_VENTANA = 160


def identificadores_en_modificacion(texto: str) -> Set[str]:
    """Solo los identificadores citados justo después de «modifica», «deroga», etc. Descarta barras laterales y listados de
    «normas recientes» que cambian en cada visita (verificado en la página de DMS Jurídica: sin este filtro la foto cambia sola)."""
    t = re.sub(r"\s+", " ", texto.replace(" ", " "))
    ids: Set[str] = set()
    for m in _DISPARADOR.finditer(t):
        ids |= identificadores(t[m.start():m.start() + _VENTANA])
    return ids


def comparar(anterior: Optional[List[str]], actual: Set[str]) -> Tuple[List[str], List[str]]:
    """(nuevos, desaparecidos) frente a la foto anterior; sin foto anterior no hay comparación posible."""
    if anterior is None:
        return [], []
    previo = set(anterior)
    return sorted(actual - previo), sorted(previo - actual)


def descargar(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": AGENTE})
    with urllib.request.urlopen(req, timeout=PLAZO_S) as r:          # noqa: S310 (URLs fijas de la configuración)
        return r.read(8_000_000)


def vigilar(config: dict, estado: dict) -> Tuple[List[str], dict, bool, bool]:
    informe, nuevo_estado, alguna_ok, hay_novedad = [], {"fuentes": {}}, False, False
    for f in config["fuentes"]:
        clave = f["id"]
        try:
            texto = a_texto(descargar(f["url"]))
            ids = identificadores_en_modificacion(texto) if f.get("solo_en_contexto_de_modificacion") else identificadores(texto)
        except Exception as e:                                       # noqa: BLE001 -- se reporta, nunca se oculta
            informe.append(f"- [ERROR] {clave}: no se pudo leer ({type(e).__name__}: {e}). Sin información sobre esta fuente.")
            if clave in estado.get("fuentes", {}):
                nuevo_estado["fuentes"][clave] = estado["fuentes"][clave]
            continue
        alguna_ok = True
        nuevo_estado["fuentes"][clave] = sorted(ids)
        nuevos, desaparecidos = comparar(estado.get("fuentes", {}).get(clave), ids)
        if clave not in estado.get("fuentes", {}):
            informe.append(f"- {clave}: línea base fijada ({len(ids)} identificadores).")
        elif nuevos or desaparecidos:
            hay_novedad = True
            informe.append(f"- [NOVEDAD] {clave} ({f['norma']}): cita normas nuevas {nuevos or '—'}; dejó de citar {desaparecidos or '—'}. Revisar el texto: {f['url']}")
        else:
            informe.append(f"- {clave}: sin cambios ({len(ids)} identificadores).")
    for p in config.get("pendientes_conocidos", []):
        hay_novedad = True
        informe.append(f"- [NOVEDAD] PENDIENTE CONOCIDO {p['id']} ({p['norma']}): {p['nota']}")
    return informe, nuevo_estado, alguna_ok, hay_novedad


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--actualizar", action="store_true", help="guarda la foto nueva como línea base")
    args = ap.parse_args(argv)
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    estado: Dict = json.loads(ESTADO.read_text(encoding="utf-8")) if ESTADO.exists() else {}
    informe, nuevo, alguna_ok, hay_novedad = vigilar(config, estado)
    print("Vigilancia de vigencia normativa\n" + "\n".join(informe))
    if args.actualizar:
        ESTADO.write_text(json.dumps(nuevo, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        print(f"Foto guardada en {ESTADO.name}")
    if not alguna_ok:
        return 2
    return 3 if hay_novedad else 0


if __name__ == "__main__":
    sys.exit(main())
