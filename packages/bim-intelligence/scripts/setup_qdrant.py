"""
Inicializa las colecciones Qdrant para Construdata BIM Intelligence.
Ejecutar una sola vez antes de la ingesta.

    python scripts/setup_qdrant.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parents[2] / ".env")

from qdrant.client import get_client
from qdrant.collections import setup_collections

if __name__ == "__main__":
    print("Conectando a Qdrant...")
    client = get_client()
    setup_collections(client)
    print("\nColecciones creadas:")
    for col in client.get_collections().collections:
        info = client.get_collection(col.name)
        print(f"  {col.name}: {info.points_count} puntos")
