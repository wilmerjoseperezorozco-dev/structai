"""Mapa de sensibilidad de la lluvia a El Nino y La Nina en Colombia, 1981-2024 (CHIRPS v3.0 + ONI).
Diseno en PROTOCOLO_ANALISIS.md seccion 15, fijado antes de correr. Salidas: mapas_enso/*.png y
mapas_enso/enso_lluvia_municipios.csv.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parents[1] / "scripts" / "macro"))
import enso_energia as e  # noqa: E402  (oni(), ic(); configura la salida UTF-8)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon as MplPolygon
from shapely.geometry import shape

SALIDA = AQUI / "mapas_enso"
N_BOOT = 2000
BLOQUE = 12
RNG = np.random.default_rng(20261107)
REGIONES = {"Caribe": ["08", "13", "20", "23", "44", "47", "70"], "Andina": ["05", "11", "15", "17", "25", "41", "54", "63", "66", "68", "73"],
            "Pacifica": ["19", "27", "52", "76"], "Orinoquia": ["50", "81", "85", "99"], "Amazonia": ["18", "86", "91", "94", "95", "97"]}
DEP_A_REGION = {d: r for r, ds in REGIONES.items() for d in ds}


def cargar():
    a = json.loads((AQUI / "chirps_mensual_colombia_1981_2018.json").read_text(encoding="utf-8"))
    b = json.loads((AQUI / "chirps_mensual_colombia.json").read_text(encoding="utf-8"))
    comunes = sorted(set(a["municipios"]) & set(b["municipios"]))
    meses = a["meses"] + b["meses"]
    P = np.array([a["municipios"][c]["precip_mm"] + b["municipios"][c]["precip_mm"] for c in comunes], float)
    nombres = {c: a["municipios"][c]["nombre"] for c in comunes}
    return comunes, nombres, meses, P


def ajustar_todos(Z, X):
    """MCO para todos los municipios a la vez: Z (n_mun x T), X (T x k) -> coef (n_mun x k)."""
    return np.linalg.solve(X.T @ X, X.T @ Z.T).T


def main() -> None:
    SALIDA.mkdir(exist_ok=True)
    comunes, nombres, meses, P = cargar()
    nm, T = P.shape
    print(f"{nm} municipios x {T} meses ({meses[0]} a {meses[-1]})")
    mes_cal = np.array([int(m[5:]) for m in meses])
    Z = np.zeros_like(P)
    clim = np.zeros_like(P)
    for k in range(1, 13):
        c = mes_cal == k
        mu, sd = P[:, c].mean(1, keepdims=True), P[:, c].std(1, ddof=1, keepdims=True)
        sd[sd == 0] = np.nan
        Z[:, c] = (P[:, c] - mu) / sd
        clim[:, c] = mu
    ok_mun = ~np.isnan(Z).any(1)
    comunes = [c for c, o in zip(comunes, ok_mun) if o]
    Z, P, clim = Z[ok_mun], P[ok_mun], clim[ok_mun]
    nm = len(comunes)
    oni = e.oni()
    idx = pd.to_datetime([m + "-01" for m in meses])
    o = oni.reindex(idx).to_numpy(float)
    assert not np.isnan(o).any(), "faltan valores del ONI"
    NINO, NINA = np.maximum(o, 0), np.maximum(-o, 0)
    X = np.column_stack([np.ones(T), NINO, NINA])
    reg = np.array([DEP_A_REGION.get(c[:2], "otra") for c in comunes])
    regiones = [r for r in REGIONES if (reg == r).any()]
    print("Municipios por region:", {r: int((reg == r).sum()) for r in regiones})

    coef = ajustar_todos(Z, X)
    delta, gamma = coef[:, 1], coef[:, 2]
    zreg = {r: Z[reg == r].mean(0) for r in regiones}
    Zr = np.array([zreg[r] for r in regiones])

    # ---- bootstrap de bloques (mismo indice de tiempo para todos)
    nb = int(np.ceil(T / BLOQUE))
    bd, bg = np.zeros((N_BOOT, nm)), np.zeros((N_BOOT, nm))
    brd, brg = np.zeros((N_BOOT, len(regiones))), np.zeros((N_BOOT, len(regiones)))
    for b in range(N_BOOT):
        ini = RNG.integers(0, T - BLOQUE + 1, nb)
        ix = np.concatenate([np.arange(i, i + BLOQUE) for i in ini])[:T]
        Xb = X[ix]
        if np.linalg.matrix_rank(Xb) < 3:
            bd[b], bg[b], brd[b], brg[b] = np.nan, np.nan, np.nan, np.nan
            continue
        cb = ajustar_todos(Z[:, ix], Xb)
        bd[b], bg[b] = cb[:, 1], cb[:, 2]
        cr = ajustar_todos(Zr[:, ix], Xb)
        brd[b], brg[b] = cr[:, 1], cr[:, 2]
    lo_d, hi_d = np.nanpercentile(bd, [2.5, 97.5], axis=0)
    lo_g, hi_g = np.nanpercentile(bg, [2.5, 97.5], axis=0)

    # ---- resumen regional (confirmatorios)
    cr = ajustar_todos(Zr, X)
    print("\n== CONFIRMATORIOS POR REGION (z por 1 C de ONI; IC95 % de bloques sobre la serie regional) ==")
    print(f"{'region':<10}{'n':>5}{'delta (El Nino)':>22}{'R1':>5}{'gamma (La Nina)':>22}{'R2':>5}{'|d|-|g|':>9}{'IC asimetria':>20}{'R3':>5}")
    resumen = {}
    for i, r in enumerate(regiones):
        d, g = cr[i, 1], cr[i, 2]
        ld, hd = np.nanpercentile(brd[:, i], [2.5, 97.5])
        lg, hg = np.nanpercentile(brg[:, i], [2.5, 97.5])
        asim = np.abs(brd[:, i]) - np.abs(brg[:, i])
        la, ha = np.nanpercentile(asim, [2.5, 97.5])
        r1, r2, r3 = hd < 0, lg > 0, (la > 0 or ha < 0)
        resumen[r] = dict(delta=d, gamma=g, r1=bool(r1), r2=bool(r2), r3=bool(r3), asim=abs(d) - abs(g), ic_asim=[la, ha])
        print(f"{r:<10}{int((reg == r).sum()):>5}{d:>+9.2f} [{ld:+.2f},{hd:+.2f}]{'SI' if r1 else 'no':>5}{g:>+9.2f} [{lg:+.2f},{hg:+.2f}]{'SI' if r2 else 'no':>5}"
              f"{abs(d) - abs(g):>+9.2f}  [{la:+.2f},{ha:+.2f}]{'SI' if r3 else 'no':>5}")

    # ---- validacion reservada
    print("\n== VALIDACION RESERVADA (ajuste 1981-2010, prueba 2011-2024): R2 fuera de muestra de la serie regional ==")
    tr = np.array([m[:4] <= "2010" for m in meses])
    nt = int((~tr).sum())
    print(f"{'region':<10}{'R2 fuera de muestra':>22}{'IC95% bloques':>20}   ENSO explica la lluvia (regla fija)")
    for i, r in enumerate(regiones):
        coef_tr = np.linalg.lstsq(X[tr], Zr[i][tr], rcond=None)[0]
        err_m = (Zr[i][~tr] - X[~tr] @ coef_tr) ** 2
        err_c = Zr[i][~tr] ** 2
        r2 = 1 - err_m.sum() / err_c.sum()
        bs = []
        for _ in range(N_BOOT):
            ini = RNG.integers(0, nt - BLOQUE + 1, int(np.ceil(nt / BLOQUE)))
            ix = np.concatenate([np.arange(a, a + BLOQUE) for a in ini])[:nt]
            bs.append(1 - err_m[ix].sum() / err_c[ix].sum())
        lo, hi = np.percentile(bs, [2.5, 97.5])
        s = (resumen[r]["r1"] or resumen[r]["r2"]) and lo > 0
        resumen[r]["r2_oos"], resumen[r]["ic_oos"], resumen[r]["explica"] = r2, [lo, hi], bool(s)
        print(f"{r:<10}{r2:>+22.3f}   [{lo:+.3f}, {hi:+.3f}]   {'SI' if s else 'NO'}")

    # ---- significancia de campo
    sig_d = (hi_d < 0).mean()
    sig_g = (lo_g > 0).mean()
    print(f"\nSignificancia de campo: {100 * sig_d:.0f} % de los municipios con delta < 0 y IC que excluye 0; {100 * sig_g:.0f} % con gamma > 0 (azar: ~2,5 % por cola; "
          "municipios vecinos comparten pixeles: no son pruebas independientes)")
    for r in regiones:
        m = reg == r
        print(f"   {r:<10} delta<0 robusto: {100 * (hi_d[m] < 0).mean():>3.0f} % | gamma>0 robusto: {100 * (lo_g[m] > 0).mean():>3.0f} % | delta mediano {np.median(delta[m]):+.2f}, gamma mediano {np.median(gamma[m]):+.2f}")

    # ---- rezagos (descriptivo)
    print("\n== REZAGOS 0-3 (descriptivo): delta y gamma de la serie regional ==")
    for i, r in enumerate(regiones):
        fila = []
        for L in range(4):
            o2 = pd.Series(o).shift(L).fillna(0).to_numpy()
            X2 = np.column_stack([np.ones(T), np.maximum(o2, 0), np.maximum(-o2, 0)])
            c2 = np.linalg.lstsq(X2, Zr[i], rcond=None)[0]
            fila.append(f"L{L}: d={c2[1]:+.2f} g={c2[2]:+.2f}")
        print(f"   {r:<10} " + " | ".join(fila))

    # ---- episodios
    print("\n== EPISODIOS (|ONI| >= 0.5 durante >= 5 meses): desviacion % de la lluvia regional respecto de su climatologia ==")
    P_reg = {r: P[reg == r].sum(0) for r in regiones}
    C_reg = {r: clim[reg == r].sum(0) for r in regiones}
    eps = []
    for signo, nombre in [(1, "El Nino"), (-1, "La Nina")]:
        act = signo * o >= 0.5
        i = 0
        while i < T:
            if act[i]:
                j = i
                while j + 1 < T and act[j + 1]:
                    j += 1
                if j - i + 1 >= 5:
                    eps.append((nombre, i, j))
                i = j + 1
            else:
                i += 1
    eps.sort(key=lambda x: x[1])
    print(f"   {'fase':<8}{'periodo':<18}{'ONI pico':>9}" + "".join(f"{r:>11}" for r in regiones))
    for nombre, i, j in eps:
        pico = o[i:j + 1][np.argmax(np.abs(o[i:j + 1]))]
        dev = [100 * (P_reg[r][i:j + 1].sum() / C_reg[r][i:j + 1].sum() - 1) for r in regiones]
        print(f"   {nombre:<8}{meses[i]} a {meses[j]:<9}{pico:>+9.1f}" + "".join(f"{x:>+10.0f}%" for x in dev))

    # ---- mapas
    print("\nGenerando mapas...")
    geoms = {}
    for d in sorted({c[:2] for c in comunes}):
        f = AQUI / "_cache" / f"poligonos_nac_{d}.geojson"
        if f.exists():
            for ft in json.loads(f.read_text(encoding="utf-8"))["features"]:
                g = shape(ft["geometry"])
                geoms[ft["properties"]["CODIGO"]] = g.buffer(0)

    def parches(vals):
        ps, vs = [], []
        for c, v in zip(comunes, vals):
            g = geoms.get(c)
            if g is None or np.isnan(v):
                continue
            pol = g if g.geom_type == "Polygon" else max(g.geoms, key=lambda x: x.area)
            ps.append(MplPolygon(np.array(pol.exterior.coords), closed=True))
            vs.append(v)
        return ps, np.array(vs)

    fig, axs = plt.subplots(2, 3, figsize=(17, 12))
    lim = np.nanpercentile(np.abs(np.concatenate([delta, gamma])), 98)
    paneles = [("Efecto de El Nino (delta, z por C)\nazul/negativo = seca", delta, "RdBu", -lim, lim),
               ("Efecto de La Nina (gamma, z por C)\nazul/positivo = moja", gamma, "RdBu_r", -lim, lim),
               ("Asimetria |delta| - |gamma|\nrojo = pesa mas El Nino", np.abs(delta) - np.abs(gamma), "PuOr", -lim, lim)]
    for k, (tit, v, cmap, lo, hi) in enumerate(paneles):
        ps, vs = parches(v)
        pc = PatchCollection(ps, cmap=cmap, edgecolor="0.6", linewidth=0.1)
        pc.set_array(vs); pc.set_clim(lo, hi)
        axs[0, k].add_collection(pc); axs[0, k].autoscale(); axs[0, k].set_aspect("equal"); axs[0, k].axis("off"); axs[0, k].set_title(tit, fontsize=10)
        plt.colorbar(pc, ax=axs[0, k], shrink=0.6)
    masks = [("Municipios con delta<0 y IC (bloques) que excluye 0", (hi_d < 0).astype(float)),
             ("Municipios con gamma>0 y IC (bloques) que excluye 0", (lo_g > 0).astype(float)),
             ("Municipios con asimetria |d|-|g| distinta de 0 (IC)", np.zeros(nm))]
    asim_b = np.abs(bd) - np.abs(bg)
    la, ha = np.nanpercentile(asim_b, [2.5, 97.5], axis=0)
    masks[2] = (masks[2][0], ((la > 0) | (ha < 0)).astype(float))
    for k, (tit, v) in enumerate(masks):
        ps, vs = parches(v)
        pc = PatchCollection(ps, cmap="Greys", edgecolor="0.7", linewidth=0.1)
        pc.set_array(vs); pc.set_clim(0, 1.3)
        axs[1, k].add_collection(pc); axs[1, k].autoscale(); axs[1, k].set_aspect("equal"); axs[1, k].axis("off")
        axs[1, k].set_title(f"{tit}\n({100 * vs.mean():.0f} % de los municipios)", fontsize=10)
    fig.suptitle("Sensibilidad de la lluvia mensual (CHIRPS v3.0, 1981-2024) a El Nino y La Nina por municipio. Descriptivo: municipios vecinos comparten pixeles de 5 km", fontsize=11)
    fig.tight_layout()
    fig.savefig(SALIDA / "mapa_enso_lluvia.png", dpi=105)
    pd.DataFrame({"codigo": comunes, "municipio": [nombres[c] for c in comunes], "region": reg, "delta_nino": delta, "ic_delta_lo": lo_d, "ic_delta_hi": hi_d,
                  "gamma_nina": gamma, "ic_gamma_lo": lo_g, "ic_gamma_hi": hi_g}).to_csv(SALIDA / "enso_lluvia_municipios.csv", index=False)
    (SALIDA / "enso_lluvia_resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Guardado en", SALIDA)
    print("\nLIMITES: ~11 episodios por fase; CHIRPS de los 80 menos preciso; ~5 km; el ONI no captura el Atlantico/Caribe; correlacion espacial entre municipios; "
          "no se modelan MJO ni NAO.")


if __name__ == "__main__":
    main()
