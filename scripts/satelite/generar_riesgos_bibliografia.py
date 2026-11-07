"""Genera el documento Word 'Registro de riesgos de la investigacion y bibliografia verificada' a partir de
refs_verificadas.json (verificar_referencias.py) + registros por DOI de OpenAlex. Uso: python generar_riesgos_bibliografia.py refs.json salida.docx"""
from __future__ import annotations

import json
import sys
import time
import urllib.request
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

# --------------------------------------------------------------------------------------------- riesgos
# (id, riesgo, donde aplica, que se ve en los datos, mitigacion y estado, claves de referencia)
RIESGOS = [
    ("R1", "Multiplicidad de pruebas: decenas de contrastes con IC; cada uno se fijó antes de correr, pero un resultado aislado sale de una familia grande.",
     "Todo el programa (§§11-22)", "Más de 30 criterios confirmatorios evaluados; algunos IC apenas excluyen 0.",
     "Citar los resultados como familia, no aislados; en los análisis por municipio reportar la fracción significativa frente al ~5 % esperable; aplicar control de tasa de falsos descubrimientos (Benjamini-Hochberg) a los contrastes por región o por estación. Estado: parcial (se reporta la fracción; falta un FDR formal).", "Wilks2016,Benjamini1995"),
    ("R2", "Autocorrelación espacial: municipios y estaciones vecinos comparten píxeles, cuencas y clima; los IC ingenuos son demasiado estrechos.",
     "§§11, 14, 15, 16-18, 21, 22", "CHIRPS de 5 km compartido entre municipios vecinos; estaciones de una misma cuenca.",
     "Bootstrap de bloques por departamento y validación dejando un departamento fuera. Los departamentos tampoco son independientes entre sí: el IC sigue siendo optimista. Falta un análisis con tamaño de muestra efectivo. Estado: parcial.", "Dutilleul1993,Brenning2012,Petschko2014"),
    ("R3", "Falacia ecológica: casi todo se analiza a nivel municipal; una asociación municipal no implica la misma relación entre sitios o personas.",
     "§§11, 14, 16-18", "Relaciones municipales de ρ entre 0,3 y 0,76.",
     "Rotular cada resultado como municipal; no inferir relaciones a escala de predio ni de obra. Estado: declarado en cada protocolo.", "Robinson1950"),
    ("R4", "Circularidad: el mapa de amenaza del SGC probablemente usa la pendiente como insumo, así que su coincidencia con el relieve no es validación independiente.",
     "§16, §17", "ρ(pendiente, SGC) = +0,52 en el Caribe.",
     "Tratar la prueba como consistencia; la evidencia independiente viene de SIMMA (C3 parcial) y de eventos fechados. Estado: declarado.", "Reichenbach2018"),
    ("R5", "Sesgo de reporte e inventario: la UNGRD mide cuánto se reporta, no cuánto ocurre; SIMMA cubre zonas estudiadas, no el país.",
     "§§16, 19, 22", "El 56 % de los eventos UNGRD de movimiento en masa (4.176 de 7.451) es de 2022; SIMMA sin fecha ni magnitud.",
     "Limitar el negativo a municipios con reportes demostrados; no comparar regiones con distinta capacidad de reporte como si midieran riesgo. Estado: declarado; sin corrección cuantitativa.", "Kirschbaum2010,Froude2018,Petschko2014"),
    ("R6", "Datos de solo presencia: el AUC mide discriminación frente al fondo, no probabilidad, y depende de cómo se elige el fondo.",
     "§22", "Fondo aleatorio en proporción 5:1.",
     "Reportar AUC espacial, no probabilidades; comprobar sensibilidad a la razón de fondo; no leer el puntaje como amenaza. Estado: pendiente la prueba de sensibilidad.", "Lobo2008,BarbetMassin2012"),
    ("R7", "Calidad de los datos del IDEAM: 32 % de las estaciones con ≥ 30 años repiten valores de caudal máximo entre años; el «máximo anual» es horario y no el pico instantáneo; la mediana de la última observación es 2019.",
     "§21", "160 de 504 estaciones con más de 10 % de valores repetidos (verificado el día de la descarga).",
     "Análisis con y sin esas estaciones; el caudal de diseño real puede ser mayor que el estimado. Estado: previsto en el protocolo.", "England2019,Milly2008"),
    ("R8", "Estacionariedad: los extremos se ajustan como si el clima fuera estable, pero 2010-2011 y 2022 son años dominantes y existen tendencias.",
     "§21, §19", "La Niña 2010-2011 elevó la lluvia 49 % en el Caribe.",
     "Reportar tendencia (Mann-Kendall) y validar con años posteriores. No hay ajuste no estacionario. Estado: parcial.", "Milly2008"),
    ("R9", "Lluvia satelital: CHIRPS tiene resolución de ~5 km, menor calidad en los años 80, y subestima la intensidad convectiva local.",
     "§§12, 15, 19", "Resultado atípico: La Niña 1985 con −33 % en el Caribe.",
     "Tratar episodios individuales de los años 80 como no interpretables; usar CHIRPS para patrones regionales y no para umbrales locales de diseño. Estado: declarado.", "Funk2015,Beck2017,Dinku2018,Urrea2019"),
    ("R10", "Topografía: el DEM de ~90 m de superficie no resuelve llanuras ni costa; el HAND de superficie sobrestima en zonas costeras.",
     "§§11, 14, 18", "70 % de las rutas aguas arriba terminan en «sumidero interior»; Tolú, Galeras y Algarrobo con HAND bajo y casi sin huella.",
     "No concluir sobre conexión hidráulica en llanuras; buscar un DEM corregido o la red de drenaje del IGAC. Estado: red de drenaje descargada, sin usar todavía.", "Nobre2011,GarousiNejad2019"),
    ("R11", "Fecha del evento: en la UNGRD la fecha es la del reporte y no la de ocurrencia; el desfase degrada los umbrales de lluvia.",
     "§19", "No verificable con los datos disponibles.",
     "Analizar con ventanas que incluyan el día previo; reconocer que el umbral resultante es un umbral de reporte. Estado: declarado.", "Segoni2018,Guzzetti2008"),
    ("R12", "Extrapolación: con 30-60 años de registro, el caudal de 100 años es extrapolación y su intervalo es amplio.",
     "§21", "Razón ancho IC / Q50 por calcular.",
     "T ≤ 50 como rango principal; T = 100 rotulado como extrapolación. Estado: previsto.", "Coles2001,England2019,Katz2002"),
    ("R13", "Fuga de información y elecciones post hoc: elegir D* o el modelo con los mismos datos de prueba, o rescatar un resultado negativo con un diagnóstico posterior.",
     "§§13, 19, 22", "En el caso de energía, el diagnóstico sin tendencia mejora el ajuste pero no rescata el veredicto.",
     "D* y los umbrales se eligen solo con la calibración; todo análisis posterior se rotula exploratorio. Estado: aplicado.", "Brenning2012"),
    ("R14", "Uso indebido: leer un resultado de investigación como cálculo de diseño de puentes, alcantarillado, diques o zonificación normativa.",
     "§§19-22", "Los resultados son comparativos y regionales; varios usan datos de resolución gruesa.",
     "Mantener el aviso de responsabilidad profesional y rotular cada salida como «no sustituye el estudio de un proyecto con ingeniero responsable». Estado: aplicado en los protocolos.", "Corominas2014"),
    ("R15", "Licencias y términos de uso de los datos: CHIRPS, IGAC, SGC, IDEAM y datos.gov.co tienen condiciones distintas; algunos derivados públicos podrían requerir atribución o permiso.",
     "Todo el programa", "No se ha leído el README de CHIRPS ni verificado la licencia de cada capa del IGAC y del SGC.",
     "Revisar licencia y atribución antes de publicar derivados; citar la fuente en cada resultado. Estado: pendiente.", ""),
    ("R16", "Reproducibilidad: los servidores cambian, bloquean con 429 y reescriben archivos; la caché local no está versionada.",
     "Todo el programa", "CHIRPS devolvió 429 durante horas; el IDEAM actualiza archivos sin versionar.",
     "Registrar fecha de descarga y tamaño de cada insumo; scripts reanudables; fijar semillas. Estado: parcial (semillas fijas, sin manifiesto de insumos).", ""),
    ("R17", "Privacidad y sensibilidad: SECOP incluye proveedores y contratos reales; los análisis de desastres recientes (sismo y Venezuela) son sensibles.",
     "SECOP, desastres 2026", "Análisis de obras sin identidad de proveedores; cruce con empresas descartado.",
     "No publicar identidad ni cruces con empresas; no divulgar los análisis de eventos recientes sin revisión. Estado: aplicado.", ""),
    ("R18", "Dependencias externas: APIs gratuitas, claves y créditos (OpenAI sin crédito el 6 de noviembre) pueden detener procesos y respaldos de producción.",
     "Producción, CI", "Clave local con 429 por falta de crédito.",
     "Verificar el estado de créditos y de la cuota antes de despliegues. Estado: pendiente de confirmar.", ""),
]

