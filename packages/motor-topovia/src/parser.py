"""
══════════════════════════════════════════════════════════════
MOTOR TOPOVÍA — PARSER DE ARCHIVOS DE CAMPO
Lee archivos de estaciones totales (CSV, GSI Leica, RAW Topcon)
y los convierte a objetos Punto/Vertice normalizados.
══════════════════════════════════════════════════════════════
"""
import csv
import re
from pathlib import Path
from typing import Optional
from .models import Punto, Vertice


def detectar_formato(ruta: Path) -> str:
    """Detecta el formato del archivo de campo."""
    ext = ruta.suffix.lower()
    if ext == ".gsi":
        return "gsi"
    if ext == ".raw":
        return "raw"
    if ext in (".csv", ".txt"):
        with open(ruta, "r", encoding="utf-8-sig") as f:
            primera = f.readline()
        if "," in primera or ";" in primera:
            return "csv"
        if "*" in primera:
            return "gsi"
    return "csv"


def leer_csv(ruta: Path) -> list[Punto]:
    """
    Lee CSV con columnas: ID, Norte, Este, Cota[, Descripción]
    Detecta separador automáticamente (coma o punto y coma).
    """
    puntos: list[Punto] = []
    with open(ruta, "r", encoding="utf-8-sig") as f:
        contenido = f.read()

    sep = ";" if ";" in contenido.split("\n")[0] else ","
    lineas = contenido.strip().split("\n")

    # Saltar encabezado si no es numérico
    inicio = 0
    campos_1 = lineas[0].split(sep)
    if len(campos_1) >= 3:
        try:
            float(campos_1[1].strip())
        except ValueError:
            inicio = 1

    for linea in lineas[inicio:]:
        campos = [c.strip() for c in linea.split(sep)]
        if len(campos) < 3:
            continue
        try:
            punto_id = campos[0]
            norte = float(campos[1])
            este = float(campos[2])
            cota = float(campos[3]) if len(campos) > 3 and campos[3] else 0.0
            desc = campos[4] if len(campos) > 4 else ""
            puntos.append(Punto(
                id=punto_id, norte=norte, este=este,
                cota=cota, descripcion=desc,
            ))
        except (ValueError, IndexError):
            continue

    return puntos


def leer_gsi_leica(ruta: Path) -> list[Punto]:
    """
    Lee formato GSI-16 de Leica.
    Campos: 11=ID, 81=Norte, 82=Este, 83=Cota
    """
    puntos: list[Punto] = []
    with open(ruta, "r", encoding="utf-8-sig") as f:
        for linea in f:
            campos = linea.strip().split()
            datos: dict[str, str] = {}
            for campo in campos:
                if campo.startswith("*"):
                    campo = campo[1:]
                wi = campo[:2]
                valor = campo[7:]  # GSI-16: posición 7+
                datos[wi] = valor

            if "81" in datos and "82" in datos:
                punto_id = datos.get("11", "").lstrip("0") or "P"
                try:
                    norte = int(datos["81"]) / 10000.0 if "." not in datos["81"] else float(datos["81"])
                    este = int(datos["82"]) / 10000.0 if "." not in datos["82"] else float(datos["82"])
                    cota = 0.0
                    if "83" in datos:
                        cota = int(datos["83"]) / 10000.0 if "." not in datos["83"] else float(datos["83"])
                    puntos.append(Punto(
                        id=punto_id, norte=norte, este=este, cota=cota,
                    ))
                except (ValueError, KeyError):
                    continue

    return puntos


def leer_raw_topcon(ruta: Path) -> list[Punto]:
    """
    Lee formato RAW de Topcon (GTS/GPT series).
    Líneas CO=comentario, SS/SD=observación, ST=estación.
    Busca coordenadas en líneas con formato: ID,N,E,Z
    """
    puntos: list[Punto] = []
    with open(ruta, "r", encoding="utf-8-sig") as f:
        for linea in f:
            linea = linea.strip()
            if linea.startswith("CO") or not linea:
                continue
            partes = linea.split(",")
            if len(partes) >= 5:
                try:
                    punto_id = partes[1].strip()
                    norte = float(partes[2])
                    este = float(partes[3])
                    cota = float(partes[4])
                    puntos.append(Punto(
                        id=punto_id, norte=norte, este=este, cota=cota,
                    ))
                except (ValueError, IndexError):
                    continue

    return puntos


def importar_puntos(ruta: str | Path) -> list[Punto]:
    """
    Importa puntos de cualquier formato soportado.
    Detecta automáticamente el formato del archivo.
    """
    ruta = Path(ruta)
    if not ruta.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {ruta}")

    formato = detectar_formato(ruta)

    if formato == "gsi":
        return leer_gsi_leica(ruta)
    elif formato == "raw":
        return leer_raw_topcon(ruta)
    else:
        return leer_csv(ruta)


def exportar_replanteo_csv(
    puntos: list[Punto],
    ruta: str | Path,
    separador: str = ",",
) -> None:
    """
    Exporta puntos en CSV para cargar en estación total.
    Formato: ID,Norte,Este,Cota,Descripción
    """
    ruta = Path(ruta)
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=separador)
        writer.writerow(["ID", "Norte", "Este", "Cota", "Descripcion"])
        for p in puntos:
            writer.writerow([p.id, f"{p.norte:.4f}", f"{p.este:.4f}", f"{p.cota:.3f}", p.descripcion])
