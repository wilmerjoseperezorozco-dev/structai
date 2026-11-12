"""Aplica a `nsr10_apendice_a4_municipios` la modificación del Apéndice A-4 que trae el anexo técnico del
Decreto 1711 de 2021: Supía (Caldas, 17777) pasa a Aa = 0,25 (Av 0,30, zona Alta, Ae 0,20 y Ad 0,10 sin cambio).

Fuente verificada 2026-11-11 (issue #189): PDF oficial de MinVivienda, que incluye el anexo técnico (39 páginas):
https://minvivienda.gov.co/sites/default/files/normativa/decreto-1711-del-13-de-diciembre-de-2021.pdf
(página 4 del PDF, primera del anexo: "Se modifica la información de amenaza sísmica del Apéndice A-4 correspondiente
al municipio de Supia, Departamento de Caldas"). Resuelve la observación que dejó _actualizar_a4_con_decreto_092.py
("anexo oficial sin revisar"). Mismo patrón que ese script: conserva el valor de 2010 en `valores_originales_2010`.

El espejo del SGC (`sgc_amenaza_sismica_municipios`) NO se edita: refleja el servicio oficial del SGC tal como está.
La diferencia se advierte en la respuesta del chat (rag_multi_norma._advertencia_a4_modificado).

Uso: python _actualizar_a4_con_decreto_1711.py [--aplicar]   (sin la bandera solo muestra lo que haría)"""
from __future__ import annotations

import io
import os
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
RAIZ = Path(__file__).resolve().parents[3]
CODIGO = "17777"
NUEVO = {"aa": 0.25, "av": 0.30, "ae": 0.20, "ad": 0.10, "zona": "Alta"}
DECRETO = "Decreto 1711 de 2021 (anexo técnico, pág. 4 del PDF oficial de MinVivienda)"


def main() -> None:
    from dotenv import load_dotenv
    from supabase import create_client

    load_dotenv(RAIZ / "apps" / "api" / ".env")
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    fila = sb.table("nsr10_apendice_a4_municipios").select("*").eq("codigo", CODIGO).single().execute().data
    original = {k: fila[k] for k in NUEVO}
    print(f"{fila['municipio']} ({fila['departamento']}): {original} -> {NUEVO}")
    if fila.get("modificado_por"):
        print(f"Ya modificado por: {fila['modificado_por']}; no se toca.")
        return
    cambios = {**NUEVO, "modificado_por": DECRETO, "valores_originales_2010": original,
               "vigencia": "texto original 2010 modificado por el Decreto 1711 de 2021 (Aa 0,15 -> 0,25)",
               "observacion": "Valor del Decreto 1711 de 2021, verificado en su anexo técnico oficial (issue #189). "
                              "El servicio del SGC aún muestra el valor de 2010 (Aa 0,15)."}
    if "--aplicar" not in sys.argv:
        print("dry-run: no se escribió nada")
        return
    sb.table("nsr10_apendice_a4_municipios").update(cambios).eq("codigo", CODIGO).execute()
    verif = sb.table("nsr10_apendice_a4_municipios").select("aa,av,ae,ad,zona,modificado_por,valores_originales_2010").eq("codigo", CODIGO).single().execute().data
    print("Aplicado. Leído de vuelta:", verif)


if __name__ == "__main__":
    main()
