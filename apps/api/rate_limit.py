"""Instancia compartida de slowapi Limiter.

Vive en su propio módulo (no en main.py) porque main.py importa los routers
de los motores ANTES de crear el limiter (ver orden real en main.py: los
`from routers.X import router` corren antes de `limiter = Limiter(...)`),
así que un router no puede hacer `from main import limiter` sin toparse con
un import circular / módulo parcialmente inicializado. Tanto main.py como
cada router importan `limiter` desde acá.
"""
from slowapi import Limiter

from auth import rate_limit_key

limiter = Limiter(key_func=rate_limit_key)
