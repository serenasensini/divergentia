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
  },
  language: {
    label: 'Language',
    en: 'English',
    it: 'Italiano',
  },
  welcome: {
    title: 'Welcome to your Document Workshop',
    intro:
      'A calm, one-step-at-a-time place to reshape documents so they are easier to read. First, choose a companion and set things up your way. You can change any of this later.',
    chooseCompanion: 'Choose your companion',
    companionLegend: 'Assistant companion',
    setup: 'Set things up your way',
    readingFont: 'Reading font',
    colourTheme: 'Colour theme',
    textSize: 'Text size',
    reduceMotion: 'Reduce motion and animation',
    classicMode: 'Classic mode (plain layout, no game scene)',
    gameTheme: 'Playful diamond theme (Sims-style step markers and colours)',
    enter: 'Enter the workshop',
    fonts: {
      system: 'Default',
      atkinson: 'Atkinson Hyperlegible',
      dyslexic: 'OpenDyslexic-style',
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
    uploadingFile: 'Uploading "{name}"…',
    done: '"{name}" is on the desk ({size}). You\'re ready to start.',
    unsupported:
      'Sorry, ".{ext}" files aren\'t supported yet. Try: {list}.',
    genericError: 'Something went wrong while uploading. Please try again.',
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
    model: 'AI model (optional)',
    apply: 'Add keywords',
    working: 'Finding keywords…',
    done: 'Keywords added above each section.',
    stepLabel: 'Section keywords',
    stepDetail: 'Up to {n} per section.',
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
    showText: 'Show text only',
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
  },
  language: {
    label: 'Lingua',
    en: 'English',
    it: 'Italiano',
  },
  welcome: {
    title: 'Benvenuto nel tuo Laboratorio Documenti',
    intro:
      'Un luogo tranquillo, un passo alla volta, per rimodellare i documenti e renderli più facili da leggere. Prima scegli un compagno e imposta tutto come preferisci. Potrai cambiare ogni cosa in seguito.',
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
    fonts: {
      system: 'Predefinito',
      atkinson: 'Atkinson Hyperlegible',
      dyslexic: 'Stile OpenDyslexic',
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
    uploadingFile: 'Caricamento di "{name}"…',
    done: '"{name}" è sulla scrivania ({size}). Puoi iniziare.',
    unsupported:
      'Spiacente, i file ".{ext}" non sono ancora supportati. Prova: {list}.',
    genericError: 'Qualcosa è andato storto durante il caricamento. Riprova.',
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
    model: 'Modello AI (opzionale)',
    apply: 'Aggiungi parole chiave',
    working: 'Sto cercando le parole chiave…',
    done: 'Parole chiave aggiunte sopra ogni sezione.',
    stepLabel: 'Parole chiave per sezione',
    stepDetail: 'Fino a {n} per sezione.',
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
    showText: 'Mostra solo testo',
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

