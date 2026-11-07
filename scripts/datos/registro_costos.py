"""P0 (PROTOCOLO_VALOR_INFORMATIVO.md): registro de costos de datos. Bytes locales por carpeta (sin node_modules ni .git), tamaño de las tablas
de producción (consulta pg_total_relation_size guardada en _cache/db_tamanos.json) y tiempos registrados en los logs. Salida: REGISTRO_COSTOS.md.
Uso: python registro_costos.py"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
EXCLUIR = {"node_modules", ".git", "__pycache__", ".next", ".turbo"}


def tam(ruta: Path) -> tuple[int, int]:
    total = n = 0
    for dp, dn, fn in os.walk(ruta):
        dn[:] = [d for d in dn if d not in EXCLUIR]
        for f in fn:
            try:
                total += os.path.getsize(os.path.join(dp, f)); n += 1
            except OSError:
                pass
    return total, n


def mb(b: int) -> str:
    return f"{b / 1e6:,.1f} MB"


def main() -> None:
    filas = []
    for p in sorted((RAIZ / "scripts").iterdir()):
        if p.is_dir() and p.name not in EXCLUIR:
            for sub in sorted(p.iterdir()):
                if sub.is_dir() and sub.name not in EXCLUIR:
                    b, n = tam(sub)
                    filas.append((f"scripts/{p.name}/{sub.name}", b, n))
            b, n = tam(p)
            filas.append((f"scripts/{p.name} (total)", b, n))
    for nombre in ("apps", "packages", "docs", "infra"):
        if (RAIZ / nombre).is_dir():
            b, n = tam(RAIZ / nombre); filas.append((nombre, b, n))
    filas.sort(key=lambda x: -x[1])
    db = json.loads((AQUI / "_cache" / "db_tamanos.json").read_text(encoding="utf-8"))
    tot_db = sum(x["bytes_total"] for x in db)
    log = (RAIZ / "scripts" / "satelite" / "resultados_corrida" / "chirps_diario.log")
    seg = re.findall(r"(\d+)/(\d+) \((\d+)s\)", log.read_text(encoding="utf-8", errors="replace")) if log.exists() else []
    chirps = (int(seg[-1][0]), int(seg[-1][1]), int(seg[-1][2])) if seg else None
    L = ["# Registro de costos de datos (P0)", "", "Generado por `registro_costos.py`. Mide lo que existe hoy; no estima ahorros.", "",
         "## Almacenamiento local (sin `node_modules` ni `.git`)", "", "| Carpeta | Tamaño | Archivos |", "|---|---:|---:|"]
    L += [f"| `{r}` | {mb(b)} | {n:,} |" for r, b, n in filas[:22]]
    L += ["", "## Almacenamiento en producción (Supabase, tablas principales)", "", "| Tabla | Filas (estimadas) | Total | Datos | Índices |", "|---|---:|---:|---:|---:|"]
    L += [f"| `{x['tabla']}` | {x['filas_est']:,} | {x['total']} | {x['datos']} | {x['indices']} |" for x in db]
    L += ["", f"Suma de estas tablas: {mb(tot_db)}."]
    if chirps:
        L += ["", "## Tiempo de procesamiento registrado", "", f"- Descarga diaria de CHIRPS para Colombia: {chirps[0]:,} de {chirps[1]:,} días en {chirps[2] / 3600:.1f} h ({chirps[2] / chirps[0]:.1f} s por día)."]
    (AQUI / "REGISTRO_COSTOS.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
