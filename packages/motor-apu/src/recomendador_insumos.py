"""Recomendador de insumos para un APU: dado un conjunto parcial de insumos, sugiere los que suelen acompañarlos en actividades INVIAS parecidas.

Método (el mejor de los tres evaluados en scripts/precios/p2_recomendador_apu.py): vecinos más cercanos. Se representa cada actividad como un vector TF-IDF
sobre sus insumos, se buscan las K actividades más parecidas al conjunto visible (similitud coseno) y se puntúa cada insumo por la similitud acumulada de los
vecinos que lo contienen. Solo numpy.

ALCANCE: sugiere insumos frecuentes en actividades parecidas del catálogo INVIAS de obra vial 2026-1 (324 actividades con composición). NO verifica que el
APU sea correcto, no optimiza costo y no sustituye el criterio de un presupuestador. Evaluación offline: acierto@10 de 0,78 a 0,84 al ocultar un insumo.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

RUTA = Path(__file__).resolve().parents[1] / "data" / "composicion_invias_2026_1.json"
K_VECINOS = 10


class RecomendadorInsumos:
    def __init__(self, actividades: list[dict], insumos: dict[str, dict]):
        self.actividades = actividades
        self.insumos = insumos
        self.codigos = sorted({c for a in actividades for c in a["insumos"]})
        self._ix = {c: i for i, c in enumerate(self.codigos)}
        self._B = np.zeros((len(actividades), len(self.codigos)))
        for i, a in enumerate(actividades):
            for c in a["insumos"]:
                self._B[i, self._ix[c]] = 1.0
        df = self._B.sum(0)
        self._idf = np.log((len(actividades) + 1) / (df + 1)) + 1
        self._W = self._B * self._idf

    @classmethod
    def desde_json(cls, ruta: Path = RUTA) -> "RecomendadorInsumos":
        d = json.loads(Path(ruta).read_text(encoding="utf-8"))
        return cls(d["actividades"], d["insumos"])

    def _consulta(self, visibles: list[str]) -> np.ndarray:
        v = np.zeros(len(self.codigos))
        for c in visibles:
            if c in self._ix:
                v[self._ix[c]] = 1.0
        return v * self._idf

    def _similitud(self, v: np.ndarray, excluir: int | None = None) -> np.ndarray:
        n = np.linalg.norm(self._W, axis=1) * np.linalg.norm(v)
        s = np.divide(self._W @ v, n, out=np.zeros(len(self._W)), where=n > 0)
        if excluir is not None:
            s[excluir] = -1.0
        return s

    def actividades_parecidas(self, visibles: list[str], k: int = 5) -> list[dict]:
        s = self._similitud(self._consulta(visibles))
        return [{"numeral": self.actividades[i]["numeral"], "descripcion": self.actividades[i]["descripcion"], "similitud": round(float(s[i]), 3)}
                for i in np.argsort(-s)[:k] if s[i] > 0]

    def sugerir(self, visibles: list[str], k: int = 10, excluir_numeral: str | None = None) -> list[dict]:
        """Hasta k insumos que no están en `visibles`, ordenados por puntaje, con las actividades que los respaldan."""
        v = self._consulta(visibles)
        if not v.any():
            return []
        excl = next((i for i, a in enumerate(self.actividades) if a["numeral"] == excluir_numeral), None)
        s = self._similitud(v, excluir=excl)
        vec = [i for i in np.argsort(-s)[:K_VECINOS] if s[i] > 0]
        puntaje = np.zeros(len(self.codigos))
        for i in vec:
            puntaje += s[i] * self._B[i]
        puntaje[[self._ix[c] for c in visibles if c in self._ix]] = -1.0
        out = []
        for j in np.argsort(-puntaje)[:k]:
            if puntaje[j] <= 0:
                break
            cod = self.codigos[j]
            apoyo = [self.actividades[i]["numeral"] for i in vec if self._B[i, j] > 0][:3]
            info = self.insumos.get(cod, {})
            out.append({"codigo": cod, "descripcion": info.get("descripcion"), "unidad": info.get("unidad"), "tipo": info.get("tipo"),
                        "puntaje": round(float(puntaje[j]), 3), "actividades_de_apoyo": apoyo})
        return out
