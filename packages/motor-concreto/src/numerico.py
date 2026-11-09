"""Compatibilidad numérica: `np.trapezoid` existe desde NumPy 2.0; la API en producción fija NumPy 1.26 (donde se llama `np.trapz`)."""
import numpy as np

trapezoid = getattr(np, "trapezoid", None) or np.trapz
