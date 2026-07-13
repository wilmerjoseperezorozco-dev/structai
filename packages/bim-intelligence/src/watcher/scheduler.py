"""
Scheduler de sincronización periódica.
Ejecuta sync delta cada N minutos sin bloquear el hilo principal.
Complementa el file_watcher (que reacciona a eventos) con un ciclo
de seguridad que garantiza consistencia aunque se pierdan eventos.
"""
from __future__ import annotations

import threading
import time
from datetime import datetime

from rich.console import Console

from ..observabilidad.sensor import inicializar_sensor, veedor

console = Console()
logger = inicializar_sensor(__name__)

DEFAULT_INTERVAL_MIN = 15  # cada 15 minutos


class SyncScheduler(threading.Thread):
    """Hilo daemon que ejecuta sync delta en intervalos regulares."""

    def __init__(self, interval_minutes: int = DEFAULT_INTERVAL_MIN) -> None:
        super().__init__(daemon=True, name="sync-scheduler")
        self._interval = interval_minutes * 60
        self._stop_event = threading.Event()

    def run(self) -> None:
        console.print(
            f"[blue]Sync scheduler activo — cada {DEFAULT_INTERVAL_MIN} min[/]"
        )
        while not self._stop_event.wait(self._interval):
            self._cycle()

    def stop(self) -> None:
        self._stop_event.set()

    def _cycle(self) -> None:
        from ..ingest.sync import run_delta_sync, SCAN_ROOTS

        start = time.monotonic()
        try:
            count = run_delta_sync(SCAN_ROOTS)
            elapsed = round(time.monotonic() - start, 2)
            veedor.sync_delta(archivos=count, duracion_s=elapsed)
            console.print(
                f"[green][{datetime.now().strftime('%H:%M')}] Sync delta:"
                f" {count} archivos en {elapsed}s[/]"
            )
        except Exception as e:
            logger.error("Error en ciclo sync", exc_info=True)
            console.print(f"[red]Error sync: {e}[/]")
