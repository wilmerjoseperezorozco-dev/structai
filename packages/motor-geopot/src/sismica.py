"""
Módulo NSR-10: Clasificación sísmica de Colombia por departamento.
Datos: Aa, Av, Fa, Fv, Sa(T=0.3s), Zona, Riesgo y recomendaciones constructivas.
"""

DEPARTAMENTOS = [
    {"n":1,"dept":"Amazonas","capital":"Leticia","aa":0.12,"av":0.15,"zona":"Baja","fa":0.8,"fv":0.8,"sa":0.24,"clasificacion":"BAJA","riesgo":"BAJO"},
    {"n":2,"dept":"Antioquia","capital":"Medellín","aa":0.25,"av":0.35,"zona":"Alta","fa":1.3,"fv":1.8,"sa":0.8125,"clasificacion":"ALTA","riesgo":"MEDIO"},
    {"n":3,"dept":"Arauca","capital":"Arauca","aa":0.15,"av":0.2,"zona":"Intermedia","fa":1.2,"fv":1.7,"sa":0.45,"clasificacion":"INTERMEDIA","riesgo":"BAJO"},
    {"n":4,"dept":"Atlántico","capital":"Barranquilla","aa":0.15,"av":0.2,"zona":"Intermedia","fa":1.2,"fv":1.7,"sa":0.45,"clasificacion":"INTERMEDIA","riesgo":"BAJO"},
    {"n":5,"dept":"Bolívar","capital":"Cartagena","aa":0.12,"av":0.15,"zona":"Baja","fa":0.8,"fv":0.8,"sa":0.24,"clasificacion":"BAJA","riesgo":"BAJO"},
    {"n":6,"dept":"Boyacá","capital":"Tunja","aa":0.25,"av":0.35,"zona":"Alta","fa":1.3,"fv":1.8,"sa":0.8125,"clasificacion":"ALTA","riesgo":"MEDIO"},
    {"n":7,"dept":"Caldas","capital":"Manizales","aa":0.25,"av":0.35,"zona":"Alta","fa":1.3,"fv":1.8,"sa":0.8125,"clasificacion":"ALTA","riesgo":"MEDIO"},
    {"n":8,"dept":"Caquetá","capital":"Florencia","aa":0.15,"av":0.2,"zona":"Intermedia","fa":1.2,"fv":1.7,"sa":0.45,"clasificacion":"INTERMEDIA","riesgo":"BAJO"},
    {"n":9,"dept":"Casanare","capital":"Yopal","aa":0.15,"av":0.2,"zona":"Intermedia","fa":1.2,"fv":1.7,"sa":0.45,"clasificacion":"INTERMEDIA","riesgo":"BAJO"},
    {"n":10,"dept":"Cauca","capital":"Popayán","aa":0.2,"av":0.28,"zona":"Intermedia","fa":1.2,"fv":1.7,"sa":0.6,"clasificacion":"INTERMEDIA","riesgo":"MEDIO"},
    {"n":11,"dept":"Cesar","capital":"Valledupar","aa":0.15,"av":0.2,"zona":"Intermedia","fa":1.2,"fv":1.7,"sa":0.45,"clasificacion":"INTERMEDIA","riesgo":"BAJO"},
    {"n":12,"dept":"Córdoba","capital":"Montería","aa":0.12,"av":0.15,"zona":"Baja","fa":0.8,"fv":0.8,"sa":0.24,"clasificacion":"BAJA","riesgo":"BAJO"},
    {"n":13,"dept":"Cundinamarca","capital":"Bogotá","aa":0.25,"av":0.35,"zona":"Alta","fa":1.3,"fv":1.8,"sa":0.8125,"clasificacion":"ALTA","riesgo":"MEDIO"},
    {"n":14,"dept":"Guainía","capital":"Inírida","aa":0.12,"av":0.15,"zona":"Baja","fa":0.8,"fv":0.8,"sa":0.24,"clasificacion":"BAJA","riesgo":"BAJO"},
    {"n":15,"dept":"Guaviare","capital":"San José Guaviare","aa":0.12,"av":0.15,"zona":"Baja","fa":0.8,"fv":0.8,"sa":0.24,"clasificacion":"BAJA","riesgo":"BAJO"},
    {"n":16,"dept":"Huila","capital":"Neiva","aa":0.2,"av":0.28,"zona":"Intermedia","fa":1.2,"fv":1.7,"sa":0.6,"clasificacion":"INTERMEDIA","riesgo":"MEDIO"},
    {"n":17,"dept":"La Guajira","capital":"Riohacha","aa":0.12,"av":0.15,"zona":"Baja","fa":0.8,"fv":0.8,"sa":0.24,"clasificacion":"BAJA","riesgo":"BAJO"},
    {"n":18,"dept":"Magdalena","capital":"Santa Marta","aa":0.15,"av":0.2,"zona":"Intermedia","fa":1.2,"fv":1.7,"sa":0.45,"clasificacion":"INTERMEDIA","riesgo":"BAJO"},
    {"n":19,"dept":"Meta","capital":"Villavicencio","aa":0.15,"av":0.2,"zona":"Intermedia","fa":1.2,"fv":1.7,"sa":0.45,"clasificacion":"INTERMEDIA","riesgo":"BAJO"},
    {"n":20,"dept":"Nariño","capital":"Pasto","aa":0.25,"av":0.35,"zona":"Alta","fa":1.3,"fv":1.8,"sa":0.8125,"clasificacion":"ALTA","riesgo":"MEDIO"},
    {"n":21,"dept":"Norte Santander","capital":"Cúcuta","aa":0.2,"av":0.28,"zona":"Intermedia","fa":1.2,"fv":1.7,"sa":0.6,"clasificacion":"INTERMEDIA","riesgo":"MEDIO"},
    {"n":22,"dept":"Putumayo","capital":"Mocoa","aa":0.15,"av":0.2,"zona":"Intermedia","fa":1.2,"fv":1.7,"sa":0.45,"clasificacion":"INTERMEDIA","riesgo":"BAJO"},
    {"n":23,"dept":"Quindío","capital":"Armenia","aa":0.25,"av":0.35,"zona":"Alta","fa":1.3,"fv":1.8,"sa":0.8125,"clasificacion":"ALTA","riesgo":"MEDIO"},
    {"n":24,"dept":"Risaralda","capital":"Pereira","aa":0.25,"av":0.35,"zona":"Alta","fa":1.3,"fv":1.8,"sa":0.8125,"clasificacion":"ALTA","riesgo":"MEDIO"},
    {"n":25,"dept":"Santander","capital":"Bucaramanga","aa":0.2,"av":0.28,"zona":"Intermedia","fa":1.2,"fv":1.7,"sa":0.6,"clasificacion":"INTERMEDIA","riesgo":"MEDIO"},
    {"n":26,"dept":"Sucre","capital":"Sincelejo","aa":0.15,"av":0.2,"zona":"Intermedia","fa":1.2,"fv":1.7,"sa":0.45,"clasificacion":"INTERMEDIA","riesgo":"BAJO"},
    {"n":27,"dept":"Tolima","capital":"Ibagué","aa":0.2,"av":0.28,"zona":"Intermedia","fa":1.2,"fv":1.7,"sa":0.6,"clasificacion":"INTERMEDIA","riesgo":"MEDIO"},
    {"n":28,"dept":"Valle del Cauca","capital":"Cali","aa":0.25,"av":0.35,"zona":"Alta","fa":1.3,"fv":1.8,"sa":0.8125,"clasificacion":"ALTA","riesgo":"MEDIO"},
    {"n":29,"dept":"Vaupés","capital":"Mitú","aa":0.12,"av":0.15,"zona":"Baja","fa":0.8,"fv":0.8,"sa":0.24,"clasificacion":"BAJA","riesgo":"BAJO"},
    {"n":30,"dept":"Vichada","capital":"Puerto Carreño","aa":0.12,"av":0.15,"zona":"Baja","fa":0.8,"fv":0.8,"sa":0.24,"clasificacion":"BAJA","riesgo":"BAJO"},
    {"n":31,"dept":"Bogotá D.C.","capital":"Bogotá","aa":0.25,"av":0.35,"zona":"Alta","fa":1.3,"fv":1.8,"sa":0.8125,"clasificacion":"ALTA","riesgo":"MEDIO"},
]

