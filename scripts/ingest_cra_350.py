"""
Carga la única regla real y generalizable de la Resolución UAE-CRA No. 350
de 2022 a motor_chunks (motor='aquai').

La Res. 350/2022 es un acto administrativo PARTICULAR: liquida en $0 la
contribución especial (Art. 85 Ley 142/1994) para ~15 prestadores pequeños
específicos (listados por NIT) para la vigencia 2019 — no es normativa
general. Su par, la Res. 386/2022, es solo una corrección de digitación
del número de esta resolución (360→386) y no tiene contenido propio; no
se registra como norma separada.

Se carga solo el umbral/regla generalizable que sí aplica a cualquier
prestador: contribución ≤50% de un SMLMV → valor liquidado $0 (Art. 85
Ley 142/1994), con la tarifa 2019 (0.65%, Res. CRA 884/2019) como
contexto. Ver normas_registro.notas_vigencia (codigo='RES-CRA-350-2022')
para el detalle completo de esta decisión de alcance.

Uso: python scripts/ingest_cra_350.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")


CHUNK = {
    "seccion": "Contribución especial — umbral de liquidación en $0",
    "titulo": "Art. 85 Ley 142/1994 — Contribución especial ≤50% SMLMV",
    "contenido": (
        "El artículo 85 de la Ley 142 de 1994 faculta a la CRA para cobrar anualmente a los "
        "prestadores de acueducto, alcantarillado y aseo una contribución especial que recupera "
        "el costo del servicio de regulación, con una tarifa que no puede superar el 1% de los "
        "gastos de funcionamiento del año anterior. Para la vigencia 2019, la Res. CRA 884/2019 "
        "fijó esa tarifa en 0.65%. El propio artículo 4 de la Res. CRA 884/2019 establece que "
        "cuando el resultado de la liquidación de la contribución especial sea igual o inferior "
        "al 50% de un salario mínimo legal mensual vigente (SMLMV) al momento de liquidar, el "
        "valor de la contribución de ese prestador es de cero pesos ($0). La Resolución "
        "UAE-CRA No. 350 de 2022 aplicó esta regla para la vigencia 2019 a un grupo específico "
        "de prestadores pequeños (identificados por NIT en el acto administrativo, no "
        "reproducidos aquí por ser un listado particular, no una regla general)."
    ),
    "norma_ref": "Ley 142/1994 Art. 85 + Res. CRA 884/2019 Art. 4, aplicado en Res. UAE-CRA 350/2022",
    "motor": "aquai",
}


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SERVICE_KEY"]
    sb = create_client(supabase_url, supabase_key)

    norma_row = sb.table("normas_registro").select("id").eq("codigo", "RES-CRA-350-2022").execute()
    if not norma_row.data:
        raise RuntimeError("RES-CRA-350-2022 no existe en normas_registro — registrarlo primero")
    norma_id = norma_row.data[0]["id"]

    row = dict(CHUNK)
    row["norma_id"] = norma_id

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    texto = f"{row['titulo']}. {row['contenido']}"
    vector = model.encode([texto], normalize_embeddings=True)[0]
    row["embedding"] = vector.tolist()

    borrado = sb.table("motor_chunks").delete().eq("norma_id", norma_id).execute()
    print(f"Limpiados {len(borrado.data)} chunks previos")

    sb.table("motor_chunks").insert(row).execute()
    print("OK: 1 chunk cargado en motor_chunks (motor='aquai', RES-CRA-350-2022)")


if __name__ == "__main__":
    main()