# --------------------------------------------------------------------------------------------- bibliografia
USO = {  # titulo buscado (inicio) -> uso previsto
    "The rainfall intensity-duration control of shallow landslides and debris flows:": "Actualización con 2.626 eventos; define la forma E–D que usa el protocolo §19.",
    "The rainfall intensity-duration control of shallow landslides and debris flows": "Origen de los umbrales intensidad–duración; referencia histórica.",
    "A review of the recent literature on rainfall thresholds": "Estado del arte de umbrales; criterios para calibrar y validar el umbral E–D.",
    "Rainfall thresholds for possible landslide occurrence in Italy": "Método estadístico frecuentista para umbrales con incertidumbre; comparar con el percentil 5 del §19.",
    "Satellite-based assessment of rainfall-triggered landslide hazard": "Uso de lluvia satelital (IMERG) para alerta de deslizamientos; respalda usar lluvia satelital.",
    "A global landslide catalog for hazard applications": "Catálogo global con sus sesgos de reporte; contexto para el sesgo de la UNGRD.",
    "Satellite rainfall products outperform ground observations": "Evidencia de que la lluvia satelital puede superar a los pluviómetros para predecir deslizamientos.",
    "Global fatal landslide occurrence from 2004 to 2016": "Contexto global de víctimas; sesgo de registro por país.",
    "A review of statistically-based landslide susceptibility models": "Marco general para pesos de evidencia, regresión logística y validación (§22).",
    "Spatial prediction models for landslide hazards": "Comparación de modelos y de validación espacial para susceptibilidad.",
    "Weights of evidence modelling": "Método original de pesos de evidencia (Bonham-Carter y Agterberg).",
    "Assessing the quality of landslide susceptibility maps": "Evaluación de calidad de mapas de susceptibilidad y efecto de la validación.",
    "Recommendations for the quantitative analysis of landslide risk": "Terminología y marco del riesgo cuantitativo (alcance del WRA).",
    "Selecting pseudo-absences": "Cómo elegir el fondo en datos de solo presencia (sensibilidad pendiente).",
    "AUC: a misleading measure": "Limitaciones del AUC en modelos de solo presencia.",
    "Assessing the accuracy of species distribution models": "Definición del TSS usado en el §19.",
    "Landslide inventories and their statistical properties": "Distribución del área de deslizamientos (inversa gamma); base del §20.",
    "Power-law distributions in empirical data": "Ajuste de la cola con KS y bootstrap (§20).",
    "Probabilistic landslide hazard assessment at the basin scale": "Probabilidad temporal y espacial; marco para extender la amenaza.",
    "Guidelines for determining flood flow frequency": "Procedimiento estadounidense (Bulletin 17C) para Log-Pearson III y datos con incertidumbre.",
    "L-moments: analysis and estimation": "L-momentos usados como valores iniciales y para regionalizar.",
    "Statistics of extremes in hydrology": "Fundamentos de GEV y de períodos de retorno en hidrología.",
    "Stationarity is dead": "Límites de suponer estacionariedad en frecuencia de crecientes.",
    "Regional frequency analysis": "Regionalización por L-momentos (libro de Hosking y Wallis, 1997; OpenAlex lista la reseña de Tasker y Hosking).",
    "An introduction to statistical modeling of extreme values": "Texto de referencia para GEV, incertidumbre y extrapolación.",
    "Generalized rainfall-duration-frequency relationships": "Relaciones lluvia–duración–frecuencia para estimar duraciones cortas a partir de lluvias diarias.",
    "Seasonality in ENSO-related precipitation": "ENSO y lluvia/caudales en Colombia; contrasta con el mapa del §15.",
    "Hydro-climatic variability over the Andes of Colombia": "Revisión de ENSO sobre los Andes colombianos.",
    "Feedbacks between hydrological processes": "ENSO y procesos hidrológicos en Sudamérica tropical.",
    "The climate hazards infrared precipitation with stations": "Descripción y límites de CHIRPS.",
    "Global-scale evaluation of 22 precipitation datasets": "Comparación de productos de lluvia con pluviómetros.",
    "Validation of the CHIRPS satellite rainfall estimates": "Validación de CHIRPS en África; límites sobre eventos extremos.",
    "Seasonality of rainfall in Colombia": "Estacionalidad de la lluvia en Colombia; contexto regional.",
    "Height Above the Nearest Drainage": "Método HAND original.",
    "HAND, a new terrain descriptor": "HAND aplicado a Amazonia con SRTM.",
    "Terrain analysis enhancements": "Mejoras de HAND para mapeo de inundación.",
    "Ecological correlations": "Falacia ecológica.",
    "The stippling shows": "Sobrerreporte de significancia en campos espaciales.",
    "Controlling the false discovery rate": "Control de falsos descubrimientos en pruebas múltiples.",
    "The jackknife and the bootstrap for general stationary observations": "Fundamento del bootstrap de bloques.",
    "Modifying the t test": "Corrección por autocorrelación espacial al contrastar correlaciones.",
    "Spatial cross-validation and bootstrap": "Validación cruzada espacial (sperrorest).",
}
CLAVES = {  # titulo buscado (inicio) -> clave usada en RIESGOS
    "The rainfall intensity-duration control of shallow landslides and debris flows:": "Guzzetti2008", "A review of the recent literature": "Segoni2018",
    "A global landslide catalog": "Kirschbaum2010", "Global fatal landslide": "Froude2018", "A review of statistically-based": "Reichenbach2018",
    "Assessing the quality of landslide": "Petschko2014", "Recommendations for the quantitative": "Corominas2014",
    "Selecting pseudo-absences": "BarbetMassin2012", "AUC: a misleading": "Lobo2008", "Guidelines for determining flood": "England2019",
    "Statistics of extremes": "Katz2002", "Stationarity is dead": "Milly2008", "An introduction to statistical": "Coles2001",
    "The climate hazards": "Funk2015", "Global-scale evaluation": "Beck2017", "Validation of the CHIRPS": "Dinku2018", "Seasonality of rainfall": "Urrea2019",
    "Height Above the Nearest": "Nobre2011", "Terrain analysis enhancements": "GarousiNejad2019", "Ecological correlations": "Robinson1950",
    "The stippling": "Wilks2016", "Controlling the false": "Benjamini1995", "Modifying the t test": "Dutilleul1993", "Spatial cross-validation": "Brenning2012",
}
BLOQUES = {"umbrales": "Umbrales de lluvia y catálogos de deslizamientos", "susceptibilidad": "Susceptibilidad y riesgo de movimientos en masa",
           "magnitud": "Distribuciones de tamaño y probabilidad de amenaza", "crecientes": "Frecuencia de crecientes y regionalización",
           "idf": "Curvas IDF", "clima": "Clima, ENSO y lluvia satelital", "hand": "Terreno e inundación (HAND)", "estadistica": "Estadística y validación"}
