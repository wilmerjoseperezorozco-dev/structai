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


class InfracortexEngine:
    """
    Motor central: lee un archivo IFC y extrae la topología matemática
    del nudo (rotación R3, posición global) para pasarla a load_engine.py.

    Traía además una MultidisciplinaryPINN (red neuronal PyTorch) que se
    instanciaba en cada análisis real pero cuyo .forward()/.loss_function()
    nunca se llamaba desde ningún camino de código -- el veredicto real
    de /estructural/analizar-nudo siempre salió 100% de las fórmulas
    clásicas de load_engine.py. Eliminada en la auditoría de seguridad/
    higiene de ingeniería del 2026-08-26 (verificado con grep exhaustivo +
    la suite de tests, que nunca la importaba tampoco) -- no cambia ningún
    resultado que este motor ya entregaba. Ver el commit para la corrección
    completa sobre el ahorro real de RAM: torch NO se libera del proceso
    por esto (sentence-transformers, siempre activo para el RAG, ya lo
    exige como dependencia dura) -- lo que sí se gana es no instalar una
    segunda copia de torch (requirements-estructural.txt) solo para código
    muerto, y dejar de aparentar una capacidad de IA que no existía.
    """

    def __init__(self, ifc_path: str) -> None:
        self.model = ifcopenshell.open(ifc_path)

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