MEDIDAS = {
    "BAJA": {
        "concreto_fc_min": "17.5 MPa (2500 PSI)",
        "acero": "Grado 40 permitido",
        "recubrimiento": "30 mm",
        "estribos": "No requeridos en vigas simples",
        "cimentacion": "FS ≥ 2.0 capacidad portante",
        "supervision": "ST básica suficiente",
        "analisis_dinamico": "No requerido",
        "estudio_geotecnico": "Estándar",
    },
    "INTERMEDIA": {
        "concreto_fc_min": "21 MPa (3000 PSI)",
        "acero": "Grado 60 (G-60) recomendado",
        "recubrimiento": "35 mm",
        "estribos": "Máx 2×h ó 16 db ó 300 mm",
        "cimentacion": "FS ≥ 2.5 + amortiguación",
        "supervision": "STI recomendada",
        "analisis_dinamico": "Estático equivalente mínimo",
        "estudio_geotecnico": "Detallado con perfil dinámico",
    },
    "ALTA": {
        "concreto_fc_min": "21 MPa (3000 PSI) OBLIGATORIO",
        "acero": "G-60 fy=420 MPa OBLIGATORIO (DES)",
        "recubrimiento": "40 mm — NSR-10 C.7.7",
        "estribos": "Max 100 mm — NSR-10 C.21.4.4.2",
        "cimentacion": "FS ≥ 3.0 + análisis dinámico detallado",
        "supervision": "STI PERMANENTE OBLIGATORIA — Cap. I",
        "analisis_dinamico": "Espectral tiempo-historia requerido",
        "estudio_geotecnico": "Profundo con respuesta de sitio + microzonificación",
    },
}