EXTRAS = [  # DOI, bloque, uso
    ("10.1029/2012gc004370", "susceptibilidad", "Mapa global de litología (GLiM); alternativa a la geología a 1:1.000.000 del SGC."),
    ("10.1007/s11069-023-05848-8", "umbrales", "Distribución espacio-temporal de deslizamientos con bases abiertas (incluye Colombia); revisar cobertura."),
    ("10.1007/s10346-024-02225-9", "umbrales", "Relación espacio-temporal entre deslizamientos y variabilidad de la lluvia en un país andino; verificar si el estudio es de Colombia."),
    ("10.3390/w11020379", "clima", "Tendencias de precipitación y crecientes en los Andes colombianos."),
    ("10.17533/udea.redin.20230212", "idf", "IMERG para derivar curvas IDF; revisar región de estudio."),
    ("10.17533/udea.redin.20201215", "umbrales", "Efecto de la intensidad de lluvia en la amenaza por deslizamientos en los Andes del noroeste de Colombia."),
    ("10.3390/rs14092239", "umbrales", "Factor numérico de deslizamientos derivado de CHIRPS; uso de CHIRPS para deslizamientos superficiales."),
    ("10.3390/w14192998", "idf", "Curva IDF para eventos extremos en una zona alta andina; verificar el país."),
]


