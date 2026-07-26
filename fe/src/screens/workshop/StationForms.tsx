import { useState } from 'react';
import { apiClient } from '../../api/client';
import type {
  FormattingOptions,
  FramingOptions,
  HighlightingOptions,
  ParaphraseResponse,
  ParaphraseStyle,
  SummarizeResponse,
  SummaryType,
} from '../../api/types';
import { useDocument } from '../../state/document';
import { useI18n } from '../../state/i18n';
import { useStationRunner, type RunPhase } from '../../state/useStationRunner';
import { Tooltip } from '../../components/Tooltip';
import { usePreferences } from '../../state/preferences';
import { AI_MODEL_TIERS, resolveAiModel, type AiModelTier } from '../../state/aiModels';

/**
 * Shared AI model tier selector used by every Ollama-backed station
 * (keywords, summarise, rephrase). The user picks a friendly tier label —
 * never a raw model name — and the choice is persisted as a preference so it
 * carries over between stations (see issue #22).
 */
function AiModelTierField({ idPrefix }: { idPrefix: string }) {
  const { t } = useI18n();
  const { preferences, setPreference } = usePreferences();
  const fieldId = `${idPrefix}-ai-model`;
  return (
    <div className="field">
      <label htmlFor={fieldId} className="field__label-row">
        {t('aiModel.label')}
        <Tooltip label={t('aiModel.label')} content={t('aiModel.tooltip')} />
      </label>
      <select
        id={fieldId}
        value={preferences.aiModel}
        onChange={(e) =>
          setPreference('aiModel', e.target.value as AiModelTier)
        }
      >
        {AI_MODEL_TIERS.map((tier) => (
          <option key={tier} value={tier}>
            {t(`aiModel.tiers.${tier}`)}
          </option>
        ))}
      </select>
    </div>
  );
}
export interface StationProps {
  documentId: string;
  onApplied: () => void;
}
/**
 * Inline status line. Working/error states are shown here; success is surfaced
 * as a toast (see useStationRunner), so 'idle' and 'done' render nothing.
 */
