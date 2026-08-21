import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  type ReactNode,
} from 'react';
import { usePreferences, type Language } from './preferences';

/**
 * Lightweight, dependency-free internationalisation.
 *
 * Strings are looked up by dot-path (e.g. `t('hub.title')`). A second argument
 * interpolates `{placeholders}` in the resolved string. The active language is
 * driven by the persisted user preference, so switching updates the whole UI.
 */

type Dict = Record<string, unknown>;

const en = {
  common: {
    close: 'Close',
    refresh: 'Refresh',
    working: 'Working…',
    download: 'Download document',
  },
  app: {
    skip: 'Skip to main content',
    settings: 'Settings & companion',
    credits: 'Made by Serena Sensini & Martina Ricci',
    repo: 'Source code',
  },
  language: {
    label: 'Language',
    en: 'English',
    it: 'Italiano',
  },
  welcome: {
    title: 'Welcome to DivergentIA',
    intro:
      'A calm place where, one step at a time, you can reshape documents and make them more adaptable. First, choose a companion and set things up your way. You can change any of this later.',
    chooseCompanion: 'Choose your companion',
    companionLegend: 'Assistant companion',
    setup: 'Set things up your way',
    readingFont: 'Reading font',
    colourTheme: 'Colour theme',
    textSize: 'Text size',
    reduceMotion: 'Reduce motion and animation',
    classicMode: 'Classic mode (plain layout, no game scene)',
    gameTheme: 'Playful diamond theme (Sims-style step markers and colours)',
    soundEffects:
      'Play a soft sound when you complete a stage (diamond theme)',
    enter: 'Enter the workshop',
    moreInfo: 'More information',
    reset: 'Reset to defaults',
    resetConfirmTitle: 'Reset all preferences?',
    resetConfirmBody:
      'This restores every setting — companion, font, theme, text size and toggles — to its original value. This cannot be undone.',
    resetConfirm: 'Yes, reset',
    resetCancel: 'Cancel',
    resetDone: 'Preferences have been reset to their defaults.',
    help: {
      font: 'How letters are shaped on screen. Pick whichever is most comfortable to read.',
      theme: 'The overall colour mood of the interface.',
      textSize: 'How large the text appears throughout the app.',
      reduceMotion:
        'Removes animations and movement for a calmer, more predictable interface.',
      classicMode:
        'Swaps the illustrated scene for a plain, list-based layout with less visual detail.',
      gameTheme:
        'A cosmetic, Sims-inspired skin: diamond step markers and brighter accent colours. It never changes your font, theme, text size or motion settings.',
      soundEffects:
        'Plays a gentle two-note chime when you finish a stage. Only available with the diamond theme, and off unless you turn it on.',
    },
    fonts: {
      system: 'Default',
      atkinson: 'Atkinson Hyperlegible',
      dyslexic: 'OpenDyslexic-style',
    },
    fontDesc: {
      system: 'Your device’s standard font — familiar and fast to load.',
      atkinson:
        'A typeface designed for low vision, with letters that are easy to tell apart.',
      dyslexic:
        'Weighted, distinct letter shapes that many dyslexic readers find easier to follow.',
    },
    themes: {
      calm: 'Calm (light)',
      dark: 'Calm (dark)',
      'high-contrast': 'High contrast',
    },
    sizes: {
      small: 'Small',
      medium: 'Medium',
      large: 'Large',
      'x-large': 'Extra large',
    },
  },
  characters: {
    lumi: { blurb: 'A calm owl who reads slowly and never rushes you.' },
    pip: { blurb: 'A tidy fox who loves sorting and structuring documents.' },
    nova: {
      blurb: 'A steady turtle who keeps everything one clear step at a time.',
    },
  },
  notifications: {
    region: 'Notifications',
    dismiss: 'Dismiss notification',
  },
  upload: {
    title: 'Bring in a document',
    checking: 'Waking up the workshop…',
    offline: 'The workshop is asleep — the server is not responding right now.',
    onlineAwake: 'Workshop is open and your assistant is awake.',
    onlineAsleep:
      'Workshop is open. Your assistant is napping (AI features rest for now).',
    deskHint: 'Drag a document onto the desk, or choose one from your computer.',
    choose: 'Choose a document',
    chooseAria: 'Choose a document to upload',
    uploading: 'Uploading…',
    supported: 'Supported: {list}',
    maxSize: 'Maximum size: {size}',
    uploadingFile: 'Uploading "{name}"…',
    done: '"{name}" is on the desk ({size}). You\'re ready to start.',
    unsupported:
      'Sorry, ".{ext}" files aren\'t supported yet. Try: {list}.',
    tooLarge:
      '"{name}" is too large ({size}). The maximum allowed size is {max}.',
    genericError: 'Something went wrong while uploading. Please try again.',
    timeout:
      'The upload did not go through. Your browser could not read that file — try copying it somewhere else (for example your Documents folder) and choosing it again.',
    resultName: 'Name',
    resultType: 'Type',
    resultSize: 'Size',
    resultId: 'Document ID',
    enter: 'Enter the workshop',
  },
  hub: {
    title: 'Your workshop',
    workingOn: 'Working on {name}',
    bringAnother: 'Bring another document',
    napping:
      'Your assistant is napping, so AI tools (keywords, summary, rephrase) are resting for now. The reading tools still work.',
    appliedSoFar: 'Applied so far',
    nothingApplied:
      'Nothing applied yet. Pick a tool to begin — you can undo by starting fresh from the original inside any tool.',
    ai: ' · AI',
  },
  groups: {
    'Make it readable': 'Make it readable',
    'Understand it': 'Understand it',
  },
  stations: {
    format: {
      title: 'Colour & style',
      description: 'Colour titles, headings and text to make structure clear.',
    },
    spacing: {
      title: 'Breathing room',
      description: 'Add calm space between paragraphs or sentences.',
    },
    framing: {
      title: 'Frames & borders',
      description:
        'Draw gentle boxes around sections, paragraphs or sentences.',
    },
    highlighting: {
      title: 'Word highlighting',
      description: 'Highlight nouns, verbs and more to aid focus.',
    },
    keywords: {
      title: 'Section keywords',
      description: 'Add the key words above each section.',
    },
    summarize: {
      title: 'Summary',
      description: 'Get a shorter version of the whole document.',
    },
    paraphrase: {
      title: 'Rephrase',
      description: 'Rewrite the text in a simpler, easier style.',
    },
  },
  fields: {
    fromOriginal: 'Start fresh from the original document',
  },
  format: {
    whichParts: 'Which parts to colour',
    primaryColour: 'Primary colour',
    secondaryColour: 'Secondary colour',
    scheme: 'Palette scheme',
    schemeHelp: 'How the two colours generate the full palette:',
    apply: 'Apply colours',
    working: 'Colouring your document…',
    done: 'Colours applied. Check the preview.',
    stepLabel: 'Colour & style',
    stepDetail: 'Applied colours to selected parts.',
    roles: {
      titles: 'Document title',
      section_titles: 'Section titles (Heading 1)',
      paragraphs_titles: 'Sub-headings (Heading 2+)',
      paragraphs: 'Body paragraphs',
      captions: 'Captions',
      bibliography: 'Bibliography',
    },
    schemes: {
      complementary: 'Complementary',
      triadic: 'Triadic',
      tetradic: 'Tetradic',
      even: 'Even',
      analogous: 'Analogous',
    },
    schemeDesc: {
      complementary:
        'Two opposite colours on the wheel — maximum contrast, bold and clear.',
      triadic:
        'Three colours evenly spaced — vivid and balanced variety.',
      tetradic:
        'Four colours in two complementary pairs — rich, varied palette.',
      even: 'Colours spread evenly around the wheel for uniform variety.',
      analogous:
        'Neighbouring colours on the wheel — harmonious and gentle.',
    },
  },
  framing: {
    whatToFrame: 'What to frame',
    borderStyle: 'Border style',
    borderWidth: 'Border thickness (⅛ pt, 8 = 1pt)',
    borderColour: 'Border colour',
    preserveSpacing: 'Preserve original spacing',
    apply: 'Add frames',
    working: 'Drawing frames…',
    done: 'Frames added. Check the preview.',
    stepLabel: 'Frames & borders',
    stepDetail: 'Framed selected parts.',
    parts: {
      sections: 'Whole sections',
      paragraphs: 'Each paragraph',
      subparagraphs: 'Sub-paragraphs',
      sentences: 'Each sentence',
    },
    borderStyles: {
      single: 'Single line',
      double: 'Double line',
      dashed: 'Dashed',
      dotted: 'Dotted',
      thick: 'Thick line',
    },
  },
  spacing: {
    where: 'Where to add space',
    paragraphs: 'Between paragraphs',
    sentences: 'Between sentences',
    apply: 'Add spacing',
    working: 'Adding space…',
    done: 'Spacing added. Check the preview.',
    stepLabel: 'Breathing room',
    stepDetail: 'Added spacing.',
  },
  keywords: {
    perSection: 'Keywords per section (1–10)',
    includeNames: 'Include names & places',
    apply: 'Add keywords',
    working: 'Finding keywords…',
    done: 'Keywords added above each section.',
    stepLabel: 'Section keywords',
    stepDetail: 'Up to {n} per section.',
  },
  aiModel: {
    label: 'AI model',
    tiers: {
      fast: 'Fast (lighter)',
      balanced: 'Balanced',
      advanced: 'Advanced (best quality)',
    },
    tooltip:
      'Choosing a lighter model is faster but less accurate. A heavier, advanced model is slower but gives higher-quality results.',
  },
  highlighting: {
    which: 'Which words to highlight',
    how: 'How to style them',
    colour: 'Highlight colour',
    apply: 'Highlight words',
    working: 'Highlighting words…',
    done: 'Highlighting applied. Check the preview.',
    stepLabel: 'Word highlighting',
    stepDetail: 'Highlighted parts of speech.',
    pos: {
      nouns: 'Nouns',
      verbs: 'Verbs',
      adjectives: 'Adjectives',
      adverbs: 'Adverbs',
    },
    styles: {
      bold: 'bold',
      italic: 'italic',
      underline: 'underline',
    },
  },
  summarize: {
    hint: 'Your assistant reads the document and writes a shorter version. This can take a little while.',
    length: 'Summary length',
    apply: 'Summarise',
    working: 'Reading and summarising…',
    done: 'Summary ready.',
    stepLabel: 'Summary',
    stepDetail: '{type} summary created.',
    resultTitle: 'Summary',
    keyPoints: 'Key points',
    addToDocument:
      'Add the summary to the top of the document, after the title and before the content',
    addedToDocument: 'The summary was added to the top of the document.',
    types: { brief: 'Brief', detailed: 'Detailed', executive: 'Executive' },
  },
  paraphrase: {
    hint: 'Your assistant rewrites the text in a different, easier style.',
    style: 'Rewrite style',
    apply: 'Rephrase',
    working: 'Rephrasing the text…',
    done: 'Rephrased text ready.',
    stepLabel: 'Rephrase',
    stepDetail: '{style} rewrite created.',
    resultTitle: 'Rephrased sections',
    applyToDocument:
      'Apply the rewrite to the document, replacing the body content (titles and headings are kept)',
    appliedToDocument: 'The rewrite was applied to the document.',
    styles: {
      simple: 'Simple',
      casual: 'Casual',
      professional: 'Professional',
    },
  },
  preview: {
    title: 'Preview',
    loading: 'Loading preview…',
    error: 'Could not load the preview.',
    counts: '{words} words · {chars} characters',
    showDocument: 'Show document',
    renderError:
      'Could not render the document preview. The text preview is still available.',
  },
  errors: {
    generic: 'Something went wrong. Please try again.',
  },
} as const;

