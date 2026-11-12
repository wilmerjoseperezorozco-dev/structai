"""
Descarga acotada (tope 1 GB) de datos abiertos de contratación y regalías para StructAI (#201, #202, #203).

Fuente: datos.gov.co (API Socrata). Licencia de los datasets de SECOP: CC BY-SA 4.0 (atribución a Colombia Compra
Eficiente); DNP: datos abiertos del Gobierno de Colombia. Se descarga en páginas de 50.000 filas con pausa entre
páginas, solo las COLUMNAS necesarias (minimización de datos).

Datos personales: SECOP publica nombres y documentos de representantes legales, ordenadores del gasto y
supervisores, cédulas de proveedores personas naturales y hasta números de cuenta bancaria. NADA de eso se pide a la
API ni se escribe en disco. Para proveedores personas naturales (o NIT ambiguo) el nombre y el documento se
reemplazan por un seudónimo HMAC con una clave local (`_privado/clave_seudonimo.bin`, gitignored), que permite contar
concentración de proveedores sin identificar a la persona.

Salida: scripts/ingesta/secop_sgr/raw/*.csv  (gitignored)

Uso: python scripts/ingesta/secop_sgr/descargar.py
"""
from __future__ import annotations

import csv
import hashlib
import hmac
import os
import re
import secrets
import sys
import time
from pathlib import Path

import httpx

AQUI = Path(__file__).resolve().parent
RAW = AQUI / "raw"
PRIVADO = AQUI / "_privado"
TOPE_BYTES = 1024 ** 3
PAGINA = 50_000
BASE = "https://www.datos.gov.co/resource/{id}.csv"

DATASETS = [
    {"nombre": "secop2_contratos_obra", "id": "jbjy-vk9h", "where": "tipo_de_contrato='Obra'", "orden": "id_contrato",
     "columnas": ["nombre_entidad", "nit_entidad", "codigo_entidad", "departamento", "ciudad", "localizaci_n", "orden",
                  "sector", "rama", "entidad_centralizada", "proceso_de_compra", "id_contrato", "referencia_del_contrato",
                  "estado_contrato", "codigo_de_categoria_principal", "descripcion_del_proceso", "objeto_del_contrato",
                  "tipo_de_contrato", "modalidad_de_contratacion", "justificacion_modalidad_de", "fecha_de_firma",
                  "fecha_de_inicio_del_contrato", "fecha_de_fin_del_contrato", "duraci_n_del_contrato",
                  "tipodocproveedor", "documento_proveedor", "proveedor_adjudicado", "codigo_proveedor", "es_grupo",
                  "es_pyme", "origen_de_los_recursos", "destino_gasto", "valor_del_contrato", "valor_de_pago_adelantado",
                  "valor_facturado", "valor_pagado", "valor_pendiente_de_ejecucion", "dias_adicionados",
                  "el_contrato_puede_ser_prorrogado", "presupuesto_general_de_la_nacion_pgn",
                  "sistema_general_de_participaciones", "sistema_general_de_regal_as", "recursos_propios",
                  "recursos_de_credito", "documentos_tipo", "direcci_n_de_ejecuci_n_del_contrato", "urlproceso",
                  "ultima_actualizacion"]},
    {"nombre": "secop2_procesos_obra", "id": "p6dx-8zbt", "where": "tipo_de_contrato='Obra'", "orden": "id_del_proceso",
     "columnas": ["entidad", "nit_entidad", "departamento_entidad", "ciudad_entidad", "ordenentidad", "codigo_pci",
                  "id_del_proceso", "referencia_del_proceso", "ppi", "id_del_portafolio", "nombre_del_procedimiento",
                  "descripci_n_del_procedimiento", "fase", "fecha_de_publicacion_del", "fecha_de_ultima_publicaci",
                  "fecha_de_publicacion_fase_3", "precio_base", "modalidad_de_contratacion",
                  "justificaci_n_modalidad_de", "duracion", "unidad_de_duracion", "ciudad_de_la_unidad_de",
                  "nombre_de_la_unidad_de", "proveedores_invitados", "proveedores_con_invitacion",
                  "visualizaciones_del", "proveedores_que_manifestaron", "respuestas_al_procedimiento",
                  "respuestas_externas", "conteo_de_respuestas_a_ofertas", "proveedores_unicos_con", "numero_de_lotes",
                  "estado_del_procedimiento", "id_estado_del_procedimiento", "adjudicado", "id_adjudicacion",
                  "codigoproveedor", "departamento_proveedor", "ciudad_proveedor", "valor_total_adjudicacion",
                  "nit_del_proveedor_adjudicado", "nombre_del_proveedor", "codigo_principal_de_categoria",
                  "estado_de_apertura_del_proceso", "tipo_de_contrato", "subtipo_de_contrato", "urlproceso",
                  "estado_resumen"]},
    {"nombre": "sgr_proyectos", "id": "mzgh-shtp", "where": None, "orden": "codigobpin", "columnas": None},
    {"nombre": "dnp_proyectos_infraestructura", "id": "cf9k-55fw", "orden": "bpin", "columnas": None,
     "where": "sector in ('Transporte','Vivienda, Ciudad y Territorio','Minas y Energía','Educación')"},
]
# Columnas de proveedor a seudonimizar si no son claramente una empresa
PROVEEDOR = {"secop2_contratos_obra": ("tipodocproveedor", "documento_proveedor", "proveedor_adjudicado"),
             "secop2_procesos_obra": (None, "nit_del_proveedor_adjudicado", "nombre_del_proveedor")}
