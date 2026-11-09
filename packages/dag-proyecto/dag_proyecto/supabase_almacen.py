"""Almacén de artefactos en Supabase (tabla ``proyecto_artefactos``), aislado por usuario.

``resultado_texto`` es la fuente de verdad del hash (jsonb no conserva el formato exacto de los números).
Cualquier error del cliente se propaga: un fallo de lectura no se interpreta como «no existe».
"""
from __future__ import annotations

import json
from dataclasses import replace
from typing import Any

from . import Almacen, Artefacto, _verificar, texto_canonico

TABLA = "proyecto_artefactos"


class AlmacenSupabase(Almacen):
    def __init__(self, cliente: Any, user_id: str) -> None:
        super().__init__()
        if not user_id:
            raise ValueError("AlmacenSupabase requiere el id del usuario: los artefactos se aíslan por usuario.")
        self._sb = cliente
        self._user = user_id

    def obtener(self, id_: str) -> Artefacto | None:
        filas = (self._sb.table(TABLA).select("*").eq("user_id", self._user).eq("id", id_).limit(1).execute()).data
        if not filas:
            return None
        f = filas[0]
        return _verificar(Artefacto(
            f["id"], f["nodo"], f["version_motor"], f["norma_version"], f["hash_entrada"], f["hash_contenido"],
            tuple(f["entradas"]), json.loads(f["resultado_texto"]), f["estado"]))

    def guardar(self, a: Artefacto) -> None:
        texto = texto_canonico(a.resultado)
        self._sb.table(TABLA).upsert({
            "user_id": self._user, "id": a.id, "nodo": a.nodo, "version_motor": a.version_motor,
            "norma_version": a.norma_version, "hash_entrada": a.hash_entrada, "hash_contenido": a.hash_contenido,
            "entradas": list(a.entradas), "resultado_texto": texto, "resultado": json.loads(texto), "estado": a.estado,
        }, on_conflict="user_id,id").execute()

    def marcar_obsoleto(self, id_: str) -> None:
        a = self.obtener(id_)
        if a is not None and a.estado != "obsoleto":
            self._sb.table(TABLA).update({"estado": "obsoleto"}).eq("user_id", self._user).eq("id", id_).execute()
