"""
Prueba de carga: simula ~50 ingenieros civiles consultando /consultar y /ask
al mismo tiempo desde obra.

Por qué estos endpoints son el cuello de botella real de este backend:
  - Están definidos con `def` normal (no `async def`) — CORRECTO para código
    bloqueante (Supabase síncrono, sentence-transformers.encode() que es
    CPU-bound, Groq vía cliente síncrono de OpenAI). FastAPI/Starlette los
    ejecuta en un threadpool aparte para no congelar el event loop.
  - PERO ese threadpool tiene tamaño limitado (default de Starlette:
    ~40 threads). Con 50 usuarios concurrentes, las peticiones #41+ deben
    esperar a que se libere un hilo — eso es cola, no error, pero si el
    LLM externo (Groq) no tiene timeout explícito (ver hallazgo real:
    rag_multi_norma.py no configura timeout en el cliente OpenAI), un
    hilo colgado en una llamada lenta bloquea ese cupo indefinidamente y
    la cola crece sin límite.

Métricas de FastAPI/Starlette a monitorear durante la corrida:
  1. Latencia p50 vs p95/p99 en /ask y /consultar — si p50 se mantiene bajo
     pero p95/p99 se dispara, es señal de saturación del threadpool
     (peticiones esperando hilo libre), no de que el RAG en sí sea lento.
  2. Tasa de error 5xx bajo carga vs. en baseline (1 usuario) — un
     incremento indica que el timeout por defecto del SDK de Groq (o de
     Supabase) se está alcanzando bajo contención.
  3. RPS sostenido vs. RPS objetivo — si Locust reporta que no logra
     alcanzar la tasa de "users" configurada, el threadpool ya está
     saturado antes de llegar a 50 usuarios simultáneos.
  4. Uso de RAM del proceso uvicorn durante la corrida (vía /health
     robustecido, o `top`/Task Manager) — sentence-transformers carga el
     modelo de embeddings en memoria una sola vez al importar el módulo,
     pero cada .encode() concurrente reserva tensores temporales; con
     muchas peticiones simultáneas puede acumularse.
  5. Conteo de conexiones abiertas a Supabase — el cliente se crea una
     vez a nivel de módulo (patrón correcto, es un wrapper HTTP, no un
     socket persistente por request), pero vale confirmar que no hay
     fugas de conexiones HTTP subyacentes bajo carga sostenida.

Uso:
  pip install locust
  locust -f apps/api/tests/locustfile.py --host=http://localhost:8000
  # abre http://localhost:8089, configura 50 usuarios, spawn rate ~5/s
"""
from __future__ import annotations

import random

from locust import HttpUser, between, task

# Preguntas variadas — evita que todas las peticiones pidan exactamente lo
# mismo (lo cual sesgaría los resultados por caché interna de Supabase/BM25
# en vez de medir carga real de cómputo+red).
PREGUNTAS_NORMATIVA = [
    "¿Qué resistencia mínima de concreto exige NSR-10 para columnas sísmicas?",
    "¿Cuál es el recubrimiento mínimo para vigas expuestas a la intemperie?",
    "¿Qué norma regula el acero corrugado grado 60 en Colombia?",
    "¿Cuándo es obligatorio el uso de arnés en trabajos en altura?",
    "¿Qué espaciamiento máximo de estribos se permite en zona de confinamiento?",
    "¿Qué coeficiente C de Hazen-Williams uso para tubería PVC?",
    "¿Cuál es el CBR mínimo para clasificar una subrasante como buena?",
    "¿Qué significa un CPI menor a 0.9 en earned value management?",
]


class IngenieroEnObra(HttpUser):
    """
    Simula un ingeniero civil consultando desde el celular en obra: lee la
    respuesta antes de preguntar de nuevo — no dispara peticiones en ráfaga
    como un bot, por eso el wait_time es largo (5-15s), no milisegundos.
    """

    # Tiempo de "lectura" entre una consulta y la siguiente — realista para
    # una persona leyendo una respuesta técnica en el celular, no un
    # benchmark de throughput puro.
    wait_time = between(5, 15)

    @task(3)
    def consultar_normativa_general(self):
        """80% del tráfico: preguntas normativas generales vía /ask."""
        pregunta = random.choice(PREGUNTAS_NORMATIVA)
        with self.client.post(
            "/ask",
            json={"pregunta": pregunta, "top_k": 6},
            name="/ask",
            catch_response=True,
        ) as res:
            self._validar_respuesta_rag(res)

    @task(1)
    def consultar_delegado_multidominio(self):
        """20% del tráfico: /consultar, que enruta a AquAI/GeoPot/vías/gerencia."""
        pregunta = random.choice(PREGUNTAS_NORMATIVA)
        with self.client.post(
            "/consultar",
            json={"pregunta": pregunta, "top_k": 6},
            name="/consultar",
            catch_response=True,
        ) as res:
            self._validar_respuesta_rag(res)

    def _validar_respuesta_rag(self, res) -> None:
        if res.status_code == 200:
            body = res.json()
            if "respuesta" not in body:
                res.failure("200 pero sin campo 'respuesta' — contrato de API roto")
            else:
                res.success()
        elif res.status_code == 503:
            # Módulo RAG caído — falla legítima del sistema, se cuenta como
            # error para que Locust lo reporte, pero no es un crash.
            res.failure("RAG no disponible (503) — verificar salud del servicio")
        else:
            res.failure(f"status inesperado: {res.status_code}")

    @task(1)
    def health_check(self):
        """Simula el ping periódico que haría el frontend/monitoreo (StatusBar en Chat.tsx)."""
        self.client.get("/health", name="/health")
