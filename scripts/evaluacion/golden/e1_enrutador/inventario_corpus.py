"""
Issue #170, fase 1: inventario completo de normas y datos de StructAI, solo
lectura, con la matriz norma -> dominios que la usan.

La pertenencia de cada norma a un dominio NO se declara aquí: se calcula con
las mismas reglas que usa la recuperación (FUENTES_DOMINIO, _norma_empieza y
prefijos de chunk_id en rag_multi_norma.py). Así el inventario y la
recuperación no pueden divergir. Todo lo de nsr10_chunks y ntc_chunks
pertenece además a normativa_general (búsqueda global).

Las tablas de datos estructurados (precios, SGC, IDEAM...) se consumen en
ramas propias del código, no por FUENTES_DOMINIO; su dominio consumidor se
declara en DATOS_ESTRUCTURADOS, con la función que las lee.

Salidas: inventario_corpus.json e INVENTARIO_CORPUS.md (en esta carpeta).
Conteos exactos (count="exact"); nunca list_tables (ver CLAUDE.md).

Uso: python scripts/evaluacion/golden/e1_enrutador/inventario_corpus.py
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import e1_enrutador as e

r = e.r
NG = e.NG
AQUI = Path(__file__).parent

# tabla -> (dominio que la consume, dónde se lee). Verificable con grep.
DATOS_ESTRUCTURADOS = {
    "apu_precios_referencia": ("apu_precios", "buscar_precios_apu"),
    "apu_insumos_referencia": ("apu_precios", "buscar_precios_apu"),
    "apu_items_nacional": ("apu_precios", "precios nacionales MiPymes"),
    "apu_precios_nacional_detalle": ("apu_precios", "precios nacionales MiPymes"),
    "invias_actividades": ("apu_precios+vias", "buscar_precios_invias_vias"),
    "invias_insumos_precios": ("apu_precios+vias", "buscar_precios_invias_vias"),
    "invias_provincias": ("apu_precios+vias", "buscar_precios_invias_vias"),
    "sgc_amenaza_sismica_municipios": ("geopot+aquai+vivienda+NG", "sgc_amenaza_sismica"),
    "nsr10_apendice_a4_municipios": ("geopot", "Apéndice A-4 municipal"),
    "microzonificacion_sismica_local": ("geopot", "microzonificacion_local"),
    "igac_suelos_ufh": ("geopot", "igac_client"),
    "ideam_estaciones_caudal": ("aquai", "ideam_client"),
    "ideam_caudal_historico": ("aquai", "ideam_client"),
    "ideam_caudal_estadisticas_mes": ("aquai", "ideam_client"),
    "sisben_vulnerabilidad_vivienda_municipio": ("vulnerabilidad_vivienda", "_bloque_vulnerabilidad_vivienda"),
    "ungrd_emergencias": ("geopot+NG", "informe de sitio"),
    "peru_e030_zonificacion_distrital": ("peru_e030", "pais_zonificacion"),
    "ecuador_nec_se_ds_zonificacion_poblacion": ("ecuador_nec_se_ds", "pais_zonificacion"),
    "normas_registro": ("todos (vigencia)", "metadata de búsqueda"),
    "normas_modificaciones": ("todos (vigencia)", "vigilancia normativa"),
    "normas_referencias_cruzadas": ("todos", "referencias cruzadas"),
    "noticias_relevantes": ("NG (actualidad)", "_bloque_contexto_noticias"),
}


def contar(tabla: str):
    try:
        return r.sb.table(tabla).select("*", count="exact").limit(1).execute().count
    except Exception as ex:  # noqa: BLE001
        return f"error: {str(ex)[:80]}"


def paginar(tabla: str, columnas: str) -> list[dict]:
    filas, off = [], 0
    while True:
        d = r.sb.table(tabla).select(columnas).range(off, off + 999).execute().data
        filas += d
        off += 1000
        if len(d) < 1000:
            return filas


def unidad_nsr10(cid: str) -> str:
    """Unidad de inventario de un chunk de nsr10_chunks: título NSR-10 o documento."""
    m = re.match(r"^NSR10-([A-Z]+)-", cid)
    if m:
        return f"NSR-10 Título {m.group(1)}" if m.group(1) != "ALCANCE" else "NSR-10 Alcance"
    return re.match(r"^([A-Za-z0-9]+)", cid).group(1) if re.match(r"^([A-Za-z0-9]+)", cid) else cid


def dominios_nsr10(cid: str) -> set[str]:
    ds = {NG}
    for d, fuentes in r.FUENTES_DOMINIO.items():
        for tipo, valor in fuentes:
            if tipo == "nsr10_prefijos" and cid.startswith(valor):
                ds.add(d)
    return ds


def dominios_ntc(norma: str) -> set[str]:
    ds = {NG}
    for d, fuentes in r.FUENTES_DOMINIO.items():
        for tipo, valor in fuentes:
            if tipo == "ntc_normas" and r._norma_empieza(norma, valor):
                ds.add(d)
    return ds


def dominios_motor(motor: str, norma_ref: str) -> set[str]:
    ds = set()
    for d, fuentes in r.FUENTES_DOMINIO.items():
        for tipo, valor in fuentes:
            if tipo == "motor_chunks" and valor == motor:
                ds.add(d)
            elif tipo == "motor_chunks_normas" and valor[0] == motor and r._norma_empieza(norma_ref, valor[1]):
                ds.add(d)
    return ds


def main():
    unidades: dict[tuple[str, str], dict] = {}

    def sumar(tabla, unidad, doms, chunk_id=None):
        k = (tabla, unidad)
        u = unidades.setdefault(k, {"tabla": tabla, "unidad": unidad, "n": 0, "dominios": Counter()})
        u["n"] += 1
        for d in doms:
            u["dominios"][d] += 1

    for f in paginar("nsr10_chunks", "id"):
        sumar("nsr10_chunks", unidad_nsr10(f["id"]), dominios_nsr10(f["id"]))
    for f in paginar("ntc_chunks", "norma"):
        sumar("ntc_chunks", f["norma"], dominios_ntc(f["norma"]))
    for f in paginar("motor_chunks", "motor,norma_ref"):
        sumar("motor_chunks", f"[{f['motor']}] {f['norma_ref']}", dominios_motor(f["motor"], f["norma_ref"]))
    for t, d in (("peru_e030_chunks", "peru_e030"), ("ecuador_nec_se_ds_chunks", "ecuador_nec_se_ds")):
        n = contar(t)
        unidades[(t, t)] = {"tabla": t, "unidad": t, "n": n if isinstance(n, int) else 0, "dominios": Counter({d: n if isinstance(n, int) else 0})}

    corpus = []
    for u in sorted(unidades.values(), key=lambda x: (x["tabla"], -x["n"])):
        doms = {d: c for d, c in u["dominios"].items()}
        # Un dominio especializado es primario solo si cubre al menos la mitad
        # de la norma (el Título A no es de geopot por sus 235 chunks de A.2).
        no_ng = [d for d in doms if d != NG and doms[d] >= u["n"] / 2]
        if no_ng:
            primario = max(no_ng, key=lambda d: doms[d])
        elif NG in doms:
            primario = NG
        else:
            primario = max(doms, key=doms.get) if doms else "SIN_DOMINIO"
        corpus.append({"tabla": u["tabla"], "unidad": u["unidad"], "n_chunks": u["n"], "dominio_primario": primario,
                       "dominios": doms, "parcial": any(c < u["n"] for d, c in doms.items() if d != NG)})

    totales = {t: contar(t) for t in ("nsr10_chunks", "ntc_chunks", "motor_chunks", "peru_e030_chunks", "ecuador_nec_se_ds_chunks")}
    datos = [{"tabla": t, "filas": contar(t), "dominio": d, "uso": uso} for t, (d, uso) in DATOS_ESTRUCTURADOS.items()]
    por_dominio = defaultdict(int)
    for c in corpus:
        for d, n in c["dominios"].items():
            por_dominio[d] += n

    salida = {"totales_corpus": totales, "chunks_por_dominio": dict(sorted(por_dominio.items(), key=lambda x: -x[1])),
              "corpus": corpus, "datos_estructurados": datos}
    (AQUI / "inventario_corpus.json").write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")

    md = ["# Inventario de normas y datos de StructAI (issue #170)", "",
          "Generado por `inventario_corpus.py` (solo lectura, conteos exactos). La pertenencia a dominios sale de "
          "`FUENTES_DOMINIO`; todo lo de `nsr10_chunks` y `ntc_chunks` es además de `normativa_general`.", "",
          "## Totales del corpus RAG", "", "| Tabla | Chunks |", "|---|---|"]
    md += [f"| `{t}` | {n} |" for t, n in totales.items()]
    md += ["", "## Chunks disponibles por dominio (un chunk compartido cuenta en cada dominio)", "", "| Dominio | Chunks |", "|---|---|"]
    md += [f"| `{d}` | {n} |" for d, n in salida["chunks_por_dominio"].items()]
    md += ["", "## Matriz norma → dominios", "", "| Tabla | Norma / unidad | Chunks | Dominio primario | Otros dominios | Parcial |", "|---|---|---|---|---|---|"]
    for c in corpus:
        otros = ", ".join(f"{d} ({n})" for d, n in c["dominios"].items() if d != c["dominio_primario"])
        md.append(f"| {c['tabla']} | {c['unidad'][:90]} | {c['n_chunks']} | `{c['dominio_primario']}` | {otros} | {'sí' if c['parcial'] else ''} |")
    md += ["", "## Datos estructurados (ramas propias del código)", "", "| Tabla | Filas | Dominio que la usa | Dónde se lee |", "|---|---|---|---|"]
    md += [f"| `{d['tabla']}` | {d['filas']} | {d['dominio']} | {d['uso']} |" for d in datos]
    (AQUI / "INVENTARIO_CORPUS.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print("totales:", totales)
    print("chunks por dominio:", salida["chunks_por_dominio"])
    print(f"unidades de norma: {len(corpus)} | sin dominio: {[c['unidad'] for c in corpus if c['dominio_primario'] == 'SIN_DOMINIO']}")
    print("datos estructurados:", {d["tabla"]: d["filas"] for d in datos})


if __name__ == "__main__":
    main()