const it: Dict = {
  common: {
    close: 'Chiudi',
    refresh: 'Aggiorna',
    working: 'In corso…',
    download: 'Scarica documento',
  },
  app: {
    skip: 'Vai al contenuto principale',
    settings: 'Impostazioni generali',
    credits: 'Creato da Serena Sensini & Martina Ricci',
    repo: 'Codice sorgente',
  },
  language: {
    label: 'Lingua',
    en: 'English',
    it: 'Italiano',
  },
  welcome: {
    title: 'Benvenuto/a in DivergentIA',
    intro:
      'Un luogo tranquillo dove, un passo alla volta, puoi dare forma ai documenti e renderli più adattivi. Prima scegli un compagno e imposta tutto come preferisci. Potrai cambiare ogni cosa in seguito.',
    chooseCompanion: 'Scegli il tuo compagno',
    companionLegend: 'Compagno assistente',
    setup: 'Imposta tutto come preferisci',
    readingFont: 'Carattere di lettura',
    colourTheme: 'Tema colori',
    textSize: 'Dimensione del testo',
    reduceMotion: 'Riduci movimento e animazioni',
    classicMode: 'Modalità classica (layout semplice, senza scena di gioco)',
    gameTheme: 'Tema diamante giocoso (indicatori di passo e colori stile Sims)',
    soundEffects:
      'Riproduci un lieve suono quando completi una tappa (tema diamante)',
    enter: 'Entra nel laboratorio',
    moreInfo: 'Maggiori informazioni',
    reset: 'Ripristina i valori predefiniti',
    resetConfirmTitle: 'Ripristinare tutte le preferenze?',
    resetConfirmBody:
      'Ripristina ogni impostazione — compagno, carattere, tema, dimensione del testo e interruttori — al valore originale. L’operazione non può essere annullata.',
    resetConfirm: 'Sì, ripristina',
    resetCancel: 'Annulla',
    resetDone: 'Le preferenze sono state ripristinate ai valori predefiniti.',
    help: {
      font: 'Come sono disegnate le lettere sullo schermo. Scegli quello più comodo da leggere per te.',
      theme: 'L’atmosfera cromatica generale dell’interfaccia.',
      textSize: 'Quanto appare grande il testo in tutta l’applicazione.',
      reduceMotion:
        'Rimuove animazioni e movimenti per un’interfaccia più calma e prevedibile.',
      classicMode:
        'Sostituisce la scena illustrata con un layout semplice, a elenco, con meno dettagli visivi.',
      gameTheme:
        'Una veste estetica ispirata a The Sims: indicatori di passo a diamante e colori d’accento più vivaci. Non modifica mai carattere, tema, dimensione del testo o impostazioni di movimento.',
      soundEffects:
        'Riproduce un lieve suono di due note quando completi una tappa. Disponibile solo con il tema diamante e disattivato finché non lo attivi.',
    },
    fonts: {
      system: 'Predefinito',
      atkinson: 'Atkinson Hyperlegible',
      dyslexic: 'Stile OpenDyslexic',
    },
    fontDesc: {
      system:
        'Il carattere standard del tuo dispositivo — familiare e veloce da caricare.',
      atkinson:
        'Un carattere progettato per l’ipovisione, con lettere facili da distinguere.',
      dyslexic:
        'Forme delle lettere marcate e distinte, che molti lettori dislessici trovano più facili da seguire.',
    },
    themes: {
      calm: 'Tenue (chiaro)',
      dark: 'Tenue (scuro)',
      'high-contrast': 'Alto contrasto',
    },
    sizes: {
      small: 'Piccolo',
      medium: 'Medio',
      large: 'Grande',
      'x-large': 'Molto grande',
    },
  },
  characters: {
    lumi: { blurb: 'Un gufo tranquillo che legge con calma e non ti mette mai fretta.' },
    pip: { blurb: 'Una volpe ordinata che adora ordinare e strutturare i documenti.' },
    nova: {
      blurb: 'Una tartaruga costante che procede sempre un passo chiaro alla volta.',
    },
  },
  notifications: {
    region: 'Notifiche',
    dismiss: 'Chiudi notifica',
  },
  upload: {
    title: 'Porta un documento',
    checking: 'Sto svegliando il laboratorio…',
    offline: 'Il laboratorio dorme — il server non risponde al momento.',
    onlineAwake: 'Il laboratorio è aperto e il tuo assistente è sveglio.',
    onlineAsleep:
      'Il laboratorio è aperto. Il tuo assistente sta riposando (le funzioni AI riposano per ora).',
    deskHint: 'Trascina un documento sulla scrivania, o scegline uno dal computer.',
    choose: 'Scegli un documento',
    chooseAria: 'Scegli un documento da caricare',
    uploading: 'Caricamento…',
    supported: 'Supportati: {list}',
    maxSize: 'Dimensione massima: {size}',
    uploadingFile: 'Caricamento di "{name}"…',
    done: '"{name}" è sulla scrivania ({size}). Puoi iniziare.',
    unsupported:
      'Spiacente, i file ".{ext}" non sono ancora supportati. Prova: {list}.',
    tooLarge:
      '"{name}" è troppo grande ({size}). La dimensione massima consentita è {max}.',
    genericError: 'Qualcosa è andato storto durante il caricamento. Riprova.',
    timeout:
      'Il caricamento non è andato a buon fine. Il browser non è riuscito a leggere quel file — prova a copiarlo altrove (per esempio nella cartella Documenti) e a selezionarlo di nuovo.',
    resultName: 'Nome',
    resultType: 'Tipo',
    resultSize: 'Dimensione',
    resultId: 'ID documento',
    enter: 'Entra nel laboratorio',
  },
  hub: {
    title: 'Il tuo laboratorio',
    workingOn: 'Stai lavorando su {name}',
    bringAnother: 'Carica un nuovo documento',
    napping:
      'Il tuo assistente sta riposando, quindi gli strumenti AI (parole chiave, riassunto, riformulazione) riposano per ora. Gli strumenti di lettura funzionano comunque.',
    appliedSoFar: 'Applicato finora',
    appliedSoFarGame: 'Sbloccato finora',
    nothingApplied:
      'Ancora nulla di applicato. Scegli uno strumento per iniziare — puoi annullare ripartendo dall\'originale dentro qualsiasi strumento.',
    nothingAppliedGame:
      'Ancora nessuna tappa sbloccata. Scegli una stazione per iniziare la tua impresa — puoi sempre ripartire dall\'originale dentro qualsiasi strumento.',
    ai: ' · AI',
  },
  groups: {
    'Make it readable': 'Rendilo leggibile',
    'Understand it': 'Comprendilo',
  },
  stations: {
    format: {
      title: 'Colore e stile',
      description:
        'Colora titoli, intestazioni e testo per rendere chiara la struttura.',
    },
    spacing: {
      title: 'Spazio per respirare',
      description: 'Aggiungi spazio tranquillo tra paragrafi o frasi.',
    },
    framing: {
      title: 'Cornici e bordi',
      description: 'Disegna riquadri delicati attorno a sezioni, paragrafi o frasi.',
    },
    highlighting: {
      title: 'Evidenziazione parole',
      description: 'Evidenzia nomi, verbi e altro per aiutare la concentrazione.',
    },
    keywords: {
      title: 'Parole chiave per sezione',
      description: 'Aggiungi le parole chiave sopra ogni sezione.',
    },
    summarize: {
      title: 'Riassunto',
      description: 'Ottieni una versione più breve dell\'intero documento.',
    },
    paraphrase: {
      title: 'Riformula',
      description: 'Riscrive il testo in uno stile più semplice e facile.',
    },
  },
  fields: {
    fromOriginal: 'Riparti dal documento originale',
  },
  format: {
    whichParts: 'Quali parti colorare',
    primaryColour: 'Colore primario',
    secondaryColour: 'Colore secondario',
    scheme: 'Schema della palette',
    schemeHelp: 'Come i due colori generano l\'intera palette:',
    apply: 'Applica colori',
    working: 'Sto colorando il documento…',
    done: 'Colori applicati. Controlla l\'anteprima.',
    stepLabel: 'Colore e stile',
    stepDetail: 'Colori applicati alle parti selezionate.',
    roles: {
      titles: 'Titolo del documento',
      section_titles: 'Titoli di sezione (Titolo 1)',
      paragraphs_titles: 'Sottotitoli (Titolo 2+)',
      paragraphs: 'Paragrafi di testo',
      captions: 'Didascalie',
      bibliography: 'Bibliografia',
    },
    schemes: {
      complementary: 'Complementare',
      triadic: 'Triadico',
      tetradic: 'Tetradico',
      even: 'Uniforme',
      analogous: 'Analogo',
    },
    schemeDesc: {
      complementary:
        'Due colori opposti sulla ruota — massimo contrasto, deciso e chiaro.',
      triadic: 'Tre colori equidistanti — varietà vivace ed equilibrata.',
      tetradic:
        'Quattro colori in due coppie complementari — palette ricca e varia.',
      even: 'Colori distribuiti uniformemente sulla ruota per una varietà omogenea.',
      analogous: 'Colori vicini sulla ruota — armoniosi e delicati.',
    },
  },
  framing: {
    whatToFrame: 'Cosa incorniciare',
    borderStyle: 'Stile del bordo',
    borderWidth: 'Spessore del bordo (⅛ pt, 8 = 1pt)',
    borderColour: 'Colore del bordo',
    preserveSpacing: 'Mantieni la spaziatura originale',
    apply: 'Aggiungi cornici',
    working: 'Sto disegnando le cornici…',
    done: 'Cornici aggiunte. Controlla l\'anteprima.',
    stepLabel: 'Cornici e bordi',
    stepDetail: 'Incorniciate le parti selezionate.',
    parts: {
      sections: 'Intere sezioni',
      paragraphs: 'Ogni paragrafo',
      subparagraphs: 'Sotto-paragrafi',
      sentences: 'Ogni frase',
    },
    borderStyles: {
      single: 'Linea singola',
      double: 'Linea doppia',
      dashed: 'Tratteggiato',
      dotted: 'Punteggiato',
      thick: 'Linea spessa',
    },
  },
  spacing: {
    where: 'Dove aggiungere spazio',
    paragraphs: 'Tra i paragrafi',
    sentences: 'Tra le frasi',
    apply: 'Aggiungi spazio',
    working: 'Sto aggiungendo spazio…',
    done: 'Spazio aggiunto. Controlla l\'anteprima.',
    stepLabel: 'Spazio per respirare',
    stepDetail: 'Spazio aggiunto.',
  },
  keywords: {
    perSection: 'Parole chiave per sezione (1–10)',
    includeNames: 'Includi nomi e luoghi',
    apply: 'Aggiungi parole chiave',
    working: 'Sto cercando le parole chiave…',
    done: 'Parole chiave aggiunte sopra ogni sezione.',
    stepLabel: 'Parole chiave per sezione',
    stepDetail: 'Fino a {n} per sezione.',
  },
  aiModel: {
    label: 'Modello AI',
    tiers: {
      fast: 'Veloce (più leggero)',
      balanced: 'Bilanciato',
      advanced: 'Avanzato (qualità migliore)',
    },
    tooltip:
      'Un modello più leggero è più veloce ma meno accurato. Un modello avanzato è più lento ma offre risultati di qualità migliore.',
  },
  highlighting: {
    which: 'Quali parole evidenziare',
    how: 'Come stilizzarle',
    colour: 'Colore evidenziazione',
    apply: 'Evidenzia parole',
    working: 'Sto evidenziando le parole…',
    done: 'Evidenziazione applicata. Controlla l\'anteprima.',
    stepLabel: 'Evidenziazione parole',
    stepDetail: 'Evidenziate le parti del discorso.',
    pos: {
      nouns: 'Nomi',
      verbs: 'Verbi',
      adjectives: 'Aggettivi',
      adverbs: 'Avverbi',
    },
    styles: {
      bold: 'grassetto',
      italic: 'corsivo',
      underline: 'sottolineato',
    },
  },
  summarize: {
    hint: 'Il tuo assistente legge il documento e ne scrive una versione più breve. Può richiedere un po\' di tempo.',
    length: 'Lunghezza del riassunto',
    apply: 'Riassumi',
    working: 'Sto leggendo e riassumendo…',
    done: 'Riassunto pronto.',
    stepLabel: 'Riassunto',
    stepDetail: 'Creato riassunto {type}.',
    resultTitle: 'Riassunto',
    keyPoints: 'Punti chiave',
    addToDocument:
      'Aggiungi il riassunto all\'inizio del documento, dopo il titolo e prima del contenuto',
    addedToDocument: 'Il riassunto è stato aggiunto all\'inizio del documento.',
    types: { brief: 'Breve', detailed: 'Dettagliato', executive: 'Esecutivo' },
  },
  paraphrase: {
    hint: 'Il tuo assistente riscrive il testo in uno stile diverso e più facile.',
    style: 'Stile di riscrittura',
    apply: 'Riformula',
    working: 'Sto riformulando il testo…',
    done: 'Testo riformulato pronto.',
    stepLabel: 'Riformula',
    stepDetail: 'Creata riscrittura {style}.',
    resultTitle: 'Sezioni riformulate',
    applyToDocument:
      'Applica la riformulazione al documento, sostituendo il contenuto (titoli e intestazioni vengono mantenuti)',
    appliedToDocument: 'La riformulazione è stata applicata al documento.',
    styles: {
      simple: 'Semplice',
      casual: 'Informale',
      professional: 'Professionale',
    },
  },
  preview: {
    title: 'Anteprima',
    loading: 'Caricamento anteprima…',
    error: 'Impossibile caricare l\'anteprima.',
    counts: '{words} parole · {chars} caratteri',
    showDocument: 'Mostra documento',
    renderError:
      'Impossibile mostrare l\'anteprima del documento. L\'anteprima testuale è comunque disponibile.',
  },
  errors: {
    generic: 'Qualcosa è andato storto. Riprova.',
  },
};

