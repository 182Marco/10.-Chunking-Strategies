"""Genera i 3 documenti lunghi di Lumen in dataset/ — i testi della serata.

Stessa azienda fittizia di L18-L21 (Lumen S.r.l., scrivanie regolabili
LumaDesk), ma dataset NUOVO: per la prima volta i testi sono LUNGHI — tre
documenti multipagina in testo semplice, già puliti (il cleaning è materia
chiusa: L17-L18). I testi brevi di L19-L21 stasera non servono.

  guida-smart-working.txt   → policy interna HR (contributo postazione…)
  policy-resi-garanzia.txt  → resi, rimborsi, garanzia, SRV-03
  manuale-lumadesk.txt      → manuale d'uso LD-200/LD-210 (centralina, errori)

I documenti NON sono neutri: ognuno nasconde la risposta a una query nota,
posizionata per far scattare una trappola precisa (le posizioni sono tarate
al carattere e VERIFICATE dal blocco in fondo a questo file — se si tocca
un testo, rilanciare e sistemare finché la verifica non torna verde):

  TRAPPOLA A · policy-resi-garanzia — "Quanti giorni per il reso in saldo?"
      La frase chiave (FRASE_SALDI: finestra ridotta a 14 giorni, rimborso
      solo in buono) è a cavallo di un multiplo di 500: con
      chunk_fixed(500, 0) il taglio la SPEZZA subito prima di "14 giorni".
      Con OVERLAP=150 un chunk la contiene intera; chunk_recursive taglia
      sui separatori e la frase resta intera comunque.

  TRAPPOLA B · guida-smart-working — "Contributo postazione: quanto e
      entro quando?" L'importo (250 euro) chiude un paragrafo e la scadenza
      (entro 60 giorni) apre il successivo: l'informazione è A CAVALLO di
      due paragrafi. chunk_fixed(500, 0) li separa (un multiplo di 500 cade
      nel mezzo); con OVERLAP=150 un chunk li contiene entrambi;
      chunk_recursive taglia PROPRIO sul confine di paragrafo — qui
      l'overlap salva e il rispetto dei paragrafi no.

  TRAPPOLA C · manuale-lumadesk — "La centralina mostra E07: cosa faccio?"
      La procedura E07 vive dentro il paragrafo CODICI DI ERRORE (>1000
      caratteri, argomenti che cambiano di frase in frase): i tagli fixed
      la spezzano a caso, chunk_semantic vede il cambio di argomento tra
      una frase e l'altra e isola le istruzioni da solo (verificato con
      chiave vera in preparazione, non da questo blocco offline).

    python scaffolding/make_dataset.py

Il file è deterministico (nessuna data di generazione, nessun random):
rigenerarlo produce byte identici. Serve solo per (ri)generare i documenti,
già versionati in dataset/.
"""
from pathlib import Path

DATASET = Path(__file__).parent.parent / "dataset"

# Le frasi chiave delle trappole (usate anche da check_lab22.py):
FRASE_SALDI = ("la finestra di reso scende a 14 giorni dalla consegna e il "
               "rimborso viene emesso esclusivamente come buono acquisto di "
               "pari importo")
FRASE_IMPORTO = "contributo una tantum di 250 euro"
FRASE_SCADENZA = "entro 60 giorni dall'attivazione"
FRASE_E07 = "scollega l'alimentazione per 30 secondi"


