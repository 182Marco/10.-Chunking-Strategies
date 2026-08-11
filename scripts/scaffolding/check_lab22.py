"""check_lab22.py — [OK]/[FAIL] sui RISULTATI, non sul come.

Strumento del DOCENTE (preparazione, regressione, diagnosi in aula):
non compare nel percorso studente. Da lanciare dalla cartella scripts/:

    python scaffolding/check_lab22.py               # verifica working/ (istantanea, zero costi)
    python scaffolding/check_lab22.py --live        # in più: semantic + giro completo via OpenAI (~$0.001)
    python scaffolding/check_lab22.py --solutions   # verifica solutions/ (per il docente)

La verifica base non chiama nessun servizio: le funzioni di chunking sono
Python puro e le trappole del dataset si controllano sulle stringhe
(chunk_semantic si prova con un embed FINTO, giusto la meccanica). Il giro
reale — semantic con embedding veri + indicizzazione e query su un DB
usa-e-getta — sta dietro --live.
"""
import os
import shutil
import sys
import tempfile

from pathlib import Path

import numpy as np

SCRIPTS = Path(__file__).parent.parent
TARGET = SCRIPTS / ("solutions" if "--solutions" in sys.argv else "working")

sys.path.insert(0, str(SCRIPTS / "scaffolding"))
sys.path.insert(0, str(TARGET))

from make_dataset import (FRASE_SALDI, FRASE_IMPORTO,   # noqa: E402
                          FRASE_SCADENZA, FRASE_E07)

FALLIMENTI = 0


def esito(ok, msg):
    global FALLIMENTI
    print(("[OK]  " if ok else "[FAIL]") + " " + msg)
    if not ok:
        FALLIMENTI += 1


def check_fixed(c, policy, guida):
    print("\n— TODO 1 · chunk_fixed: taglie, overlap e trappole")
    try:
        pezzi = c.chunk_fixed("x" * 1234, 500, 0)
    except NotImplementedError:
        esito(False, "chunk_fixed ancora da fare")
        return False
    except Exception as e:
        esito(False, f"chunk_fixed solleva {type(e).__name__}: {e}")
        return False
    esito([len(p) for p in pezzi] == [500, 500, 234]
          and "".join(pezzi) == "x" * 1234,
          "senza overlap: blocchi da 500 e nessun carattere perso")

    abc = "".join(chr(65 + i % 26) * 10 for i in range(200))   # 2000 car
    pezzi = c.chunk_fixed(abc, 500, 100)
    esito(all(p1[-100:] == p2[:100] for p1, p2 in zip(pezzi, pezzi[1:])
              if len(p2) >= 100),
          "con overlap 100: ogni chunk riparte 100 caratteri indietro")

    spezzata = not any(FRASE_SALDI in p for p in c.chunk_fixed(policy, 500, 0))
    esito(spezzata, "trappola A: fixed(500,0) SPEZZA la frase dei saldi")
    salvata = any(FRASE_SALDI in p for p in c.chunk_fixed(policy, 500, 150))
    esito(salvata, "trappola A: con overlap 150 un chunk la contiene intera")

    def insieme(pezzi):
        return any(FRASE_IMPORTO in p and FRASE_SCADENZA in p for p in pezzi)
    esito(not insieme(c.chunk_fixed(guida, 500, 0)),
          "trappola B: fixed(500,0) separa importo e scadenza del contributo")
    esito(insieme(c.chunk_fixed(guida, 500, 150)),
          "trappola B: con overlap 150 un chunk li contiene entrambi")
    return True


def check_recursive(c, policy, guida, manuale):
    print("\n— TODO 2 · chunk_recursive: separatori rispettati")
    try:
        pezzi = c.chunk_recursive(policy, 500)
    except NotImplementedError:
        esito(False, "chunk_recursive ancora da fare")
        return False
    except Exception as e:
        esito(False, f"chunk_recursive solleva {type(e).__name__}: {e}")
        return False
    tutti = {"policy": pezzi,
             "guida": c.chunk_recursive(guida, 500),
             "manuale": c.chunk_recursive(manuale, 500)}
    esito(all(len(p) <= 500 for pezzi in tutti.values() for p in pezzi),
          "tutti i pezzi stanno in 500 caratteri, su tutti e 3 i documenti")
    testo_totale = sum(len(t) for t in (policy, guida, manuale))
    testo_pezzi = sum(len(p) for pezzi in tutti.values() for p in pezzi)
    n_pezzi = sum(len(pezzi) for pezzi in tutti.values())
    esito(testo_pezzi >= testo_totale - 2 * n_pezzi,
          "si perdono al più i separatori, mai il contenuto")
    esito(any(FRASE_SALDI in p for p in tutti["policy"]),
          "la frase dei saldi resta INTERA (il taglio cade sui separatori)")
    esito(not any(FRASE_IMPORTO in p and FRASE_SCADENZA in p
                  for p in tutti["guida"]),
          "trappola B: recursive taglia SUL confine di paragrafo — "
          "importo e scadenza restano separati (qui salva solo l'overlap)")
    return True


