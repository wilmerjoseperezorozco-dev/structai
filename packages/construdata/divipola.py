"""
Resolver único de nombres/códigos oficiales de departamento y municipio de
Colombia (DIVIPOLA -- División Político-Administrativa), expuesto vía la
misma plataforma Socrata de datos.gov.co que ideam_client.py/igac_client.py
(API SODA, JSON, sin API key). Fuente: DANE, resource id gdxc-w37w
("DIVIPOLA- Códigos municipios"), corte 30-dic-2024, verificado en vivo
2026-08-21: 1.122 municipios reales, cobertura nacional completa.

Por qué existe este módulo: hasta ahora cada cliente geográfico
(ideam_client.py, igac_client.py, sgc_amenaza_sismica.py) resolvía nombres
de departamento/municipio por su cuenta, cada uno con su propia lógica de
tildes/mayúsculas -- y ahí salieron DOS bugs reales esta sesión (IDEAM:
'Cauca' matcheaba 'Valle Del Cauca' por LIKE; mismo patrón de riesgo
existía en igac_client.py, ya evitado desde el primer commit gracias a esa
lección). Este módulo es la fuente única de verdad: dado un nombre como lo
escribió un usuario o como lo tenga cualquier fuente externa, devuelve la
forma CANÓNICA exacta (departamento, municipio, códigos DIVIPOLA,
latitud/longitud) para que los demás clientes filtren con igualdad exacta
contra esa forma canónica, en vez de adivinar con LIKE.

NO reemplaza automáticamente la lógica de los 3 clientes existentes en este
commit -- eso es un refactor aparte, más riesgoso, sobre código que ya
tiene tests pasando. Este módulo se deja listo y verificado para que ese
refactor se haga como un cambio focalizado, no mezclado con la ingesta.

Uso:
    from divipola import resolver_municipio, resolver_departamento

    m = resolver_municipio("repelon", "atlantico")
    # {"municipio": "Repelón", "departamento": "Atlántico",
    #  "codigo_municipio": "08606", "codigo_departamento": "08",
    #  "latitud": 10.493357, "longitud": -75.125534}
"""
from __future__ import annotations

import unicodedata
from typing import Optional

import httpx

BASE_URL = "https://www.datos.gov.co/resource"
DATASET_MUNICIPIOS = "gdxc-w37w"  # DIVIPOLA - Códigos municipios (DANE)

_TIMEOUT = 20.0

# Caché en memoria de proceso: se llena UNA vez por proceso con el dataset
# completo (1.122 filas, liviano) en vez de una consulta por cada
# resolución -- los códigos DIVIPOLA casi no cambian (corte anual), así que
# no hace falta ir a la red en cada pregunta del chat.
_CACHE: Optional[list[dict]] = None
_INDICE_MUNICIPIO: Optional[dict[str, list[dict]]] = None
_INDICE_DEPARTAMENTO: Optional[dict[str, str]] = None
_INDICE_CODIGO: Optional[dict[str, dict]] = None


