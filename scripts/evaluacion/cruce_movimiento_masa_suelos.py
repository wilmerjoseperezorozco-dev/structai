"""Cruce real: municipios con mas eventos historicos de MOVIMIENTO EN MASA
(UNGRD, 2019-2024) vs. su perfil de suelo/pendiente (IGAC/UPRA UFH) --
misma metodologia del caso real ya publicado para Medellin (SVM, pendiente
+ geomorfologia + precipitacion como variables clave), aplicada a escala
nacional con los datos que StructAI ya tiene cargados.

Metodologia (documentada para que sea auditable, no una caja negra):
1. Contar eventos reales de "MOVIMIENTO EN MASA" por municipio en
   ungrd_emergencias (tabla completa, 41.893 filas, paginada -- nunca
   select() sin paginar, ver bug real ya documentado en el proyecto).
2. Tomar el top N municipios con mas eventos (grupo ALTO) y un grupo de
   control de municipios con CERO eventos registrados (grupo BAJO),
   pareado por region cuando es posible para no comparar Amazonas con
   Antioquia sin mas.
3. Para cada municipio de ambos grupos, traer su perfil de suelo real de
   igac_suelos_ufh (169.088 filas) -- distribucion de pendiente (codigos
   IGAC a-g) y taxonomia dominante.
4. Validar EMPIRICAMENTE (no asumida de una fuente no confirmada) que el
   orden alfabetico a->g corresponde a pendiente creciente: si es cierto,
   las zonas con codigo 'a' deberian tener mucha mas incidencia de
   inundacion (inund != 'No hay') que las de codigo 'g'. Si el patron no
   aparece, no se puede confiar en el orden alfabetico como proxy de
   pendiente creciente y hay que decirlo honestamente.
5. Comparar el % de area en pendientes altas (los 2-3 codigos mas
   inclinados segun el paso 4) entre el grupo ALTO y el grupo BAJO.
"""
import io
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from dotenv import load_dotenv
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "construdata"))
import rag_multi_norma as rm

TAM_PAGINA = 1000


def _paginar(tabla: str, columnas: str, filtro=None) -> list[dict]:
    filas = []
    inicio = 0
    while True:
        q = rm.sb.table(tabla).select(columnas).range(inicio, inicio + TAM_PAGINA - 1)
        if filtro is not None:
            q = filtro(q)
        pagina = q.execute().data or []
        filas.extend(pagina)
        if len(pagina) < TAM_PAGINA:
            break
        inicio += TAM_PAGINA
    return filas


