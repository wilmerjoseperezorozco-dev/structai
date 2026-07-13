"""
Alias de compatibilidad — permite que los módulos originales de Gemini
importen `from sistema_nervioso import inicializar_sensor` sin modificación.

Los módulos de Gemini usan este nombre. Todo el código nuevo debe
importar directamente desde logging.sensor.
"""
from .observabilidad.sensor import inicializar_sensor, VeedorEventos, veedor  # noqa: F401