GUIDA_SMART_WORKING = [
    "GUIDA ALLO SMART WORKING\n"
    "Lumen S.r.l. — Persone & Organizzazione\n"
    "Edizione luglio 2026 — documento interno",

    "A CHI SI RIVOLGE",

    "Questa guida vale per tutte le persone Lumen con contratto a tempo "
    "indeterminato, o determinato di durata superiore a sei mesi, che "
    "abbiano superato il periodo di prova. Restano esclusi i ruoli che "
    "richiedono presenza fisica: magazzino, showroom e assistenza tecnica "
    "a domicilio. Per stage e apprendistati il lavoro da remoto va "
    "concordato caso per caso con il proprio tutor e con Persone & "
    "Organizzazione.",

    "QUANTE GIORNATE E COME SI PIANIFICANO",

    "Puoi lavorare da remoto fino a 3 giorni a settimana; per il team "
    "commerciale il limite è 2, per lasciare spazio alle visite in showroom "
    "con i clienti. Le giornate si pianificano sul portale HR entro il "
    "venerdì della settimana precedente e vanno approvate dal responsabile. "
    "Ogni team mantiene un giorno fisso di presenza comune in sede — "
    "l'ancora di team — deciso a inizio trimestre: in quel giorno lo smart "
    "working non si pianifica.",

    "LA POSTAZIONE DI CASA",

    "Lavorare bene da casa richiede una postazione vera: un piano stabile "
    "di almeno 100 cm, una sedia regolabile in altezza, luce naturale di "
    "lato allo schermo e una connessione da almeno 30 Mbps in download. "
    "Una webcam decente completa il quadro. "
    "Per aiutarti ad allestirla, Lumen riconosce un contributo una tantum "
    "di 250 euro per una sedia ergonomica o una scrivania regolabile (lo "
    "sconto dipendenti sul catalogo LumaDesk si cumula).",

    "La richiesta del contributo va presentata entro 60 giorni "
    "dall'attivazione dello smart working, caricando la ricevuta "
    "d'acquisto sul portale HR nella sezione Rimborsi. Oltre questa "
    "finestra il contributo decade e non è recuperabile negli anni "
    "successivi; il contributo è personale e non cedibile ai colleghi.",

    "STRUMENTI E ACCESSI",

    "La dotazione standard è il laptop aziendale: è l'unico dispositivo da "
    "cui accedere ai sistemi Lumen. La VPN è obbligatoria per gestionale, "
    "CRM e cartelle condivise; l'autenticazione a due fattori va attivata "
    "su tutti gli account entro il primo giorno di remoto. Se qualcosa non "
    "funziona apri un ticket IT dal portale: per i blocchi che impediscono "
    "di lavorare c'è il canale telefonico d'emergenza, attivo dalle 8:00 "
    "alle 19:00.",

    "SICUREZZA DELLE INFORMAZIONI",

    "Da casa valgono le stesse regole dell'ufficio, più qualche attenzione: "
    "niente reti Wi-Fi pubbliche senza VPN, schermo bloccato ogni volta che "
    "ti allontani, familiari e coinquilini non devono vedere dati di "
    "clienti. I documenti cartacei con dati personali non si stampano a "
    "casa; se proprio serve, si distruggono con cura e non finiscono nella "
    "raccolta indifferenziata. Le riunioni in cui si parla di dati "
    "sensibili si fanno con gli auricolari.",

    "SALUTE E POSTURA",

    "Alterna seduta e posizione in piedi durante la giornata: se hai una "
    "scrivania regolabile, cambia posizione almeno una volta l'ora (in "
    "Lumen lo chiamiamo ritmo 50-10: cinquanta minuti seduti, dieci in "
    "piedi). Ogni 20 minuti sposta lo sguardo dallo schermo per 20 secondi "
    "su qualcosa ad almeno 6 metri di distanza: gli occhi ringraziano. Le "
    "pause valgono anche da remoto: alzarsi dalla postazione non è tempo "
    "rubato al lavoro.",

    "REPERIBILITÀ E COMUNICAZIONE",

    "Nelle giornate da remoto vale la fascia di reperibilità comune: "
    "9:30-12:30 e 14:30-17:00, con il calendario aggiornato e lo stato "
    "visibile sui canali interni. Fuori fascia gestisci il tuo tempo "
    "liberamente, nel rispetto delle scadenze del team. Vale il diritto "
    "alla disconnessione: dopo le 19:00 e nel weekend nessuno è tenuto a "
    "rispondere a messaggi ed email, e gli invii programmati vanno evitati "
    "in quegli orari.",

    "LAVORARE DA FUORI CITTÀ E DALL'ESTERO",

    "Il remoto ordinario si intende dall'Italia. Puoi lavorare dall'estero "
    "per un massimo di 2 settimane l'anno, previa autorizzazione di Persone "
    "& Organizzazione con almeno 30 giorni di anticipo, e solo da Paesi "
    "dell'Unione Europea: contano fisco, assicurazione e protezione dei "
    "dati, non solo il fuso orario.",

    "DOMANDE FREQUENTI",

    "Chi paga la linea internet? Resta a carico tuo, come la corrente "
    "elettrica: fa parte dei requisiti visti sopra. Posso spostare la mia "
    "giornata d'ancora? Solo per la settimana in corso e con l'accordo di "
    "tutto il team. Le giornate remote non godute si accumulano? No: non "
    "si trasferiscono alla settimana successiva.",

    "COSA NON CAMBIA",

    "Lo smart working non tocca inquadramento, retribuzione, ferie e "
    "permessi: le giornate da remoto sono giornate di lavoro a tutti gli "
    "effetti, buono pasto compreso. Gli obiettivi si concordano e si "
    "misurano come sempre nei colloqui trimestrali: conta il risultato, "
    "non da dove lo raggiungi. Anche la formazione obbligatoria segue il "
    "calendario ordinario, in presenza o a distanza a seconda del corso.",

    "I PRIMI MESI IN LUMEN",

    "Per chi è appena arrivato l'ingresso in smart working è graduale: nel "
    "primo mese si lavora in sede, per conoscere il team e i processi dal "
    "vivo; dal secondo mese si accede al remoto con il calendario "
    "ordinario. Il buddy assegnato all'onboarding resta il riferimento "
    "anche a distanza: la domanda veloce che in ufficio faresti alla "
    "scrivania accanto, falla in chat senza timore di disturbare.",
]