RX_NIT_EMPRESA = re.compile(r"^[89]\d{8}(-?\d)?$")      # NIT de persona jurídica: 9 dígitos que empiezan por 8 o 9


def clave() -> bytes:
    PRIVADO.mkdir(parents=True, exist_ok=True)
    f = PRIVADO / "clave_seudonimo.bin"
    if not f.exists():
        f.write_bytes(secrets.token_bytes(32))
    return f.read_bytes()


def seudonimo(k: bytes, doc: str) -> str:
    return "PN-" + hmac.new(k, doc.strip().encode(), hashlib.sha256).hexdigest()[:12]


def anonimizar(nombre_ds: str, fila: dict, k: bytes) -> dict:
    cols = PROVEEDOR.get(nombre_ds)
    if not cols:
        return fila
    c_tipo, c_doc, c_nom = cols
    doc = re.sub(r"[^\d-]", "", fila.get(c_doc) or "")
    es_empresa = (fila.get(c_tipo, "") == "NIT" if c_tipo else True) and bool(RX_NIT_EMPRESA.match(doc))
    if not es_empresa and (fila.get(c_doc) or fila.get(c_nom)):
        fila[c_doc] = seudonimo(k, doc or fila.get(c_nom, ""))
        fila[c_nom] = "PERSONA NATURAL U OTRO (seudonimizado)"
    return fila


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    k = clave()
    total = sum(f.stat().st_size for f in RAW.glob("*.csv"))
    cliente = httpx.Client(timeout=300, headers={"User-Agent": "structai-datos-abiertos/1.0"})
    for ds in DATASETS:
        destino = RAW / f"{ds['nombre']}.csv"
        completo = destino.with_suffix(".completo")
        if completo.exists():
            print(f"{ds['nombre']}: ya completo ({destino.stat().st_size / 1e6:.1f} MB), se omite", flush=True)
            continue
        ya = 0
        if destino.exists():           # retomar: contar filas ya escritas (sin la cabecera)
            with destino.open(encoding="utf-8", newline="") as fh:
                ya = sum(1 for _ in csv.reader(fh)) - 1
            print(f"{ds['nombre']}: se retoma desde la fila {ya:,}", flush=True)
        params = {"$limit": PAGINA, "$order": ds["orden"]}
        if ds["where"]:
            params["$where"] = ds["where"]
        if ds["columnas"]:
            params["$select"] = ",".join(ds["columnas"])
        escritos, offset, encabezado = ya, ya, None
        with destino.open("a" if ya else "w", encoding="utf-8", newline="") as fh:
            w = None
            while True:
                params["$offset"] = offset
                for intento in range(5):
                    r = cliente.get(BASE.format(id=ds["id"]), params=params)
                    if r.status_code < 500:
                        break
                    print(f"  error {r.status_code} en offset {offset:,}; reintento {intento + 1}/5", flush=True)
                    time.sleep(10 * (intento + 1))
                r.raise_for_status()
                filas = list(csv.DictReader(r.text.splitlines()))
                if not filas:
                    break
                if w is None:
                    encabezado = list(filas[0])
                    w = csv.DictWriter(fh, fieldnames=encabezado, extrasaction="ignore")
                    if not ya:
                        w.writeheader()
                for f in filas:
                    w.writerow(anonimizar(ds["nombre"], f, k))
                escritos += len(filas)
                offset += PAGINA
                fh.flush()
                tam = total + destino.stat().st_size
                print(f"  {ds['nombre']}: {escritos:,} filas, acumulado {tam / 1e6:.0f} MB", flush=True)
                if tam > TOPE_BYTES:
                    print("TOPE DE 1 GB ALCANZADO: se detiene la descarga", flush=True)
                    total = tam
                    return
                if len(filas) < PAGINA:
                    break
                time.sleep(1.5)
        total += destino.stat().st_size
        completo.write_text(str(escritos))
        print(f"{ds['nombre']}: {escritos:,} filas, {destino.stat().st_size / 1e6:.1f} MB", flush=True)
    print(f"TOTAL en raw/: {total / 1e6:.0f} MB (tope {TOPE_BYTES / 1e6:.0f} MB)")


if __name__ == "__main__":
    sys.exit(main())
