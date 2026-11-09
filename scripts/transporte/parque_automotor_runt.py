"""Parque automotor activo del RUNT (datos.gov.co `u3vn-bdcy`, foto de noviembre de 2026, 22,8 millones de vehículos activos) para caracterizar la flota de carga y
de maquinaria de obra por departamento.

Campos: departamento y municipio de matrícula, clase, servicio, año de `fecha_de_registro` (se lee como año modelo/registro; 1900 = sin dato), cantidad.
Es UNA foto, no una serie; el municipio es el de matrícula, no el de operación (los camiones de empresas de carga se matriculan en pocas ciudades).

HIPÓTESIS FIJADA ANTES DE CALCULAR (validez convergente de la medida de pesados de 5l/5m): el porcentaje de tractocamiones en la flota pesada del departamento,
T = tractocamión / (camión + tractocamión + volqueta), se correlaciona POSITIVAMENTE (Spearman) con el porcentaje de pesados de la mezcla INVIAS 2011 y con el de ANI 2024
(siete categorías), porque las configuraciones de 5 o más ejes (C-5, >C-5; VI y VII) son casi todas tractocamiones con semirremolque. Una correlación débil o negativa
indicaría que la medida de tráfico refleja otra cosa (p. ej. dónde se mide, no qué flota circula). Dos pruebas; Holm entre ellas. Lo demás es descriptivo.

Descriptivo: flota por clase, edad (2026 menos año) por clase y servicio, proporción mayor de 20 años, maquinaria amarilla por departamento.
Salida: data/transporte/parque_automotor_runt.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cruces_peajes_secop as base  # noqa: E402
import cruces_seguridad_institucional as seg  # noqa: E402
import cruces_trafico_ani as ani  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
SALIDA = base.RAIZ / "data" / "transporte" / "parque_automotor_runt.json"
ANIO_FOTO = 2026
CARGA = ("CAMION", "CAMIÓN", "TRACTOCAMION", "VOLQUETA")
MAQUINARIA = ("EXCAVADORA", "RETROEXCAVADORA", "MOTONIVELADORA", "BULDOZER", "VIBROCOMPACTADORA", "MINICARGADOR", "CARGADOR", "COMPACTADOR", "MINI EXCAVADORA",
              "RETROCARGADOR", "AUTOHORMIGONERA", "DUMPER (VOLQUETA ARTICULADA)")
OTROS = ("SEMIREMOLQUE", "REMOLQUE")
ALIAS_DPTO = {"BOGOTA D.C.": "CUNDINAMARCA", "LA GUAJIRA": "GUAJIRA", "VALLE DEL CAUCA": "VALLE"}


def lista(clases) -> str:
    return ",".join("'" + c + "'" for c in clases)


def cargar() -> list[dict]:
    return seg.soql("u3vn-bdcy", **{"$select": "nombre_departamento,nombre_de_la_clase,nombre_servicio,fecha_de_registro,sum(cantidad) as n",
                                    "$where": f"nombre_de_la_clase in ({lista(CARGA + MAQUINARIA + OTROS)}) AND estado_del_vehiculo='ACTIVO'",
                                    "$group": "nombre_departamento,nombre_de_la_clase,nombre_servicio,fecha_de_registro", "$limit": 200000})


def clave_dpto(nombre: str) -> str:
    n = base.norm(nombre)
    return ALIAS_DPTO.get(n, n)


def clase(c: str) -> str:
    return "CAMION" if c in ("CAMION", "CAMIÓN") else c


def cuantil_ponderado(edades: np.ndarray, pesos: np.ndarray, q: float) -> float:
    o = np.argsort(edades)
    cum = np.cumsum(pesos[o])
    return float(edades[o][np.searchsorted(cum, q * cum[-1])])


def resumen_edad(filas: list[dict]) -> dict:
    ed = np.array([ANIO_FOTO - int(r["fecha_de_registro"]) for r in filas], float)
    w = np.array([float(r["n"]) for r in filas])
    ok = (ed >= 0) & (ed <= 80)       # 1900 (sin dato) y fechas futuras quedan fuera
    ed, w = ed[ok], w[ok]
    return {"n": float(w.sum()), "mediana_anios": cuantil_ponderado(ed, w, 0.5), "p25": cuantil_ponderado(ed, w, 0.25), "p75": cuantil_ponderado(ed, w, 0.75),
            "pct_mas_20_anios": float(100 * w[ed > 20].sum() / w.sum()), "descartados_sin_anio": float(sum(float(r["n"]) for r, o in zip(filas, ok) if not o))}


def por_departamento(filas: list[dict]) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for r in filas:
        d = out.setdefault(clave_dpto(r["nombre_departamento"]), {})
        c = clase(r["nombre_de_la_clase"])
        d[c] = d.get(c, 0.0) + float(r["n"])
    return out


if __name__ == "__main__":
    rng = np.random.default_rng(base.SEMILLA)
    filas = cargar()
    print(f"{len(filas)} filas agregadas; vehículos de las clases consideradas: {sum(float(r['n']) for r in filas):,.0f}")
    res: dict = {"nacional": {}, "edad": {}, "departamentos": {}}
    por_clase: dict[str, list[dict]] = {}
    for r in filas:
        por_clase.setdefault(clase(r["nombre_de_la_clase"]), []).append(r)
    print(f"\n{'clase':32s}{'n':>10s}{'% público':>10s}{'mediana':>9s}{'IQR':>11s}{'>20 años':>10s}")
    for c, rs in sorted(por_clase.items(), key=lambda kv: -sum(float(r['n']) for r in kv[1])):
        tot = sum(float(r["n"]) for r in rs)
        pub = sum(float(r["n"]) for r in rs if r["nombre_servicio"] == "PÚBLICO")
        e = resumen_edad(rs)
        res["nacional"][c] = {"n": tot, "pct_publico": 100 * pub / tot}
        res["edad"][c] = e
        print(f"{c:32s}{tot:10.0f}{100 * pub / tot:9.1f}%{e['mediana_anios']:9.0f}{e['p25']:6.0f}-{e['p75']:<4.0f}{e['pct_mas_20_anios']:9.1f}%")

    dep = por_departamento(filas)
    for d, v in dep.items():
        pesada = v.get("CAMION", 0) + v.get("TRACTOCAMION", 0) + v.get("VOLQUETA", 0)
        res["departamentos"][d] = {"camion": v.get("CAMION", 0), "tractocamion": v.get("TRACTOCAMION", 0), "volqueta": v.get("VOLQUETA", 0),
                                   "semirremolque": v.get("SEMIREMOLQUE", 0), "maquinaria_amarilla": sum(v.get(c, 0) for c in MAQUINARIA if c != "AUTOHORMIGONERA"),
                                   "autohormigonera": v.get("AUTOHORMIGONERA", 0), "pct_tractocamion": 100 * v.get("TRACTOCAMION", 0) / pesada if pesada else float("nan")}
    # Validez convergente
    mezcla = base.cargar_mezcla(2011)
    p11 = {d: float(np.vstack(v)[:, 3:].sum() / np.vstack(v).sum()) for d, v in mezcla.items()}
    ub = ani.ubicacion_peajes()
    dep24, _, _ = ani.por_departamento(ani.trafico_ani(2024), ub)
    h24 = {d: ani.pesados(v) for d, v in dep24.items() if not np.isnan(ani.pesados(v))}
    print("\n== Validez convergente (hipótesis fijada de antemano)")
    pruebas = []
    for nombre, serie in (("INVIAS 2011", p11), ("ANI 2024", h24)):
        ds = sorted(d for d in serie if d in res["departamentos"] and not np.isnan(res["departamentos"][d]["pct_tractocamion"]))
        r = base.spearman_boot(np.array([res["departamentos"][d]["pct_tractocamion"] for d in ds]), np.array([serie[d] for d in ds]), rng, 5000)
        pruebas.append(r["p_perm"])
        res[f"T_vs_pesados_{nombre}"] = r
        print(f"% tractocamión (RUNT) vs % pesados {nombre:12s} n={r['n']:2d} rho={r['rho']:.2f} IC95 ({r['ic95'][0]:.2f}, {r['ic95'][1]:.2f}) p_perm={r['p_perm']:.3f}")
    holm, previo = [], 0.0
    for i, p in enumerate(sorted(pruebas)):          # Holm con monotonía: el ajustado no puede bajar respecto del anterior
        previo = max(previo, min(1.0, p * (len(pruebas) - i)))
        holm.append(previo)
    res["p_holm"] = holm
    print("p ajustado por Holm (ordenado):", [round(p, 3) for p in res["p_holm"]])
    SALIDA.write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
