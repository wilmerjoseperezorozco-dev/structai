"""
InfraCortex — motor central: lectura BIM (IFC), topología del nudo
viga-columna, y red neuronal de regresión multidisciplinar.

NOTA DE ALCANCE — MultidisciplinaryPINN: el nombre sugiere una Physics-
Informed Neural Network en el sentido técnico estricto (que impone
residuales de ecuaciones diferenciales — Navier-Cauchy, Navier-Stokes —
vía diferenciación automática de la salida respecto a las coordenadas de
entrada). Lo implementado aquí es una red de regresión MSE de 2 salidas
contra un valor objetivo fijo por lote (Vn_max, presión hidrostática) —
útil como componente, pero no impone ninguna restricción de EDP todavía.
Pendiente si se quiere una PINN real: agregar términos de pérdida basados
en gradientes de la salida vía autograd.
"""

import ifcopenshell
import ifcopenshell.util.placement
import numpy as np
from scipy.linalg import block_diag
import torch
import torch.nn as nn


class MultidisciplinaryPINN(nn.Module):
    """
    Red neuronal de regresión multidisciplinar (ver nota de alcance arriba).
    Evalúa simultáneamente el esfuerzo estructural y la termodinámica del fluido.
    """

    def __init__(self):
        super().__init__()
        self.red = nn.Sequential(
            nn.Linear(3, 64),
            nn.Tanh(),
            nn.Linear(64, 64),
            nn.Tanh(),
            nn.Linear(64, 2),  # [Esfuerzo_Cortante_Estructural, Presion_Fluido]
        )
        # float64 obligatorio para PDEs (truncación numérica inaceptable en float32)
        self.double()

    def forward(self, coordenadas: torch.Tensor) -> torch.Tensor:
        return self.red(coordenadas)

    def loss_function(
        self,
        coordenadas: torch.Tensor,
        propiedades_concreto: dict,
        propiedades_fluido: dict,
    ) -> torch.Tensor:
        """
        Función de pérdida híbrida: regresión hacia Vn_max (estructural) +
        presión hidrostática (fluido). Ver nota de alcance del módulo.
        """
        prediccion = self.forward(coordenadas)
        esfuerzo = prediccion[:, 0]
        presion = prediccion[:, 1]

        loss_estructural = torch.mean((esfuerzo - propiedades_concreto["Vn_max"]) ** 2)
        loss_fluido = torch.mean((presion - propiedades_fluido["presion_hidrostatica"]) ** 2)

        return loss_estructural + loss_fluido


class InfracortexEngine:
    """
    Motor central que orquesta la lectura BIM, la topología y el análisis físico.
    """

    def __init__(self, ifc_path: str):
        print("Iniciando Motor Científico Multidisciplinario...")
        self.model = ifcopenshell.open(ifc_path)
        self.pinn = MultidisciplinaryPINN()

    def extraer_topologia_nudo(
        self, guid_viga: str, guid_columna: str
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Transforma entidades IFC en matrices espaciales homogéneas (4x4).
        Retorna (rotación 3x3 de la viga, rotación 3x3 de la columna,
        posición global del nudo).

        BUG CORREGIDO (2026-07-21): la versión original calculaba la matriz
        de ubicación de la columna pero nunca la guardaba (llamada sin
        asignar a ninguna variable) — una función que por nombre extrae la
        topología del NUDO (viga + columna) en realidad descartaba la
        columna por completo y solo devolvía datos de la viga. No se
        notaba en el test sintético porque ahí la columna está en el
        origen con matriz identidad; con una columna real rotada, el
        resultado habría sido incorrecto.
        """
        viga = self.model.by_guid(guid_viga)
        columna = self.model.by_guid(guid_columna)

        m_viga = ifcopenshell.util.placement.get_local_placement(viga.ObjectPlacement)
        m_columna = ifcopenshell.util.placement.get_local_placement(columna.ObjectPlacement)

        rotacion_viga = m_viga[:3, :3]
        rotacion_columna = m_columna[:3, :3]
        posicion_nudo = m_viga[:3, 3]

        print(f"Topología extraída. Coordenada global del nudo: {posicion_nudo}")
        return rotacion_viga, rotacion_columna, posicion_nudo

    def ensamblar_rigidez_local(self, rotacion_R3: np.ndarray) -> np.ndarray:
        """
        Construye la matriz de transformación (12x12) para los 12 GDL de UN
        elemento barra (2 nodos x 6 GDL). Se llama una vez por cada miembro
        (viga, columna) que concurre al nudo — no una sola vez para ambos.
        """
        return block_diag(rotacion_R3, rotacion_R3, rotacion_R3, rotacion_R3)
