"""
Carga el Anexo II COMPLETO de la E.030 (Perú) -- listado oficial de zona
sísmica por región/provincia/distrito -- en peru_e030_zonificacion_distrital.

Reemplaza y completa cargar_zonificacion_loreto_tacna.py (que cargó Loreto
parcial + Tacna completa como prueba de concepto el 2026-08-24). Este
script cierra las ~22 regiones restantes -- las 40 páginas completas del
Anexo II (páginas internas 38-77, páginas PDF 41-80).

Fuente: mismo PDF oficial del MVCS ya usado para los Capítulos I-IX y el
Anexo I (Resolución Ministerial N° 043-2019-VIVIENDA, que consolida la
modificación de la R.M. N° 355-2018-VIVIENDA) --
https://cdn.www.gob.pe/uploads/document/file/2366641/51%20E.030%20DISEÑO%20SISMORRESISTENTE%20RM-043-2019-VIVIENDA.pdf
80 páginas totales, confirmado con pypdf antes de transcribir. El texto
extraído por pypdf tiene un problema real de codificación de fuente (los
caracteres acentuados salen corruptos, ej. "RAMÓN" -> "RauóH") -- por eso
esta transcripción es LECTURA VISUAL directa del PDF renderizado como
imagen (Read tool), no del texto extraído automáticamente, para no
arrastrar errores de OCR a un dato de consulta exacta.

Base legal: misma que el resto de la E.030 -- Art. 9(b) del Decreto
Legislativo N° 822 (Perú), ver insert_capitulo1_disposiciones_generales.py.

Cobertura real de este script -- LAS 24 REGIONES + CALLAO, verificado
contra el número real de provincias de cada región (INEI):
  Loreto (8/8 provincias -- completa la carga parcial anterior), Ucayali (4/4),
  Madre de Dios (3/3), Puno (13/13), Amazonas (7/7), San Martín (10/10),
  Huánuco (11/11), Pasco (3/3), Junín (9/9), Cusco (13/13),
  Huancavelica (7/7), Ayacucho (11/11), Apurímac (7/7), Tumbes (3/3),
  Piura (8/8), Lambayeque (3/3), Cajamarca (13/13), La Libertad (12/12),
  Áncash (20/20), Lima (10/10), Callao (1/1), Ica (5/5), Arequipa (8/8),
  Moquegua (3/3), Tacna (4/4, ya cargada -- se reinserta idéntica, mismo
  on_conflict, sin cambio de datos).

Único punto de incertidumbre honesto: el distrito "Mi Perú" (Callao,
creado en 2014) NO aparece en la tabla de esta edición del PDF -- Callao
se cargó con los 6 distritos que sí trae el documento oficial (Bellavista,
Callao, Carmen de la Legua-Reynoso, La Perla, La Punta, Ventanilla). No se
agregó "Mi Perú" por inferencia -- si el PDF no lo trae, no se inventa.

Uso: python scripts/ingesta/peru_e030/cargar_zonificacion_anexo2_completo.py [--dry-run]
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")


def _filas(region: str, provincia: str, zona: int, ambito: str, distritos: list[str]) -> list[dict]:
    return [
        {
            "region": region,
            "provincia": provincia,
            "distrito": d,
            "zona_sismica": zona,
            "ambito": ambito,
        }
        for d in distritos
    ]


FILAS: list[dict] = []

# ═══════════════════════════════════════════════════════════════════════
# LORETO -- completa las 5 provincias ya cargadas + 2 nuevas (8/8)
# ═══════════════════════════════════════════════════════════════════════
FILAS += _filas("LORETO", "UCAYALI", 2, "TODOS LOS DISTRITOS",
                 ["CONTAMANA", "INAHUAYA", "PADRE MÁRQUEZ", "PAMPA HERMOSA",
                  "SARAYACU", "ALFREDO VARGAS GUERRA", "YANAYACU"])
FILAS += _filas("LORETO", "DATEM DEL MARAÑÓN", 2, "CUATRO DISTRITOS",
                 ["MANSERICHE", "MORONA", "PASTAZA", "ANDOAS"])
FILAS += _filas("LORETO", "DATEM DEL MARAÑÓN", 3, "DOS DISTRITOS",
                 ["BARRANCA", "CAHUAPANAS"])

# ═══════════════════════════════════════════════════════════════════════
# UCAYALI (región, 4/4 provincias)
# ═══════════════════════════════════════════════════════════════════════
FILAS += _filas("UCAYALI", "PURÚS", 1, "ÚNICO DISTRITO", ["PURÚS"])
FILAS += _filas("UCAYALI", "ATALAYA", 2, "TODOS LOS DISTRITOS",
                 ["RAIMONDI", "SEPAHUA", "TAHUANÍA", "YURÚA"])
FILAS += _filas("UCAYALI", "PADRE ABAD", 2, "TODOS LOS DISTRITOS",
                 ["CURIMANÁ", "IRAZOLA", "PADRE ABAD"])
FILAS += _filas("UCAYALI", "CORONEL PORTILLO", 2, "TODOS LOS DISTRITOS",
                 ["CALLERÍA", "CAMPOVERDE", "IPARÍA", "MANANTAY", "MASISEA",
                  "NUEVA REQUENA", "YARINACOCHA"])

# ═══════════════════════════════════════════════════════════════════════
# MADRE DE DIOS (región, 3/3 provincias)
# ═══════════════════════════════════════════════════════════════════════
FILAS += _filas("MADRE DE DIOS", "TAMBOPATA", 1, "TODOS LOS DISTRITOS",
                 ["INAMBARI", "LABERINTO", "LAS PIEDRAS", "TAMBOPATA"])
FILAS += _filas("MADRE DE DIOS", "TAHUAMANU", 1, "TODOS LOS DISTRITOS",
                 ["IBERIA", "IÑAPARI", "TAHUAMANU"])
FILAS += _filas("MADRE DE DIOS", "MANU", 2, "TODOS LOS DISTRITOS",
                 ["FITZCARRALD", "HUEPETUHE", "MADRE DE DIOS", "MANU"])

# ═══════════════════════════════════════════════════════════════════════
# PUNO (región, 13/13 provincias)
# ═══════════════════════════════════════════════════════════════════════
FILAS += _filas("PUNO", "SANDIA", 1, "TRES DISTRITOS",
                 ["ALTO INAMBARI", "SAN JUAN DEL ORO", "YANAHUAYA"])
FILAS += _filas("PUNO", "SANDIA", 2, "SIETE DISTRITOS",
                 ["CUYOCUYO", "LIMBANI", "PATAMBUCO", "PHARA", "QUIACA",
                  "SAN PEDRO DE PUTINA PUNCO", "SANDIA"])
FILAS += _filas("PUNO", "SAN ANTONIO DE PUTINA", 2, "TODOS LOS DISTRITOS",
                 ["ANANEA", "QUILCAPUNCU", "SINA", "PEDRO VILCA APAZA", "PUTINA"])
FILAS += _filas("PUNO", "CARABAYA", 2, "TODOS LOS DISTRITOS",
                 ["AYAPATA", "COASA", "CRUCERO", "ITUATA", "SAN GABÁN",
                  "USICAYOS", "AJOYANI", "CORANI", "MACUSANI", "OLLACHEA"])
FILAS += _filas("PUNO", "HUANCANÉ", 2, "TODOS LOS DISTRITOS",
                 ["COJATA", "HUANCANÉ", "HUATASANI", "INCHUPALLA", "PUSI",
                  "ROSASPATA", "TARACO", "VILQUE CHICO"])
FILAS += _filas("PUNO", "MOHO", 2, "TODOS LOS DISTRITOS",
                 ["HUAYRAPATA", "MOHO", "CONIMA", "TILALI"])
FILAS += _filas("PUNO", "PUNO", 2, "TRES DISTRITOS",
                 ["COATA", "CAPACHICA", "AMANTANI"])
FILAS += _filas("PUNO", "PUNO", 3, "DOCE DISTRITOS",
                 ["ACORA", "ATUNCOLLA", "CHUCUITO", "HUATA", "MAÑAZO",
                  "PAUCARCOLLA", "PICHACANI", "PLATERIA", "PUNO", "SAN ANTONIO",
                  "TIQUILLACA", "VILQUE"])
FILAS += _filas("PUNO", "AZÁNGARO", 2, "TODOS LOS DISTRITOS",
                 ["AZÁNGARO", "ACHAYA", "ARAPA", "ASILLO", "CAMINACA", "CHUPA",
                  "JOSÉ DOMINGO CHOQUEHUANCA", "MUÑANI", "POTONI", "SAMAN",
                  "SAN ANTÓN", "SAN JOSÉ", "SAN JUAN DE SALINAS",
                  "SANTIAGO DE PUPUJA", "TIRAPATA"])
FILAS += _filas("PUNO", "CHUCUITO", 3, "TODOS LOS DISTRITOS",
                 ["DESAGUADERO", "HUACULLANI", "JULI", "KELLUYO", "PISACOMA",
                  "POMATA", "ZEPITA"])
FILAS += _filas("PUNO", "EL COLLAO", 3, "TODOS LOS DISTRITOS",
                 ["CAPAZO", "CONDURIRI", "ILAVE", "PILCUYO", "SANTA ROSA"])
FILAS += _filas("PUNO", "LAMPA", 2, "TRES DISTRITOS",
                 ["CALAPUJA", "NICASIO", "PUCARÁ"])
FILAS += _filas("PUNO", "LAMPA", 3, "SIETE DISTRITOS",
                 ["CABANILLA", "LAMPA", "OCUVIRI", "PALCA", "PARATIA",
                  "SANTA LUCÍA", "VILAVILA"])
FILAS += _filas("PUNO", "MELGAR", 2, "TODOS LOS DISTRITOS",
                 ["ANTAUTA", "AYAVIRI", "CUPI", "LLALLI", "MACARI", "NUÑOA",
                  "ORURILLO", "SANTA ROSA", "UMACHIRI"])
FILAS += _filas("PUNO", "SAN ROMÁN", 3, "TODOS LOS DISTRITOS",
                 ["JULIACA", "CABANA", "CABANILLAS", "CARACOTO"])
FILAS += _filas("PUNO", "YUNGUYO", 3, "TODOS LOS DISTRITOS",
                 ["YUNGUYO", "ANAPIA", "COPANI", "CUTURAPI", "OLLARAYA",
                  "TINICACHI", "UNICACHI"])

# ═══════════════════════════════════════════════════════════════════════
# AMAZONAS (región, 7/7 provincias)
# ═══════════════════════════════════════════════════════════════════════
FILAS += _filas("AMAZONAS", "CHACHAPOYAS", 2, "TODOS LOS DISTRITOS",
                 ["ASUNCIÓN", "BALSAS", "CHACHAPOYAS", "CHETO", "CHILIQUÍN",
                  "CHUQUIBAMBA", "GRANADA", "HUANCAS", "LA JALCA", "LEVANTO",
                  "LEYMEBAMBA", "MAGDALENA", "MARISCAL CASTILLA", "MOLINOPAMPA",
                  "MONTEVIDEO", "OLLEROS", "QUINJALCA",
                  "SAN FRANCISCO DE DAGUAS", "SAN ISIDRO DE MAINO", "SOLOCO",
                  "SONCHE"])
FILAS += _filas("AMAZONAS", "BAGUA", 2, "TODOS LOS DISTRITOS",
                 ["ARAMANGO", "BAGUA", "COPALLIN", "EL PARCO", "IMAZA", "LA PECA"])
FILAS += _filas("AMAZONAS", "BONGARÁ", 2, "TODOS LOS DISTRITOS",
                 ["CHISQUILLA", "CHURUJA", "COROSHA", "CUISPES", "FLORIDA",
                  "JAZAN", "JUMBILLA", "RECTA", "SAN CARLOS", "SHIPASBAMBA",
                  "VALERA", "YAMBRASBAMBA"])
FILAS += _filas("AMAZONAS", "CONDORCANQUI", 2, "TODOS LOS DISTRITOS",
                 ["EL CENEPA", "NIEVA", "RÍO SANTIAGO"])
FILAS += _filas("AMAZONAS", "LUYA", 2, "TODOS LOS DISTRITOS",
                 ["CAMPORREDONDO", "COCABAMBA", "COLCAMAR", "CONILA",
                  "INGUILPATA", "LAMUD", "LONGUITA", "LONYA CHICO", "LUYA",
                  "LUYA VIEJO", "MARÍA", "OCALLI", "OCUMAL", "PISUQUIA",
                  "PROVIDENCIA", "SAN CRISTÓBAL", "SAN FRANCISCO DEL YESO",
                  "SAN JERÓNIMO", "SAN JUAN DE LOPECANCHA", "SANTA CATALINA",
                  "SANTO TOMÁS", "TINGO", "TRITA"])
FILAS += _filas("AMAZONAS", "UTCUBAMBA", 2, "TODOS LOS DISTRITOS",
                 ["BAGUA GRANDE", "CAJARURO", "CUMBA", "EL MILAGRO", "JAMALCA",
                  "LONYA GRANDE", "YAMON"])
FILAS += _filas("AMAZONAS", "RODRÍGUEZ DE MENDOZA", 2, "ONCE DISTRITOS",
                 ["CHIRIMOTO", "COCHAMAL", "HUAMBO", "LIMABAMBA", "LONGAR",
                  "MARISCAL BENAVIDES", "MILPUC", "OMIA", "SAN NICOLÁS",
                  "SANTA ROSA", "TOTORA"])
FILAS += _filas("AMAZONAS", "RODRÍGUEZ DE MENDOZA", 3, "UN DISTRITO",
                 ["VISTA ALEGRE"])

# ═══════════════════════════════════════════════════════════════════════
# SAN MARTÍN (región, 10/10 provincias)
# ═══════════════════════════════════════════════════════════════════════
FILAS += _filas("SAN MARTÍN", "BELLAVISTA", 2, "TODOS LOS DISTRITOS",
                 ["BELLAVISTA", "ALTO BIAVO", "BAJO BIAVO", "HUALLAGA",
                  "SAN PABLO", "SAN RAFAEL"])
FILAS += _filas("SAN MARTÍN", "HUALLAGA", 2, "TODOS LOS DISTRITOS",
                 ["SAPOSOA", "EL ESLABÓN", "PISCOYACU", "SACANCHE",
                  "TINGO DE SAPOSOA", "ALTO SAPOSOA"])
FILAS += _filas("SAN MARTÍN", "LAMAS", 3, "TODOS LOS DISTRITOS",
                 ["LAMAS", "ALONSO DE ALVARADO", "BARRANQUILLA", "CAYNARACHI",
                  "CUÑUMBUQUI", "PINTO RECODO", "RUMISAPA",
                  "SAN ROQUE DE CUMBAZA", "SHANAO", "TABALOSOS", "ZAPATEROS"])
FILAS += _filas("SAN MARTÍN", "MARISCAL CÁCERES", 2, "TODOS LOS DISTRITOS",
                 ["JUANJUÍ", "CAMPANILLA", "HUICUNGO", "PACHIZA", "PAJARILLO",
                  "JUANJUICILLO"])
FILAS += _filas("SAN MARTÍN", "PICOTA", 2, "TODOS LOS DISTRITOS",
                 ["PICOTA", "BUENOS AIRES", "CASPISAPA", "PILLUANA",
                  "PUCACACA", "SAN CRISTÓBAL", "SAN HILARIÓN", "SHAMBOYACU",
                  "TINGO DE PONAZA", "TRES UNIDOS"])
FILAS += _filas("SAN MARTÍN", "MOYOBAMBA", 3, "TODOS LOS DISTRITOS",
                 ["MOYOBAMBA", "CALZADA", "HABANA", "JEPELACIO", "SORITOR", "YANTALO"])
FILAS += _filas("SAN MARTÍN", "RIOJA", 3, "TODOS LOS DISTRITOS",
                 ["RIOJA", "AWAJÚN", "ELÍAS SOPLÍN VARGAS", "NUEVA CAJAMARCA",
                  "PARDO MIGUEL", "POSIC", "SAN FERNANDO", "YORONGOS", "YURACYACU"])
FILAS += _filas("SAN MARTÍN", "SAN MARTÍN", 2, "CUATRO DISTRITOS",
                 ["CHIPURANA", "EL PORVENIR", "HUIMBAYOC", "PAPAPLAYA"])
FILAS += _filas("SAN MARTÍN", "SAN MARTÍN", 3, "DIEZ DISTRITOS",
                 ["TARAPOTO", "ALBERTO LEVEAU", "CACATACHI", "CHAZUTA",
                  "JUAN GUERRA", "LA BANDA DE SHILCAYO", "MORALES",
                  "SAN ANTONIO", "SAUCE", "SHAPAJA"])
FILAS += _filas("SAN MARTÍN", "TOCACHE", 2, "TODOS LOS DISTRITOS",
                 ["TOCACHE", "NUEVO PROGRESO", "PÓLVORA", "SHUNTE", "UCHIZA"])
FILAS += _filas("SAN MARTÍN", "EL DORADO", 3, "TODOS LOS DISTRITOS",
                 ["SAN JOSÉ DE SISA", "AGUA BLANCA", "SAN MARTÍN", "SANTA ROSA",
                  "SHATOJA"])

# ═══════════════════════════════════════════════════════════════════════
# HUÁNUCO (región, 11/11 provincias)
# ═══════════════════════════════════════════════════════════════════════
FILAS += _filas("HUÁNUCO", "HUÁNUCO", 2, "TODOS LOS DISTRITOS",
                 ["HUÁNUCO", "AMARILIS", "CHINCHAO", "CHURUMBAMBA", "MARGOS",
                  "PILLCO MARCA", "QUISQUI", "SAN FRANCISCO DE CAYRÁN",
                  "SAN PEDRO DE CHAULÁN", "SANTA MARÍA DEL VALLE", "YARUMAYO",
                  "YACUS", "SAN PABLO DE PILLAO"])
FILAS += _filas("HUÁNUCO", "HUACAYBAMBA", 2, "TODOS LOS DISTRITOS",
                 ["HUACAYBAMBA", "CANCHABAMBA", "COCHABAMBA", "PINRA"])
FILAS += _filas("HUÁNUCO", "LEONCIO PRADO", 2, "TODOS LOS DISTRITOS",
                 ["RUPA-RUPA", "JOSÉ CRESPO Y CASTILLO",
                  "MARIANO DÁMASO BERAÚN", "DANIEL ALOMÍA ROBLES",
                  "FELIPE LUYANDO", "HERMILIO VALDIZÁN", "CASTILLO GRANDE",
                  "PUCAYACU", "SANTO DOMINGO DE ANDA"])
FILAS += _filas("HUÁNUCO", "MARAÑÓN", 2, "TODOS LOS DISTRITOS",
                 ["HUACRACHUCO", "CHOLÓN", "SAN BUENAVENTURA", "LA MORADA",
                  "SANTA ROSA DE ALTO YANAJANCA"])
FILAS += _filas("HUÁNUCO", "PUERTO INCA", 2, "TODOS LOS DISTRITOS",
                 ["PUERTO INCA", "CODO DEL POZUZO", "HONORIA", "TOURNAVISTA",
                  "YUYAPICHIS"])
FILAS += _filas("HUÁNUCO", "YAROWILCA", 2, "TODOS LOS DISTRITOS",
                 ["CHAVINILLO", "CAHUAC", "CHACABAMBA", "CHUPAN", "JACAS CHICO",
                  "OBAS", "PAMPAMARCA", "CHORAS"])
FILAS += _filas("HUÁNUCO", "PACHITEA", 2, "TODOS LOS DISTRITOS",
                 ["PANAO", "CHAGLLA", "MOLINO", "UMARI"])
FILAS += _filas("HUÁNUCO", "AMBO", 2, "TODOS LOS DISTRITOS",
                 ["AMBO", "CAYNA", "COLPAS", "CONCHAMARCA", "HUÁCAR",
                  "SAN FRANCISCO", "SAN RAFAEL", "TOMAY KICHWA"])
FILAS += _filas("HUÁNUCO", "HUAMALÍES", 2, "OCHO DISTRITOS",
                 ["ARANCAY", "CHAVÍN DE PARIARCA", "JACAS GRANDE", "JIRCAN",
                  "MONZÓN", "PUNCHAO", "SINGA", "TANTAMAYO"])
FILAS += _filas("HUÁNUCO", "HUAMALÍES", 3, "TRES DISTRITOS",
                 ["LLATA", "MIRAFLORES", "PUÑOS"])
FILAS += _filas("HUÁNUCO", "DOS DE MAYO", 2, "TRES DISTRITOS",
                 ["CHUQUIS", "MARÍAS", "QUIVILLA"])
FILAS += _filas("HUÁNUCO", "DOS DE MAYO", 3, "SEIS DISTRITOS",
                 ["LA UNIÓN", "PACHAS", "RIPÁN", "SHUNQUI", "SILLAPATA", "YANAS"])
FILAS += _filas("HUÁNUCO", "LAURICOCHA", 3, "TODOS LOS DISTRITOS",
                 ["BAÑOS", "JESÚS", "JIVIA", "QUEROPALCA", "RONDOS",
                  "SAN FRANCISCO DE ASÍS", "SAN MIGUEL DE CAURI"])

# ═══════════════════════════════════════════════════════════════════════
# PASCO (región, 3/3 provincias)
# ═══════════════════════════════════════════════════════════════════════
FILAS += _filas("PASCO", "OXAPAMPA", 2, "TODOS LOS DISTRITOS",
                 ["OXAPAMPA", "CHONTABAMBA", "HUANCABAMBA", "PALCAZU",
                  "POZUZO", "PUERTO BERMÚDEZ", "VILLA RICA"])
FILAS += _filas("PASCO", "PASCO", 2, "OCHO DISTRITOS",
                 ["HUACHÓN", "HUARIACA", "NINACACA", "PALLANCHACRA",
                  "PAUCARTAMBO", "SAN FRANCISCO DE ASÍS DE YARUSYACÁN",
                  "TICLACAYÁN", "YANACANCHA"])
FILAS += _filas("PASCO", "PASCO", 3, "CINCO DISTRITOS",
                 ["CHAUPIMARCA", "HUAYLLAY", "SIMÓN BOLÍVAR", "TINYAHUARCO",
                  "VICCO"])
FILAS += _filas("PASCO", "DANIEL A. CARRIÓN", 3, "TODOS LOS DISTRITOS",
                 ["YANAHUANCA", "CHACAYAN", "GOYLLARISQUIZGA", "PAUCAR",
                  "SAN PEDRO DE PILLAO", "SANTA ANA DE TUSI", "TAPUC",
                  "VILCABAMBA"])

# ═══════════════════════════════════════════════════════════════════════
# JUNÍN (región, 9/9 provincias)
# ═══════════════════════════════════════════════════════════════════════
FILAS += _filas("JUNÍN", "CHANCHAMAYO", 2, "TODOS LOS DISTRITOS",
                 ["CHANCHAMAYO", "PERENÉ", "PICHANAQUI", "SAN LUIS DE SHUARO",
                  "SAN RAMÓN", "VITOC"])
FILAS += _filas("JUNÍN", "SATIPO", 2, "TODOS LOS DISTRITOS",
                 ["COVIRIALI", "LLAYLLA", "MAZAMARI", "PAMPA HERMOSA",
                  "PANGOA", "RÍO NEGRO", "RÍO TAMBO", "SATIPO",
                  "VIZCATÁN DEL ENE"])
FILAS += _filas("JUNÍN", "TARMA", 2, "SEIS DISTRITOS",
                 ["ACOBAMBA", "HUASAHUASI", "PALCA", "PALCAMAYO",
                  "SAN PEDRO DE CAJAS", "TAPO"])
FILAS += _filas("JUNÍN", "TARMA", 3, "TRES DISTRITOS",
                 ["HUARICOLCA", "LA UNIÓN", "TARMA"])
FILAS += _filas("JUNÍN", "CONCEPCIÓN", 2, "CUATRO DISTRITOS",
                 ["ANDAMARCA", "COCHAS", "COMAS", "MARISCAL CASTILLA"])
FILAS += _filas("JUNÍN", "CONCEPCIÓN", 3, "ONCE DISTRITOS",
                 ["ACO", "CHAMBARA", "CONCEPCIÓN", "HEROÍNAS DE TOLEDO",
                  "MANZANARES", "MATAHUASI", "MITO", "NUEVE DE JULIO",
                  "ORCOTUNA", "SAN JOSÉ DE QUERO", "SANTA ROSA DE OCOPA"])
FILAS += _filas("JUNÍN", "CHUPACA", 3, "TODOS LOS DISTRITOS",
                 ["AHUAC", "CHONGOS BAJO", "CHUPACA", "HUACHAC",
                  "HUAMANCACA CHICO", "SAN JUAN DE JARPA", "SAN JUAN DE YSCOS",
                  "TRES DE DICIEMBRE", "YANACANCHA"])
FILAS += _filas("JUNÍN", "HUANCAYO", 2, "DOS DISTRITOS",
                 ["PARIAHUANCA", "SANTO DOMINGO DE ACOBAMBA"])
FILAS += _filas("JUNÍN", "HUANCAYO", 3, "VEINTISEIS DISTRITOS",
                 ["CARHUACALLANGA", "CHACAPAMPA", "CHICCHE", "CHILCA",
                  "CHONGOS ALTO", "CHUPURO", "COLCA", "CULLHUAS", "EL TAMBO",
                  "HUACRAPUQUIO", "HUALHUAS", "HUANCAN", "HUANCAYO",
                  "HUASICANCHA", "HUAYUCACHI", "INGENIO", "PILCOMAYO",
                  "PUCARA", "QUICHUAY", "QUILCAS", "SAN AGUSTÍN",
                  "SAN JERÓNIMO DE TUNÁN", "SAÑO", "SAPALLANGA", "SICAYA",
                  "VIQUES"])
FILAS += _filas("JUNÍN", "JAUJA", 2, "CUATRO DISTRITOS",
                 ["APATA", "MOLINOS", "MONOBAMBA", "RICRAN"])
FILAS += _filas("JUNÍN", "JAUJA", 3, "TREINTA DISTRITOS",
                 ["ACOLLA", "ATAURA", "CANCHAYLLO", "CURICACA", "EL MANTARO",
                  "HUAMALI", "HUARIPAMPA", "HUERTAS", "JANJAILLO", "JAUJA",
                  "JULCAN", "LEONOR ORDÓÑEZ", "LLOCLLAPAMPA", "MARCO", "MASMA",
                  "MASMA CHICCHE", "MUQUI", "MUQUIYAUYO", "PACA", "PACCHA",
                  "PANCÁN", "PARCO", "POMACANCHA", "SAN LORENZO",
                  "SAN PEDRO DE CHUNAN", "SAUSA", "SINCOS", "TUNANMARCA",
                  "YAULI", "YAUYOS"])
FILAS += _filas("JUNÍN", "JUNÍN", 2, "DOS DISTRITOS",
                 ["CARHUAMAYO", "ULCUMAYO"])
FILAS += _filas("JUNÍN", "JUNÍN", 3, "DOS DISTRITOS",
                 ["JUNÍN", "ONDORES"])
FILAS += _filas("JUNÍN", "YAULI", 3, "TODOS LOS DISTRITOS",
                 ["CHACAPALPA", "HUAY-HUAY", "LA OROYA", "MARCAPOMACOCHA",
                  "MOROCOCHA", "PACCHA", "SANTA BÁRBARA DE CARHUACAYÁN",
                  "SANTA ROSA DE SACCO", "SUITUCANCHA", "YAULI"])

# ═══════════════════════════════════════════════════════════════════════
# CUSCO (región, 13/13 provincias)
# ═══════════════════════════════════════════════════════════════════════
FILAS += _filas("CUSCO", "CALCA", 2, "TODOS LOS DISTRITOS",
                 ["CALCA", "COYA", "LAMAY", "LARES", "PISAC", "SAN SALVADOR",
                  "TARAY", "YANATILE"])
FILAS += _filas("CUSCO", "URUBAMBA", 2, "TODOS LOS DISTRITOS",
                 ["CHINCHERO", "HUAYLLABAMBA", "MACHU PICCHU", "MARAS",
                  "OLLANTAYTAMBO", "URUBAMBA", "YUCAY"])
FILAS += _filas("CUSCO", "PAUCARTAMBO", 2, "TODOS LOS DISTRITOS",
                 ["CAICAY", "CHALLABAMBA", "COLQUEPATA", "HUANCARANI",
                  "KOSÑIPATA", "PAUCARTAMBO"])
FILAS += _filas("CUSCO", "ANTA", 2, "TODOS LOS DISTRITOS",
                 ["ANCAHUASI", "ANTA", "CACHIMAYO", "CHINCHAYPUJIO",
                  "HUAROCONDO", "LIMATAMBO", "MOLLEPATA", "PUCYURA", "ZURITE"])
FILAS += _filas("CUSCO", "QUISPICANCHIS", 2, "TODOS LOS DISTRITOS",
                 ["ANDAHUAYLILLAS", "CAMANTI", "CCARHUAYO", "CCATCA", "CUSIPATA",
                  "HUARO", "LUCRE", "MARCAPATA", "OCONGATE", "OROPESA",
                  "QUIQUIJANA", "URCOS"])
FILAS += _filas("CUSCO", "PARURO", 2, "TODOS LOS DISTRITOS",
                 ["ACCHA", "CCAPI", "COLCHA", "HUANOQUITE", "OMACHA",
                  "PACCARITAMBO", "PARURO", "PILLPINTO"])
FILAS += _filas("CUSCO", "CANCHIS", 2, "TODOS LOS DISTRITOS",
                 ["ALTO PICHIGUA", "COMBAPATA", "MARANGANI", "PITUMARCA",
                  "SAN PABLO", "SAN PEDRO", "SUYCKUTAMBO", "TINTA"])
FILAS += _filas("CUSCO", "CANAS", 2, "TODOS LOS DISTRITOS",
                 ["CHECCA", "KUNTURKANKI", "LANGUI", "LAYO", "PAMPAMARCA",
                  "QUEHUE", "TÚPAC AMARU", "YANAOCA"])
FILAS += _filas("CUSCO", "ACOMAYO", 2, "TODOS LOS DISTRITOS",
                 ["ACOMAYO", "ACOPIA", "ACOS", "MOSOC LLACTA", "POMACANCHI",
                  "RONDOCAN", "SANGARARÁ"])
FILAS += _filas("CUSCO", "CUSCO", 2, "TODOS LOS DISTRITOS",
                 ["CCORCA", "CUSCO", "POROY", "SAN JERÓNIMO", "SAN SEBASTIÁN",
                  "SANTIAGO", "SAYLLA", "WANCHAQ"])
FILAS += _filas("CUSCO", "LA CONVENCIÓN", 2, "TODOS LOS DISTRITOS",
                 ["ECHARATI", "HUAYOPATA", "MARANURA", "OCOBAMBA", "PICHARI",
                  "QUELLOUNO", "QUIMBIRI", "SANTA ANA", "SANTA TERESA",
                  "VILCABAMBA", "MEGANTONI", "VILLA KINTIARINA"])
FILAS += _filas("CUSCO", "CHUMBIVILCAS", 2, "CUATRO DISTRITOS",
                 ["CAPACMARCA", "CHAMACA", "COLQUEMARCA", "LIVITACA"])
FILAS += _filas("CUSCO", "CHUMBIVILCAS", 3, "CUATRO DISTRITOS",
                 ["LLUSCO", "QUIÑOTA", "SANTO TOMÁS", "VELILLE"])
FILAS += _filas("CUSCO", "ESPINAR", 3, "TODOS LOS DISTRITOS",
                 ["CONDOROMA", "COPORAQUE", "ESPINAR", "OCORURO", "PALLPATA",
                  "PICHIGUA"])

# ═══════════════════════════════════════════════════════════════════════
# HUANCAVELICA (región, 7/7 provincias)
# ═══════════════════════════════════════════════════════════════════════
FILAS += _filas("HUANCAVELICA", "CHURCAMPA", 2, "TODOS LOS DISTRITOS",
                 ["ANCO", "CHINCHIHUASI", "CHURCAMPA", "COSME", "EL CARMEN",
                  "LA MERCED", "LOCROJA", "PACHAMARCA", "PAUCARBAMBA",
                  "SAN MIGUEL DE MAYOC", "SAN PEDRO DE CORIS"])
FILAS += _filas("HUANCAVELICA", "ACOBAMBA", 2, "TODOS LOS DISTRITOS",
                 ["ACOBAMBA", "ANDABAMBA", "ANTA", "CAJA", "MARCAS", "PAUCARÁ",
                  "POMACOCHA", "ROSARIO"])
FILAS += _filas("HUANCAVELICA", "TAYACAJA", 2, "DOCE DISTRITOS",
                 ["COLCABAMBA", "DANIEL HERNÁNDEZ", "HUACHOCOLPA",
                  "HUARIBAMBA", "QUISHUAR", "SALCABAMBA",
                  "SAN MARCOS DE ROCCHAC", "SARCAHUASI", "SURCUBAMBA",
                  "TINTAY PUNCU", "PICHOS", "ROBLE"])
FILAS += _filas("HUANCAVELICA", "TAYACAJA", 3, "OCHO DISTRITOS",
                 ["ACOSTAMBO", "ACRAQUIA", "AHUAYCHA", "HUANDO",
                  "ÑAHUIMPUQUIO", "PAMPAS", "PAZOS", "SANTIAGO DE TUCUMA"])
FILAS += _filas("HUANCAVELICA", "ANGARAES", 2, "UN DISTRITO", ["CHINCHO"])
FILAS += _filas("HUANCAVELICA", "ANGARAES", 3, "ONCE DISTRITOS",
                 ["ANCHONGA", "CALLANMARCA", "CCOCHACCASA", "CONGALLA",
                  "HUANCA HUANCA", "HUAYLLAY GRANDE", "JULCAMARCA", "LIRCAY",
                  "SAN ANTONIO DE ANTAPARCO", "SECCLLA", "STO TOMÁS DE PATA"])
FILAS += _filas("HUANCAVELICA", "HUANCAVELICA", 3, "TODOS LOS DISTRITOS",
                 ["ACOBAMBILLA", "ACORIA", "ASCENSIÓN", "CONAYCA", "CUENCA",
                  "HUACHOCOLPA", "HUANCAVELICA", "HUAYLLAHUARA", "IZCUCHACA",
                  "LARIA", "MANTA", "MARISCAL CÁCERES", "MOYA", "NUEVO OCCORO",
                  "PALCA", "PILCHACA", "VILCA", "YAULI"])
FILAS += _filas("HUANCAVELICA", "CASTROVIRREYNA", 3, "ONCE DISTRITOS",
                 ["ARMA", "AURAHUA", "CASTROVIRREYNA", "CHUPAMARCA", "COCAS",
                  "HUACHOS", "HUAMATAMBO", "MOLLEPAMPA", "SANTA ANA",
                  "TANTARÁ", "TICRAPO"])
FILAS += _filas("HUANCAVELICA", "CASTROVIRREYNA", 4, "DOS DISTRITOS",
                 ["CAPILLAS", "SAN JUAN"])
FILAS += _filas("HUANCAVELICA", "HUAYTARÁ", 3, "TRES DISTRITOS",
                 ["SAN ANTONIO DE CUSICANCHA", "PILPICHACA", "QUERCO"])
FILAS += _filas("HUANCAVELICA", "HUAYTARÁ", 4, "TRECE DISTRITOS",
                 ["AYAVÍ", "CÓRDOVA", "HUAYACUNDO ARMA", "HUAYTARÁ",
                  "LARAMARCA", "OCOYO", "QUITO ARMA",
                  "SAN FRANCISCO DE SANGAYAICO", "SAN ISIDRO",
                  "SANTIAGO DE CHOCORVOS", "SANTIAGO DE QUIRAHUARA",
                  "SANTO DOMINGO DE CAPILLAS", "TAMBO"])

# ═══════════════════════════════════════════════════════════════════════
# AYACUCHO (región, 11/11 provincias)
# ═══════════════════════════════════════════════════════════════════════
FILAS += _filas("AYACUCHO", "HUANTA", 2, "TODOS LOS DISTRITOS",
                 ["AYAHUANCO", "HIGUAIN", "HUAMANGUILLA", "HUANTA",
                  "LLOCHEGUA", "LURICOCHA", "SANTILLANA", "SIVIA", "CHACA"])
FILAS += _filas("AYACUCHO", "LA MAR", 2, "TODOS LOS DISTRITOS",
                 ["ANCO", "AYNA", "CHILCAS", "CHUNGUI", "LUIS CARRANZA",
                  "SAN MIGUEL", "SANTA ROSA", "TAMBO", "ORONCCOY"])
FILAS += _filas("AYACUCHO", "HUAMANGA", 2, "DIEZ DISTRITOS",
                 ["ACOCRO", "ACOSVINCHOS", "AYACUCHO", "JESÚS NAZARENO",
                  "OCROS", "PACAYCASA", "QUINUA", "SAN JOSÉ DE TICLLAS",
                  "SANTIAGO DE PISCHA", "TAMBILLO"])
FILAS += _filas("AYACUCHO", "HUAMANGA", 3, "CINCO DISTRITOS",
                 ["CARMEN ALTO", "CHIARA", "SAN JUAN BAUTISTA", "SOCOS",
                  "VINCHOS"])
FILAS += _filas("AYACUCHO", "VILCASHUAMÁN", 2, "UN DISTRITO", ["CONCEPCIÓN"])
FILAS += _filas("AYACUCHO", "VILCASHUAMÁN", 3, "SIETE DISTRITOS",
                 ["ACOMARCA", "CARHUANCA", "HUAMBALPA", "INDEPENDENCIA",
                  "SAURAMA", "VILCASHUAMÁN", "VISCHONGO"])
FILAS += _filas("AYACUCHO", "HUANCASANCOS", 3, "TODOS LOS DISTRITOS",
                 ["CARAPO", "SACSAMARCA", "SANCOS", "SANTIAGO DE LUCANAMARCA"])
FILAS += _filas("AYACUCHO", "CANGALLO", 3, "TODOS LOS DISTRITOS",
                 ["CANGALLO", "CHUSCHI", "LOS MOROCHUCOS",
                  "MARÍA PARADO DE BELLIDO", "PARAS", "TOTOS"])
FILAS += _filas("AYACUCHO", "PÁUCAR DEL SARA SARA", 3, "TODOS LOS DISTRITOS",
                 ["COLTA", "CORCULLA", "LAMPA", "MARCABAMBA", "OYOLO",
                  "PARARCA", "PAUSA", "SAN JAVIER DE ALPABAMBA",
                  "SAN JOSÉ DE USHUA", "SARA SARA"])
FILAS += _filas("AYACUCHO", "SUCRE", 3, "TODOS LOS DISTRITOS",
                 ["BELÉN", "CHALCOS", "CHILCAYOC", "HUACAÑA", "MORCOLLA",
                  "PAICO", "QUEROBAMBA", "SAN PEDRO DE LARCAY",
                  "SAN SALVADOR DE QUIJE", "SANTIAGO DE PAUCARAY", "SORAS"])
FILAS += _filas("AYACUCHO", "VÍCTOR FAJARDO", 3, "TODOS LOS DISTRITOS",
                 ["ALCAMENCA", "APONGO", "ASQUIPATA", "CANARIA", "CAYARA",
                  "COLCA", "HUAMANQUIQUIA", "HUANCAPI", "HUANCARAYLLA", "HUAYA",
                  "SARHUA", "VILCANCHOS"])
FILAS += _filas("AYACUCHO", "PARINACOCHAS", 3, "SEIS DISTRITOS",
                 ["CHUMPI", "CORACORA", "CORONEL CASTAÑEDA", "PACAPAUSA",
                  "SAN FRANCISCO DE RAVACAYCU", "UPAHUACHO"])
FILAS += _filas("AYACUCHO", "PARINACOCHAS", 4, "DOS DISTRITOS",
                 ["PULLO", "PUYUSCA"])
FILAS += _filas("AYACUCHO", "LUCANAS", 3, "DIEZ DISTRITOS",
                 ["AUCARA", "CABANA", "CARMEN SALCEDO", "CHAVIÑA", "CHIPAO",
                  "LUCANAS", "PUQUIO", "SAN JUAN", "SAN PEDRO DE PALCO",
                  "SANTA ANA DE HUAYCAHUACHO"])
FILAS += _filas("AYACUCHO", "LUCANAS", 4, "ONCE DISTRITOS",
                 ["HUAC HUAS", "LARAMATE", "LEONCIO PRADO", "LLAUTA", "OCAÑA",
                  "OTOCA", "SAISA", "SAN CRISTOBAL", "SAN PEDRO", "SANCOS",
                  "SANTA LUCÍA"])

# ═══════════════════════════════════════════════════════════════════════
# APURÍMAC (región, 7/7 provincias)
# ═══════════════════════════════════════════════════════════════════════
FILAS += _filas("APURÍMAC", "COTABAMBAS", 2, "TODOS LOS DISTRITOS",
                 ["CALLHUAHUACHO", "COTABAMBAS", "COYLLURQUI", "HAQUIRA",
                  "MARA", "TAMBOBAMBA"])
FILAS += _filas("APURÍMAC", "GRAU", 2, "TODOS LOS DISTRITOS",
                 ["CHUQUIBAMBILLA", "CURASCO", "CURPAHUASI", "GAMARRA",
                  "HUAYLLATI", "MAMARA", "MICAELA BASTIDAS", "PATAYPAMPA",
                  "PROGRESO", "SAN ANTONIO", "SANTA ROSA", "TURPAY",
                  "VILCABAMBA", "VIRUNDO"])
FILAS += _filas("APURÍMAC", "ABANCAY", 2, "TODOS LOS DISTRITOS",
                 ["ABANCAY", "CHACOCHE", "CIRCA", "CURAHUASI", "HUANIPACA",
                  "LAMBRAMA", "PICHIRHUA", "SAN PEDRO DE CACHORA", "TAMBURCO"])
FILAS += _filas("APURÍMAC", "CHINCHEROS", 2, "TODOS LOS DISTRITOS",
                 ["ANCO-HUALLO", "CHINCHEROS", "COCHARCAS", "HUACCANA",
                  "OCOBAMBA", "ONGOY", "RANRACANCHA", "URANMARCA",
                  "EL PORVENIR", "LOS CHANKAS", "ROCHACC"])
FILAS += _filas("APURÍMAC", "ANDAHUAYLAS", 2, "TRECE DISTRITOS",
                 ["ANDAHUAYLAS", "ANDARAPA", "HUANCARAMA", "HUANCARAY",
                  "KAQUIABAMBA", "KISHUARA", "PACOBAMBA", "PACUCHA",
                  "SAN ANTONIO DE CACHI", "SAN JERÓNIMO", "SANTA MARÍA DE CHICMO",
                  "TALAVERA", "TURPO"])
FILAS += _filas("APURÍMAC", "ANDAHUAYLAS", 3, "SEIS DISTRITOS",
                 ["CHIARA", "HUAYANA", "PAMPACHIRI", "POMACOCHA",
                  "SAN MIGUEL DE CHACCRAMPA", "TUMAY HUARACA"])
FILAS += _filas("APURÍMAC", "AYMARAES", 2, "CINCO DISTRITOS",
                 ["CHAPIMARCA", "COLCABAMBA", "LUCRE", "SAN JUAN DE CHACÑA",
                  "TINTAY"])
FILAS += _filas("APURÍMAC", "AYMARAES", 3, "DOCE DISTRITOS",
                 ["CAPAYA", "CARAYBAMBA", "CHALHUANCA", "COTARUSE", "HUAYLLO",
                  "JUSTO APU SAHUARAURA", "POCOHUANCA", "SAÑAYCA", "SORAYA",
                  "TAPAIRIHUA", "TORAYA", "YANACA"])
FILAS += _filas("APURÍMAC", "ANTABAMBA", 3, "TODOS LOS DISTRITOS",
                 ["ANTABAMBA", "EL ORO", "HIAQUIRCA",
                  "JUAN ESPINOZA MEDRANO", "OROPESA", "PACHACONAS", "SABAINO"])

# ═══════════════════════════════════════════════════════════════════════
# TUMBES (región, 3/3 provincias)
# ═══════════════════════════════════════════════════════════════════════
FILAS += _filas("TUMBES", "CONTRALMIRANTE VILLAR", 4, "TODOS LOS DISTRITOS",
                 ["CASITAS", "ZORRITOS"])
FILAS += _filas("TUMBES", "TUMBES", 4, "TODOS LOS DISTRITOS",
                 ["CORRALES", "LA CRUZ", "PAMPAS DE HOSPITAL", "SAN JACINTO",
                  "SAN JUAN DE LA VIRGEN", "TUMBES"])
FILAS += _filas("TUMBES", "ZARUMILLA", 4, "TODOS LOS DISTRITOS",
                 ["AGUAS VERDES", "MATAPALO", "PAPAYAL", "ZARUMILLA"])

# ═══════════════════════════════════════════════════════════════════════
# PIURA (región, 8/8 provincias)
# ═══════════════════════════════════════════════════════════════════════
FILAS += _filas("PIURA", "HUANCABAMBA", 3, "TODOS LOS DISTRITOS",
                 ["CANCHAQUE", "EL CARMEN DE LA FRONTERA", "HUANCABAMBA",
                  "HUARMACA", "LALAQUIZ", "SAN MIGUEL DE EL FAIQUE", "SONDOR",
                  "SONDORILLO"])
FILAS += _filas("PIURA", "AYABACA", 3, "SEIS DISTRITOS",
                 ["AYABACA", "JILILÍ", "LAGUNAS", "MONTERO", "PACAIPAMPA",
                  "SICCHEZ"])
FILAS += _filas("PIURA", "AYABACA", 4, "CUATRO DISTRITOS",
                 ["FRÍAS", "PAIMAS", "SAPILLICA", "SUYO"])
FILAS += _filas("PIURA", "MORROPÓN", 3, "SEIS DISTRITOS",
                 ["BUENOS AIRES", "CHALACO", "SALITRAL", "SAN JUAN DE BIGOTE",
                  "SANTA CATALINA DE MOSSA", "YAMANGO"])
FILAS += _filas("PIURA", "MORROPÓN", 4, "CUATRO DISTRITOS",
                 ["CHULUCANAS", "LA MATANZA", "MORROPÓN", "SANTO DOMINGO"])
FILAS += _filas("PIURA", "PIURA", 4, "TODOS LOS DISTRITOS",
                 ["CASTILLA", "CATACAOS", "CURA MORI", "EL TALLÁN", "LA ARENA",
                  "LA UNIÓN", "LAS LOMAS", "PIURA", "TAMBO GRANDE"])
FILAS += _filas("PIURA", "PAITA", 4, "TODOS LOS DISTRITOS",
                 ["AMOTAPE", "ARENAL", "COLÁN", "LA HUACA", "PAITA",
                  "TAMARINDO", "VICHAYAL"])
FILAS += _filas("PIURA", "SECHURA", 4, "TODOS LOS DISTRITOS",
                 ["BELLAVISTA LA UNIÓN", "BERNAL", "CRISTO NOS VALGA",
                  "RINCONADA LLICUAR", "SECHURA", "VICE"])
FILAS += _filas("PIURA", "SULLANA", 4, "TODOS LOS DISTRITOS",
                 ["BELLAVISTA", "IGNACIO ESCUDERO", "LANCONES", "MARCAVELICA",
                  "MIGUEL CHECA", "QUERECOTILLO", "SALITRAL", "SULLANA"])
FILAS += _filas("PIURA", "TALARA", 4, "TODOS LOS DISTRITOS",
                 ["EL ALTO", "LA BREA", "LOBITOS", "LOS ÓRGANOS", "MÁNCORA",
                  "PARIÑAS"])

# ═══════════════════════════════════════════════════════════════════════
# LAMBAYEQUE (región, 3/3 provincias)
# ═══════════════════════════════════════════════════════════════════════
FILAS += _filas("LAMBAYEQUE", "FERREÑAFE", 3, "DOS DISTRITOS",
                 ["CAÑARIS", "INCAHUASI"])
FILAS += _filas("LAMBAYEQUE", "FERREÑAFE", 4, "CUATRO DISTRITOS",
                 ["FERREÑAFE", "MANUEL A. MESONES MURO", "PITIPO",
                  "PUEBLO NUEVO"])
FILAS += _filas("LAMBAYEQUE", "LAMBAYEQUE", 3, "UN DISTRITO", ["SALAS"])
FILAS += _filas("LAMBAYEQUE", "LAMBAYEQUE", 4, "ONCE DISTRITOS",
                 ["CHOCHOPE", "ILLIMO", "JAYANCA", "LAMBAYEQUE", "MOCHUMI",
                  "MÓRROPE", "MOTUPE", "OLMOS", "PACORA", "SAN JOSÉ", "TÚCUME"])
FILAS += _filas("LAMBAYEQUE", "CHICLAYO", 4, "TODOS LOS DISTRITOS",
                 ["CAYALTÍ", "CHICLAYO", "CHONGOYAPE", "ETEN", "ETEN PUERTO",
                  "JOSÉ LEONARDO ORTIZ", "LA VICTORIA", "LAGUNAS", "MONSEFÚ",
                  "NUEVA ARICA", "OYOTÚN", "PATAPO", "PICSI", "PIMENTEL",
                  "POMALCA", "PUCALÁ", "REQUE", "SANTA ROSA", "SAÑA", "TUMÁN"])

# ═══════════════════════════════════════════════════════════════════════
# CAJAMARCA (región, 13/13 provincias)
# ═══════════════════════════════════════════════════════════════════════
FILAS += _filas("CAJAMARCA", "HUALGAYOC", 2, "TODOS LOS DISTRITOS",
                 ["BAMBAMARCA", "CHUGUR", "HUALGAYOC"])
FILAS += _filas("CAJAMARCA", "SAN IGNACIO", 2, "CINCO DISTRITOS",
                 ["CHIRINOS", "HUARANGO", "LA COIPA", "NAMBALLE", "SAN IGNACIO"])
FILAS += _filas("CAJAMARCA", "SAN IGNACIO", 2, "DOS DISTRITOS",
                 ["SAN JOSÉ DE LOURDES", "TABACONAS"])
FILAS += _filas("CAJAMARCA", "CELENDÍN", 2, "TODOS LOS DISTRITOS",
                 ["CELENDÍN", "CHUMUCH", "CORTEGANA", "HUASMIN",
                  "JORGE CHÁVEZ", "JOSÉ GÁLVEZ", "LA LIBERTAD DE PALLAN",
                  "MIGUEL IGLESIAS", "OXAMARCA", "SOROCHUCO", "SUCRE", "UTCO"])
FILAS += _filas("CAJAMARCA", "CUTERVO", 2, "CATORCE DISTRITOS",
                 ["CALLAYUC", "CHOROS", "CUJILLO", "CUTERVO", "LA RAMADA",
                  "PIMPINGOS", "SAN ANDRÉS DE CUTERVO", "SAN JUAN DE CUTERVO",
                  "SAN LUIS DE LUCMA", "SANTA CRUZ",
                  "SANTO DOMINGO DE LA CAPILLA", "SANTO TOMÁS", "SOCOTA",
                  "TORIBIO CASANOVA"])
FILAS += _filas("CAJAMARCA", "CUTERVO", 3, "UN DISTRITO", ["QUEROCOTILLO"])
FILAS += _filas("CAJAMARCA", "JAÉN", 2, "OCHO DISTRITOS",
                 ["BELLAVISTA", "CHONTALI", "COLASAY", "HUABAL", "JAÉN",
                  "LAS PIRIAS", "SAN JOSÉ DEL ALTO", "SANTA ROSA"])
FILAS += _filas("CAJAMARCA", "JAÉN", 3, "CUATRO DISTRITOS",
                 ["POMAHUACA", "PUCARÁ", "SALLIQUE", "SAN FELIPE"])
FILAS += _filas("CAJAMARCA", "SAN MARCOS", 2, "CUATRO DISTRITOS",
                 ["GREGORIO PITA", "ICHOCÁN", "JOSÉ MANUEL QUIROZ",
                  "JOSÉ SABOGAL"])
FILAS += _filas("CAJAMARCA", "SAN MARCOS", 3, "TRES DISTRITOS",
                 ["CHANCAY", "EDUARDO VILLANUEVA", "PEDRO GÁLVEZ"])
FILAS += _filas("CAJAMARCA", "CHOTA", 2, "DOCE DISTRITOS",
                 ["ANGUIA", "CHADÍN", "CHALAMARCA", "CHIGUIRIP", "CHIMBAN",
                  "CHOROPAMPA", "CHOTA", "CONCHAN", "LAJAS", "PACCHA", "PIÓN",
                  "TACABAMBA"])
FILAS += _filas("CAJAMARCA", "CHOTA", 3, "SIETE DISTRITOS",
                 ["COCHABAMBA", "HUAMBOS", "LLAMA", "MIRACOSTA", "QUEROCOTO",
                  "SAN JUAN DE LICUPIS", "TOCMOCHE"])
FILAS += _filas("CAJAMARCA", "CAJABAMBA", 2, "UN DISTRITO", ["SITACOCHA"])
FILAS += _filas("CAJAMARCA", "CAJABAMBA", 3, "TRES DISTRITOS",
                 ["CACHACHI", "CAJABAMBA", "CONDEBAMBA"])
FILAS += _filas("CAJAMARCA", "CAJAMARCA", 2, "UN DISTRITO", ["ENCAÑADA"])
FILAS += _filas("CAJAMARCA", "CAJAMARCA", 3, "ONCE DISTRITOS",
                 ["ASUNCIÓN", "CAJAMARCA", "CHETILLA", "COSPÁN", "JESÚS",
                  "LLACANORA", "LOS BAÑOS DEL INCA", "MAGDALENA", "MATARA",
                  "NAMORA", "SAN JUAN"])
FILAS += _filas("CAJAMARCA", "CONTUMAZÁ", 3, "TODOS LOS DISTRITOS",
                 ["CHILETE", "CONTUMAZÁ", "CUPISNIQUE", "GUZMANGO",
                  "SAN BENITO", "SANTA CRUZ DE TOLEDO", "TANTARICA", "YONÁN"])
FILAS += _filas("CAJAMARCA", "SAN MIGUEL", 3, "TODOS LOS DISTRITOS",
                 ["BOLÍVAR", "CALQUIS", "CATILLUC", "EL PRADO", "LA FLORIDA",
                  "LLAPA", "NANCHOC", "NIEPOS", "SAN GREGORIO", "SAN MIGUEL",
                  "SAN SILVESTRE DE COCHAN", "TONGOD", "UNIÓN AGUA BLANCA"])
FILAS += _filas("CAJAMARCA", "SAN PABLO", 2, "TODOS LOS DISTRITOS",
                 ["SAN BERNARDINO", "SAN LUIS", "SAN PABLO", "TUMBADEN"])
FILAS += _filas("CAJAMARCA", "SANTA CRUZ", 2, "TODOS LOS DISTRITOS",
                 ["ANDABAMBA", "CATACHE", "CHANCAYBAÑOS", "LA ESPERANZA",
                  "NINABAMBA", "PULÁN", "SANTA CRUZ", "SAUCEPAMPA", "SEXI",
                  "UTICYACU", "YAUYUCAN"])

# ═══════════════════════════════════════════════════════════════════════
# LA LIBERTAD (región, 12/12 provincias)
# ═══════════════════════════════════════════════════════════════════════
FILAS += _filas("LA LIBERTAD", "BOLÍVAR", 2, "TODOS LOS DISTRITOS",
                 ["BAMBAMARCA", "BOLÍVAR", "CONDORMARCA", "LONGOTEA",
                  "UCHUMARCA", "UCUNCHA"])
FILAS += _filas("LA LIBERTAD", "PATAZ", 2, "TODOS LOS DISTRITOS",
                 ["BULDIBUYO", "CHILLIA", "HUANCASPATA", "HUAYLILLAS", "HUAYO",
                  "ONGÓN", "PARCOY", "PATAZ", "PIAS", "SANTIAGO DE CHALLAS",
                  "TAURIJA", "TAYABAMBA", "URPAY"])
FILAS += _filas("LA LIBERTAD", "SÁNCHEZ CARRIÓN", 2, "DOS DISTRITOS",
                 ["COCHORCO", "SARTIMBAMBA"])
FILAS += _filas("LA LIBERTAD", "SÁNCHEZ CARRIÓN", 3, "SEIS DISTRITOS",
                 ["CHUGAY", "CURGOS", "HUAMACHUCO", "MARCABAL", "SANAGORAN",
                  "SARÍN"])
FILAS += _filas("LA LIBERTAD", "SANTIAGO DE CHUCO", 3, "TODOS LOS DISTRITOS",
                 ["ANGASMARCA", "CACHICADÁN", "MOLLEBAMBA", "MOLLEPATA",
                  "QUIRUVILCA", "SANTA CRUZ DE CHUCA", "SANTIAGO DE CHUCO",
                  "SITABAMBA"])
FILAS += _filas("LA LIBERTAD", "GRAN CHIMÚ", 3, "TODOS LOS DISTRITOS",
                 ["CASCAS", "LUCMA", "MARMOT", "SAYAPULLO"])
FILAS += _filas("LA LIBERTAD", "JULCÁN", 3, "TODOS LOS DISTRITOS",
                 ["CALAMARCA", "CARABAMBA", "HUASO", "JULCÁN"])
FILAS += _filas("LA LIBERTAD", "OTUZCO", 3, "TODOS LOS DISTRITOS",
                 ["AGALLPAMPA", "CHARAT", "HUARANCHAL", "LA CUESTA", "MACHE",
                  "OTUZCO", "PARANDAY", "SALPO", "SINSICAP", "USQUIL"])
FILAS += _filas("LA LIBERTAD", "CHEPÉN", 4, "TODOS LOS DISTRITOS",
                 ["CHEPÉN", "PACANGA", "PUEBLO NUEVO"])
FILAS += _filas("LA LIBERTAD", "ASCOPE", 4, "TODOS LOS DISTRITOS",
                 ["ASCOPE", "CASA GRANDE", "CHICAMA", "CHOCOPE",
                  "MAGDALENA DE CAO", "PAIJÁN", "RÁZURI", "SANTIAGO DE CAO"])
FILAS += _filas("LA LIBERTAD", "PACASMAYO", 4, "TODOS LOS DISTRITOS",
                 ["GUADALUPE", "JEQUETEPEQUE", "PACASMAYO", "SAN JOSÉ",
                  "SAN PEDRO DE LLOC"])
FILAS += _filas("LA LIBERTAD", "TRUJILLO", 4, "TODOS LOS DISTRITOS",
                 ["EL PORVENIR", "FLORENCIA DE MORA", "HUANCHACO",
                  "LA ESPERANZA", "LAREDO", "MOCHE", "POROTO", "SALAVERRY",
                  "SIMBAL", "TRUJILLO", "VÍCTOR LARCO HERRERA"])
FILAS += _filas("LA LIBERTAD", "VIRÚ", 4, "TODOS LOS DISTRITOS",
                 ["CHAO", "GUADALUPITO", "VIRÚ"])

# ═══════════════════════════════════════════════════════════════════════
# ÁNCASH (región, 20/20 provincias)
# ═══════════════════════════════════════════════════════════════════════
FILAS += _filas("ÁNCASH", "ANTONIO RAYMONDI", 2, "TRES DISTRITOS",
                 ["CHACCHO", "CHINGA", "LLAMELLIN"])
FILAS += _filas("ÁNCASH", "ANTONIO RAYMONDI", 3, "TRES DISTRITOS",
                 ["ACZO", "MIRGAS", "SAN JUAN DE RONTOY"])
FILAS += _filas("ÁNCASH", "HUARI", 2, "SEIS DISTRITOS",
                 ["ANRA", "HUACACHI", "HUACCHIS", "PAUCAS", "RAPAYÁN", "UCO"])
FILAS += _filas("ÁNCASH", "HUARI", 3, "DIEZ DISTRITOS",
                 ["CAJAY", "CHAVÍN DE HUANTAR", "HUACHIS", "HUANTAR", "HUARI",
                  "MASIN", "PONTO", "RAHUAPAMPA", "SAN MARCOS",
                  "SAN PEDRO DE CHANA"])
FILAS += _filas("ÁNCASH", "ASUNCIÓN", 3, "TODOS LOS DISTRITOS",
                 ["ACOCHACA", "CHACAS"])
FILAS += _filas("ÁNCASH", "CARHUAZ", 3, "TODOS LOS DISTRITOS",
                 ["ACOPAMPA", "AMASHCA", "ANTA", "ATAQUERO", "CARHUAZ",
                  "MARCARÁ", "PARIAHUANCA", "SAN MIGUEL DE ACO", "SHILLA",
                  "TINCO", "YUNGAR"])
FILAS += _filas("ÁNCASH", "CARLOS F. FITZCARRALD", 3, "TODOS LOS DISTRITOS",
                 ["SAN LUIS", "SAN NICOLÁS", "YAUYA"])
FILAS += _filas("ÁNCASH", "CORONGO", 3, "TODOS LOS DISTRITOS",
                 ["ACO", "BAMBAS", "CORONGO", "CUSCA", "LA PAMPA", "YÁNAC",
                  "YUPÁN"])
FILAS += _filas("ÁNCASH", "MARISCAL LUZURIAGA", 3, "TODOS LOS DISTRITOS",
                 ["CASCA", "ELEAZAR GUZMÁN BARRÓN", "FIDEL OLIVAS ESCUDERO",
                  "LLAMA", "LLUMPA", "LUCMA", "MUSGA", "PISCOBAMBA"])
FILAS += _filas("ÁNCASH", "PALLASCA", 3, "TODOS LOS DISTRITOS",
                 ["BOLOGNESI", "CABANA", "CONCHUCOS", "HUACASCHUQUE",
                  "HUANDOVAL", "LACABAMBA", "LLAPO", "PALLASCA", "PAMPAS",
                  "SANTA ROSA", "TAUCA"])
FILAS += _filas("ÁNCASH", "POMABAMBA", 3, "TODOS LOS DISTRITOS",
                 ["HUAYLLÁN", "PAROBAMBA", "POMABAMBA", "QUINUABAMBA"])
FILAS += _filas("ÁNCASH", "SIHUAS", 3, "TODOS LOS DISTRITOS",
                 ["ACOBAMBA", "ALFONSO UGARTE", "CASHAPAMPA", "CHINGALPO",
                  "HUAYLLABAMBA", "QUICHES", "RAGASH", "SAN JUAN",
                  "SICSIBAMBA", "SIHUAS"])
FILAS += _filas("ÁNCASH", "HUAYLAS", 3, "TODOS LOS DISTRITOS",
                 ["CARAZ", "HUALLANCA", "HUATA", "HUAYLAS", "MATO",
                  "PAMPAROMAS", "PUEBLO LIBRE", "SANTA CRUZ", "SANTO TORIBIO",
                  "YURACMARCA"])
FILAS += _filas("ÁNCASH", "YUNGAY", 3, "TODOS LOS DISTRITOS",
                 ["CASCAPARA", "MANCOS", "MATACOTO", "QUILLO", "RANRAHIRCA",
                  "SHUPLUY", "YANAMA", "YUNGAY"])
FILAS += _filas("ÁNCASH", "HUARAZ", 3, "TODOS LOS DISTRITOS",
                 ["COCHABAMBA", "COLCABAMBA", "HUANCHAY", "HUARAZ",
                  "INDEPENDENCIA", "JANGAS", "LA LIBERTAD", "OLLEROS", "PAMPAS",
                  "PARIACOTO", "PIRA", "TARICA"])
FILAS += _filas("ÁNCASH", "BOLOGNESI", 3, "TODOS LOS DISTRITOS",
                 ["ABELARDO PARDO LEZAMETA", "ANTONIO RAYMONDI", "AQUIA",
                  "CAJACAY", "CANIS", "CHIQUIAN", "COLQUIOC", "HUALLANCA",
                  "HUASTA", "HUAYLLACAYAN", "LA PRIMAVERA", "MANGAS",
                  "PACLLON", "SAN MIGUEL DE CORPANQUI", "TICLLOS"])
FILAS += _filas("ÁNCASH", "RECUAY", 3, "TODOS LOS DISTRITOS",
                 ["CATAC", "COTAPARACO", "HUAYLLAPAMPA", "LLACLLIN", "MARCA",
                  "PAMPAS CHICO", "PARARIN", "RECUAY", "TAPACOCHA",
                  "TICAPAMPA"])
FILAS += _filas("ÁNCASH", "AIJA", 3, "DOS DISTRITOS", ["AIJA", "CORIS"])
FILAS += _filas("ÁNCASH", "AIJA", 4, "TRES DISTRITOS",
                 ["LA MERCED", "HUACLLÁN", "SUCCHA"])
FILAS += _filas("ÁNCASH", "OCROS", 3, "OCHO DISTRITOS",
                 ["ACAS", "CAJAMARQUILLA", "CARHUAPAMPA", "CONGAS", "LLIPA",
                  "OCROS", "S. CRISTÓBAL DE RAJÁN", "SANTIAGO DE CHILCAS"])
FILAS += _filas("ÁNCASH", "OCROS", 4, "DOS DISTRITOS", ["COCHAS", "SAN PEDRO"])
FILAS += _filas("ÁNCASH", "HUARMEY", 3, "TRES DISTRITOS",
                 ["COCHAPETI", "HUAYAN", "MALVAS"])
FILAS += _filas("ÁNCASH", "HUARMEY", 4, "DOS DISTRITOS",
                 ["CULEBRAS", "HUARMEY"])
FILAS += _filas("ÁNCASH", "SANTA", 3, "TRES DISTRITOS",
                 ["CÁCERES DEL PERÚ", "MACATE", "MORO"])
FILAS += _filas("ÁNCASH", "SANTA", 4, "SEIS DISTRITOS",
                 ["CHIMBOTE", "COISHCO", "NEPEÑA", "NUEVO CHIMBOTE",
                  "SAMANCO", "SANTA"])
FILAS += _filas("ÁNCASH", "CASMA", 4, "TODOS LOS DISTRITOS",
                 ["BUENA VISTA ALTA", "CASMA", "COMANDANTE NOEL", "YAUTÁN"])

# ═══════════════════════════════════════════════════════════════════════
# LIMA (región, 10/10 provincias)
# ═══════════════════════════════════════════════════════════════════════
FILAS += _filas("LIMA", "CAJATAMBO", 3, "CINCO DISTRITOS",
                 ["CAJATAMBO", "COPA", "GORGOR", "HUACAPÓN", "MANÁS"])
FILAS += _filas("LIMA", "OYÓN", 3, "TODOS LOS DISTRITOS",
                 ["ANDAJES", "CAUJUL", "COCHAMARCA", "NAVÁN", "OYÓN",
                  "PACHANGARA"])
FILAS += _filas("LIMA", "YAUYOS", 3, "VEINTINUEVE DISTRITOS",
                 ["ALIS", "AYAUCA", "AYAVIRÍ", "AZÁNGARO", "CACRA", "CARANIA",
                  "CATAHUASI", "CHOCOS", "COCHAS", "COLONIA", "HONGOS",
                  "HUAMPARA", "HUANCAYA", "HUANGÁSCAR", "HUANTÁN", "HUAÑEC",
                  "LARAOS", "LINCHA", "MADEAN", "MIRAFLORES", "QUINCHES",
                  "SAN JOAQUÍN", "SAN LORENZO DE PUTINZA",
                  "SAN PEDRO DE PILAS", "TANTA", "TOMAS", "TUPE", "VIÑAC",
                  "VITIS", "YAUYOS"])
FILAS += _filas("LIMA", "YAUYOS", 4, "TRES DISTRITOS",
                 ["OMAS", "QUINOCAY", "TAURIPAMPA"])
FILAS += _filas("LIMA", "HUAROCHIRÍ", 3, "VEINTICINCO DISTRITOS",
                 ["CALLAHUANCA", "CARAMPOMA", "CHICLA", "HUACHUPAMPA",
                  "HUANZA", "HUAROCHIRÍ", "LAHUAYTAMBO", "LANGA", "LARAOS",
                  "MATUCANA", "SAN ANDRÉS DE TUPICOCHA", "SAN BARTOLOMÉ",
                  "SAN DAMIÁN", "S. JERÓNIMO DE SURCO", "SAN JUAN DE IRIS",
                  "SAN JUAN DE TANTARANCHE", "SAN LORENZO DE QUINTI",
                  "SAN MATEO", "SAN MATEO DE OTAO", "SAN PEDRO DE CASTA",
                  "SAN PEDRO DE HUANCAYRE", "SANGALLAYA",
                  "SANTA CRUZ DE COCACHACRA", "SANTIAGO DE ANCHUCAYA",
                  "SANTIAGO DE TUNA"])
FILAS += _filas("LIMA", "HUAROCHIRÍ", 4, "SIETE DISTRITOS",
                 ["ANTIOQUÍA", "CUENCA", "MARIATANA", "RICARDO PALMA",
                  "SAN ANTONIO DE CHACLLA", "SANTA EULALIA",
                  "SANTO DOMINGO DE OLLEROS"])
FILAS += _filas("LIMA", "CANTA", 3, "CUATRO DISTRITOS",
                 ["CANTA", "HUAROS", "LACHAQUI", "SAN BUENAVENTURA"])
FILAS += _filas("LIMA", "CANTA", 4, "TRES DISTRITOS",
                 ["ARAHUAY", "HUAMANTANGA", "SANTA ROSA DE QUIVES"])
FILAS += _filas("LIMA", "HUARAL", 3, "NUEVE DISTRITOS",
                 ["ATAVILLOS ALTO", "ATAVILLOS BAJO", "IHUARÍ", "LAMPIÁN",
                  "PACARAOS", "SAN MIGUEL DE ACOS", "SANTA CRUZ DE ANDAMARCA",
                  "SUMBILCA", "VEINTISIETE DE NOVIEMBRE"])
FILAS += _filas("LIMA", "HUARAL", 4, "TRES DISTRITOS",
                 ["AUCALLAMA", "CHANCAY", "HUARAL"])
FILAS += _filas("LIMA", "HUAURA", 3, "CUATRO DISTRITOS",
                 ["CHECRAS", "LEONCIO PRADO", "PACCHO", "SANTA LEONOR"])
FILAS += _filas("LIMA", "HUAURA", 4, "OCHO DISTRITOS",
                 ["ÁMBAR", "CALETA DE CARQUÍN", "HUACHO", "HUALMAY", "HUAURA",
                  "SANTA MARÍA", "SAYÁN", "VEGUETA"])
FILAS += _filas("LIMA", "CAÑETE", 3, "UN DISTRITO", ["ZÚÑIGA"])
FILAS += _filas("LIMA", "CAÑETE", 4, "QUINCE DISTRITOS",
                 ["ASIA", "CALANGO", "CERRO AZUL", "CHILCA", "COAYLLO",
                  "IMPERIAL", "LUNAHUANÁ", "MALA", "NUEVO IMPERIAL", "PACARÁN",
                  "QUILMANÁ", "SAN ANTONIO", "SAN LUIS",
                  "SAN VICENTE DE CAÑETE", "SANTA CRUZ DE FLORES"])
FILAS += _filas("LIMA", "BARRANCA", 4, "TODOS LOS DISTRITOS",
                 ["BARRANCA", "PARAMONGA", "PATIVILCA", "SUPE", "SUPE PUERTO"])
FILAS += _filas("LIMA", "LIMA", 4, "TODOS LOS DISTRITOS",
                 ["ANCÓN", "ATE", "BARRANCO", "BREÑA", "CARABAYLLO",
                  "CHACLACAYO", "CHORRILLOS", "CIENEGUILLA", "COMAS",
                  "EL AGUSTINO", "INDEPENDENCIA", "JESÚS MARÍA", "LA MOLINA",
                  "LA VICTORIA", "LIMA", "LINCE", "LOS OLIVOS",
                  "LURIGANCHO-CHOSICA", "LURÍN", "MAGDALENA DEL MAR",
                  "MIRAFLORES", "PACHACÁMAC", "PUCUSANA", "PUEBLO LIBRE",
                  "PUENTE PIEDRA", "PUNTA HERMOSA", "PUNTA NEGRA", "RÍMAC",
                  "SAN BARTOLO", "SAN BORJA", "SAN ISIDRO",
                  "SAN JUAN DE LURIGANCHO", "SAN JUAN DE MIRAFLORES",
                  "SAN LUIS", "SAN MARTÍN DE PORRES", "SAN MIGUEL",
                  "SANTA ANITA", "SANTA MARÍA DEL MAR", "SANTA ROSA",
                  "SANTIAGO DE SURCO", "SURQUILLO", "VILLA EL SALVADOR",
                  "VILLA MARÍA DEL TRIUNFO"])

# ═══════════════════════════════════════════════════════════════════════
# CALLAO (región, 1/1 provincia) -- el PDF no incluye "Mi Perú" en esta
# edición, no se agrega por inferencia.
# ═══════════════════════════════════════════════════════════════════════
FILAS += _filas("CALLAO", "CALLAO", 4, "TODOS LOS DISTRITOS",
                 ["BELLAVISTA", "CALLAO", "CARMEN DE LA LEGUA-REYNOSO",
                  "LA PERLA", "LA PUNTA", "VENTANILLA"])

# ═══════════════════════════════════════════════════════════════════════
# ICA (región, 5/5 provincias)
# ═══════════════════════════════════════════════════════════════════════
FILAS += _filas("ICA", "CHINCHA", 3, "UN DISTRITO", ["SAN PEDRO DE HUACARPANA"])
FILAS += _filas("ICA", "CHINCHA", 4, "DIEZ DISTRITOS",
                 ["ALTO LARÁN", "CHAVÍN", "CHINCHA ALTA", "CHINCHA BAJA",
                  "EL CARMEN", "GROCIO PRADO", "PUEBLO NUEVO",
                  "SAN JUAN DE YANAC", "SUNAMPE", "TAMBO DE MORA"])
FILAS += _filas("ICA", "PALPA", 4, "TODOS LOS DISTRITOS",
                 ["LLIPATA", "PALPA", "RÍO GRANDE", "SANTA CRUZ", "TIBILLO"])
FILAS += _filas("ICA", "ICA", 4, "TODOS LOS DISTRITOS",
                 ["ICA", "LA TINGUIÑA", "LOS AQUIJES", "OCUCAJE", "PACHACÚTEC",
                  "PARCONA", "PUEBLO NUEVO", "SALAS", "SAN JOSÉ DE LOS MOLINOS",
                  "SAN JUAN BAUTISTA", "SANTIAGO", "SUBTANJALLA", "TATE",
                  "YAUCA DEL ROSARIO"])
FILAS += _filas("ICA", "NAZCA", 4, "TODOS LOS DISTRITOS",
                 ["CHANGUILLO", "EL INGENIO", "MARCONA", "NAZCA", "VISTA ALEGRE"])
FILAS += _filas("ICA", "PISCO", 4, "TODOS LOS DISTRITOS",
                 ["HUANCANO", "HUMAY", "INDEPENDENCIA", "PARACAS", "PISCO",
                  "SAN ANDRÉS", "SAN CLEMENTE", "TÚPAC AMARU INCA"])

# ═══════════════════════════════════════════════════════════════════════
# AREQUIPA (región, 8/8 provincias)
# ═══════════════════════════════════════════════════════════════════════
FILAS += _filas("AREQUIPA", "LA UNIÓN", 3, "TODOS LOS DISTRITOS",
                 ["ALCA", "CHARCANA", "COTAHUASI", "HUAYNACOTAS", "PAMPAMARCA",
                  "PUYCA", "QUECHUALLA", "SAYLA", "TAURIA", "TOMEPAMPA",
                  "TORO"])
FILAS += _filas("AREQUIPA", "CAYLLOMA", 3, "DIECINUEVE DISTRITOS",
                 ["ACHOMA", "CABANACONDE", "CALLALLI", "CAYLLOMA", "CHIVAY",
                  "COPORAQUE", "HUAMBO", "HUANCA", "ICHUPAMPA", "LARI",
                  "LLUTA", "MACA", "MADRIGAL", "SAN ANTONIO DE CHUCA",
                  "SIBAYO", "TAPAY", "TISCO", "TUTI", "YANQUE"])
FILAS += _filas("AREQUIPA", "CAYLLOMA", 4, "UN DISTRITO", ["MAJES"])
FILAS += _filas("AREQUIPA", "CASTILLA", 3, "ONCE DISTRITOS",
                 ["ANDAGUA", "AYO", "CHACHAS", "CHILCAYMARCA", "CHOCO",
                  "MACHAGUAY", "ORCOPAMPA", "PAMPACOLCA", "TIPÁN", "UÑÓN",
                  "VIRACO"])
FILAS += _filas("AREQUIPA", "CASTILLA", 4, "TRES DISTRITOS",
                 ["APLAO", "HUANCARQUI", "URACA"])
FILAS += _filas("AREQUIPA", "AREQUIPA", 3, "VEINTIUN DISTRITOS",
                 ["ALTO SELVA ALEGRE", "AREQUIPA", "CAYMA", "CERRO COLORADO",
                  "CHARACATO", "CHIGUATA", "JACOBO HUNTER",
                  "JOSÉ LUIS BUSTAMANTE Y RIVERO", "MARIANO MELGAR",
                  "MIRAFLORES", "MOLLEBAYA", "PAUCARPATA", "POCSI",
                  "QUEQUEÑA", "SABANDIA", "SACHACA", "SAN JUAN DE TARUCANI",
                  "SOCABAYA", "TIABAYA", "YANAHUARA", "YURA"])
FILAS += _filas("AREQUIPA", "AREQUIPA", 4, "OCHO DISTRITOS",
                 ["LA JOYA", "POLOBAYA", "SAN JUAN DE SIGUAS",
                  "SANTA ISABEL DE SIGUAS", "SANTA RITA DE SIGUAS",
                  "UCHUMAYO", "VÍTOR", "YARABAMBA"])
FILAS += _filas("AREQUIPA", "CONDESUYOS", 3, "TRES DISTRITOS",
                 ["CAYARANI", "CHICHAS", "SALAMANCA"])
FILAS += _filas("AREQUIPA", "CONDESUYOS", 4, "CINCO DISTRITOS",
                 ["ANDARAY", "CHUQUIBAMBA", "IRAY", "RÍO GRANDE", "YANAQUIHUA"])
FILAS += _filas("AREQUIPA", "ISLAY", 4, "TODOS LOS DISTRITOS",
                 ["COCACHACRA", "DEAN VALDIVIA", "ISLAY", "MEJÍA", "MOLLENDO",
                  "PUNTA DE BOMBÓN"])
FILAS += _filas("AREQUIPA", "CAMANÁ", 4, "TODOS LOS DISTRITOS",
                 ["CAMANÁ", "JOSÉ MARÍA QUIMPER", "MARIANO NICOLÁS VALCÁRCEL",
                  "MARISCAL CÁCERES", "NICOLÁS DE PIÉROLA", "OCOÑA", "QUILCA",
                  "SAMUEL PASTOR"])
FILAS += _filas("AREQUIPA", "CARAVELÍ", 4, "TODOS LOS DISTRITOS",
                 ["ACARÍ", "ATICO", "ATIQUIPA", "BELLA UNIÓN", "CAHUACHO",
                  "CARAVELÍ", "CHALA", "CHAPARRA", "HUANUHUANU", "JAQUI",
                  "LOMAS", "QUICACHA", "YAUCA"])

# ═══════════════════════════════════════════════════════════════════════
# MOQUEGUA (región, 3/3 provincias)
# ═══════════════════════════════════════════════════════════════════════
FILAS += _filas("MOQUEGUA", "GENERAL SÁNCHEZ CERRO", 3, "DIEZ DISTRITOS",
                 ["CHOJATA", "COALAQUE", "ICHUÑA", "LLOQUE", "MATALAQUE",
                  "OMATE", "PUQUINA", "QUINISTAQUILLAS", "UBINAS", "YUNGA"])
FILAS += _filas("MOQUEGUA", "GENERAL SÁNCHEZ CERRO", 4, "UN DISTRITO",
                 ["LA CAPILLA"])
FILAS += _filas("MOQUEGUA", "MARISCAL NIETO", 3, "CINCO DISTRITOS",
                 ["CARUMAS", "CUCHUMBAYA", "SAMEGUA", "SAN CRISTÓBAL DE CALACOA",
                  "TORATA"])
FILAS += _filas("MOQUEGUA", "MARISCAL NIETO", 4, "UN DISTRITO", ["MOQUEGUA"])
FILAS += _filas("MOQUEGUA", "ILO", 4, "TODOS LOS DISTRITOS",
                 ["EL AGARROBAL", "PACOCHA", "ILO"])

# ═══════════════════════════════════════════════════════════════════════
# TACNA (región, 4/4 provincias) -- ya cargada en la sesión anterior
# (cargar_zonificacion_loreto_tacna.py), se reinserta con datos idénticos;
# el upsert por (region, provincia, distrito) la deja igual, no duplica.
# ═══════════════════════════════════════════════════════════════════════
FILAS += _filas("TACNA", "TARATA", 3, "TODOS LOS DISTRITOS",
                 ["CHUCATAMANI", "ESTIQUE", "ESTIQUE-PAMPA", "SITAJARA",
                  "SUSAPAYA", "TARATA", "TARUCACHI", "TICACO"])
FILAS += _filas("TACNA", "CANDARAVE", 3, "TODOS LOS DISTRITOS",
                 ["CAIRANI", "CAMILACA", "CANDARAVE", "CURIBAYA", "HUANUARA",
                  "QUILAHUANI"])
FILAS += _filas("TACNA", "JORGE BASADRE", 4, "TODOS LOS DISTRITOS",
                 ["ILABAYA", "ITE", "LOCUMBA"])
FILAS += _filas("TACNA", "TACNA", 3, "UN DISTRITO", ["PALCA"])
FILAS += _filas("TACNA", "TACNA", 4, "NUEVE DISTRITOS",
                 ["ALTO DE LA ALIANZA", "CALANA", "CIUDAD NUEVA", "INCLÁN",
                  "PACHIA", "POCOLLAY", "SAMA", "TACNA", "LA YARADA LOS PALOS"])


def cargar(dry_run: bool = False):
    print(f"{len(FILAS)} filas a cargar (Anexo II completo -- 24 regiones + Callao).")
    por_region: dict[str, int] = {}
    for f in FILAS:
        por_region[f["region"]] = por_region.get(f["region"], 0) + 1
    for region, n in sorted(por_region.items()):
        print(f"  {region}: {n} distritos")
    print(f"\nTotal regiones/áreas distintas: {len(por_region)}")

    if dry_run:
        print("[dry-run] No se inserta en Supabase.")
        return

    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not supabase_url or not supabase_key:
        print("ERROR: Configura SUPABASE_URL y SUPABASE_SERVICE_KEY en .env")
        return

    from supabase import create_client
    sb = create_client(supabase_url, supabase_key)
    # Insertar en lotes para evitar payloads gigantes en una sola llamada.
    LOTE = 300
    for i in range(0, len(FILAS), LOTE):
        lote = FILAS[i:i + LOTE]
        sb.table("peru_e030_zonificacion_distrital").upsert(
            lote, on_conflict="region,provincia,distrito"
        ).execute()
        print(f"  OK lote {i // LOTE + 1}: {len(lote)} filas")
    print(f"OK: {len(FILAS)} filas insertadas/actualizadas en peru_e030_zonificacion_distrital.")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    cargar(dry_run=dry)