def traer_por_doi(doi: str) -> dict | None:
    for i in range(3):
        try:
            req = urllib.request.Request(f"https://api.openalex.org/works/doi:{doi}", headers={"User-Agent": "structai-research/0.1"})
            with urllib.request.urlopen(req, timeout=60) as r:
                w = json.load(r)
            aut = [a["author"]["display_name"] for a in (w.get("authorships") or [])]
            loc = (w.get("primary_location") or {}).get("source") or {}
            return {"titulo": w.get("title"), "anio": w.get("publication_year"), "autores": aut[:6], "revista": loc.get("display_name"), "doi": w.get("doi"), "citas": w.get("cited_by_count")}
        except Exception:
            time.sleep(2 * (i + 1))
    return None


def sombrear(celda, hex_):
    tcPr = celda._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), hex_); tcPr.append(sh)


def fijar_ancho(tabla, anchos_cm):
    tabla.autofit = False
    for fila in tabla.rows:
        for c, w in zip(fila.cells, anchos_cm):
            c.width = Cm(w)


def cita(r: dict) -> str:
    aut = r["autores"]
    a = ", ".join(aut[:3]) + (" et al." if len(aut) > 3 else "")
    return f"{a} ({r['anio']}). {r['titulo']}. {r.get('revista') or 'sin revista indexada'}. {r['doi'] or 'sin DOI'}"