POLICY_RESI_GARANZIA = [
    "POLICY RESI E GARANZIA\n"
    "Lumen S.r.l. — Servizio Clienti\n"
    "Edizione luglio 2026 — vale per gli acquisti online e in showroom",

    "DIRITTO DI RECESSO",

    "Hai 30 giorni di tempo dalla consegna per cambiare idea: il diritto "
    "di recesso vale su tutti i prodotti del catalogo LumaDesk acquistati "
    "online, purché il prodotto sia integro, completo di tutti gli "
    "accessori e riposto nell'imballo originale. Il termine si calcola "
    "dalla data di consegna registrata dal corriere, non dalla data "
    "dell'ordine. Le spese di reso sono a carico del cliente, salvo il "
    "caso di prodotto difettoso o di errore di spedizione da parte nostra: "
    "in quei casi organizziamo e paghiamo noi il ritiro.",

    "COME SI AVVIA UN RESO",

    "La richiesta si apre dall'area personale: entra in Ordini, seleziona "
    "l'ordine e premi Richiedi reso, indicando il motivo della "
    "restituzione. Entro un giorno lavorativo ricevi via email l'etichetta "
    "prepagata del corriere convenzionato e le istruzioni per fissare il "
    "ritiro o consegnare il collo in un punto di raccolta. Se non hai più "
    "il cartone originale puoi usare un imballo equivalente, purché "
    "protegga piano e centralina: un reso danneggiato dal trasporto per "
    "imballo inadeguato può essere rifiutato o rimborsato solo in parte.",

    "RIMBORSI",

    "Il rimborso parte quando il prodotto rientra in magazzino e supera il "
    "controllo di integrità: da quel momento servono al massimo 14 giorni "
    "lavorativi. Riaccreditiamo sempre sul metodo di pagamento usato per "
    "l'ordine; per i pagamenti a rate la finanziaria annulla le rate "
    "residue e restituisce quelle già versate. Il contributo di spedizione "
    "dell'ordine originario viene rimborsato solo se il reso riguarda "
    "l'intero ordine. Se restituisci solo una parte dell'ordine, il "
    "rimborso è proporzionale e copre soltanto i prodotti effettivamente "
    "rientrati in magazzino.",

    "PRODOTTI IN PROMOZIONE E SALDI",

    "Le regole cambiano per gli acquisti in promozione. I prodotti "
    "acquistati durante i saldi stagionali o con un codice promozionale, "
    "come ESTATE15, fanno eccezione: la finestra di reso scende a 14 "
    "giorni dalla consegna e il rimborso viene emesso esclusivamente come "
    "buono acquisto di pari importo, spendibile entro dodici mesi su tutto "
    "il catalogo. Il buono arriva via email al superamento del controllo "
    "di integrità e non è convertibile in denaro.",

    "GARANZIA LEGALE E COMMERCIALE",

    "Ogni prodotto LumaDesk è coperto dalla garanzia legale di conformità "
    "di 2 anni prevista per i consumatori. A questa si aggiunge la "
    "garanzia commerciale Lumen: 5 anni sul motore e sulla struttura "
    "meccanica, 2 anni sulle parti elettroniche, centralina e alimentatore "
    "inclusi. La garanzia commerciale copre riparazione o sostituzione del "
    "componente, manodopera e spedizioni comprese, e decorre dalla data di "
    "consegna.",

    "ESTENSIONE DELLA GARANZIA (SRV-03)",

    "Con il servizio SRV-03 estendi di ulteriori 2 anni la copertura delle "
    "parti elettroniche, centralina compresa. L'estensione si può attivare "
    "al momento dell'acquisto oppure entro 90 giorni dalla consegna, "
    "dall'area personale o in showroom; oltre i 90 giorni non è più "
    "attivabile. SRV-03 è nominativo: segue il prodotto se lo regali, ma "
    "non è trasferibile su un prodotto diverso.",

    "COSA NON COPRE LA GARANZIA",

    "Restano esclusi i danni da urto, caduta o trasporto successivo alla "
    "consegna, i danni da liquidi versati sulla centralina o sui motori, "
    "l'usura estetica del piano (graffi, aloni, segni d'uso) e ogni guasto "
    "conseguente a manomissione o riparazione non autorizzata. Il piano in "
    "bambù è un materiale naturale: piccole variazioni di venatura e di "
    "colore non sono difetti coperti.",

    "CANCELLARE UN ORDINE PRIMA DELLA SPEDIZIONE",

    "Finché l'ordine è in stato In preparazione puoi annullarlo dall'area "
    "personale, con storno immediato e integrale del pagamento. Quando "
    "passa in stato Spedito non è più annullabile: in quel caso puoi "
    "rifiutare la consegna al corriere oppure avviare un reso ordinario "
    "una volta ricevuto il collo.",

    "PRODOTTI SU MISURA",

    "I piani tagliati su misura e le finiture fuori catalogo sono esclusi "
    "dal diritto di recesso, come previsto dalla normativa per i beni "
    "personalizzati: prima della produzione ricevi un disegno tecnico da "
    "approvare, e l'approvazione vale come conferma definitiva. La "
    "garanzia commerciale resta identica a quella dei prodotti a catalogo.",

    "SERVIZIO CLIENTI",

    "Per ogni pratica di reso o garanzia tieni a portata di mano il numero "
    "d'ordine e, per i difetti, qualche foto del problema: accorciano i "
    "tempi di diagnosi. Ci trovi via email a supporto@lumen.example, in "
    "chat dal lunedì al venerdì dalle 9:00 alle 18:00, o su appuntamento "
    "in showroom a Milano.",

    "CONSEGNA E DANNI DA TRASPORTO",

    "La spedizione è gratuita per gli ordini sopra i 199 euro; sotto "
    "questa soglia il contributo è di 14,90 euro. La consegna avviene in "
    "3-5 giorni lavorativi con corriere espresso, al piano strada. Se il "
    "collo arriva visibilmente danneggiato, accetta con riserva scrivendo "
    "due righe sulla bolla del corriere e fotografa l'imballo prima di "
    "aprirlo: i danni da trasporto vanno segnalati entro 3 giorni dalla "
    "consegna per avere diritto alla sostituzione.",

    "ORDINI AZIENDALI",

    "Per gli ordini con fattura inserisci ragione sociale, partita IVA e "
    "codice destinatario in fase di checkout; la fattura elettronica "
    "arriva entro 24 ore nell'area personale. Per le forniture sopra le "
    "10 postazioni il team Enterprise prepara un preventivo dedicato, con "
    "consegna concordata e resi gestiti da un referente unico: scrivi a "
    "sales@lumen.example.",
]

