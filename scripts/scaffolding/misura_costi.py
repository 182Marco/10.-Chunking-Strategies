"""misura_costi.py — quanto costa indicizzare i 3 documenti, configurazione
per configurazione. Strumento del DOCENTE: i numeri della slide sui costi
escono da QUI (eseguito davvero, ~$0.001 a lancio).

    python scaffolding/misura_costi.py

Per ogni configurazione: si chunkano i 3 documenti, si embeddano i chunk
(chiamata VERA a text-embedding-3-small) e si contano token e dollari dal
campo usage della risposta. Per semantic il conto include anche gli
embedding delle singole frasi: il chunking stesso si paga — è il punto.
"""
import sys

from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

SCRIPTS = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPTS / "scaffolding"))
sys.path.insert(0, str(SCRIPTS / "solutions"))

load_dotenv()

import chunk as soluzione                                # noqa: E402

TOTALE = {"token": 0}
_client = OpenAI()


def embed_contando(texts, backend="openai"):
    """Come aikit.embed, ma accumula i token in TOTALE (per il conto)."""
    r = _client.embeddings.create(model="text-embedding-3-small", input=list(texts))
    TOTALE["token"] += r.usage.total_tokens
    return np.array([d.embedding for d in r.data], dtype=np.float32)


soluzione.embed = embed_contando   # anche chunk_semantic passa dal contatore

CONFIG = [
    ("documenti interi", "fixed", 10**6, 0),
    ("fixed 500 / 0", "fixed", 500, 0),
    ("fixed 500 / 150", "fixed", 500, 150),
    ("fixed 1000 / 0", "fixed", 1000, 0),
    ("fixed 300 / 100", "fixed", 300, 100),
    ("recursive 500", "recursive", 500, None),
    ("semantic 0.4", "semantic", None, None),
]

if __name__ == "__main__":
    documenti = soluzione.carica_documenti()
    car_totali = sum(len(t) for t in documenti.values())
    print(f"corpus: {len(documenti)} documenti, {car_totali} caratteri\n")
    print(f"{'configurazione':<18} {'chunk':>6} {'token':>7} {'costo':>10}")

    for nome, strategia, size, overlap in CONFIG:
        TOTALE["token"] = 0
        pezzi = []
        for testo in documenti.values():
            if strategia == "fixed":
                pezzi += soluzione.chunk_fixed(testo, size, overlap)
            elif strategia == "recursive":
                pezzi += soluzione.chunk_recursive(testo, size)
            elif strategia == "semantic":
                pezzi += soluzione.chunk_semantic(testo, 0.4)
        embed_contando(pezzi)                     # il costo di indicizzazione
        costo = TOTALE["token"] / 1_000_000 * 0.02
        print(f"{nome:<18} {len(pezzi):>6} {TOTALE['token']:>7} ${costo:>9.6f}")

    print("\n(semantic include gli embedding delle frasi: il chunking si paga)")
