"""Almacén de artefactos en Supabase (tabla ``proyecto_artefactos``), aislado por usuario.

``resultado_texto`` es la fuente de verdad del hash (jsonb no conserva el formato exacto de los números).
Cualquier error del cliente se propaga: un fallo de lectura no se interpreta como «no existe».
"""
from __future__ import annotations

import datetime as dt
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


# ---------------------------------------------------------------- Registro de idempotencia durable (#221, fase 2)

from .flujo import RegistroEfectos  # noqa: E402

TABLA_IDEMPOTENCIA = "idempotencia_efectos"


def _es_llave_duplicada(e: Exception) -> bool:
    return getattr(e, "code", None) == "23505" or "23505" in str(e) or "duplicate key" in str(e).lower()


class RegistroEfectosSupabase(RegistroEfectos):
    """`RegistroEfectos` sobre la tabla ``idempotencia_efectos`` (migración 20261116121000).

    La llave primaria es la garantía entre instancias de Cloud Run: se registra con INSERT, no con UPSERT, así que si dos
    instancias hacen el mismo efecto a la vez, la segunda choca con la llave, relee y devuelve el artefacto de la primera.
    El resultado se guarda como texto canónico (jsonb no conserva el formato exacto de los números) y se verifica su hash
    al leer, como en `AlmacenSupabase`. Una fila vencida (``expira_en``) se trata como inexistente y se reemplaza.
    Cualquier otro error del cliente se propaga: un fallo de lectura no se interpreta como «no se hizo»."""

    def __init__(self, cliente: Any, *, vigencia_dias: int = 7, ahora=None) -> None:
        super().__init__()
        self._sb = cliente
        self._dias = vigencia_dias
        self._ahora = ahora or (lambda: dt.datetime.now(dt.timezone.utc))

    def _leer(self, llave: str):
        filas = self._sb.table(TABLA_IDEMPOTENCIA).select("*").eq("llave", llave).limit(1).execute().data
        return filas[0] if filas else None

    def _vigente(self, fila) -> bool:
        return dt.datetime.fromisoformat(str(fila["expira_en"]).replace("Z", "+00:00")) > self._ahora()

    def obtener(self, llave: str) -> Artefacto | None:
        f = self._leer(llave)
        if f is None or not self._vigente(f):
            return None
        d = dict(f["artefacto"])
        d["resultado"] = json.loads(d.pop("resultado_texto"))
        return _verificar(Artefacto.desde_dict(d))

    def registrar(self, llave: str, a: Artefacto, flujo: str = "") -> Artefacto:
        previa = self._leer(llave)
        if previa is not None and not self._vigente(previa):
            self._sb.table(TABLA_IDEMPOTENCIA).delete().eq("llave", llave).execute()
        d = a.a_dict()
        d["resultado_texto"] = texto_canonico(d.pop("resultado"))
        fila = {"llave": llave, "flujo": flujo, "paso": a.nodo, "hash_entrada": a.hash_entrada, "artefacto": d,
                "expira_en": (self._ahora() + dt.timedelta(days=self._dias)).isoformat()}
        try:
            self._sb.table(TABLA_IDEMPOTENCIA).insert(fila).execute()
        except Exception as e:
            if not _es_llave_duplicada(e):
                raise
            ganador = self.obtener(llave)                 # otra instancia registró primero: gana la primera
            if ganador is None:
                raise
            return ganador
        return a
