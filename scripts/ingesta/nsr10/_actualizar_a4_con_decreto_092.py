"""Aplica a `nsr10_apendice_a4_municipios` las modificaciones del Apéndice A-4 que trae el anexo del Decreto 092 de 2011
(29 municipios, págs. 9-11 del anexo, extraídas por buscar_a4_en_decretos.py a `a4_en_decretos.json`).
Conserva el valor original de 2010 en `valores_originales_2010`. También deja anotadas las dos diferencias SIN resolver
(Supía por el Decreto 1711/2021 y Guamal) en `observacion`, sin cambiar sus valores.
Uso: python _actualizar_a4_con_decreto_092.py [--aplicar]   (sin la bandera solo muestra lo que haría)"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
CAMPOS = ("aa", "av", "ae", "ad", "zona")
DECRETO = "Decreto 092 de 2011 (anexo técnico, págs. 9-11)"


def main() -> None:
    original = {f["codigo"]: f for f in json.loads((AQUI / "apendice_a4_extraido.json").read_text(encoding="utf-8"))}
    d092 = json.loads((AQUI / "a4_en_decretos.json").read_text(encoding="utf-8"))["d092_anexo.pdf"]
    cambios = []
    for c, f in d092.items():
        o = original.get(c)
        if o is None or all(o[k] == f[k] for k in CAMPOS):
            continue
        cambios.append({"codigo": c, "nuevo": {k: f[k] for k in CAMPOS}, "original": {k: o[k] for k in CAMPOS}, "municipio": o["municipio"]})
    print(f"Municipios cuyo valor cambia por el Decreto 092/2011: {len(cambios)}")
    for x in cambios[:5]:
        print(f"  {x['codigo']} {x['municipio']}: {x['original']} -> {x['nuevo']}")
    if "--aplicar" not in sys.argv:
        return
    sys.path.insert(0, str(RAIZ / "scripts" / "satelite"))
    import _datos_caribe as dc
    sb = dc._sb()
    for x in cambios:
        sb.table("nsr10_apendice_a4_municipios").update({**x["nuevo"], "modificado_por": DECRETO, "valores_originales_2010": x["original"],
                                                          "vigencia": "texto original 2010 modificado por el Decreto 092 de 2011; posteriores sin verificar"}).eq("codigo", x["codigo"]).execute()
    sb.table("nsr10_apendice_a4_municipios").update({"observacion": "Posible modificación por el Decreto 1711 de 2021 (fila de Supía con Aa 0,25 solo vista en un documento de consulta del Ministerio; anexo oficial sin revisar). El valor mostrado es el del texto de 2010."}).eq("codigo", "17777").execute()
    sb.table("nsr10_apendice_a4_municipios").update({"observacion": "Ae y Ad difieren de la tabla del SGC (0,05 y 0,03). Ningún anexo revisado explica la diferencia; sin resolver."}).eq("codigo", "47318").execute()
    print("Aplicado.")


if __name__ == "__main__":
    main()
