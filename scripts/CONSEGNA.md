# L22 — Chunking Strategies · consegna

Stasera arrivano i **documenti lunghi**: tre file di Lumen che non stanno
sensatamente in un embedding solo. Si spezzano (chunking), si embeddano, si
indicizzano e si interrogano — e a ogni configurazione il retrieval cambia
faccia. Un solo file per tutta la serata: `working/chunk.py`. Tutto si
lancia dalla cartella `scripts/`.

## Setup (una volta sola, nei primi minuti)

Ogni lezione ha la sua cartella `scripts/` col suo venv: quello di stasera
è **nuovo** (non si riusa quello di L21). Aprite il terminale nella cartella
della lezione (quella scaricata da Drive, che contiene `scripts/`), poi:

```bash
cd scripts
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env    # dentro: la STESSA chiave OpenAI di L13-L21
```

> Chiave persa? **Alzate la mano**: il docente ha una chiave di riserva.

Niente corpus embeddato da copiare stasera: i documenti sono in `dataset/`
in chiaro e gli embedding si calcolano **a ogni giro** (backend `openai`
per tutti). La collection `lumen_chunks` si **ricrea da zero** a ogni
lancio: è il punto della serata.

## Live coding col docente (🎤 si replica) — `working/chunk.py`

| TODO | Cosa | Fatto quando |
|---|---|---|
| 1 | `chunk_fixed(testo, size, overlap)`: blocchi di `size` caratteri, ogni blocco riparte `overlap` caratteri indietro | lanciando lo script, i tagli stampati cadono ogni 500 caratteri esatti — anche in mezzo alle parole |
| 2 | `chunk_recursive(testo, size)`: il taglio cade sull'ultimo separatore che ci sta (paragrafo → riga → frase), poi si riparte sul resto | i tagli stampati cadono su titoli e confini di frase, mai a metà parola |

`chunk_semantic(testo, soglia)` è **già scritta**: il docente la mostra in
demo (taglia dove la similarità tra frasi adiacenti cala: un calo = cambio
di argomento). Voi la **usate** negli esperimenti, non la scrivete.

## Esperimenti (⌨️ da soli) — le manopole in testa al file

In testa a `working/chunk.py` ci sono quattro costanti:

```python
STRATEGIA = "fixed"      # "fixed" | "recursive" | "semantic"
CHUNK_SIZE = 500         # caratteri (fixed e recursive)
OVERLAP = 0              # caratteri ripetuti tra chunk vicini (solo fixed)
SOGLIA = 0.4             # sotto questa similarità si taglia (solo semantic)
```

Il giro è sempre lo stesso: **cambiate UNA manopola → rilanciate → leggete
→ annotate** una riga nella tabella in fondo al file. Lo script rifà tutto
da solo: ri-chunk, ri-embed, ri-indicizza (collection ricreata), ri-cerca
le tre query note.

Come si legge l'output: il **1° risultato è stampato per intero** — la
risposta c'è tutta (✔)? arriva **tagliata** a metà (✂)? o il chunk parla
d'altro e la risposta è **sepolta** altrove (∿)?

**Fatto quando:** avete trovato almeno una configurazione in cui il chunk
con la risposta esce **in testa e integro** per ognuna delle tre query — e
sapete dire quale manopola ha fatto la differenza. Occhio anche alla riga
`[openai] … token → $…` a ogni giro: l'indicizzazione si ri-paga ogni
volta, e alcune configurazioni costano più di altre.

```bash
python working/chunk.py     # un esperimento = un lancio (~$0.0001-0.0002 a giro)
```

## Cosa portate a casa

`chunk.py` con le vostre due strategie scritte a mano, la **tabella
esperimenti** compilata (la vostra mappa di cosa funziona su questo corpus)
e la collection `lumen_chunks` su disco con la configurazione migliore:
giovedì (L23) quei chunk finiscono **dentro un prompt** — il primo RAG
completo del corso.