const DICTS: Record<Language, Dict> = { en: en as unknown as Dict, it };

function resolve(dict: Dict, path: string): string | undefined {
  const value = path
    .split('.')
    .reduce<unknown>(
      (acc, key) =>
        acc && typeof acc === 'object'
          ? (acc as Record<string, unknown>)[key]
          : undefined,
      dict,
    );
  return typeof value === 'string' ? value : undefined;
}

function interpolate(template: string, vars?: Record<string, string | number>) {
  if (!vars) return template;
  return template.replace(/\{(\w+)\}/g, (_, key: string) =>
    key in vars ? String(vars[key]) : `{${key}}`,
  );
}

export type TranslateFn = (
  path: string,
  vars?: Record<string, string | number>,
) => string;

interface I18nContextValue {
  lang: Language;
  t: TranslateFn;
}

const I18nContext = createContext<I18nContextValue | null>(null);

export function I18nProvider({ children }: { children: ReactNode }) {
  const { preferences } = usePreferences();
  const lang = preferences.language;

  const t = useCallback<TranslateFn>(
    (path, vars) => {
      const str =
        resolve(DICTS[lang], path) ?? resolve(DICTS.en, path) ?? path;
      return interpolate(str, vars);
    },
    [lang],
  );

  const value = useMemo(() => ({ lang, t }), [lang, t]);

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nContextValue {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error('useI18n must be used within an I18nProvider');
  return ctx;
}