def _normalizar(texto: str) -> str:
    """Quita tildes/diéresis para comparar sin depender de que el usuario las escriba."""
    import unicodedata
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return sin_tildes.lower().strip()


def zona_sismica(departamento: str) -> dict:
    """Retorna clasificación sísmica NSR-10 para un departamento colombiano."""
    dept_norm = _normalizar(departamento)
    for d in DEPARTAMENTOS:
        if dept_norm in _normalizar(d["dept"]) or dept_norm in _normalizar(d["capital"]):
            resultado = dict(d)
            resultado["medidas_nsr10"] = MEDIDAS.get(d["clasificacion"], {})
            return resultado
    return {"error": f"Departamento '{departamento}' no encontrado. Verifica el nombre."}


def listar_zonas() -> dict:
    """Resumen de departamentos por zona sísmica."""
    alta = [d["dept"] for d in DEPARTAMENTOS if d["clasificacion"] == "ALTA"]
    inter = [d["dept"] for d in DEPARTAMENTOS if d["clasificacion"] == "INTERMEDIA"]
    baja = [d["dept"] for d in DEPARTAMENTOS if d["clasificacion"] == "BAJA"]
    return {
        "ALTA (Aa ≥ 0.25g)": alta,
        "INTERMEDIA (0.15 ≤ Aa < 0.25g)": inter,
        "BAJA (Aa < 0.15g)": baja,
        "totales": {"alta": len(alta), "intermedia": len(inter), "baja": len(baja)},
    }


if __name__ == "__main__":
    import json
    print("=== Consulta: Antioquia ===")
    print(json.dumps(zona_sismica("Antioquia"), ensure_ascii=False, indent=2))
    print("\n=== Resumen nacional ===")
    resumen = listar_zonas()
    for zona, depts in resumen.items():
        if isinstance(depts, list):
            print(f"\n{zona} ({len(depts)} depts):")
            print(", ".join(depts))
