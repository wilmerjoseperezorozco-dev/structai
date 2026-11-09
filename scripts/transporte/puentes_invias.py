"""Inventario de puentes de la red vial nacional (INVIAS, datos.gov.co `nsdj-ep2p`, 2.830 puentes de INVIAS, ANI y concesiones departamentales).

Qué se obtiene: composición por administrador, material, tipología longitudinal y transversal (códigos del diccionario del propio conjunto), época de construcción
frente a los códigos colombianos de puentes (antes de 1995 = antes del CCDSP-95; 1995-2014 = CCDSP-95; desde 2015 = CCP-14, que es la norma vigente), vigencia de
la inspección, estadísticos de luz máxima por material (para contrastar los rangos de luz de los motores de diseño) y distribución departamental.

PRUEBA EXPLORATORIA fijada antes de calcular (2 pruebas, Holm entre ellas): el porcentaje de puentes construidos antes de 1995 en el departamento se asocia con el
porcentaje de pesados de peajes (INVIAS 2011 y ANI 2024, mismas medidas de 5l/5m). No hay una teoría sólida para el signo (corredores antiguos y carga pesada podrían coincidir),
por eso se declara exploratoria y se interpreta solo con el IC.

Límites que condicionan toda lectura: (1) el inventario es de 2012: el 83 % de las inspecciones es de ese año y la última es de 2015, así que la edad y el estado se refieren a
esa fecha y el conjunto no se actualizó en 14 años; (2) no trae estado, calificación, capacidad de carga ni carga de diseño; (3) `tablero` figura como «superficie» en el diccionario
pero sus valores (5 a 12) se parecen a un ancho en metros: no se usa para conclusiones; (4) la fecha de construcción es un año; (5) solo red nacional, no vías departamentales ni municipales.
Salida: data/transporte/puentes_invias.json.
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from shapely.geometry import Point, shape

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cruces_peajes_secop as base  # noqa: E402
import cruces_seguridad_institucional as seg  # noqa: E402
import cruces_trafico_ani as ani  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
SALIDA = base.RAIZ / "data" / "transporte" / "puentes_invias.json"
ANIO_INVENTARIO = 2012
GRUPO_MATERIAL = {10: "Concreto simple/ciclópeo", 11: "Concreto simple/ciclópeo", 20: "Concreto reforzado", 21: "Concreto reforzado", 30: "Concreto presforzado", 31: "Concreto presforzado",
                  32: "Concreto presforzado", 50: "Acero", 51: "Acero y concreto", 60: "Piedra/ladrillo", 70: "Piedra/ladrillo"}
LONGITUDINAL = {10: "Simplemente apoyado", 11: "Simplemente apoyado", 20: "Viga continua", 21: "Viga continua", 30: "Viga Gerber", 31: "Viga Gerber", 40: "Pórtico", 41: "Pórtico",
                42: "Cajón (box culvert)", 50: "Colgante", 60: "Atirantado"}
TRANSVERSAL = {10: "Losa", 11: "Losa/viga", 12: "Losa/viga", 13: "Losa/viga", 14: "Losa/viga", 30: "Cajón", 31: "Cajón", 40: "Armadura", 41: "Armadura", 42: "Armadura",
               50: "Arco", 51: "Arco", 52: "Arco", 80: "Provisional (Bailey/Callender)", 81: "Provisional (Bailey/Callender)"}


def num(valor, defecto: float = float("nan")) -> float:
    try:
        return float(valor)
    except (TypeError, ValueError):
        return defecto


def cargar() -> list[dict]:
    """Convierte el texto de la fuente: el año viene como «2.015» (separador de miles) y la inspección como «2012.05.07» o «verificar»."""
    pol = [(base.norm(f["properties"].get("NOMBRE_DPT") or f["properties"]["DPTO_CNMBR"]), shape(f["geometry"]))
           for f in json.loads((base.CACHE / "dpto_mgn2018.geojson").read_text(encoding="utf-8"))["features"]]
    out = []
    for r in seg.soql("nsdj-ep2p", **{"$limit": 5000}):
        c = (r.get("point") or {}).get("coordinates")
        dep = None
        if c:
            pt = Point(*c)
            dep = next((n for n, g in pol if g.contains(pt)), None) or min(pol, key=lambda t: t[1].distance(pt))[0]
        insp = (r.get("fecha_de_inspecci_n") or "")[:4]
        out.append({"admin": "ANI" if (r.get("administrador") or "").startswith("ANI") else r.get("administrador", "?"),
                    "anio": int(round(num(r.get("fecha_de_construcci_n")) * 1000)), "insp": int(insp) if insp.isdigit() else None,
                    "material": GRUPO_MATERIAL.get(int(num(r.get("material"), -1)), "Otro/sin dato"),
                    "longitudinal": LONGITUDINAL.get(int(num(r.get("secci_n_longitudinal"), -1)), "Otro/sin dato"),
                    "transversal": TRANSVERSAL.get(int(num(r.get("secci_n_transversal"), -1)), "Otro/sin dato"),
                    "luz_max": num(r.get("luz_maxima"), 0.0), "luz_total": num(r.get("luz_total"), 0.0), "luces": num(r.get("luces"), 0.0), "dpto": dep})
    return out


def epoca(anio: int) -> str:
    return "antes de 1995" if anio < 1995 else "1995-2014" if anio < 2015 else "2015 en adelante"


def pct(parte: int, total: int) -> float:
    return 100 * parte / total if total else float("nan")


if __name__ == "__main__":
    rng = np.random.default_rng(base.SEMILLA)
    p = cargar()
    n = len(p)
    res: dict = {"n": n}
    print(f"{n} puentes; años de construcción {min(x['anio'] for x in p)}-{max(x['anio'] for x in p)}; sin año válido: {sum(not 1900 <= x['anio'] <= 2030 for x in p)}")
    for campo in ("admin", "material", "longitudinal", "transversal"):
        c = Counter(x[campo] for x in p)
        res[campo] = {k: v for k, v in c.most_common()}
        print(f"\n{campo}: " + "; ".join(f"{k} {v} ({pct(v, n):.1f} %)" for k, v in c.most_common()))
    e = Counter(epoca(x["anio"]) for x in p)
    res["epoca"] = dict(e)
    print("\népoca de construcción:", {k: f"{v} ({pct(v, n):.1f} %)" for k, v in e.items()})
    for a in ("INVIAS", "ANI"):
        s = [x for x in p if x["admin"] == a]
        ea = Counter(epoca(x["anio"]) for x in s)
        res[f"epoca_{a}"] = dict(ea)
        print(f"  {a}: n={len(s)}  antes de 1995 {pct(ea['antes de 1995'], len(s)):.1f} %  mediana de año {int(np.median([x['anio'] for x in s]))}")
    ins = Counter(x["insp"] for x in p)
    res["inspeccion"] = {str(k): v for k, v in ins.items()}
    print("\naño de última inspección:", dict(sorted(ins.items(), key=lambda kv: (kv[0] is None, kv[0]))))
    print(f"edad en {ANIO_INVENTARIO}: mediana {np.median([ANIO_INVENTARIO - x['anio'] for x in p if x['anio'] <= ANIO_INVENTARIO]):.0f} años; con más de 50 años: "
          f"{pct(sum(ANIO_INVENTARIO - x['anio'] > 50 for x in p), n):.1f} %")
    prov = [x for x in p if x["transversal"].startswith("Provisional")]
    res["provisionales"] = {"n": len(prov), "luz_media": float(np.mean([x["luz_max"] for x in prov])) if prov else None, "antes_de_1995_pct": pct(sum(x["anio"] < 1995 for x in prov), len(prov))}
    print(f"provisionales (Bailey/Callender-Hamilton): {len(prov)} ({pct(len(prov), n):.1f} %), construidos antes de 1995: {res['provisionales']['antes_de_1995_pct']:.0f} %")
    print(f"\n{'material':26s}{'n':>6s}{'luz máx p50':>13s}{'p90':>7s}{'p99':>7s}{'máx':>7s}")
    res["luz_por_material"] = {}
    for m in sorted(set(x["material"] for x in p), key=lambda k: -sum(x["material"] == k for x in p)):
        v = np.array([x["luz_max"] for x in p if x["material"] == m and x["luz_max"] > 0])
        if len(v) >= 10:
            res["luz_por_material"][m] = {"n": int(len(v)), "p50": float(np.percentile(v, 50)), "p90": float(np.percentile(v, 90)), "p99": float(np.percentile(v, 99)), "max": float(v.max())}
            print(f"{m:26s}{len(v):6d}{np.percentile(v, 50):13.1f}{np.percentile(v, 90):7.1f}{np.percentile(v, 99):7.1f}{v.max():7.1f}")
    print(f"luz máxima = 0 en {sum(x['luz_max'] <= 0 for x in p)} puentes ({pct(sum(x['luz_max'] <= 0 for x in p), n):.1f} %)")
    dep: dict[str, list[dict]] = defaultdict(list)
    for x in p:
        dep[x["dpto"]].append(x)
    res["departamentos"] = {d: {"n": len(v), "pct_antes_1995": pct(sum(x["anio"] < 1995 for x in v), len(v)), "pct_provisional": pct(sum(x["transversal"].startswith("Prov") for x in v), len(v))}
                            for d, v in dep.items()}
    # prueba exploratoria
    mezcla = base.cargar_mezcla(2011)
    p11 = {d: float(np.vstack(v)[:, 3:].sum() / np.vstack(v).sum()) for d, v in mezcla.items()}
    d24, _, _ = ani.por_departamento(ani.trafico_ani(2024), ani.ubicacion_peajes())
    h24 = {d: ani.pesados(v) for d, v in d24.items() if not np.isnan(ani.pesados(v))}
    print("\n== Exploratoria: % puentes anteriores a 1995 vs % pesados (departamentos con >= 10 puentes)")
    ps, rr = [], {}
    for nombre, serie in (("INVIAS 2011", p11), ("ANI 2024", h24)):
        ds = sorted(d for d in serie if d in res["departamentos"] and res["departamentos"][d]["n"] >= 10)
        r = base.spearman_boot(np.array([res["departamentos"][d]["pct_antes_1995"] for d in ds]), np.array([serie[d] for d in ds]), rng, 5000)
        rr[nombre] = r
        ps.append(r["p_perm"])
        print(f"{nombre:12s} n={r['n']:2d} rho={r['rho']:.2f} IC95 ({r['ic95'][0]:.2f}, {r['ic95'][1]:.2f}) p_perm={r['p_perm']:.3f}")
    holm, previo = [], 0.0
    for i, pv in enumerate(sorted(ps)):
        previo = max(previo, min(1.0, pv * (len(ps) - i)))
        holm.append(previo)
    res["exploratoria"] = rr
    res["p_holm"] = holm
    print("p Holm:", [round(h, 3) for h in holm])
    print("\ndepartamentos con más puentes:", sorted(((len(v), d) for d, v in dep.items()), reverse=True)[:6])
    SALIDA.write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
