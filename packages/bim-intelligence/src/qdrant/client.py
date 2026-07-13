"""
Cliente Qdrant singleton con fallback local/cloud.
"""
from __future__ import annotations

import os
from functools import lru_cache

from qdrant_client import QdrantClient


@lru_cache(maxsize=1)
def get_client() -> QdrantClient:
    url = os.getenv("QDRANT_URL", "http://localhost:6333")
    api_key = os.getenv("QDRANT_API_KEY")  # None en local → sin auth

    return QdrantClient(url=url, api_key=api_key, timeout=30)