def check_semantic_meccanica(c, manuale):
    print("\n— chunk_semantic (già data) · la meccanica, con un embed finto")
    finti = lambda texts, backend="finto": np.array(
        [[1.0, 0.0] if (i // 4) % 2 == 0 else [0.0, 1.0]
         for i in range(len(texts))])
    embed_vero = c.embed
    c.embed = finti
    try:
        pezzi = c.chunk_semantic(manuale, 0.5)
    except Exception as e:
        esito(False, f"chunk_semantic solleva {type(e).__name__}: {e}")
        return
    finally:
        c.embed = embed_vero
    esito(len(pezzi) > 1 and all(isinstance(p, str) and p for p in pezzi),
          "spezza in più chunk non vuoti quando la similarità cala")
    frasi_dentro = sum(len(p.split(". ")) for p in pezzi)
    esito(frasi_dentro >= 4, "le frasi finiscono nei chunk, nessuna persa")


def check_live(c, manuale):
    print("\n— LIVE · semantic vero + tre giri su DB usa-e-getta (~$0.002)")
    if not os.getenv("OPENAI_API_KEY", "").strip():
        esito(False, "serve OPENAI_API_KEY nel .env per il check --live")
        return

    pezzi = c.chunk_semantic(manuale, 0.4)
    con_e07 = [p for p in pezzi if FRASE_E07 in p]
    esito(bool(con_e07), "semantic(0.4): la procedura E07 resta intera in un chunk")
    if con_e07:
        esito("ricalibrata" in con_e07[0] and "MONTAGGIO" not in con_e07[0],
              "…e quel chunk parla di errori, non di montaggio")

    from aikit import vectorstore
    _tmp = Path(tempfile.mkdtemp(prefix="chroma_check22_"))
    _chroma_vera = vectorstore.CHROMA_DIR
    vectorstore.CHROMA_DIR = _tmp

    QUERY_CONTRIBUTO = ("Quanto vale il contributo per la postazione e "
                        "entro quanti giorni va presentata la richiesta?")

    def indicizza_con(spezza):
        documenti = c.carica_documenti()
        ids, testi = [], []
        for nome, testo in documenti.items():
            for numero, pezzo in enumerate(spezza(testo)):
                ids.append(f"{nome}-{numero:03d}")
                testi.append(pezzo)
        collection = vectorstore.crea_collection("check22")
        vectorstore.indicizza(collection, ids, testi, c.embed(testi))
        return collection

    try:
        # giro 1 · recursive(500): i tagli sui separatori pagano su saldi e E07
        collection = indicizza_con(lambda t: c.chunk_recursive(t, 500))
        primo = vectorstore.search(
            collection, "Quanti giorni ho per restituire un prodotto "
            "comprato durante i saldi?", 3)[0]
        esito("14 giorni" in primo["testo"] and "buono acquisto" in primo["testo"],
              f"recursive(500) · query saldi: risposta in testa e INTERA "
              f"(score {primo['score']:.3f})")
        primo = vectorstore.search(
            collection, "La centralina mostra il codice E07: cosa devo fare?", 3)[0]
        esito(FRASE_E07 in primo["testo"],
              f"recursive(500) · query E07: procedura in testa "
              f"(score {primo['score']:.3f})")

        # giro 2 · fixed(500,150): l'overlap RICUCE il cavallo di paragrafo
        #          (il chunk completo entra in top-3; in testa resta un
        #          frammento — misurato in preparazione, luglio 2026)
        collection = indicizza_con(lambda t: c.chunk_fixed(t, 500, 150))
        ris = vectorstore.search(collection, QUERY_CONTRIBUTO, 3)
        esito(any("250 euro" in r["testo"] and "60 giorni" in r["testo"]
                  for r in ris),
              "fixed(500,150) · query contributo: il chunk ricucito "
              "dall'overlap (importo E scadenza) compare nei top-3")

        # giro 3 · semantic(0.4): il taglio che segue il discorso vince
        collection = indicizza_con(lambda t: c.chunk_semantic(t, 0.4))
        primo = vectorstore.search(collection, QUERY_CONTRIBUTO, 3)[0]
        esito("250 euro" in primo["testo"] and "60 giorni" in primo["testo"],
              f"semantic(0.4) · query contributo: importo E scadenza in "
              f"testa, nello stesso chunk (score {primo['score']:.3f})")
    finally:
        vectorstore.CHROMA_DIR = _chroma_vera
        shutil.rmtree(_tmp, ignore_errors=True)


if __name__ == "__main__":
    print(f"verifico: {TARGET.name}/")

    import chunk as c

    DATASET = SCRIPTS / "dataset"
    policy = (DATASET / "policy-resi-garanzia.txt").read_text(encoding="utf-8")
    guida = (DATASET / "guida-smart-working.txt").read_text(encoding="utf-8")
    manuale = (DATASET / "manuale-lumadesk.txt").read_text(encoding="utf-8")

    ok_fixed = check_fixed(c, policy, guida)
    ok_recursive = check_recursive(c, policy, guida, manuale)
    check_semantic_meccanica(c, manuale)
    if "--live" in sys.argv and ok_fixed and ok_recursive:
        check_live(c, manuale)

    print("\n" + ("Tutto a posto ✔" if FALLIMENTI == 0
                  else f"{FALLIMENTI} requisito/i ancora da sistemare."))
    sys.exit(0 if FALLIMENTI == 0 else 1)
