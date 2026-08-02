"""Cache en memoria del proceso, con expiración (TTL).

No usa Redis: hoy la API corre en una sola instancia (un solo worker de
uvicorn — ver tarea pendiente de escalar a varios), así que un cache en
memoria del proceso ya cubre el caso real sin sumar infraestructura nueva
ni un servicio más que mantener. docker-compose.yml SÍ declara un servicio
de Redis ("caché Motor APU") pero es solo para desarrollo local y nunca
se conectó a nada — no existe un Redis real en producción hoy.

Si en el futuro se escala a varias instancias, este módulo es el único
punto a cambiar por un backend compartido — la interfaz (get/set) no
cambiaría para quien lo usa, solo la implementación interna.
"""
from __future__ import annotations

import threading
import time
from typing import Any, Optional


class TTLCache:
    """Cache clave→valor con expiración por tiempo y tope de tamaño.

    Thread-safe: FastAPI corre las rutas sync en un threadpool, así que
    múltiples requests pueden leer/escribir el mismo cache en paralelo.
    """

    def __init__(self, ttl_seconds: float, max_size: int = 500):
        self._ttl = ttl_seconds
        self._max_size = max_size
        self._store: dict[str, tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            expira_en, valor = entry
            if time.monotonic() >= expira_en:
                del self._store[key]
                return None
            return valor

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            if len(self._store) >= self._max_size and key not in self._store:
                # Tope simple: bota la entrada más próxima a expirar en vez
                # de un LRU real — evita crecer sin límite sin necesitar
                # una librería extra para algo de esta escala.
                clave_mas_vieja = min(self._store, key=lambda k: self._store[k][0])
                del self._store[clave_mas_vieja]
            self._store[key] = (time.monotonic() + self._ttl, value)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def __len__(self) -> int:
        return len(self._store)
