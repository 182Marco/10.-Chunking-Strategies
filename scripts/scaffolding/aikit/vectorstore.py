"""vectorstore.py — la collection ChromaDB, da oggi nel toolkit aikit/.

È il modulo che avete scritto sabato a L21 (la collection persistente su
disco, l'upsert con embedding ESPLICITI, la ricerca che parla in score),
promosso in aikit/ — lo stesso percorso di embeddings.py (L19) e search.py
(L20). NON si tocca, si importa:

    from aikit import vectorstore

    collection = vectorstore.crea_collection("lumen_chunks")
    vectorstore.indicizza(collection, ids, testi, vettori, metadati)
    vectorstore.search(collection, "una domanda", 3)

Due ritocchi rispetto a sabato: le funzioni prendono il NOME della
collection (non è più solo "lumen") e c'è crea_collection(), che riparte
da zero — stasera la collection dei chunk si RICREA a ogni esperimento:
cambi le manopole e i chunk vecchi non valgono più.
"""
from pathlib import Path

import chromadb

from aikit.embeddings import embed

CHROMA_DIR = Path(__file__).parent.parent.parent / "chroma"


def apri_collection(nome):
    """La collection su disco: la crea la prima volta, poi la riapre (L21)."""
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        nome, metadata={"hnsw:space": "cosine"}   # la metrica di L19-L21
    )


def crea_collection(nome):
    """Come apri_collection(), ma da ZERO: se la collection esiste la cancella.

    È la funzione della serata: a ogni esperimento si ri-chunk, si ri-embedda
    e si ri-indicizza — ripartire da una collection vuota è il modo più
    onesto di non mischiare i chunk di due configurazioni diverse.
    """
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    if nome in [c.name for c in client.list_collections()]:
        client.delete_collection(nome)
    return client.create_collection(nome, metadata={"hnsw:space": "cosine"})


def indicizza(collection, ids, testi, embeddings, metadatas=None):
    """Upsert con embedding ESPLICITI (mai l'embedder di default del DB)."""
    collection.upsert(ids=ids, documents=testi, embeddings=embeddings,
                      metadatas=metadatas)


def search(collection, query, k, backend="openai"):
    """I k documenti più simili alla query, dal più simile in giù.

    Ogni risultato è un dict {"id", "testo", "score", ...metadata}: la query
    viene embeddata nello stesso spazio del corpus (regola di L20) e il DB
    risponde in DISTANZE — lo score è 1 - distanza, come a L21.
    """
    q = embed([query], backend=backend)[0]
    ris = collection.query(query_embeddings=[q], n_results=k)
    risultati = []
    for i in range(len(ris["ids"][0])):
        r = {
            "id": ris["ids"][0][i],
            "testo": ris["documents"][0][i],
            "score": 1 - ris["distances"][0][i],
        }
        if ris["metadatas"][0][i]:
            r.update(ris["metadatas"][0][i])
        risultati.append(r)
    return risultati
