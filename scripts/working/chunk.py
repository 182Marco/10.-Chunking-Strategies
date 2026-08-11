"""chunk.py — spezzare i documenti lunghi, e vedere l'effetto sul retrieval.

L'unico file della serata. Le due strategie dei TODO 1-2 si scrivono COL
DOCENTE (guardate e replicate); chunk_semantic è già scritta — il docente
la mostra in demo e voi la usate negli esperimenti. Poi il main: si cambia
UNA manopola, si rilancia, si annota nella tabella in fondo.

    python working/chunk.py
"""
import sys

from pathlib import Path

SCRIPTS = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPTS / "scaffolding"))

from aikit.embeddings import embed, cosine_similarity   # noqa: E402 — L19
from aikit import vectorstore                           # noqa: E402 — L21

DATASET = SCRIPTS / "dataset"

# Le manopole degli esperimenti: si cambia UNA manopola, si rilancia,
# si annota l'esito nella tabella in fondo al file.
STRATEGIA = "fixed"          # "fixed" | "recursive" | "semantic"
CHUNK_SIZE = 500             # caratteri (fixed e recursive)
OVERLAP = 0                  # caratteri ripetuti tra chunk vicini (solo fixed)
SOGLIA = 0.4                 # sotto questa similarità si taglia (solo semantic)


# --------------------------------------------------- TODO 1 · col docente 🎤
def chunk_fixed(testo, size, overlap):
    """Blocchi di `size` caratteri; ogni blocco riparte `overlap` caratteri
    prima della fine del precedente. Restituisce la lista dei pezzi."""
    raise NotImplementedError


# --------------------------------------------------- TODO 2 · col docente 🎤
def chunk_recursive(testo, size):
    """Taglia sull'ULTIMO separatore che ci sta in `size` caratteri, provando
    i separatori dal più forte al più debole (paragrafo, riga, frase); se
    nessuno ci sta, taglio secco a `size`. Poi riparte sul resto (per questo
    si chiama ricorsivo). Restituisce pezzi lunghi al massimo `size`."""
    raise NotImplementedError


# ------------------------- già scritta: la mostra il DOCENTE in demo 🎤 —
def chunk_semantic(testo, soglia):
    """Taglia dove il DISCORSO cambia: embedda le frasi una per una e chiude
    il chunk quando la similarità tra una frase e la successiva scende sotto
    `soglia` — un calo di similarità è un cambio di argomento. Stasera si
    USA (negli esperimenti), non si scrive."""
    frasi = []
    for riga in testo.split("\n"):
        for frase in riga.split(". "):
            if frase.strip():
                frasi.append(frase.strip())

    vettori = embed(frasi)          # una chiamata sola: il chunking si paga

    pezzi = []
    corrente = [frasi[0]]
    for i in range(1, len(frasi)):
        simile = cosine_similarity(vettori[i - 1], vettori[i])
        if simile < soglia:         # il discorso cambia: si chiude il chunk
            pezzi.append(" ".join(corrente))
            corrente = []
        corrente.append(frasi[i])
    pezzi.append(" ".join(corrente))
    return pezzi


# ------------------------------------------------------- già scritte: date —
def carica_documenti():
    """I 3 documenti lunghi di Lumen, da dataset/: {nome: testo}."""
    documenti = {}
    for percorso in sorted(DATASET.glob("*.txt")):
        documenti[percorso.stem] = percorso.read_text(encoding="utf-8")
    return documenti


def mostra_chunk(pezzi):
    """Com'è venuto lo spezzatino: taglia e confini di ogni chunk."""
    for numero, pezzo in enumerate(pezzi):
        pulito = " ".join(pezzo.split())
        print(f"  {numero:3d} · {len(pezzo):4d} car · "
              f"{pulito[:34]} ⟨…⟩ {pulito[-34:]}")


if __name__ == "__main__":
    QUERY_SALDI = "Quanti giorni ho per restituire un prodotto comprato durante i saldi?"
    QUERY_CONTRIBUTO = "Quanto vale il contributo per la postazione e entro quanti giorni va presentata la richiesta?"
    QUERY_E07 = "La centralina mostra il codice E07: cosa devo fare?"
    K = 3

    print(f"config: {STRATEGIA} · size {CHUNK_SIZE} · overlap {OVERLAP} · soglia {SOGLIA}\n")

    # 1 · si spezza: ogni documento con la strategia scelta
    documenti = carica_documenti()
    pezzi_per_doc = {}
    for nome, testo in documenti.items():
        if STRATEGIA == "fixed":
            pezzi = chunk_fixed(testo, CHUNK_SIZE, OVERLAP)
        elif STRATEGIA == "recursive":
            pezzi = chunk_recursive(testo, CHUNK_SIZE)
        elif STRATEGIA == "semantic":
            pezzi = chunk_semantic(testo, SOGLIA)
        else:
            raise ValueError(f"STRATEGIA {STRATEGIA!r} sconosciuta")
        pezzi_per_doc[nome] = pezzi
        taglie = [len(p) for p in pezzi]
        print(f"{nome}: {len(pezzi)} chunk · da {min(taglie)} a {max(taglie)} caratteri")

    print("\ni tagli da vicino (policy-resi-garanzia):")
    mostra_chunk(pezzi_per_doc["policy-resi-garanzia"])

    # 2 · si indicizza: embed dei chunk + collection RICREATA da zero
    ids, testi, metadati = [], [], []
    for nome, pezzi in pezzi_per_doc.items():
        for numero, pezzo in enumerate(pezzi):
            ids.append(f"{nome}-{numero:03d}")
            testi.append(pezzo)
            metadati.append({"doc": nome})

    print(f"\nindicizzo {len(testi)} chunk (la collection si ricrea a ogni giro):")
    vettori = embed(testi)
    collection = vectorstore.crea_collection("lumen_chunks")
    vectorstore.indicizza(collection, ids, testi, vettori, metadati)

    # 3 · le query note: il primo risultato si legge PER INTERO —
    #     la risposta c'è tutta? è tagliata? è sepolta nel rumore?
    for query in (QUERY_SALDI, QUERY_CONTRIBUTO, QUERY_E07):
        print(f"\n=== {query}")
        risultati = vectorstore.search(collection, query, K)
        primo = risultati[0]
        print(f"  1° · score {primo['score']:.3f} · [{primo['id']}]")
        for riga in primo["testo"].strip().splitlines():
            print(f"  │ {riga}")
        for r in risultati[1:]:
            pulito = " ".join(r["testo"].split())
            print(f"  poi · {r['score']:.3f} · [{r['id']}] {pulito[:56]}…")


# ---------------------------------------------------------------------------
# TABELLA ESPERIMENTI — una riga per giro: annotate PRIMA di cambiare
# manopola, così la storia dei tentativi resta leggibile.
#
# Esito per query:  ✔ risposta in testa e integra · ✂ tagliata · ∿ sepolta
#
# | STRATEGIA | SIZE  | OVERLAP/SOGLIA | chunk | saldi | contributo | E07 |
# |-----------|-------|----------------|-------|-------|------------|-----|
# | fixed     | 500   | 0              |       |       |            |     |
# |           |       |                |       |       |            |     |
# |           |       |                |       |       |            |     |
# |           |       |                |       |       |            |     |
# |           |       |                |       |       |            |     |
# |           |       |                |       |       |            |     |
#
# Quale configurazione porta a casa TUTTE e tre le query? Ce n'è una sola?
# ---------------------------------------------------------------------------
