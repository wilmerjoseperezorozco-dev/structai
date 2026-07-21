"""
Capa 3 – Entrenamiento PINN + Evaluación NSR-10 Título C
=========================================================
Entrada : tensores extraídos por InfracortexEngine (Capas 1-2)
Salida  : estado del nudo (PASA / FALLA) según capacidad por cortante NSR-10
Unidades: mm, N, MPa  (sistema internacional de ingeniería estructural)
"""

import math
import sys
from pathlib import Path

# La consola de Windows (cp1252) no puede imprimir los símbolos Unicode
# (←, φ, ✓, ✗) que usan los reportes de loads.py/imprimir_reporte — sin
# esto, correr `python train_pinn.py` en cmd.exe termina en
# UnicodeEncodeError. Confirmado al ejecutar este script end-to-end.
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

import torch
import torch.nn as nn
import numpy as np

# Import plano (no relativo): "bim-intelligence" tiene guion en el nombre
# de carpeta, no es un identificador Python válido para import -m paquete.
# Mismo patrón que el resto del monorepo (scripts/*.py) — sys.path + import
# plano en vez de paquete instalado, para poder correr este archivo
# directamente con `python train_pinn.py` desde esta carpeta.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import InfracortexEngine, MultidisciplinaryPINN


# ---------------------------------------------------------------------------
# Propiedades del material (NSR-10 Título C – concreto típico colombiano)
# ---------------------------------------------------------------------------
PROPIEDADES_CONCRETO = {
    "fc":  28.0,   # MPa  – resistencia cilíndrica f'c (concreto 3000 PSI ≈ 21 MPa mín NSR-10)
    "fy": 420.0,   # MPa  – fluencia del acero longitudinal (420 = grado 60)
    "b":  300.0,   # mm   – ancho de la sección en el nudo
    "h":  300.0,   # mm   – altura de la sección en el nudo
    "d":  265.0,   # mm   – peralte efectivo (h - recubrimiento 35 mm)
    "Av":  56.5,   # mm²  – área de estribos (2 ramas Ø6 = 2×28.27)
    "s":   75.0,   # mm   – separación de estribos en zona de confinamiento
}

PROPIEDADES_FLUIDO = {
    "presion_hidrostatica": 0.03,  # MPa  – columna de agua 3 m (≈ 0.03 MPa)
    "densidad":           1000.0,  # kg/m³
    "temperatura":          20.0,  # °C
}


# ---------------------------------------------------------------------------
# NSR-10 Título C – Capacidad por cortante en el nudo (artículo C.21.7)
# ---------------------------------------------------------------------------
def calcular_Vn_max_nsr10(props: dict) -> float:
    """
    Vn_max para nudo confinado en todas las caras (C.21.7.4.1):
        Vn = 1.7 * sqrt(f'c) * Aj   [N]
    Aj = b * h  (área efectiva del nudo en mm²)
    """
    fc  = props["fc"]
    b   = props["b"]
    h   = props["h"]
    Aj  = b * h                         # mm²
    Vn  = 1.7 * math.sqrt(fc) * Aj     # N
    return Vn


def calcular_Vs_estribos(props: dict) -> float:
    """
    Contribución del acero transversal (C.11.4.7.2):
        Vs = Av * fy * d / s   [N]
    """
    return props["Av"] * props["fy"] * props["d"] / props["s"]


def calcular_Vc(props: dict) -> float:
    """
    Resistencia del concreto a cortante (C.11.3.1.1):
        Vc = 0.17 * sqrt(f'c) * b * d   [N]
    """
    return 0.17 * math.sqrt(props["fc"]) * props["b"] * props["d"]


# ---------------------------------------------------------------------------
# Generador de puntos de colocación en el dominio del nudo
# ---------------------------------------------------------------------------
def generar_puntos_nudo(posicion_mm: np.ndarray, n_puntos: int = 200) -> torch.Tensor:
    """
    Muestrea coordenadas normalizadas a [-1, 1] dentro del volumen del nudo.
    Normalizar es obligatorio para que el gradiente de la PINN sea estable.
    """
    # Puntos aleatorios en el dominio del nudo, normalizados por 1000 mm (1 m)
    puntos_raw = torch.rand(n_puntos, 3, dtype=torch.float64) * 2 - 1
    offset_norm = torch.tensor(posicion_mm / 1000.0, dtype=torch.float64)
    return puntos_raw + offset_norm