MANUALE_LUMADESK = [
    "MANUALE D'USO\n"
    "LumaDesk LD-200 e LD-210 — scrivanie regolabili a doppio motore\n"
    "Lumen S.r.l. — Edizione luglio 2026",

    "CONTENUTO DELLA CONFEZIONE",

    "Nella confezione trovi il piano in bambù certificato FSC, il telaio "
    "in acciaio con le due colonne motorizzate, la traversa regolabile, la "
    "centralina con display e i suoi quattro tasti, l'alimentatore, il "
    "passacavi adesivo e la busta della viteria con le quattro viti M8 del "
    "piano, le sedici viti autofilettanti e la chiave esagonale. Controlla "
    "il contenuto prima di iniziare: se manca qualcosa, il kit viteria si "
    "richiede gratuitamente dall'area personale.",

    "MONTAGGIO",

    "Il montaggio richiede circa 30 minuti e un cacciavite a croce oltre "
    "alla chiave inclusa; il piano da 140 centimetri si maneggia meglio in "
    "due. Lavora su una superficie morbida per non graffiare il bambù: "
    "prima si fissa la traversa alle colonne, poi le colonne al piano con "
    "le viti M8, infine i piedi. Da ultimo collega i due cavi motore e "
    "l'alimentazione alla centralina, e raddrizza la scrivania solo a viti "
    "tutte serrate. Se preferisci il montaggio a domicilio, il servizio "
    "SRV-01 porta un tecnico alla postazione che indichi.",

    "PRIMA ACCENSIONE E CALIBRAZIONE",

    "Alla prima accensione la scrivania deve imparare il suo punto zero. "
    "Tieni premuto il tasto - finché il piano non raggiunge il punto più "
    "basso e il display mostra RST: al rilascio la centralina è calibrata "
    "e il display torna a indicare l'altezza in centimetri. Ripeti questa "
    "procedura ogni volta che la scrivania viene scollegata dalla corrente "
    "o spostata in un'altra stanza.",

    "USO DELLA CENTRALINA",

    "I tasti + e - alzano e abbassano il piano; il movimento si ferma al "
    "rilascio. Tenendo premuto M per due secondi salvi la posizione "
    "corrente in una delle memorie M1-M4, che richiami poi con un tocco: "
    "l'altezza salvata compare sul display con la lettera della memoria. "
    "Il consiglio dell'ergonomo: salva in M1 l'altezza da seduto e in M2 "
    "quella in piedi, così il cambio di posizione diventa un gesto solo. "
    "La porta USB sul fianco della centralina ricarica telefono o cuffie "
    "a 5V/2A.",

    "FUNZIONI DI SICUREZZA",

    "L'anticollisione ferma e inverte il movimento quando il piano "
    "incontra un ostacolo, in salita come in discesa: di serie sulla "
    "LD-210, si attiva sulla LD-200 tenendo premuti + e - insieme per "
    "cinque secondi (il display mostra AC). La sensibilità ha tre livelli, "
    "regolabili dal menu della centralina. Con il blocco tastiera — tasto "
    "M premuto insieme a - per tre secondi — i tasti si disattivano e il "
    "display mostra LOC: utile con bambini in casa.",

    "MANUTENZIONE",

    "Il piano in bambù è trattato con olio naturale atossico: puliscilo "
    "con un panno morbido appena umido ed evita detergenti aggressivi e "
    "liquidi a contatto prolungato. Una volta l'anno puoi ravvivare la "
    "finitura con olio per legno di grado alimentare. Ogni sei mesi "
    "controlla il serraggio delle viti del telaio e la tenuta dei cavi; le "
    "colonne non vanno lubrificate: i motori sono sigillati e non "
    "richiedono manutenzione.",

    "CODICI DI ERRORE",

    "E01, sovraccarico: il piano ha superato la portata massima; togli "
    "peso dal piano e riprova dopo un minuto. E03, colonne disallineate: "
    "le due colonne si sono mosse a velocità diverse; esegui la "
    "calibrazione della prima accensione. E05, surriscaldamento: il motore "
    "ha lavorato troppo a lungo; lascia riposare la scrivania per 20 "
    "minuti, il codice sparisce da solo. E07, perdita di calibrazione: la "
    "centralina mostra questo codice dopo un'interruzione di corrente e il "
    "reset rapido non basta — scollega l'alimentazione per 30 secondi, "
    "ricollegala, poi tieni premuto - finché il piano non arriva al punto "
    "più basso e mantieni la pressione per altri 10 secondi, finché RST "
    "non lampeggia due volte: al rilascio la centralina è ricalibrata. "
    "E09, centralina che non comunica con i "
    "motori: controlla che i due cavi motore siano innestati a fondo; se "
    "il codice resta, la centralina va sostituita con il ricambio LM-200.",

    "SPECIFICHE TECNICHE",

    "Piano in bambù certificato FSC da 140x70 cm (LD-200) o 160x80 cm "
    "(LD-210), spessore 22 mm. Escursione in altezza da 71 a 119 cm, "
    "velocità di 38 mm al secondo, doppio motore sotto i 40 dB, portata "
    "massima 100 kg distribuiti. Alimentazione 220-240 V, consumo in "
    "standby sotto 0,1 W, porta USB 5V/2A. Peso totale 34 kg (LD-200) e "
    "39 kg (LD-210).",

    "ASSISTENZA",

    "Per ogni richiesta tieni a portata di mano il numero d'ordine e il "
    "modello, che trovi sull'etichetta sotto il piano. Le foto del "
    "problema accorciano la diagnosi, soprattutto per i danni da "
    "trasporto, da segnalare entro 3 giorni dalla consegna. Il supporto "
    "risponde via email a supporto@lumen.example e in chat dal lunedì al "
    "venerdì; per i guasti in garanzia l'intervento viene organizzato dal "
    "nostro laboratorio.",

    "PROBLEMI SENZA CODICE DI ERRORE",

    "Se il piano oscilla alla massima altezza, ricontrolla il serraggio "
    "di tutte le viti del telaio e verifica che la traversa sia regolata "
    "sulla larghezza giusta: un leggero movimento oltre i 110 cm è "
    "normale, un dondolio marcato no. Se un motore fa un rumore metallico "
    "in discesa ma non in salita, interrompi l'uso e contatta "
    "l'assistenza: è il sintomo tipico di un ingranaggio usurato, coperto "
    "dalla garanzia di 5 anni sul motore. Se il display resta spento, "
    "prova un'altra presa e controlla l'innesto dell'alimentatore prima "
    "di aprire un ticket.",

    "SMALTIMENTO E SECONDA VITA",

    "La scrivania è progettata per essere smontata: piano, telaio ed "
    "elettronica si separano con la stessa chiave del montaggio. La parte "
    "elettronica si consegna nelle isole ecologiche come RAEE; il piano in "
    "bambù, privo di vernici sintetiche, può vivere una seconda vita come "
    "piano da lavoro. Con il programma Lumen Circular ritiriamo la tua "
    "vecchia scrivania alla consegna della nuova, a costo zero.",
]

