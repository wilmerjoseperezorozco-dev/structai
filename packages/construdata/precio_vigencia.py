"""Vigencia y plausibilidad de los precios que el chat le muestra al usuario.

Por que existe (hallazgo 2026-11-06): el chat mostro "A.C.P.M. BARRANQUILLA
$3.732 COP/gl, captura 2026-08-08". Dos fallas distintas:

1. `fecha_captura` de TODAS las filas de apu_insumos_referencia es 2026-08-08:
   es la fecha en que se CARGO el archivo a StructAI, no la fecha del precio.
   Algunas fuentes son archivos antiguos (p. ej. "APU (08-11-17).xlsx"). El
   usuario leia esa fecha como la vigencia del precio.
2. El precio de un combustible estaba ~3x por debajo del valor oficial
   (ACPM Barranquilla ~$11.291/gl en nov-2026 segun MinEnergia/CREG, citado
   por Portafolio). La aritmetica del pipeline era correcta (costo de linea
   $821 / 0.22 gl = $3.731,82): el dato de origen era viejo.

Este modulo es puro (sin red ni base de datos) para poder probarse solo.
"""
from __future__ import annotations

import re
from typing import Optional

# Fuentes cuya fecha SI es la del dato: INVIAS publica una edicion fechada
# ("2026-1" va en el nombre de la fuente), el catalogo IAD trae su periodo y
# los proveedores de ferreteria se consultan en linea. El resto (catalogo
# Construdata, contratos y cotizaciones reales cargados desde archivos) solo
# tiene la fecha de carga.
_PREFIJOS_FECHA_REAL = ("invias_regional", "catalogo_iad_mipymes", "proveedor_")

# Piso de plausibilidad para combustibles, en COP por galon. Es un PISO, no un
# precio: el nominal de los combustibles en Colombia solo ha subido, asi que
# cualquier valor por debajo es dato desactualizado. Referencias verificadas
# (2026, MinEnergia/CREG via prensa): ACPM Barranquilla ~$10.951 (ene) a
# ~$11.291 (nov); gasolina corriente ~$16.126 (ene). Revisar cada ano.
PISO_COMBUSTIBLE_COP_GL = 8_000.0

_RE_COMBUSTIBLE = re.compile(r"\b(a\.?\s?c\.?\s?p\.?\s?m\.?|d[ií]esel|gasolina)\b", re.IGNORECASE)
_RE_UNIDAD_GALON = re.compile(r"^(gl|gal|galon|galón|galones)\.?$", re.IGNORECASE)


def fecha_es_de_carga(tipo_fuente: Optional[str]) -> bool:
    """True si `fecha_captura` de esa fuente es la fecha de carga a StructAI y
    no la fecha del precio."""
    if not tipo_fuente:
        return True
    return not tipo_fuente.startswith(_PREFIJOS_FECHA_REAL)


def etiqueta_fecha(tipo_fuente: Optional[str], fecha: Optional[str]) -> str:
    """Texto de fecha honesto para el contexto del LLM y para la tarjeta de
    fuentes. Nunca presenta una fecha de carga como fecha del precio."""
    if not fecha:
        return "fecha del precio: no registrada"
    if fecha_es_de_carga(tipo_fuente):
        return (f"cargado en StructAI: {fecha} (la fecha real del precio NO esta registrada; "
                "puede ser de anos anteriores)")
    return f"fecha: {fecha}"


def advertencia_plausibilidad(nombre: str, unidad: Optional[str], precio: Optional[float]) -> Optional[str]:
    """Aviso cuando un precio es implausible. Hoy cubre combustibles por galon."""
    if precio is None or not unidad or not _RE_UNIDAD_GALON.match(unidad.strip()):
        return None
    if _RE_COMBUSTIBLE.search(nombre) and precio < PISO_COMBUSTIBLE_COP_GL:
        return (f"precio de combustible por debajo de ${PISO_COMBUSTIBLE_COP_GL:,.0f}/gl, claramente "
                "desactualizado; NO usarlo. El precio vigente lo publican MinEnergia y la CREG")
    return None


def precio_utilizable(precio: Optional[float], precio_solo_mano_obra: Optional[float]) -> bool:
    """Un precio 0 (o ausente sin mano de obra) no es un precio: son filas
    placeholder, p. ej. 'A.C.P.M. BOGOTA' = 0 guardado con region Barranquilla."""
    if precio is not None and precio > 0:
        return True
    return precio_solo_mano_obra is not None and precio_solo_mano_obra > 0
