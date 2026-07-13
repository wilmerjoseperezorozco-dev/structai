"""
WPM Veedor de Fallas — Logger JSON estructurado para Claude/MCP.
Módulo original sugerido por Gemini, integrado y expandido para Construdata.

Características añadidas:
- Niveles INFO/WARNING además de ERROR
- Contexto de sesión MCP
- Rotación automática de logs
- Método sensor.evento() para métricas de negocio
- Tool MCP: leer_logs_recientes()
"""
from __future__ import annotations

import json
import logging
import os
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

# Ruta base de logs relativa al paquete
_LOGS_DIR = Path(__file__).parents[3] / "logs"
_LOGS_DIR.mkdir(exist_ok=True)

LOG_FILE = str(_LOGS_DIR / "veedor_fallas.jsonl")
EVENTOS_FILE = str(_LOGS_DIR / "eventos_negocio.jsonl")


class WPMLoggerJSON(logging.Formatter):
    """
    Formatea logs en JSON para que Claude/MCP los digiera directamente.
    Incluye traceback completo en excepciones.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_record: dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "nivel": record.levelname,
            "modulo": record.module,
            "funcion": record.funcName,
            "linea": record.lineno,
            "mensaje": record.getMessage(),
        }

        if record.exc_info:
            log_record["traceback"] = traceback.format_exception(*record.exc_info)

        # Contexto extra inyectado por el código
        for key in ("session_id", "herramienta", "proveedor", "duracion_ms"):
            if hasattr(record, key):
                log_record[key] = getattr(record, key)

        return json.dumps(log_record, ensure_ascii=False)


def inicializar_sensor(
    nombre_modulo: str,
    ruta_logs: str = LOG_FILE,
    nivel: int = logging.ERROR,
    max_bytes: int = 5 * 1024 * 1024,  # 5 MB por archivo
    backup_count: int = 3,
) -> logging.Logger:
    """
    Crea e inyecta el logger JSON en el módulo solicitante.

    Args:
        nombre_modulo: Nombre del módulo (usa __name__).
        ruta_logs:     Ruta del archivo .jsonl de logs.
        nivel:         logging.ERROR | logging.WARNING | logging.INFO
        max_bytes:     Tamaño máximo antes de rotar.
        backup_count:  Número de backups a conservar.
    """
    os.makedirs(os.path.dirname(ruta_logs), exist_ok=True)

    logger = logging.getLogger(nombre_modulo)
    logger.setLevel(nivel)

    if not logger.handlers:
        handler = RotatingFileHandler(
            ruta_logs,
            mode="a",
            encoding="utf-8",
            maxBytes=max_bytes,
            backupCount=backup_count,
        )
        handler.setFormatter(WPMLoggerJSON())
        logger.addHandler(handler)

    return logger


class VeedorEventos:
    """
    Registra eventos de negocio estructurados (no errores).
    Útil para métricas: cuántas consultas BIM, qué normas se buscan más, etc.
    """

    def __init__(self, ruta: str = EVENTOS_FILE) -> None:
        self._ruta = ruta
        os.makedirs(os.path.dirname(ruta), exist_ok=True)

    def registrar(self, tipo: str, datos: dict[str, Any]) -> None:
        """Registra un evento de negocio en el log de eventos."""
        evento = {
            "timestamp": datetime.now().isoformat(),
            "tipo": tipo,
            **datos,
        }
        with open(self._ruta, "a", encoding="utf-8") as f:
            f.write(json.dumps(evento, ensure_ascii=False) + "\n")

    def consulta_bim(self, query: str, resultados: int) -> None:
        self.registrar("consulta_bim", {"query": query[:100], "resultados": resultados})

    def consulta_gemini(self, modelo: str, tokens_aprox: int = 0) -> None:
        self.registrar("consulta_gemini", {"modelo": modelo, "tokens": tokens_aprox})

    def sync_delta(self, archivos: int, duracion_s: float) -> None:
        self.registrar("sync_delta", {"archivos": archivos, "duracion_s": round(duracion_s, 2)})


def leer_logs_recientes(max_lineas: int = 50) -> list[dict]:
    """
    Lee las últimas N líneas del log de fallas.
    Usado por el MCP tool para que Claude diagnostique errores.
    """
    path = Path(LOG_FILE)
    if not path.exists():
        return []

    try:
        lines = path.read_text(encoding="utf-8").strip().splitlines()
        recientes = lines[-max_lineas:]
        return [json.loads(l) for l in recientes if l.strip()]
    except Exception:
        return []


# Singleton del veedor de eventos
veedor = VeedorEventos()
