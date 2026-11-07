"""Extraccion de contratos de OBRA de SECOP II (datos abiertos, datos.gov.co) con sus
adiciones/modificaciones, avance de ejecucion y sanciones. Issue #95/#98: base real para
calibrar detectores de retraso, sobrecosto, anticipos sin amortizar y sanciones.

PRIVACIDAD (decision de diseno): solo se piden columnas de una LISTA EXPLICITA. NO se
descargan nombres de proveedores, representantes legales, supervisores ni ordenadores del
gasto, ni documentos de identidad, ni datos bancarios: el conjunto los contiene. Los datos
crudos se guardan en scripts/secop/_cache/ (ignorado por git: el repositorio es publico).
Solo se publican agregados.

Fuentes (Socrata, sin clave): contratos jbjy-vk9h, adiciones cb9c-h8sn, ejecucion mfmm-jqmq,
multas II it5q-hg94. Reanudable: cada lote queda en cache.

Uso: python scripts/secop/extraer_obras_secop.py
"""
from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CACHE = AQUI / "_cache"
BASE = "https://www.datos.gov.co/resource"
UA = {"User-Agent": "structai-research/0.1"}
PAGINA = 1000
LOTE_IDS = 80

COLUMNAS_CONTRATO = [
    "id_contrato", "proceso_de_compra", "nombre_entidad", "nit_entidad", "departamento", "ciudad", "sector", "rama", "orden",
    "estado_contrato", "codigo_de_categoria_principal", "tipo_de_contrato", "modalidad_de_contratacion", "objeto_del_contrato",
    "fecha_de_firma", "fecha_de_inicio_del_contrato", "fecha_de_fin_del_contrato", "duraci_n_del_contrato", "dias_adicionados",
    "es_pyme", "es_grupo", "habilita_pago_adelantado", "liquidaci_n", "origen_de_los_recursos", "el_contrato_puede_ser_prorrogado",
    "valor_del_contrato", "valor_de_pago_adelantado", "valor_facturado", "valor_pagado", "valor_amortizado",
    "valor_pendiente_de_ejecucion", "ultima_actualizacion",
]


def get(dataset: str, **params) -> list[dict]:
    url = f"{BASE}/{dataset}.json?" + urllib.parse.urlencode(params)
    for intento in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                return json.load(r)
        except Exception as e:  # red/limite: reintento con espera, nunca se descarta en silencio
            print(f"  reintento {intento + 1} ({type(e).__name__})", flush=True)
            time.sleep(3 * (intento + 1))
    raise RuntimeError(f"fallo persistente en {dataset}")


def contratos() -> list[dict]:
    f = CACHE / "contratos_obra.jsonl"
    if f.exists():
        return [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines()]
    filas, off = [], 0
    while True:
        pag = get("jbjy-vk9h", **{"$select": ",".join(COLUMNAS_CONTRATO), "$where": "tipo_de_contrato='Obra'",
                                   "$order": "id_contrato", "$limit": PAGINA, "$offset": off})
        filas.extend(pag)
        print(f"contratos: {len(filas)}", flush=True)
        if len(pag) < PAGINA:
            break
        off += PAGINA
        time.sleep(0.2)
    f.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in filas), encoding="utf-8")
    return filas


def por_lotes(nombre: str, dataset: str, col_id: str, ids: list[str], select: str, extra_where: str = "") -> None:
    f = CACHE / f"{nombre}.jsonl"
    hechos = CACHE / f"{nombre}.hechos"
    ya = set(hechos.read_text(encoding="utf-8").split()) if hechos.exists() else set()
    pendientes = [i for i in ids if i not in ya]
    print(f"{nombre}: {len(pendientes)} contratos por consultar", flush=True)
    with f.open("a", encoding="utf-8") as out, hechos.open("a", encoding="utf-8") as h:
        for k in range(0, len(pendientes), LOTE_IDS):
            lote = pendientes[k:k + LOTE_IDS]
            lista = ",".join("'" + i.replace("'", "") + "'" for i in lote)
            off = 0
            while True:
                pag = get(dataset, **{"$select": select, "$where": f"{col_id} in ({lista}){extra_where}",
                                       "$order": col_id, "$limit": 5000, "$offset": off})
                for r in pag:
                    out.write(json.dumps(r, ensure_ascii=False) + "\n")
                if len(pag) < 5000:
                    break
                off += 5000
            h.write("\n".join(lote) + "\n")
            h.flush()
            out.flush()
            if (k // LOTE_IDS) % 20 == 0:
                print(f"  {nombre}: {k + len(lote)}/{len(pendientes)}", flush=True)
            time.sleep(0.15)


def main() -> None:
    CACHE.mkdir(exist_ok=True)
    cs = contratos()
    ids = [c["id_contrato"] for c in cs if c.get("id_contrato")]
    print(f"Contratos de obra: {len(cs)} ({len(set(ids))} ids unicos)", flush=True)
    por_lotes("adiciones", "cb9c-h8sn", "id_contrato", ids, "id_contrato,tipo,fecharegistro")
    por_lotes("ejecucion", "mfmm-jqmq", "identificadorcontrato", ids,
              "identificadorcontrato,fechadeentregaesperada,porcentajedeavanceesperado,fechadeentregareal,porcentaje_de_avance_real,estado_del_contrato,fechacreacion",
              " and tipoejecucion='Porcentaje'")
    multas = get("it5q-hg94", **{"$select": "id_contrato,valor,valor_pagado,fecha_evento,tipo_de_sancion,estado,tipo", "$limit": 5000})
    (CACHE / "multas_ii.jsonl").write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in multas), encoding="utf-8")
    print(f"Multas SECOP II: {len(multas)}; de contratos de obra: {sum(1 for m in multas if m.get('id_contrato') in set(ids))}", flush=True)
    print("LISTO", flush=True)


if __name__ == "__main__":
    main()