# ---------------------------------------------------------------------------
# Bucle de entrenamiento
# ---------------------------------------------------------------------------
def entrenar_pinn(
    pinn: MultidisciplinaryPINN,
    posicion_mm: np.ndarray,
    props_concreto: dict,
    props_fluido: dict,
    epochs: int = 500,
    lr: float = 1e-3,
) -> list[float]:

    optimizador = torch.optim.Adam(pinn.parameters(), lr=lr)
    historial   = []

    # Normalizar targets a escala ~1 para estabilidad del gradiente
    # Vn_max en kN (÷1000) y presión en MPa ya está en escala pequeña
    Vn_max_tensor = torch.tensor(
        calcular_Vn_max_nsr10(props_concreto) / 1000.0, dtype=torch.float64
    )
    p_hid_tensor  = torch.tensor(
        props_fluido["presion_hidrostatica"], dtype=torch.float64
    )

    props_c = {"Vn_max": Vn_max_tensor}
    props_f = {"presion_hidrostatica": p_hid_tensor}

    print(f"\nEntrenando PINN ({epochs} épocas)…")
    for epoch in range(1, epochs + 1):
        puntos = generar_puntos_nudo(posicion_mm)
        optimizador.zero_grad()
        loss = pinn.loss_function(puntos, props_c, props_f)
        loss.backward()
        optimizador.step()
        historial.append(loss.item())

        if epoch % 100 == 0:
            print(f"  Época {epoch:4d}/{epochs}  |  Loss = {loss.item():.6f}")

    return historial


# NOTA: la función evaluar_nudo_nsr10() que existía aquí se eliminó — era
# código muerto (nunca se llamaba desde __main__, confirmado por grep antes
# de tocarla) con un bug real: definía Vu_asumido = 0.85 * Vn_disponible
# como "demanda representativa" y comparaba Vu_asumido <= Vn_disponible.
# Esa comparación es matemáticamente SIEMPRE verdadera (0.85x <= x para
# cualquier x positivo) — un chequeo estructural que nunca puede fallar,
# sin importar el caso real. El chequeo real y correcto ya existe en el
# flujo de __main__ de este archivo: usa la demanda Vu calculada de verdad
# en loads.py (cargas de gravedad + sismo NSR-10 Títulos A/B), no un
# valor fijo derivado de la propia capacidad.


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from loads import (
        calcular_demanda_cortante_nudo,
        imprimir_reporte,
        ZONA_SISMICA_ATLANTICO,
        CARGAS_GRAVEDAD,
    )

    # 1. Cargar modelo IFC ya generado
    motor   = InfracortexEngine("nudo_test.ifc")
    ifc_m   = motor.model

    elementos = ifc_m.by_type("IfcBeam") + ifc_m.by_type("IfcColumn")
    guid_viga = ifc_m.by_type("IfcBeam")[0].GlobalId
    guid_col  = ifc_m.by_type("IfcColumn")[0].GlobalId

    # 2. Capas 1 y 2 – extraer tensores y rigidez (viga Y columna, no solo la viga)
    rotacion_viga, rotacion_columna, posicion_mm = motor.extraer_topologia_nudo(guid_viga, guid_col)
    T12_viga = motor.ensamblar_rigidez_local(rotacion_viga)
    T12_columna = motor.ensamblar_rigidez_local(rotacion_columna)
    print(f"Matriz de transformación viga: {T12_viga.shape} | columna: {T12_columna.shape}")

    # 3. Capa 3 – entrenar PINN
    historial = entrenar_pinn(
        motor.pinn,
        posicion_mm,
        PROPIEDADES_CONCRETO,
        PROPIEDADES_FLUIDO,
        epochs=500,
    )
    print(f"\nLoss inicial : {historial[0]:.6f}")
    print(f"Loss final   : {historial[-1]:.6f}")
    reduccion = (1 - historial[-1] / historial[0]) * 100
    print(f"Reducción    : {reduccion:.1f}%")

    # 4. Demanda real de cargas (sismo + gravedad NSR-10)
    resultado_cargas = calcular_demanda_cortante_nudo(
        CARGAS_GRAVEDAD,
        ZONA_SISMICA_ATLANTICO,
        altura_piso_mm=float(posicion_mm[2]),  # Z extraído del IFC
    )

    # 5. Evaluación normativa NSR-10 con Vu real
    phi   = 0.75
    Vc    = calcular_Vc(PROPIEDADES_CONCRETO)
    Vs    = calcular_Vs_estribos(PROPIEDADES_CONCRETO)
    Vn    = calcular_Vn_max_nsr10(PROPIEDADES_CONCRETO)
    phi_Vn = phi * min(Vc + Vs, Vn)

    imprimir_reporte(resultado_cargas, phi_Vn)
