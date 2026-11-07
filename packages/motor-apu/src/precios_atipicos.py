"""Revisión de un precio unitario frente al catálogo IAD MIPYMES (cotizaciones de proveedores mipyme, Colombia Compra Eficiente).

QUÉ ES: una herramienta de TAMIZAJE. Dice si un precio es estadísticamente extremo respecto a lo que cotizan otros proveedores para el ítem más
parecido; NO dice si el precio es un error ni si es "el precio de mercado" (el catálogo es de un solo momento y son precios de referencia).

Método (ver scripts/precios/PROTOCOLO_PRECIOS.md): z robusto del logaritmo, z = (ln p − ln mediana) / escala, con la escala del ítem (1,4826·MAD) contraída hacia la
global para los ítems con pocas cotizaciones; extremo si |z| > UMBRAL_Z, un umbral CONFORME calibrado para marcar ≈ 5 % de las cotizaciones del catálogo. Solo numpy.
"""
from __future__ import annotations

import json
import math
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import numpy as np

RUTA_REFERENCIA = Path(__file__).resolve().parents[1] / "data" / "referencia_precios_iad.json"
UMBRAL_Z = 2.82      # umbral CONFORME (split conformal, α = 5 %, scripts/precios/p3b_conforme_por_proveedor.py, proveedores dejados fuera): marca ≈ 5 % de las cotizaciones del catálogo
PISO_ESCALA = 0.05
SIMILITUD_MINIMA = 0.45


PALABRAS_VACIAS = {"de", "del", "la", "el", "los", "las", "para", "con", "en", "y", "e", "x", "por", "a", "un", "una", "uso", "tipo"}


def normalizar(texto: str) -> list[str]:
    t = unicodedata.normalize("NFD", texto or "").encode("ascii", "ignore").decode().lower()
    return [w for w in re.findall(r"[a-z0-9]+(?:[./][0-9]+)?", t) if (len(w) > 1 or w.isdigit()) and w not in PALABRAS_VACIAS]


@dataclass(frozen=True)
class Veredicto:
    veredicto: str          # consistente | alto | bajo | posible_error_de_unidad | sin_referencia
    item: str | None
    unidad: str | None
    similitud: float
    mediana: float | None
    z: float | None
    razon: float | None
    aviso: str = ("Tamizaje estadístico frente a cotizaciones de un catálogo de referencia de un solo momento; "
                  "no establece que el precio sea erróneo ni que sea el precio de mercado.")


class ReferenciaPrecios:
    def __init__(self, items: list[dict]):
        self.items = items
        docs = [normalizar(i["nombre"]) for i in items]
        vocab = sorted({w for d in docs for w in d})
        self._ix = {w: k for k, w in enumerate(vocab)}
        df = np.zeros(len(vocab))
        for d in docs:
            for w in set(d):
                df[self._ix[w]] += 1
        self._idf = np.log((len(docs) + 1) / (df + 1)) + 1
        self._M = np.vstack([self._vector(d) for d in docs])

    def _vector(self, tokens: list[str]) -> np.ndarray:
        v = np.zeros(len(self._ix))
        desconocidas = 0
        for w in tokens:
            k = self._ix.get(w)
            if k is not None:
                v[k] += 1
            else:
                desconocidas += 1
        v = v * self._idf
        # las palabras que no están en el catálogo cuentan en la norma: una consulta con muchas palabras ajenas se parece menos a cualquier ítem
        n = math.sqrt(float(np.dot(v, v)) + desconocidas * float(self._idf.max()) ** 2)
        return v / n if n > 0 else v

    @classmethod
    def desde_json(cls, ruta: Path = RUTA_REFERENCIA) -> "ReferenciaPrecios":
        return cls(json.loads(Path(ruta).read_text(encoding="utf-8"))["items"])

    def buscar(self, descripcion: str, k: int = 3) -> list[tuple[dict, float]]:
        s = self._M @ self._vector(normalizar(descripcion))
        orden = np.argsort(-s)[:k]
        return [(self.items[i], float(s[i])) for i in orden]

    def evaluar(self, descripcion: str, precio: float) -> Veredicto:
        if not precio or precio <= 0 or not math.isfinite(precio):
            return Veredicto("sin_referencia", None, None, 0.0, None, None, None, aviso="El precio debe ser un número positivo.")
        item, sim = self.buscar(descripcion, 1)[0]
        if sim < SIMILITUD_MINIMA:
            return Veredicto("sin_referencia", item["nombre"], item["unidad"], sim, None, None, None)
        escala = max(item["mad_log"], PISO_ESCALA)
        z = (math.log(precio) - math.log(item["mediana"])) / escala
        razon = precio / item["mediana"]
        lg = math.log10(razon)
        if abs(z) > UMBRAL_Z and round(lg) != 0 and abs(lg - round(lg)) < 0.05 and abs(round(lg)) <= 3:
            v = "posible_error_de_unidad"
        elif z > UMBRAL_Z:
            v = "alto"
        elif z < -UMBRAL_Z:
            v = "bajo"
        else:
            v = "consistente"
        return Veredicto(v, item["nombre"], item["unidad"], sim, item["mediana"], float(z), float(razon))