def main() -> None:
    print("=== Paso 0: validacion empirica del orden de pendiente (a..g) ===")
    suelos_muestra = _paginar("igac_suelos_ufh", "pendiente,inund", None)
    print(f"Total filas IGAC cargadas: {len(suelos_muestra)}")
    pct_inundable_por_letra: dict[str, tuple[int, int]] = {}
    for letra in "abcdefg":
        filas_letra = [f for f in suelos_muestra if f["pendiente"] == letra]
        if not filas_letra:
            continue
        inundables = sum(1 for f in filas_letra if f["inund"] not in ("No hay", "No aplica", None))
        pct_inundable_por_letra[letra] = (inundables, len(filas_letra))
    print("Letra | % polígonos con alguna inundabilidad | n")
    for letra, (inund, total) in sorted(pct_inundable_por_letra.items()):
        pct = 100 * inund / total if total else 0
        print(f"  {letra}     | {pct:5.1f}%  | n={total}")

    print("\n=== Paso 1: eventos reales de MOVIMIENTO EN MASA por municipio (UNGRD completo) ===")
    eventos = _paginar(
        "ungrd_emergencias", "municipio,departamento,evento",
        lambda q: q.eq("evento", "MOVIMIENTO EN MASA"),
    )
    print(f"Total eventos MOVIMIENTO EN MASA reales: {len(eventos)}")
    conteo: Counter = Counter()
    depto_de: dict[str, str] = {}
    for e in eventos:
        clave = (e["municipio"] or "").strip().upper()
        if not clave:
            continue
        conteo[clave] += 1
        depto_de[clave] = e.get("departamento") or ""

    top15 = conteo.most_common(15)
    print("\nTop 15 municipios con más eventos de movimiento en masa (2019-2024):")
    for muni, n in top15:
        print(f"  {muni} ({depto_de.get(muni, '?')}): {n} eventos")

    # Grupo de control: municipios con CERO eventos de movimiento en masa
    # registrados en UNGRD, tomados del catalogo real de amenaza sismica
    # (1.121 municipios) -- para comparar contra municipios reales, no
    # inventados.
    todos_municipios = _paginar("sgc_amenaza_sismica_municipios", "municipio,departamento", None)
    sin_eventos = [
        m for m in todos_municipios
        if (m["municipio"] or "").strip().upper() not in conteo
    ]
    print(f"\nMunicipios reales con CERO eventos de movimiento en masa registrados: {len(sin_eventos)} de {len(todos_municipios)}")

    print("\n=== Paso 2: perfil de suelo/pendiente para el grupo ALTO (top 15) ===")
    def perfil_pendiente(municipio: str, departamento: str) -> Counter:
        filas = rm.sb.table("igac_suelos_ufh").select("pendiente").eq(
            "municipio_norm", municipio.upper()
        ).execute().data or []
        return Counter(f["pendiente"] for f in filas)

    perfiles_alto = {}
    for muni, n in top15:
        perfil = perfil_pendiente(muni, depto_de.get(muni, ""))
        perfiles_alto[muni] = perfil
        total = sum(perfil.values())
        if total == 0:
            print(f"  {muni}: SIN DATO en IGAC (0 polígonos encontrados)")
            continue
        top_letra = perfil.most_common(1)[0]
        print(f"  {muni} ({n} eventos): {total} polígonos IGAC, pendiente dominante '{top_letra[0]}' ({100*top_letra[1]/total:.0f}%)")

    print("\n=== Paso 3: perfil de suelo/pendiente para el grupo BAJO (muestra de 15 municipios sin eventos) ===")
    import random
    random.seed(42)
    muestra_control = random.sample(sin_eventos, min(15, len(sin_eventos)))
    perfiles_bajo = {}
    for m in muestra_control:
        muni = m["municipio"]
        perfil = perfil_pendiente(muni, m.get("departamento", ""))
        perfiles_bajo[muni] = perfil
        total = sum(perfil.values())
        if total == 0:
            print(f"  {muni}: SIN DATO en IGAC (0 polígonos encontrados)")
            continue
        top_letra = perfil.most_common(1)[0]
        print(f"  {muni} (0 eventos): {total} polígonos IGAC, pendiente dominante '{top_letra[0]}' ({100*top_letra[1]/total:.0f}%)")

    print("\n=== Paso 4: comparación agregada ===")
    def agregado(perfiles: dict) -> Counter:
        total = Counter()
        for p in perfiles.values():
            total.update(p)
        return total

    agg_alto = agregado(perfiles_alto)
    agg_bajo = agregado(perfiles_bajo)
    total_alto = sum(agg_alto.values())
    total_bajo = sum(agg_bajo.values())
    print(f"Grupo ALTO (municipios con más eventos): {total_alto} polígonos totales")
    for letra in "abcdefg":
        pct = 100 * agg_alto.get(letra, 0) / total_alto if total_alto else 0
        print(f"  pendiente {letra}: {pct:5.1f}%")
    print(f"\nGrupo BAJO (control, 0 eventos): {total_bajo} polígonos totales")
    for letra in "abcdefg":
        pct = 100 * agg_bajo.get(letra, 0) / total_bajo if total_bajo else 0
        print(f"  pendiente {letra}: {pct:5.1f}%")


if __name__ == "__main__":
    main()