DOCUMENTI = {
    "guida-smart-working": GUIDA_SMART_WORKING,
    "policy-resi-garanzia": POLICY_RESI_GARANZIA,
    "manuale-lumadesk": MANUALE_LUMADESK,
}


def _tagli_fixed(testo, size, overlap):
    """Gli estremi [inizio, fine) di chunk_fixed, per la verifica qui sotto."""
    finestre = []
    inizio = 0
    while inizio < len(testo):
        finestre.append((inizio, inizio + size))
        inizio = inizio + size - overlap
    return finestre


def _contenuta(testo, frase, size, overlap):
    """True se ALMENO un chunk fixed contiene la frase per intero."""
    posizione = testo.index(frase)
    return any(a <= posizione and posizione + len(frase) <= b
               for a, b in _tagli_fixed(testo, size, overlap))


def _a_cavallo(testo, prima, dopo, size, overlap):
    """True se NESSUN chunk fixed contiene entrambe le frasi."""
    p1 = testo.index(prima)
    p2 = testo.index(dopo)
    return not any(a <= p1 and p2 + len(dopo) <= b
                   for a, b in _tagli_fixed(testo, size, overlap))


def verifica(testi):
    """Le trappole A e B scattano davvero (e l'overlap le salva davvero)."""
    policy = testi["policy-resi-garanzia"]
    guida = testi["guida-smart-working"]

    posizione = policy.index(FRASE_SALDI)
    taglio = next((b for a, b in _tagli_fixed(policy, 500, 0)
                   if posizione < b < posizione + len(FRASE_SALDI)), None)
    assert taglio is not None, (
        "TRAPPOLA A: nessun taglio fixed(500,0) dentro FRASE_SALDI "
        f"(la frase è a {posizione}-{posizione + len(FRASE_SALDI)}: "
        "aggiustare la lunghezza dei paragrafi precedenti)")
    dove = taglio - policy.index("14 giorni", posizione)
    print(f"  trappola A: taglio a {taglio}, {abs(dove)} caratteri "
          f"{'dopo' if dove > 0 else 'prima di'} '14 giorni' — scatta")
    assert _contenuta(policy, FRASE_SALDI, 500, 150), (
        "TRAPPOLA A: con overlap 150 la frase dovrebbe salvarsi")
    print("  trappola A: con overlap 150 un chunk la contiene intera — salva")

    assert _a_cavallo(guida, FRASE_IMPORTO, FRASE_SCADENZA, 500, 0), (
        "TRAPPOLA B: fixed(500,0) NON separa importo e scadenza "
        "(aggiustare la lunghezza dei paragrafi precedenti)")
    print("  trappola B: fixed(500,0) separa '250 euro' da 'entro 60 giorni' "
          "— scatta")
    assert not _a_cavallo(guida, FRASE_IMPORTO, FRASE_SCADENZA, 500, 150), (
        "TRAPPOLA B: con overlap 150 un chunk dovrebbe contenerli entrambi")
    print("  trappola B: con overlap 150 un chunk li contiene entrambi — salva")


def main():
    DATASET.mkdir(exist_ok=True)
    testi = {}
    for nome, paragrafi in DOCUMENTI.items():
        testo = "\n\n".join(paragrafi) + "\n"
        testi[nome] = testo
        (DATASET / f"{nome}.txt").write_text(testo, encoding="utf-8")
        print(f"scritto dataset/{nome}.txt — {len(testo)} caratteri, "
              f"{len(paragrafi)} blocchi")
    print("verifica delle trappole:")
    verifica(testi)


if __name__ == "__main__":
    main()
