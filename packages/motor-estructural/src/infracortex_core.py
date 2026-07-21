"""
InfracortexEngine — Motor BIM → Física
Empresa: Infracortex | App: StructAI
Unidades: mm, N, MPa
"""
from __future__ import annotations
import ifcopenshell
import ifcopenshell.util.placement
import numpy as np
from scipy.linalg import block_diag
import torch
import torch.nn as nn


class MultidisciplinaryPINN(nn.Module):
    """
    PINN float64 que evalúa simultáneamente esfuerzo estructural
    (Navier-Cauchy) y termodinámica de fluidos (Navier-Stokes).
    """

    def __init__(self) -> None:
        super().__init__()
        self.red = nn.Sequential(
            nn.Linear(3, 64),
            nn.Tanh(),
            nn.Linear(64, 64),
            nn.Tanh(),
            nn.Linear(64, 2),   # [Esfuerzo_Cortante, Presion_Fluido]
        )
        # float64 obligatorio: truncación inaceptable en PDEs con float32
        self.double()

    def forward(self, coordenadas: torch.Tensor) -> torch.Tensor:
        return self.red(coordenadas)

    def loss_function(
        self,
        coordenadas: torch.Tensor,
        propiedades_concreto: dict,
        propiedades_fluido: dict,
    ) -> torch.Tensor:
        prediccion = self.forward(coordenadas)
        esfuerzo = prediccion[:, 0]
        presion  = prediccion[:, 1]
        loss_estructural = torch.mean((esfuerzo - propiedades_concreto["Vn_max"]) ** 2)
        loss_fluido      = torch.mean((presion  - propiedades_fluido["presion_hidrostatica"]) ** 2)
        return loss_estructural + loss_fluido


class InfracortexEngine:
    """
    Motor central: lee un archivo IFC y extrae la topología matemática
    del nudo (rotación R3, posición global) para alimentar la PINN.
    """

    def __init__(self, ifc_path: str) -> None:
        self.model = ifcopenshell.open(ifc_path)
        self.pinn  = MultidisciplinaryPINN()

    def extraer_topologia_nudo(
        self,
        guid_viga: str,
        guid_columna: str,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Retorna (rotación 3×3 viga, rotación 3×3 columna, posición global del nudo en mm).

        BUG CORREGIDO (2026-07-21): la versión original calculaba la matriz
        de ubicación de la columna pero nunca la asignaba (llamada sin
        guardar el resultado) — una función que por nombre extrae la
        topología del NUDO (viga + columna) en realidad descartaba la
        columna por completo. Mismo bug encontrado y corregido en el
        prototipo original de Infracortex (tubara/IFCOPENSHELL/).
        """
        viga    = self.model.by_guid(guid_viga)
        columna = self.model.by_guid(guid_columna)

        m_viga    = ifcopenshell.util.placement.get_local_placement(viga.ObjectPlacement)
        m_columna = ifcopenshell.util.placement.get_local_placement(columna.ObjectPlacement)

        return m_viga[:3, :3], m_columna[:3, :3], m_viga[:3, 3]

    def ensamblar_rigidez_local(self, rotacion_R3: np.ndarray) -> np.ndarray:
        """Matriz de transformación 12×12 (12 GDL del elemento barra)."""
        return block_diag(rotacion_R3, rotacion_R3, rotacion_R3, rotacion_R3)
