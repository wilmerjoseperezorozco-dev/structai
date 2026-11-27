"""H7 (#273): ¿cuánto vale conocer el nivel freático antes de diseñar pilotes en suelo granular?

Prerregistro: validacion/PRERREGISTRO_H7_NIVEL_FREATICO.md.
Políticas de diseño (nivel freático supuesto, NF):
  optimista     sin dato: se diseña sin nivel freático (perfil seco)
  conservadora  sin dato: NF en la superficie (0 m)
  alarma        regla de relieve de H2b: NF = 0 si hay alarma; si no, perfil seco
  piezometro    se mide: NF real
NF real: niveles estáticos medidos (SGC, llanura: Meta, Guaviare, Inírida, Casanare), condicionados a la alarma.
Para cada política: longitud diseñada L (Q_adm(L; NF supuesto) ≥ Q), capacidad real Q_adm(L; NF real) y costo.
Uso:
  python -I validacion/h7_valor_nivel_freatico.py --conteo   # respuesta del motor al NF (sin niveles reales)
  python -I validacion/h7_valor_nivel_freatico.py            # análisis -> h7_resultados.json
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent))
sys.path.insert(0, str(AQUI.parents[1] / "contrato-motor"))

import h1_punto_equilibrio as h1  # noqa: E402
from src.axial import Pilote  # noqa: E402
from src.mixto import capacidad_mixta  # noqa: E402

SALIDA = AQUI / "h7_resultados.json"
NIVELES = json.loads((AQUI / "niveles_freaticos_llanura_sgc.json").read_text(encoding="utf-8"))["puntos"]
PERFILES = ("arena", "mixto")
NF_REJILLA = [round(0.5 * i, 1) for i in range(0, 41)]   # 0 a 20 m; > 20 m se trata como seco
N_PILOTES = 30
REF_EXPLORACION = 10 * 973768   # 10 m de "perforación de prueba para pilote" INVIAS 621.3.1 (referencia alta)
DEFICIT = (0.9, 0.8)
N_BOOT, SEMILLA = 2000, 7273


def q_adm(perfil, pil, L, nf):
    sec, b, tipo = h1.PILOTES[pil][:3]
    return capacidad_mixta(h1.PERFILES[perfil], Pilote(seccion=sec, ancho_m=b, longitud_m=L, tipo=tipo),
                           nivel_freatico_m=nf, combinacion="cm_cv_normal")["q_adm_kn"]


class Curvas:
    """Q_adm(L, NF) en rejilla, con caché."""
    def __init__(self, perfil, pil):
        self.perfil, self.pil, self.c = perfil, pil, {}
        self.Ls = [h1.L_MIN + h1.PASO * i for i in range(int((h1.L_MAX - h1.L_MIN) / h1.PASO) + 1)]

    def q(self, L, nf):
        k = (L, nf)
        if k not in self.c:
            self.c[k] = q_adm(self.perfil, self.pil, L, nf)
        return self.c[k]

    def L(self, Q, nf):
        for L in self.Ls:
            if self.q(L, nf) >= Q:
                return L
        return None


def nf_rejilla(nivel):
    return None if nivel > NF_REJILLA[-1] else min(NF_REJILLA, key=lambda x: abs(x - nivel))


def evaluar(cur: Curvas, Q, puntos, alarma_de) -> dict | None:
    p_m = h1.PRECIOS[h1.PILOTES[cur.pil][3]]["p50"]
    L_seco, L_cero = cur.L(Q, None), cur.L(Q, 0.0)
    if L_seco is None or L_cero is None:
        return None
    res = {}
    for pol in ("optimista", "conservadora", "alarma", "piezometro"):
        Ls, ratios = [], []
        for nivel, alarma, *_ in puntos:
            nf = nf_rejilla(nivel)
            if pol == "optimista":
                L = L_seco
            elif pol == "conservadora":
                L = L_cero
            elif pol == "alarma":
                L = L_cero if alarma else L_seco
            else:
                L = cur.L(Q, nf) or h1.L_MAX
            Ls.append(L)
            ratios.append(cur.q(L, nf) / Q)
        res[pol] = {"E_L": sum(Ls) / len(Ls), "costo": N_PILOTES * p_m * sum(Ls) / len(Ls),
                    **{f"p_deficit_{int(d * 100)}": sum(r < d for r in ratios) / len(ratios) for d in DEFICIT}}
    res["L_seco"], res["L_nf0"] = L_seco, L_cero
    res["voi_vs_conservadora"] = res["conservadora"]["costo"] - res["piezometro"]["costo"]
    res["voi_vs_alarma"] = res["alarma"]["costo"] - res["piezometro"]["costo"]
    return res


def resumen(curvas, puntos):
    out = []
    for (perfil, pil), cur in curvas.items():
        for Q in h1.PILOTES[pil][5]:
            e = evaluar(cur, Q, puntos, None)
            if e:
                out.append({"perfil": perfil, "pilote": pil, "q_kn": Q, **e})
    return out


def agregados(esc):
    m = lambda f: sum(f(e) for e in esc) / len(esc)   # noqa: E731
    return {"p_deficit_90_optimista": m(lambda e: e["optimista"]["p_deficit_90"]),
            "p_deficit_80_optimista": m(lambda e: e["optimista"]["p_deficit_80"]),
            "p_deficit_90_alarma": m(lambda e: e["alarma"]["p_deficit_90"]),
            "sobrecosto_conservadora_vs_piezometro": m(lambda e: e["voi_vs_conservadora"] / e["piezometro"]["costo"]),
            "voi_vs_conservadora_cop": m(lambda e: e["voi_vs_conservadora"]),
            "voi_vs_alarma_cop": m(lambda e: e["voi_vs_alarma"])}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    curvas = {(p, pil): Curvas(p, pil) for p in PERFILES for pil in h1.COMBOS[p]}
    if "--conteo" in sys.argv:
        for (p, pil), cur in curvas.items():
            for Q in h1.PILOTES[pil][5]:
                print(p, pil, Q, {nf: cur.L(Q, nf) for nf in (None, 10.0, 5.0, 2.0, 1.0, 0.0)})
        print("puntos de nivel:", len(NIVELES), "con alarma:", sum(x[1] for x in NIVELES))
        return
    rng = random.Random(SEMILLA)
    out = {"prerregistro": "validacion/PRERREGISTRO_H7_NIVEL_FREATICO.md", "n_pilotes": N_PILOTES,
           "referencia_exploracion_cop": REF_EXPLORACION}
    for nombre, pts in (("todos", NIVELES), ("con_alarma", [x for x in NIVELES if x[1]]),
                        ("sin_alarma", [x for x in NIVELES if not x[1]])):
        esc = resumen(curvas, pts)
        bloques = sorted({x[2] for x in pts})
        por_b = {b: [x for x in pts if x[2] == b] for b in bloques}
        vals = {k: [] for k in agregados(esc)}
        for _ in range(N_BOOT // 10):   # cada réplica reevalúa el motor en caché; 200 réplicas
            muestra = [x for b in rng.choices(bloques, k=len(bloques)) for x in por_b[b]]
            for k, v in agregados(resumen(curvas, muestra)).items():
                vals[k].append(v)
        ic = {k: [sorted(v)[int(0.025 * len(v))], sorted(v)[int(0.975 * len(v)) - 1]] for k, v in vals.items()}
        out[nombre] = {"n_puntos": len(pts), "n_bloques": len(bloques), "agregados": agregados(esc), "ic95": ic,
                       "escenarios": esc}
    SALIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items() if kk != "escenarios"})
                      for k, v in out.items()}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