def _sin_tildes(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def _clave(s: str) -> str:
    """Normaliza para indexar/buscar: sin tildes, mayúsculas, sin
    puntuación, espacios colapsados. Existe porque el dato crudo de DANE
    trae 'BOGOTÁ, D.C.' -- alguien preguntando por 'Bogota' o 'Bogotá D.C.'
    (sin coma) no matcheaba con solo _sin_tildes().upper(), el mismo tipo
    de bug de matching exacto-pero-frágil que este módulo existe para
    evitar en los demás clientes."""
    sin_tilde = _sin_tildes(s).upper()
    sin_puntuacion = "".join(c if c.isalnum() else " " for c in sin_tilde)
    return " ".join(sin_puntuacion.split())


def _titulo(s: str) -> str:
    """DIVIPOLA entrega los nombres en MAYÚSCULAS ('BOGOTÁ, D.C.',
    'MEDELLÍN') -- el resto del proyecto usa Title Case ('Bogotá',
    'Medellín'). str.title() maneja bien los acentos en Python 3, pero deja
    conectores como 'DE'/'DEL' capitalizados igual que el resto de
    palabras (comportamiento aceptable para nombres propios de lugar en
    Colombia, donde 'San Juan Del Cesar' es una forma reconocible)."""
    return s.title()


def _cargar_cache() -> list[dict]:
    global _CACHE, _INDICE_MUNICIPIO, _INDICE_DEPARTAMENTO, _INDICE_CODIGO
    if _CACHE is not None:
        return _CACHE

    url = f"{BASE_URL}/{DATASET_MUNICIPIOS}.json"
    with httpx.Client(timeout=_TIMEOUT) as client:
        resp = client.get(url, params={"$limit": 1200})
        resp.raise_for_status()
        filas_crudas = resp.json()

    filas: list[dict] = []
    indice_municipio: dict[str, list[dict]] = {}
    indice_departamento: dict[str, str] = {}
    indice_codigo: dict[str, dict] = {}

    for f in filas_crudas:
        try:
            lat = float(f["latitud"].replace(",", "."))
            lon = float(f["longitud"].replace(",", "."))
        except (KeyError, ValueError, AttributeError):
            lat = lon = None

        depto_canon = _titulo(f["dpto"])
        mpio_canon = _titulo(f["nom_mpio"])
        registro = {
            "municipio": mpio_canon,
            "departamento": depto_canon,
            "codigo_municipio": f.get("cod_mpio"),
            "codigo_departamento": f.get("cod_dpto"),
            "latitud": lat,
            "longitud": lon,
        }
        filas.append(registro)

        clave_mpio = _clave(mpio_canon)
        indice_municipio.setdefault(clave_mpio, []).append(registro)

        clave_depto = _clave(depto_canon)
        indice_departamento[clave_depto] = depto_canon

        if registro["codigo_municipio"]:
            # Código DIVIPOLA de municipio (5 dígitos, 2 de depto + 3 de
            # mpio) ya es único a nivel nacional -- no necesita depto para
            # desambiguar, a diferencia de resolver_municipio() por nombre.
            indice_codigo[registro["codigo_municipio"]] = registro

    # Alias reales que DANE no cubre con el nombre oficial tal cual: la
    # capital casi nunca se escribe con el sufijo ", D.C." en una pregunta
    # normal ("Bogota", "Bogotá") -- es demasiado importante (capital,
    # ~8M hab.) para dejarla sin resolver por defecto solo porque el
    # nombre oficial DIVIPOLA es "Bogotá, D.C.".
    bogota = indice_municipio.get(_clave("Bogotá, D.C."))
    if bogota:
        indice_municipio.setdefault(_clave("Bogota"), bogota)
        indice_departamento.setdefault(_clave("Bogota"), "Bogotá, D.C.")

    _CACHE = filas
    _INDICE_MUNICIPIO = indice_municipio
    _INDICE_DEPARTAMENTO = indice_departamento
    _INDICE_CODIGO = indice_codigo
    return _CACHE


def resolver_por_codigo(codigo_municipio: str) -> Optional[dict]:
    """Resuelve un código DIVIPOLA de municipio (5 dígitos, ej. '08573') a
    su registro canónico completo -- para fuentes externas (SISBEN, censos,
    cualquier dataset del DANE/DNP) que identifican municipio por código en
    vez de nombre, donde no hace falta desambiguar por departamento porque
    el código ya es único a nivel nacional. Acepta el código con o sin
    ceros a la izquierda ('8573' o '08573') porque algunas fuentes externas
    lo devuelven como entero, perdiendo el cero inicial. None si el código
    no existe -- nunca inventa."""
    _cargar_cache()
    assert _INDICE_CODIGO is not None
    codigo = str(codigo_municipio).strip().zfill(5)
    return _INDICE_CODIGO.get(codigo)


def resolver_departamento(nombre: str) -> Optional[str]:
    """Resuelve un nombre de departamento (con o sin tilde, cualquier
    mayúscula/minúscula) a su forma canónica exacta DIVIPOLA (ej. 'narino'
    -> 'Nariño', 'VALLE DEL CAUCA' -> 'Valle Del Cauca'). None si no hay
    match -- nunca inventa ni adivina por substring."""
    _cargar_cache()
    assert _INDICE_DEPARTAMENTO is not None
    return _INDICE_DEPARTAMENTO.get(_clave(nombre))


def resolver_municipio(nombre: str, departamento: Optional[str] = None) -> Optional[dict]:
    """Resuelve un nombre de municipio (con o sin tilde) a su registro
    canónico completo: {municipio, departamento, codigo_municipio,
    codigo_departamento, latitud, longitud}.

    Varios municipios de Colombia comparten el mismo nombre en
    departamentos distintos (ej. 'San Luis' existe en Antioquia y en
    Tolima) -- si `departamento` no se da y hay más de un match, se
    devuelve el PRIMERO tal como lo entrega DANE (orden estable, no
    aleatorio) y se debe preferir siempre pasar `departamento` cuando se
    conoce, para evitar ambigüedad real. None si el nombre no existe en
    ningún departamento."""
    _cargar_cache()
    assert _INDICE_MUNICIPIO is not None
    candidatos = _INDICE_MUNICIPIO.get(_clave(nombre))
    if not candidatos:
        return None
    if departamento:
        depto_canon = resolver_departamento(departamento)
        if depto_canon:
            for c in candidatos:
                if c["departamento"] == depto_canon:
                    return c
        # departamento dado pero no coincide con ninguno de los candidatos
        # (posible error de tipeo del departamento) -- se cae al primer
        # candidato en vez de devolver None, igual que antes de filtrar.
    return candidatos[0]


if __name__ == "__main__":
    for nombre, depto in [("Repelon", "Atlantico"), ("cordoba", "bolivar"), ("Bogota", None), ("San Luis", "Tolima")]:
        print(nombre, "|", depto, "->", resolver_municipio(nombre, depto))
    print("Nariño resuelve desde 'narino':", resolver_departamento("narino"))
