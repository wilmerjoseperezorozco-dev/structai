"""Fusiona los 103 casos promovidos (ver revisar_manual_qlora.py) con el
train/heldout ya generado por exportar_dataset_qlora.py -- mismo split
85/15, misma semilla, para que el resultado siga siendo reproducible."""
import json
import random
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = PROJECT_ROOT / "scripts" / "evaluacion" / "qlora_export"

SEED_SPLIT = 42
FRACCION_HELDOUT = 0.15


def leer_jsonl(ruta: Path) -> list[dict]:
    with open(ruta, encoding="utf-8") as f:
        return [json.loads(l) for l in f]


def escribir_jsonl(ruta: Path, filas: list[dict]) -> None:
    with open(ruta, "w", encoding="utf-8") as f:
        for fila in filas:
            f.write(json.dumps(fila, ensure_ascii=False) + "\n")


def main() -> None:
    train = leer_jsonl(OUT_DIR / "train.jsonl")
    heldout = leer_jsonl(OUT_DIR / "heldout.jsonl")
    promovidos = leer_jsonl(OUT_DIR / "revisar_manual_promovidos.jsonl")

    random.seed(SEED_SPLIT)
    promovidos_shuffled = promovidos[:]
    random.shuffle(promovidos_shuffled)
    n_heldout_nuevos = max(1, round(len(promovidos_shuffled) * FRACCION_HELDOUT))
    heldout_nuevos = promovidos_shuffled[:n_heldout_nuevos]
    train_nuevos = promovidos_shuffled[n_heldout_nuevos:]

    train_final = train + train_nuevos
    heldout_final = heldout + heldout_nuevos

    escribir_jsonl(OUT_DIR / "train.jsonl", train_final)
    escribir_jsonl(OUT_DIR / "heldout.jsonl", heldout_final)

    print(f"train.jsonl: {len(train)} -> {len(train_final)} (+{len(train_nuevos)} promovidos)")
    print(f"heldout.jsonl: {len(heldout)} -> {len(heldout_final)} (+{len(heldout_nuevos)} promovidos)")
    print(f"\nTotal dataset verificado final: {len(train_final) + len(heldout_final)} pares")


if __name__ == "__main__":
    main()
