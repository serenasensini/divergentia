# Istruzioni per Copilot – Progetto Divergentia

## Priorità agli strumenti tokensave MCP

Prima di leggere i file sorgente o eseguire scansioni del codice, utilizza **sempre** gli strumenti tokensave MCP. Forniscono risultati semantici istantanei da un knowledge graph pre-costruito e sono più veloci della lettura diretta dei file.

### Strumenti da preferire

- `tokensave_context` — costruisci il contesto per un task a partire da una descrizione naturale
- `tokensave_search` — cerca simboli (funzioni, classi, struct, trait…) per nome o parola chiave
- `tokensave_callers` — trova chi chiama un simbolo
- `tokensave_callees` — trova cosa chiama un simbolo
- `tokensave_impact` — calcola il raggio d'impatto di una modifica
- `tokensave_node` — recupera i dettagli di un singolo nodo
- `tokensave_files` — esplora la struttura dei file indicizzati
- `tokensave_affected` — individua i test impattati da un cambiamento

## Flusso di lavoro consigliato

1. **Esplora prima con tokensave** — usa `tokensave_context` o `tokensave_search` per orientarti nel codice invece di aprire file a caso.
2. **Analizza l'impatto** — prima di modificare un simbolo, esegui `tokensave_callers` e `tokensave_impact` per capire cosa dipende da esso.
3. **Individua i test** — dopo aver identificato i file da cambiare, usa `tokensave_affected` per sapere quali test eseguire.
4. **Leggi i sorgenti solo quando serve** — apri i file soltanto per confermare il contesto o applicare le modifiche.

## Fallback su SQLite

Se una domanda di analisi del codice non può essere risolta completamente con gli strumenti tokensave MCP, interroga direttamente il database SQLite in `.tokensave/tokensave.db`.

Tabelle disponibili:
- `nodes` — simboli del codice
- `edges` — relazioni tra simboli
- `files` — file indicizzati

Usa query SQL per rispondere a domande strutturali complesse che vanno oltre ciò che gli strumenti integrati espongono.

## Struttura del progetto

- `be/` — backend Python (Flask), servizi, repository, modelli, blueprint e test in `be/tests/`
- `fe/` — frontend (Vite + TypeScript) in `fe/src/`
- `old/` — versione Angular precedente (legacy)

Mantieni in mente il tipo di progetto (linguaggi, framework e librerie) quando applichi le modifiche.