function StatusLine({ phase, message }: { phase: RunPhase; message: string }) {
  if (phase === 'idle' || phase === 'done') return null;
  return (
    <p
      className={`station__status station__status--${phase}`}
      role={phase === 'error' ? 'alert' : 'status'}
      aria-live="polite"
    >
      {message}
    </p>
  );
}
function SubmitButton({ phase, label }: { phase: RunPhase; label: string }) {
  const { t } = useI18n();
  return (
    <button
      type="submit"
      className="button button--primary"
      disabled={phase === 'working'}
    >
      {phase === 'working' ? t('common.working') : label}
    </button>
  );
}
function FromOriginalToggle({
  id,
  checked,
  onChange,
}: {
  id: string;
  checked: boolean;
  onChange: (v: boolean) => void;
}) {
  const { t } = useI18n();
  return (
    <div className="field field--switch">
      <input
        id={id}
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
      />
      <label htmlFor={id}>{t('fields.fromOriginal')}</label>
    </div>
  );
}
const SCHEMES: NonNullable<FormattingOptions['theme']>['scheme'][] = [
  'complementary',
  'triadic',
  'tetradic',
  'even',
  'analogous',
];
/* ------------------------------ Format ------------------------------ */
export function FormatStation({ documentId, onApplied }: StationProps) {
  const { t } = useI18n();
  const { addStep } = useDocument();
  const { phase, message, run } = useStationRunner();
  const [roles, setRoles] = useState({
    titles: true,
    section_titles: true,
    paragraphs_titles: false,
    paragraphs: false,
    captions: false,
    bibliography: false,
  });
  const [positive, setPositive] = useState('#ff7f00');
  const [negative, setNegative] = useState('#007fff');
  const [scheme, setScheme] =
    useState<NonNullable<FormattingOptions['theme']>['scheme']>('even');
  const [fromOriginal, setFromOriginal] = useState(false);
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        const options: FormattingOptions = {
          ...roles,
          theme: { positive, negative, scheme },
          from_original: fromOriginal,
        };
        void run(
          async () => {
            await apiClient.applyFormatting(documentId, options);
            addStep(t('format.stepLabel'), t('format.stepDetail'));
            onApplied();
          },
          t('format.working'),
          t('format.done'),
        );
      }}
    >
      <fieldset className="field-group">
        <legend>{t('format.whichParts')}</legend>
        {(Object.keys(roles) as (keyof typeof roles)[]).map((key) => (
          <div className="field field--switch" key={key}>
            <input
              id={`fmt-${key}`}
              type="checkbox"
              checked={roles[key]}
              onChange={(e) =>
                setRoles((r) => ({ ...r, [key]: e.target.checked }))
              }
            />
            <label htmlFor={`fmt-${key}`}>{t(`format.roles.${key}`)}</label>
          </div>
        ))}
      </fieldset>
      <div className="field">
        <label htmlFor="fmt-positive">{t('format.primaryColour')}</label>
        <input
          id="fmt-positive"
          type="color"
          value={positive}
          onChange={(e) => setPositive(e.target.value)}
        />
      </div>
      <div className="field">
        <label htmlFor="fmt-negative">{t('format.secondaryColour')}</label>
        <input
          id="fmt-negative"
          type="color"
          value={negative}
          onChange={(e) => setNegative(e.target.value)}
        />
      </div>
      <div className="field">
        <label htmlFor="fmt-scheme" className="field__label-row">
          {t('format.scheme')}
          <Tooltip
            label={t('format.scheme')}
            content={
              <>
                <strong>{t('format.schemeHelp')}</strong>
                <ul className="tooltip__list">
                  {SCHEMES.map((s) => (
                    <li key={s}>
                      <strong>{t(`format.schemes.${s}`)}</strong> —{' '}
                      {t(`format.schemeDesc.${s}`)}
                    </li>
                  ))}
                </ul>
              </>
            }
          />
        </label>
        <select
          id="fmt-scheme"
          value={scheme}
          onChange={(e) =>
            setScheme(
              e.target.value as NonNullable<FormattingOptions['theme']>['scheme'],
            )
          }
        >
          {SCHEMES.map((s) => (
            <option key={s} value={s} title={t(`format.schemeDesc.${s}`)}>
              {t(`format.schemes.${s}`)}
            </option>
          ))}
        </select>
        <p className="field__help">{t(`format.schemeDesc.${scheme}`)}</p>
      </div>
      <FromOriginalToggle
        id="fmt-from-original"
        checked={fromOriginal}
        onChange={setFromOriginal}
      />
      <SubmitButton phase={phase} label={t('format.apply')} />
      <StatusLine phase={phase} message={message} />
    </form>
  );
}
/* ------------------------------ Framing ----------------------------- */
export function FramingStation({ documentId, onApplied }: StationProps) {
  const { t } = useI18n();
  const { addStep } = useDocument();
  const { phase, message, run } = useStationRunner();
  const [parts, setParts] = useState({
    sections: false,
    paragraphs: true,
    subparagraphs: false,
    sentences: false,
  });
  const [borderStyle, setBorderStyle] = useState('single');
  const [borderWidth, setBorderWidth] = useState(8);
  const [borderColor, setBorderColor] = useState('#000000');
  const [preserveSpacing, setPreserveSpacing] = useState(true);
  const [fromOriginal, setFromOriginal] = useState(false);
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        const options: FramingOptions = {
          ...parts,
          border_style: borderStyle,
          border_width: borderWidth,
          border_color: borderColor.replace('#', ''),
          preserve_spacing: preserveSpacing,
          from_original: fromOriginal,
        };
        void run(
          async () => {
            await apiClient.applyFraming(documentId, options);
            addStep(t('framing.stepLabel'), t('framing.stepDetail'));
            onApplied();
          },
          t('framing.working'),
          t('framing.done'),
        );
      }}
    >
      <fieldset className="field-group">
        <legend>{t('framing.whatToFrame')}</legend>
        {(Object.keys(parts) as (keyof typeof parts)[]).map((key) => (
          <div className="field field--switch" key={key}>
            <input
              id={`frm-${key}`}
              type="checkbox"
              checked={parts[key]}
              onChange={(e) =>
                setParts((p) => ({ ...p, [key]: e.target.checked }))
              }
            />
            <label htmlFor={`frm-${key}`}>{t(`framing.parts.${key}`)}</label>
          </div>
        ))}
      </fieldset>
      <div className="field">
        <label htmlFor="frm-style">{t('framing.borderStyle')}</label>
        <select
          id="frm-style"
          value={borderStyle}
          onChange={(e) => setBorderStyle(e.target.value)}
        >
          {['single', 'double', 'dashed', 'dotted', 'thick'].map((s) => (
            <option key={s} value={s}>
              {t(`framing.borderStyles.${s}`)}
            </option>
          ))}
        </select>
      </div>
      <div className="field">
        <label htmlFor="frm-width">{t('framing.borderWidth')}</label>
        <input
          id="frm-width"
          type="number"
          min={1}
          max={48}
          value={borderWidth}
          onChange={(e) => setBorderWidth(Number(e.target.value))}
        />
      </div>
      <div className="field">
        <label htmlFor="frm-color">{t('framing.borderColour')}</label>
        <input
          id="frm-color"
          type="color"
          value={borderColor}
          onChange={(e) => setBorderColor(e.target.value)}
        />
      </div>
      <div className="field field--switch">
        <input
          id="frm-preserve"
          type="checkbox"
          checked={preserveSpacing}
          onChange={(e) => setPreserveSpacing(e.target.checked)}
        />
        <label htmlFor="frm-preserve">{t('framing.preserveSpacing')}</label>
      </div>
      <FromOriginalToggle
        id="frm-from-original"
        checked={fromOriginal}
        onChange={setFromOriginal}
      />
      <SubmitButton phase={phase} label={t('framing.apply')} />
      <StatusLine phase={phase} message={message} />
    </form>
  );
}
/* ------------------------------ Spacing ----------------------------- */
export function SpacingStation({ documentId, onApplied }: StationProps) {
  const { t } = useI18n();
  const { addStep } = useDocument();
  const { phase, message, run } = useStationRunner();
  const [paragraphs, setParagraphs] = useState(true);
  const [sentences, setSentences] = useState(false);
  const [fromOriginal, setFromOriginal] = useState(false);
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        void run(
          async () => {
            await apiClient.applySpacing(documentId, {
              paragraphs,
              sentences,
              from_original: fromOriginal,
            });
            addStep(t('spacing.stepLabel'), t('spacing.stepDetail'));
            onApplied();
          },
          t('spacing.working'),
          t('spacing.done'),
        );
      }}
    >
      <fieldset className="field-group">
        <legend>{t('spacing.where')}</legend>
        <div className="field field--switch">
          <input
            id="spc-paragraphs"
            type="checkbox"
            checked={paragraphs}
            onChange={(e) => setParagraphs(e.target.checked)}
          />
          <label htmlFor="spc-paragraphs">{t('spacing.paragraphs')}</label>
        </div>
        <div className="field field--switch">
          <input
            id="spc-sentences"
            type="checkbox"
            checked={sentences}
            onChange={(e) => setSentences(e.target.checked)}
          />
          <label htmlFor="spc-sentences">{t('spacing.sentences')}</label>
        </div>
      </fieldset>
      <FromOriginalToggle
        id="spc-from-original"
        checked={fromOriginal}
        onChange={setFromOriginal}
      />
      <SubmitButton phase={phase} label={t('spacing.apply')} />
      <StatusLine phase={phase} message={message} />
    </form>
  );
}
/* ------------------------------ Keywords ---------------------------- */
export function KeywordsStation({ documentId, onApplied }: StationProps) {
  const { t } = useI18n();
  const { addStep } = useDocument();
  const { phase, message, run } = useStationRunner();
  const { preferences } = usePreferences();
  const [maxKeywords, setMaxKeywords] = useState(5);
  const [includeProperNouns, setIncludeProperNouns] = useState(true);
  const [fromOriginal, setFromOriginal] = useState(false);
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        void run(
          async () => {
            await apiClient.applyKeywords(documentId, {
              max_keywords: maxKeywords,
              include_proper_nouns: includeProperNouns,
              model: resolveAiModel(preferences.aiModel),
              from_original: fromOriginal,
            });
            addStep(
              t('keywords.stepLabel'),
              t('keywords.stepDetail', { n: maxKeywords }),
            );
            onApplied();
          },
          t('keywords.working'),
          t('keywords.done'),
        );
      }}
    >
      <div className="field">
        <label htmlFor="kw-max">{t('keywords.perSection')}</label>
        <input
          id="kw-max"
          type="number"
          min={1}
          max={10}
          value={maxKeywords}
          onChange={(e) => setMaxKeywords(Number(e.target.value))}
        />
      </div>
      <div className="field field--switch">
        <input
          id="kw-proper"
          type="checkbox"
          checked={includeProperNouns}
          onChange={(e) => setIncludeProperNouns(e.target.checked)}
        />
        <label htmlFor="kw-proper">{t('keywords.includeNames')}</label>
      </div>
      <AiModelTierField idPrefix="kw" />
      <FromOriginalToggle
        id="kw-from-original"
        checked={fromOriginal}
        onChange={setFromOriginal}
      />
      <SubmitButton phase={phase} label={t('keywords.apply')} />
      <StatusLine phase={phase} message={message} />
    </form>
  );
}
/* ---------------------------- Highlighting -------------------------- */
export function HighlightingStation({ documentId, onApplied }: StationProps) {
  const { t } = useI18n();
  const { addStep } = useDocument();
  const { phase, message, run } = useStationRunner();
  const [pos, setPos] = useState({
    nouns: true,
    verbs: false,
    adjectives: false,
    adverbs: false,
  });
  const [styles, setStyles] = useState({
    bold: true,
    italic: false,
    underline: false,
  });
  const [color, setColor] = useState('#1b6ac9');
  const [fromOriginal, setFromOriginal] = useState(false);
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        const styleStr = (Object.keys(styles) as (keyof typeof styles)[])
          .filter((k) => styles[k])
          .join(',');
        const options: HighlightingOptions = {
          enabled: true,
          color,
          style: styleStr || undefined,
          ...pos,
          from_original: fromOriginal,
        };
        void run(
          async () => {
            await apiClient.applyHighlighting(documentId, options);
            addStep(t('highlighting.stepLabel'), t('highlighting.stepDetail'));
            onApplied();
          },
          t('highlighting.working'),
          t('highlighting.done'),
        );
      }}
    >
      <fieldset className="field-group">
        <legend>{t('highlighting.which')}</legend>
        {(Object.keys(pos) as (keyof typeof pos)[]).map((key) => (
          <div className="field field--switch" key={key}>
            <input
              id={`hl-${key}`}
              type="checkbox"
              checked={pos[key]}
              onChange={(e) => setPos((p) => ({ ...p, [key]: e.target.checked }))}
            />
            <label htmlFor={`hl-${key}`}>{t(`highlighting.pos.${key}`)}</label>
          </div>
        ))}
      </fieldset>
      <fieldset className="field-group">
        <legend>{t('highlighting.how')}</legend>
        {(Object.keys(styles) as (keyof typeof styles)[]).map((key) => (
          <div className="field field--switch" key={key}>
            <input
              id={`hl-style-${key}`}
              type="checkbox"
              checked={styles[key]}
              onChange={(e) =>
                setStyles((s) => ({ ...s, [key]: e.target.checked }))
              }
            />
            <label htmlFor={`hl-style-${key}`}>
              {t(`highlighting.styles.${key}`)}
            </label>
          </div>
        ))}
      </fieldset>
      <div className="field">
        <label htmlFor="hl-color">{t('highlighting.colour')}</label>
        <input
          id="hl-color"
          type="color"
          value={color}
          onChange={(e) => setColor(e.target.value)}
        />
      </div>
      <FromOriginalToggle
        id="hl-from-original"
        checked={fromOriginal}
        onChange={setFromOriginal}
      />
      <SubmitButton phase={phase} label={t('highlighting.apply')} />
      <StatusLine phase={phase} message={message} />
    </form>
  );
}
/* ---------------------------- Summarize ----------------------------- */
export function SummarizeStation({ documentId, onApplied }: StationProps) {
  const { t } = useI18n();
  const { addStep } = useDocument();
  const { phase, message, run } = useStationRunner();
  const { preferences } = usePreferences();
  const [summaryType, setSummaryType] = useState<SummaryType>('brief');
  const [addToDocument, setAddToDocument] = useState(false);
  const [result, setResult] = useState<SummarizeResponse | null>(null);
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        void run(
          async () => {
            const res = await apiClient.summarizeDocument(
              documentId,
              summaryType,
              addToDocument,
              resolveAiModel(preferences.aiModel),
            );
            setResult(res);
            addStep(
              t('summarize.stepLabel'),
              t('summarize.stepDetail', {
                type: t(`summarize.types.${summaryType}`),
              }),
            );
            onApplied();
          },
          t('summarize.working'),
          t('summarize.done'),
        );
      }}
    >
      <p className="station__hint">{t('summarize.hint')}</p>
      <AiModelTierField idPrefix="sum" />
      <div className="field">
        <label htmlFor="sum-type">{t('summarize.length')}</label>
        <select
          id="sum-type"
          value={summaryType}
          onChange={(e) => setSummaryType(e.target.value as SummaryType)}
        >
          {(['brief', 'detailed', 'executive'] as SummaryType[]).map((v) => (
            <option key={v} value={v}>
              {t(`summarize.types.${v}`)}
            </option>
          ))}
        </select>
      </div>
      <div className="field field--switch">
        <input
          id="sum-add-to-document"
          type="checkbox"
          checked={addToDocument}
          onChange={(e) => setAddToDocument(e.target.checked)}
        />
        <label htmlFor="sum-add-to-document">
          {t('summarize.addToDocument')}
        </label>
      </div>
      <SubmitButton phase={phase} label={t('summarize.apply')} />
      <StatusLine phase={phase} message={message} />
      {result && (
        <div className="station__result">
          <h3>{t('summarize.resultTitle')}</h3>
          <p>{result.summary}</p>
          {result.added_to_document && (
            <p className="station__hint">{t('summarize.addedToDocument')}</p>
          )}
          {result.key_points && result.key_points.length > 0 && (
            <>
              <h4>{t('summarize.keyPoints')}</h4>
              <ul>
                {result.key_points.map((point, i) => (
                  <li key={i}>{point}</li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </form>
  );
}
/* ---------------------------- Paraphrase ---------------------------- */
export function ParaphraseStation({ documentId, onApplied }: StationProps) {
  const { t } = useI18n();
  const { addStep } = useDocument();
  const { phase, message, run } = useStationRunner();
  const { preferences } = usePreferences();
  const [style, setStyle] = useState<ParaphraseStyle>('simple');
  const [applyToDocument, setApplyToDocument] = useState(false);
  const [result, setResult] = useState<ParaphraseResponse | null>(null);
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        void run(
          async () => {
            const res = await apiClient.paraphraseDocument(
              documentId,
              style,
              applyToDocument,
              resolveAiModel(preferences.aiModel),
            );
            setResult(res);
            addStep(
              t('paraphrase.stepLabel'),
              t('paraphrase.stepDetail', {
                style: t(`paraphrase.styles.${style}`),
              }),
            );
            onApplied();
          },
          t('paraphrase.working'),
          t('paraphrase.done'),
        );
      }}
    >
      <p className="station__hint">{t('paraphrase.hint')}</p>
      <AiModelTierField idPrefix="par" />
      <div className="field">
        <label htmlFor="par-style">{t('paraphrase.style')}</label>
        <select
          id="par-style"
          value={style}
          onChange={(e) => setStyle(e.target.value as ParaphraseStyle)}
        >
          {(['simple', 'casual', 'professional'] as ParaphraseStyle[]).map(
            (v) => (
              <option key={v} value={v}>
                {t(`paraphrase.styles.${v}`)}
              </option>
            ),
          )}
        </select>
      </div>
      <div className="field field--switch">
        <input
          id="par-apply-to-document"
          type="checkbox"
          checked={applyToDocument}
          onChange={(e) => setApplyToDocument(e.target.checked)}
        />
        <label htmlFor="par-apply-to-document">
          {t('paraphrase.applyToDocument')}
        </label>
      </div>
      <SubmitButton phase={phase} label={t('paraphrase.apply')} />
      <StatusLine phase={phase} message={message} />
      {result?.applied_to_document && (
        <p className="station__hint">{t('paraphrase.appliedToDocument')}</p>
      )}
      {result?.paraphrased_sections && (
        <div className="station__result">
          <h3>{t('paraphrase.resultTitle')}</h3>
          {Object.entries(result.paraphrased_sections).map(([key, text]) => (
            <p key={key}>{text}</p>
          ))}
        </div>
      )}
    </form>
  );
}