def main() -> None:
    refs = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    d = Document()
    for s in d.sections:
        s.left_margin = s.right_margin = Cm(2); s.top_margin = s.bottom_margin = Cm(2)
    st = d.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(10.5)
    t = d.add_heading("Registro de riesgos de la investigación y bibliografía verificada", 0)
    p = d.add_paragraph("StructAI – programa de investigación con datos abiertos de Colombia (issues #95, #98, #101). Versión del 7 de noviembre de 2026.")
    p.runs[0].italic = True
    d.add_heading("Cómo leer este documento", 1)
    d.add_paragraph("El registro de riesgos reúne los puntos donde esta investigación puede equivocarse, cómo los tratamos y qué queda pendiente. "
                    "La bibliografía contiene solo referencias cuyo registro (título, autor, año, revista y DOI) se verificó contra la base abierta OpenAlex. "
                    "Importante: se verificó que la obra existe y que coincide con el título y autor buscados; todavía no se leyó el contenido completo de cada una. "
                    "Antes de citar una afirmación concreta en un artículo, hay que leer la fuente.")
    d.add_heading("1. Registro de riesgos", 1)
    tabla = d.add_table(rows=1, cols=5); tabla.style = "Table Grid"; tabla.alignment = WD_TABLE_ALIGNMENT.CENTER
    for c, tx in zip(tabla.rows[0].cells, ["ID", "Riesgo", "Dónde aplica / qué se ve", "Tratamiento y estado", "Referencias"]):
        c.text = ""; r = c.paragraphs[0].add_run(tx); r.bold = True; r.font.size = Pt(9); sombrear(c, "D9E2F3")
    nombres = {}
    for r in refs:
        if r.get("no_encontrada"):
            continue
        clave = next((v for k, v in CLAVES.items() if r["buscado"].startswith(k)), None)
        if clave:
            nombres[clave] = r
    for rid, riesgo, donde, visto, trat, claves in RIESGOS:
        fila = tabla.add_row().cells
        fila[0].text = rid; fila[1].text = riesgo; fila[2].text = f"{donde}. {visto}"; fila[3].text = trat
        refs_txt = "; ".join(f"{nombres[k]['autores'][0].split()[-1]} {nombres[k]['anio']}" for k in claves.split(",") if k in nombres)
        fila[4].text = refs_txt or "—"
        for c in fila:
            for pp in c.paragraphs:
                for rr in pp.runs:
                    rr.font.size = Pt(8.5)
        for rr in fila[0].paragraphs[0].runs:
            rr.bold = True
    fijar_ancho(tabla, [1.0, 5.2, 4.2, 5.0, 2.2])
    d.add_heading("2. Bibliografía verificada por bloque", 1)
    por_bloque: dict[str, list[tuple[str, str]]] = {b: [] for b in BLOQUES}
    for r in refs:
        if r.get("no_encontrada"):
            continue
        uso = next((u for k, u in USO.items() if r["buscado"].startswith(k)), "")
        por_bloque[r["bloque"]].append((cita(r), uso))
    for doi, bloque, uso in EXTRAS:
        w = traer_por_doi(doi)
        if w:
            por_bloque[bloque].append((cita(w) + "  [hallazgo de búsqueda; revisar antes de citar]", uso))
    for b, titulo in BLOQUES.items():
        if not por_bloque[b]:
            continue
        d.add_heading(titulo, 2)
        for ref, uso in sorted(por_bloque[b], key=lambda x: x[0]):
            p = d.add_paragraph(style="List Bullet"); p.add_run(ref).font.size = Pt(9.5)
            if uso:
                q = p.add_run(f"  Uso previsto: {uso}"); q.italic = True; q.font.size = Pt(9); q.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
    d.add_heading("3. Vacíos de bibliografía y qué hacer", 1)
    for tx in [
        "Regionalización de crecientes en Colombia: no apareció una referencia verificable; buscar en revistas colombianas (Ingeniería y Competitividad, Dyna, Revista Facultad de Ingeniería UdeA) y en el IDEAM.",
        "Curvas IDF a partir de lluvia diaria en Colombia (p. ej. relaciones de Vargas y Díaz-Granados, 1998): no se pudo verificar; no se citan hasta tener el documento.",
        "Umbrales de lluvia para deslizamientos en los Andes colombianos con eventos fechados: hay trabajos de grupos de Medellín (Aristizábal y colaboradores); falta leerlos y fijar cuál es el comparador del §19.",
        "Pesos de evidencia aplicados a Colombia con SIMMA: no verificado; buscar tesis y artículos del SGC.",
        "Licencia y términos de uso de CHIRPS, IGAC, SGC e IDEAM: no son bibliografía, pero deben revisarse en las páginas oficiales antes de publicar derivados.",
        "Leer, como mínimo, Guzzetti et al. (umbrales E–D), Segoni et al. (revisión de umbrales), Reichenbach et al. (susceptibilidad), Clauset et al. (colas de potencia), England et al. (Bulletin 17C) y Poveda et al. (ENSO en Colombia) antes de redactar cualquier artículo. Los años de la lista siguen el registro de OpenAlex, que puede usar la fecha de publicación en línea.",
    ]:
        d.add_paragraph(tx, style="List Bullet")
    d.save(sys.argv[2])
    print("guardado", sys.argv[2])


if __name__ == "__main__":
    main()
