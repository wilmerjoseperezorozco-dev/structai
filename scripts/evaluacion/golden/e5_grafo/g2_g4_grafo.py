"""
Issue #186, experimentos G2 y G4 sobre el grafo de referencias cruzadas de la
NSR-10 (normas_referencias_cruzadas). Solo lectura en Supabase, sin LLM.

Grafo: nodos = numerales (A.3, C.21.6...). Una arista va del numeral del chunk
que cita al numeral citado. El numeral de origen es numeral_fuente o, si falta,
se deriva del id del chunk (NSR10-C-C_21_6_3-sub3 -> C.21.6.3).

G2. Priorización de huecos de ingesta
  - Los numerales citados con resolución 'sin_destino' se RE-VERIFICAN contra el
    corpus actual (pudieron ingerirse después de construir el grafo).
  - Para los que siguen faltando: citas recibidas, PageRank y si algún motor
    determinista los usa en su código. motor-aquai se excluye del cruce: sus
    numerales (B.7, D.3.5...) son del RAS / Res. 0330, no de la NSR-10.
  - Pareto: cuántos numerales cubren el 80 % de las citas a huecos.

G4. Comunidades vs taxonomía
  - Louvain sobre el grafo no dirigido de numerales (semilla fija).
  - Información mutua ajustada (AMI) entre comunidades y (a) título NSR-10,
    (b) dominio de StructAI según FUENTES_DOMINIO (H y A.2 -> geopot;
    E y A.10 -> vulnerabilidad_vivienda; resto -> normativa_general).
  - Prueba de permutación (1.000 barajadas de etiquetas) para cada AMI.
  - Comunidades mixtas (puentes entre títulos o dominios).

Salidas: resultados_g2_g4.json e INFORME_G2_G4.md en esta carpeta.
Uso: python scripts/evaluacion/golden/e5_grafo/g2_g4_grafo.py
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx
import numpy as np
from dotenv import load_dotenv
from sklearn.metrics import adjusted_mutual_info_score

RAIZ = Path(__file__).resolve().parents[4]
load_dotenv(RAIZ / "apps" / "api" / ".env")
sys.path.insert(0, str(RAIZ / "packages" / "construdata"))
import os  # noqa: E402

from supabase import create_client  # noqa: E402

AQUI = Path(__file__).parent
SEMILLA = 169
N_PERM = 1000
RE_ID = re.compile(r"^NSR10-([A-K])-\1_(\d+(?:_\d+)*)")
RE_NUM = re.compile(r"\b([A-K])\.(\d+(?:\.\d+)*)\b")
RE_SECC = re.compile(r"^\s*([A-Ka-k])[.\-](\d+(?:\.\d+)*)")
# Motores cuyos numerales NO son de la NSR-10 (espacio de nombres distinto).
MOTORES_OTRA_NORMA = {"motor-aquai"}

sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])


def paginar(tabla, cols):
    filas, off = [], 0
    while True:
        d = sb.table(tabla).select(cols).range(off, off + 999).execute().data
        filas += d
        off += 1000
        if len(d) < 1000:
            return filas


def norm(n: str | None) -> str | None:
    if not n:
        return None
    return n.strip().upper().rstrip(".-")


def numeral_de_chunk(cid: str, numeral_fuente: str | None) -> str | None:
    if numeral_fuente:
        return norm(numeral_fuente)
    m = RE_ID.match(cid)
    return f"{m.group(1)}.{m.group(2).replace('_', '.')}" if m else None


def titulo(n: str) -> str:
    return n[0]


def dominio(n: str) -> str:
    if n.startswith("H.") or n == "H" or n.startswith("A.2.") or n == "A.2":
        return "geopot"
    if n.startswith("E.") or n.startswith("A.10"):
        return "vulnerabilidad_vivienda"
    return "normativa_general"


def relacionados(hueco: str, del_motor: str) -> bool:
    """Coincidencia exacta, o relación de prefijo solo si el numeral más corto
    tiene al menos 3 niveles (F.4.2). Primera versión: con prefijo libre, un
    "F.4" genérico en el código de motor-acero-frio se relacionaba con todos los
    F.4.x faltantes e inflaba la cuenta."""
    if hueco == del_motor:
        return True
    corto, largo = sorted((hueco, del_motor), key=len)
    return corto.count(".") >= 2 and largo.startswith(corto + ".")


def numerales_de_motores() -> dict[str, set[str]]:
    out = {}
    for d in sorted((RAIZ / "packages").glob("motor-*")):
        if d.name in MOTORES_OTRA_NORMA or not (d / "src").exists():
            continue
        nums = set()
        for f in (d / "src").rglob("*.py"):
            nums |= {f"{m.group(1)}.{m.group(2)}" for m in RE_NUM.finditer(f.read_text(encoding="utf-8", errors="ignore"))}
        if nums:
            out[d.name] = nums
    return out


def ami_con_permutacion(comunidades, etiquetas, rng):
    obs = adjusted_mutual_info_score(etiquetas, comunidades)
    etq = np.array(etiquetas)
    nulos = [adjusted_mutual_info_score(rng.permutation(etq), comunidades) for _ in range(N_PERM)]
    p = (1 + sum(n >= obs for n in nulos)) / (1 + N_PERM)
    return {"ami": round(float(obs), 4), "ami_nulo_p95": round(float(np.quantile(nulos, 0.95)), 4), "p_permutacion": round(p, 4)}


def main():
    aristas = paginar("normas_referencias_cruzadas", "fuente_chunk_id,numeral_fuente,numeral_destino,resolucion")
    chunks = paginar("nsr10_chunks", "id,seccion")

    # numerales que existen HOY en el corpus (por id derivado o por sección)
    existentes = set()
    for c in chunks:
        m = RE_ID.match(c["id"])
        if m:
            existentes.add(f"{m.group(1)}.{m.group(2).replace('_', '.')}")
        s = RE_SECC.match(c.get("seccion") or "")
        if s:
            existentes.add(f"{s.group(1).upper()}.{s.group(2)}")

    def existe_hoy(n):
        return n in existentes or any(e.startswith(n + ".") for e in existentes)

    G = nx.DiGraph()
    sin_origen = 0
    for a in aristas:
        src = numeral_de_chunk(a["fuente_chunk_id"], a["numeral_fuente"])
        dst = norm(a["numeral_destino"])
        if not src or not dst:
            sin_origen += 1
            continue
        if src == dst:
            continue
        w = G.get_edge_data(src, dst, {}).get("weight", 0)
        G.add_edge(src, dst, weight=w + 1)
    pr = nx.pagerank(G, alpha=0.85, weight="weight")

    # ── G2 ──────────────────────────────────────────────────────────────────
    citas_hueco = Counter(norm(a["numeral_destino"]) for a in aristas if a["resolucion"] == "sin_destino")
    motores = numerales_de_motores()
    huecos = []
    for n, citas in citas_hueco.items():
        sigue = not existe_hoy(n)
        usan = sorted(m for m, nums in motores.items() if any(relacionados(n, x) for x in nums))
        huecos.append({"numeral": n, "titulo": titulo(n), "citas": citas, "pagerank": round(pr.get(n, 0.0), 5),
                       "sigue_faltando": sigue, "motores_que_lo_usan": usan})
    faltan = sorted([h for h in huecos if h["sigue_faltando"]],
                    key=lambda h: (-len(h["motores_que_lo_usan"]), -h["citas"], -h["pagerank"]))
    total_citas = sum(h["citas"] for h in faltan)
    acum, k80 = 0, 0
    for i, h in enumerate(sorted(faltan, key=lambda h: -h["citas"]), 1):
        acum += h["citas"]
        if acum >= 0.8 * total_citas:
            k80 = i
            break
    g2 = {"numerales_sin_destino": len(huecos), "citas_sin_destino": sum(citas_hueco.values()),
          "ya_existen_hoy": sum(not h["sigue_faltando"] for h in huecos),
          "siguen_faltando": len(faltan), "citas_a_huecos_vigentes": total_citas,
          "pareto_80": {"k": k80, "de": len(faltan)},
          "huecos_usados_por_motores": [h for h in faltan if h["motores_que_lo_usan"]],
          "top": faltan[:20], "por_titulo": dict(Counter(h["titulo"] for h in faltan).most_common()),
          "motores_analizados": {m: len(v) for m, v in motores.items()}, "motores_excluidos": sorted(MOTORES_OTRA_NORMA)}

    # ── G4 ──────────────────────────────────────────────────────────────────
    U = G.to_undirected()
    comps = list(nx.connected_components(U))
    comunidades = nx.community.louvain_communities(U, weight="weight", seed=SEMILLA)
    mod = nx.community.modularity(U, comunidades, weight="weight")
    nodo_com = {n: i for i, c in enumerate(comunidades) for n in c}
    nodos = sorted(U.nodes)
    com = [nodo_com[n] for n in nodos]
    rng = np.random.default_rng(SEMILLA)
    ami_tit = ami_con_permutacion(com, [titulo(n) for n in nodos], rng)
    ami_dom = ami_con_permutacion(com, [dominio(n) for n in nodos], rng)

    def composicion(c, f):
        return dict(Counter(f(n) for n in c).most_common())

    detalle = []
    for i, c in sorted(enumerate(comunidades), key=lambda x: -len(x[1])):
        tit, dom = composicion(c, titulo), composicion(c, dominio)
        pureza = max(tit.values()) / len(c)
        centrales = sorted(c, key=lambda n: -pr.get(n, 0))[:5]
        detalle.append({"comunidad": i, "n": len(c), "titulos": tit, "dominios": dom,
                        "pureza_titulo": round(pureza, 3), "mixta_titulos": len(tit) > 1, "mixta_dominios": len(dom) > 1,
                        "centrales": centrales})
    puentes = Counter()
    for a, b in U.edges:
        if dominio(a) != dominio(b):
            puentes[tuple(sorted((dominio(a), dominio(b))))] += 1
    g4 = {"nodos": U.number_of_nodes(), "aristas": U.number_of_edges(), "componentes_conexas": len(comps),
          "componente_mayor": max(len(c) for c in comps), "comunidades": len(comunidades),
          "modularidad": round(mod, 4), "ami_vs_titulo": ami_tit, "ami_vs_dominio": ami_dom,
          "pureza_titulo_ponderada": round(sum(d["pureza_titulo"] * d["n"] for d in detalle) / U.number_of_nodes(), 3),
          "comunidades_mixtas_titulo": sum(d["mixta_titulos"] for d in detalle),
          "comunidades_mixtas_dominio": sum(d["mixta_dominios"] for d in detalle),
          "aristas_puente_entre_dominios": {f"{a}<->{b}": n for (a, b), n in puentes.most_common()},
          "mayores": detalle[:12],
          "mixtas_dominio": [d for d in detalle if d["mixta_dominios"]][:12]}

    salida = {"aristas_leidas": len(aristas), "aristas_sin_origen": sin_origen,
              "grafo_numerales": {"nodos": G.number_of_nodes(), "aristas": G.number_of_edges()},
              "pagerank_top": [(n, round(v, 5)) for n, v in sorted(pr.items(), key=lambda x: -x[1])[:15]],
              "G2": g2, "G4": g4}
    (AQUI / "resultados_g2_g4.json").write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in salida.items() if k not in ("G2", "G4")}, ensure_ascii=False))
    print("G2:", json.dumps({k: g2[k] for k in ("numerales_sin_destino", "citas_sin_destino", "ya_existen_hoy", "siguen_faltando",
                                                "citas_a_huecos_vigentes", "pareto_80", "por_titulo", "motores_analizados")}, ensure_ascii=False))
    print("G2 huecos usados por motores:", [(h["numeral"], h["citas"], h["motores_que_lo_usan"]) for h in g2["huecos_usados_por_motores"]])
    print("G2 top 12:", [(h["numeral"], h["citas"], h["pagerank"]) for h in g2["top"][:12]])
    print("G4:", json.dumps({k: g4[k] for k in ("nodos", "aristas", "componentes_conexas", "componente_mayor", "comunidades", "modularidad",
                                                "ami_vs_titulo", "ami_vs_dominio", "pureza_titulo_ponderada", "comunidades_mixtas_titulo",
                                                "comunidades_mixtas_dominio", "aristas_puente_entre_dominios")}, ensure_ascii=False))
    for d in g4["mayores"][:8]:
        print(f"  com {d['comunidad']:3d} n={d['n']:3d} títulos={d['titulos']} dominios={d['dominios']} centrales={d['centrales']}")


if __name__ == "__main__":
    main()
