"""Mide p50/p95 por paso de las cadenas candidatas del inventario (#221, fase 1, paso 2). Solo local, nunca producción.

Uso:
    python scripts/medicion/medir_cadenas.py                       # todos los escenarios locales, repeticiones por defecto
    python scripts/medicion/medir_cadenas.py --repeticiones 10 --escenario portico-integral

Garantías (verificadas, no supuestas):
  * Variables de entorno de prueba ANTES de importar la API (python-dotenv no las sobrescribe): ninguna credencial real se carga.
  * `sin_red_externa()`: toda conexión que no sea a la propia máquina se rechaza; si un escenario la intenta, falla y se reporta.
  * Los pasos con efectos (escribir en BD, cupo mensual) se SUSTITUYEN por funciones inertes y se listan como «sustituidos»;
    su latencia no se mide aquí (se mediría en el nocturno con una base local, no con producción).

Escenarios incluidos: solo los que corren completos sin red. /consultar, /ask y /amenaza-sismica dependen de Supabase, del LLM
y del SGC: quedan para el nocturno con modelo local y lectura controlada (ver docs/LATENCIA_CADENAS.md).
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import os
import platform
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pasos import Instrumentacion, Registro, sin_red_externa  # noqa: E402

ENTORNO_PRUEBA = {
    "SUPABASE_URL": "http://localhost:54321", "SUPABASE_SERVICE_KEY": "clave-de-prueba-local", "SUPABASE_SERVICE_ROLE_KEY": "clave-de-prueba-local",
    "SUPABASE_ANON_KEY": "clave-de-prueba-local", "SUPABASE_JWT_SECRET": "secreto-de-prueba-local",
    "GROQ_API_KEY": "clave-de-prueba-local", "OPENAI_API_KEY": "clave-de-prueba-local", "SENTRY_DSN": "",
    "RESEND_API_KEY": "clave-de-prueba-local", "ENABLE_MCP": "false",
}
INVENTARIO = RAIZ / "docs" / "cadenas_ejecucion.json"
SALIDA = RAIZ / "scripts" / "medicion" / "resultados"
DOC = RAIZ / "docs" / "LATENCIA_CADENAS.md"

SOL_PORTICO = dict(luces_m=[6.0, 6.0], alturas_piso_m=[3.2, 3.0], carga_muerta_kn_m=22.0, carga_viva_kn_m=8.0, calidad_concreto="3000",
                   fy_mpa=420.0, recubrimiento_mm=40.0, municipio="Pereira", departamento="Risaralda", perfil_suelo="D",
                   grupo_uso="I", capacidad="DES", columnas_mm=[400.0, 500.0, 600.0], b_mm=[250.0, 300.0, 350.0],
                   h_mm=[500.0, 600.0, 700.0, 800.0])


def preparar_api():
    for k, v in ENTORNO_PRUEBA.items():
        os.environ[k] = v
    api = RAIZ / "apps" / "api"
    sys.path.insert(0, str(api))
    sys.path.insert(0, str(RAIZ / "packages" / "construdata"))
    import main  # noqa: E402
    if os.environ["SUPABASE_URL"] != ENTORNO_PRUEBA["SUPABASE_URL"]:
        raise RuntimeError("SUPABASE_URL no es la de prueba: se aborta para no tocar producción")
    main.limiter.enabled = False                         # el límite de tasa no es parte de la latencia de la cadena
    return main


def _usuario(main):
    from auth import AuthenticatedUser
    return AuthenticatedUser(id="u-medicion-local", email=None)


def _plantilla_apu(main, n_filas: int) -> bytes:
    """La plantilla real de GET /apu/plantilla (catálogo real), con filas alternadas de catálogo y geometría dinámica."""
    from openpyxl import load_workbook
    catalogo = main.listar_actividades()
    ids = [c["id"] for c in catalogo]
    wb = load_workbook(io.BytesIO(main.apu_excel.generar_plantilla(catalogo)))
    ws = wb["Calculo"]
    col = {k: i + 1 for i, k in enumerate(main.apu_excel.COLUMNAS_ENTRADA)}
    for i in range(n_filas):
        fila = 2 + i
        for c in col.values():
            ws.cell(fila, c).value = None
        if i % 2 == 0:
            vals = {"modo": "catalogo", "actividad_id": ids[i % len(ids)], "cantidad": 1.0 + i}
        else:
            vals = {"modo": "dinamico", "tipo": "viga", "base_m": 0.3, "altura_m": 0.45, "longitud_m": 5.0, "recubrimiento_m": 0.04,
                    "calidad_concreto": "3000", "num_barras": 4, "diametro_barra_pulg": "5", "diametro_estribo_pulg": "3",
                    "espaciamiento_estribos_m": 0.15, "gancho_desarrollo_m": 0.10, "cantidad": 1.0}
        for k, v in vals.items():
            ws.cell(fila, col[k]).value = v
    b = io.BytesIO()
    wb.save(b)
    return b.getvalue()


def escenarios(main):
    """{nombre: (entrada del inventario, preparar() -> (llamar, sustituidos, deshacer))}."""
    from fastapi.testclient import TestClient
    from auth import get_current_user

    def portico():
        main.app.dependency_overrides[get_current_user] = lambda: _usuario(main)
        cli = TestClient(main.app)

        def llamar():
            r = cli.post("/orquestador/portico-integral", json=SOL_PORTICO)
            if r.status_code != 200:
                raise RuntimeError(f"portico-integral respondió {r.status_code}: {r.text[:300]}")
        return llamar, [], lambda: main.app.dependency_overrides.clear()

    def apu_lote(n_filas: int = 20):
        originales = {k: getattr(main, k) for k in ("get_current_user", "_cupo_apu_mes_restante", "registrar_apu_calculos_lote")}
        main.get_current_user = lambda request: _usuario(main)
        main._cupo_apu_mes_restante = lambda user_id: None                    # lectura del cupo en Supabase
        main.registrar_apu_calculos_lote = lambda registros: None             # escritura en Supabase (efecto)
        archivo = _plantilla_apu(main, n_filas)
        cli = TestClient(main.app)

        def llamar():
            r = cli.post("/apu/calculate-batch", files={"archivo": ("lote.xlsx", archivo,
                         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
            if r.status_code != 200:
                raise RuntimeError(f"calculate-batch respondió {r.status_code}: {r.text[:300]}")

        def deshacer():
            for k, v in originales.items():
                setattr(main, k, v)
        return llamar, ["get_current_user (auth)", "_cupo_apu_mes_restante (lectura BD)", "registrar_apu_calculos_lote (escritura BD)"], deshacer

    return {"portico-integral": ("POST /orquestador/portico-integral", portico, 5),
            "apu-lote": ("POST /apu/calculate-batch", apu_lote, 15)}


def medir(nombres=None, repeticiones=None) -> dict:
    main = preparar_api()
    inv = json.loads(INVENTARIO.read_text(encoding="utf-8"))
    por_entrada = {c["entrada"]: c for c in inv["cadenas"]}
    reg = Registro()
    resultado = {"fecha": dt.datetime.now().isoformat(timespec="seconds"), "maquina": f"{platform.system()} {platform.machine()}",
                 "python": platform.python_version(), "escenarios": {}}
    for nombre, (entrada, preparar, rep_def) in escenarios(main).items():
        if nombres and nombre not in nombres:
            continue
        pasos = [s["paso"] for s in por_entrada[entrada]["secuencia"]]
        n = repeticiones or rep_def
        llamar, sustituidos, deshacer_esc = preparar()
        limpio = Registro()
        try:
            with sin_red_externa():
                llamar()                                       # calentamiento: carga perezosa de módulos y cachés de proceso
                # Alternadas (limpia, instrumentada, limpia, …): la deriva de carga de la máquina afecta por igual a las dos.
                # La limpia da el total sin el sobrecosto de instrumentar; la instrumentada, el desglose por paso.
                inst = Instrumentacion(reg, pasos, RAIZ)
                hechos, omitidos = inst.hechos, inst.omitidos
                for _ in range(n):
                    with limpio.peticion(entrada):
                        llamar()
                    inst.aplicar()
                    try:
                        with reg.peticion(entrada):
                            llamar()
                    finally:
                        inst.deshacer()
        finally:
            deshacer_esc()
        medido = reg.resumen()[entrada]
        total = limpio.resumen()[entrada]["peticiones"]
        sobre = medido["peticiones"]["p50_ms"] / total["p50_ms"] - 1 if total["p50_ms"] else float("nan")
        resultado["escenarios"][nombre] = {"entrada": entrada, "etiquetas": por_entrada[entrada]["etiquetas"],
                                           "pasos_instrumentados": hechos, "pasos_no_instrumentables": omitidos,
                                           "sustituidos": sustituidos, "peticiones": total,
                                           "peticiones_instrumentadas": medido["peticiones"],
                                           "sobrecosto_instrumentacion": round(sobre, 3), "pasos": medido["pasos"],
                                           "no_atribuido_ms": round(medido["peticiones"]["p50_ms"]
                                                                    - sum(x["propio_total_por_peticion_ms"] for x in medido["pasos"]), 3)}
    return resultado


def renderizar(r: dict) -> str:
    L = ["# Latencia por paso de las cadenas de ejecución (#221)", "",
         f"Medido el {r['fecha']} en {r['maquina']} (Python {r['python']}) con `scripts/medicion/medir_cadenas.py`. "
         "Local, sin red externa, con los efectos sustituidos: **no es latencia de producción**, es la línea base del cómputo propio "
         "de cada cadena para comparar antes y después del encapsulado (fase 2).", "",
         "Tiempo «propio» = tiempo del paso sin los pasos instrumentados que llama. La primera petición (calentamiento) no se cuenta.", ""]
    for nombre, e in r["escenarios"].items():
        p = e["peticiones"]
        L += [f"## `{e['entrada']}`", "",
              f"- Peticiones: {p['n']} · p50 **{p['p50_ms']:.1f} ms** · p95 **{p['p95_ms']:.1f} ms** · tasa de error {p['tasa_error']:.0%} "
              f"(pasada sin instrumentar; instrumentar añade {e['sobrecosto_instrumentacion']:.0%} al p50)",
              f"- Etiquetas del inventario: {', '.join(e['etiquetas'])}",
              f"- Pasos instrumentados: {len(e['pasos_instrumentados'])}; no instrumentables (llamadas encadenadas o externas): "
              f"{len(e['pasos_no_instrumentables'])}"]
        if e["sustituidos"]:
            L.append(f"- Sustituidos por funciones inertes (no medidos): {', '.join(e['sustituidos'])}")
        L += ["", "| Paso | Llamadas/petición | Propio por petición (ms) | p50 (ms) | p95 (ms) | Error |", "|---|---|---|---|---|---|"]
        for s in e["pasos"]:
            L.append(f"| `{s['paso']}` | {s['llamadas_por_peticion']:g} | {s['propio_total_por_peticion_ms']:.2f} | {s['p50_ms']:.2f} | "
                     f"{s['p95_ms']:.2f} | {s['tasa_error']:.0%} |")
        pi = e["peticiones_instrumentadas"]["p50_ms"]
        L += [f"| *No atribuido a ningún paso del inventario* | | {e['no_atribuido_ms']:.2f} | | | |", "",
              f"El {e['no_atribuido_ms'] / pi:.0%} del p50 instrumentado no cae en ningún paso declarado: es código propio del endpoint "
              "utilidades de CPU que el inventario no cuenta como paso (p. ej. leer y escribir el Excel) o llamadas que no resuelve. Si "
              "es grande, hay que revisar el inventario antes de priorizar con esta tabla.", ""]
    L += ["## Cómo leer y repetir esta medición", "",
          "- Los tiempos absolutos de una misma máquina cambiaron hasta ~1,8× entre corridas del mismo día (carga, energía). Por eso "
          "cada corrida alterna peticiones limpias e instrumentadas, y el antes/después de la fase 2 debe medirse **alternado en la "
          "misma corrida**, nunca comparando corridas de días distintos.",
          "- El sobrecosto de instrumentar se mide en cada corrida (columna de arriba); con el plan de reemplazos precalculado queda "
          "en pocos puntos porcentuales.",
          "- Esta medición mostró que el inventario estático no veía los módulos cargados con `importlib.import_module` ni los alias "
          "reexportados (`_dv, _viga = _dp._dv, _dp._viga`): el 83 % del pórtico quedaba sin atribuir. Se corrigió en "
          "`scripts/inventario/cadenas_ejecucion.py` y el diseño de columna apareció como el paso dominante.", "",
          "## Pendiente", "",
          "- `/consultar`, `/ask` y `/amenaza-sismica`: necesitan Supabase, el LLM y el SGC. Se medirán en el nocturno con el modelo local "
          "(#172/#178) y lectura controlada, nunca contra la cuota de producción.",
          "- Fase 2: encapsular como flujo atómico y repetir esta medición; meta preregistrada ≥ 30 % menos p95 con aciertos de caché y "
          "cero diferencias de resultado.", ""]
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--escenario", action="append", help="portico-integral | apu-lote (repetible); por defecto todos")
    ap.add_argument("--repeticiones", type=int)
    ap.add_argument("--sin-documento", action="store_true", help="no reescribe docs/LATENCIA_CADENAS.md")
    a = ap.parse_args(argv)
    r = medir(a.escenario, a.repeticiones)
    SALIDA.mkdir(parents=True, exist_ok=True)
    f = SALIDA / f"latencia_{r['fecha'][:10]}.json"
    f.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    if not a.sin_documento:
        DOC.write_text(renderizar(r), encoding="utf-8")
    for n, e in r["escenarios"].items():
        print(f"{e['entrada']}: p50 {e['peticiones']['p50_ms']:.1f} ms, p95 {e['peticiones']['p95_ms']:.1f} ms "
              f"({len(e['pasos_instrumentados'])} pasos instrumentados)")
    print(f"→ {f.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
