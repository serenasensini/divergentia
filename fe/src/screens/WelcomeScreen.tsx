import { useEffect, useId, useRef, useState } from 'react';
import { CHARACTERS } from '../state/characters';
import {
  usePreferences,
  type FontChoice,
  type ThemeChoice,
  type TextSize,
} from '../state/preferences';
import { useI18n } from '../state/i18n';
import { LanguageSelector } from '../components/LanguageSelector';
import { Plumbob } from '../components/Plumbob';
import { Tooltip } from '../components/Tooltip';

interface WelcomeScreenProps {
  onEnter: () => void;
}

const FONT_OPTIONS: FontChoice[] = ['system', 'atkinson', 'dyslexic'];
const THEME_OPTIONS: ThemeChoice[] = ['calm', 'dark', 'high-contrast'];
const TEXT_SIZE_OPTIONS: TextSize[] = ['small', 'medium', 'large', 'x-large'];

/**
 * Step 1 — Welcome room.
 * Pick a companion and set accessibility preferences before entering.
 * Everything is real DOM: keyboard-operable, screen-reader friendly.
 */
export function WelcomeScreen({ onEnter }: WelcomeScreenProps) {
  const { preferences, setPreference, reset } = usePreferences();
  const { t } = useI18n();

  // "Reset to defaults" confirmation flow (issue #5).
  const [confirmingReset, setConfirmingReset] = useState(false);
  const [resetAnnouncement, setResetAnnouncement] = useState('');
  const resetButtonRef = useRef<HTMLButtonElement>(null);
  const confirmButtonRef = useRef<HTMLButtonElement>(null);
  const dialogTitleId = useId();
  const dialogBodyId = useId();

  // Move focus into the dialog when it opens for keyboard/SR users.
  useEffect(() => {
    if (confirmingReset) confirmButtonRef.current?.focus();
  }, [confirmingReset]);

  const closeConfirm = () => {
    setConfirmingReset(false);
    resetButtonRef.current?.focus();
  };

  const handleReset = () => {
    reset();
    setConfirmingReset(false);
    setResetAnnouncement(t('welcome.resetDone'));
    resetButtonRef.current?.focus();
  };

  /** A small accessible "?" help tooltip for a first-time option (issue #4). */
  const help = (key: string) => (
    <Tooltip
      label={`${t('welcome.moreInfo')}: ${t(`welcome.${key}`)}`}
      content={t(`welcome.help.${key}`)}
    />
  );

  return (
    <main className="welcome" aria-labelledby="welcome-title">
      <div className="welcome__card">
        <h1 id="welcome-title" className="welcome__title">
          {preferences.gameTheme && (
            <Plumbob state="completed" size={26} className="welcome__title-plumbob" />
          )}
          {t('welcome.title')}
        </h1>
        <p className="welcome__intro">{t('welcome.intro')}</p>

        <section aria-labelledby="choose-companion" className="welcome__section">
          <h2 id="choose-companion">{t('welcome.chooseCompanion')}</h2>
          <fieldset className="character-grid">
            <legend className="visually-hidden">
              {t('welcome.companionLegend')}
            </legend>
            {CHARACTERS.map((character) => {
              const selected = preferences.characterId === character.id;
              return (
                <label
                  key={character.id}
                  className="character-card"
                  data-selected={String(selected)}
                >
                  <input
                    type="radio"
                    name="companion"
                    value={character.id}
                    checked={selected}
                    onChange={() => setPreference('characterId', character.id)}
                  />
                  <span className="character-card__emoji" aria-hidden="true">
                    {character.emoji}
                  </span>
                  <span className="character-card__name">{character.name}</span>
                  <span className="character-card__blurb">
                    {t(`characters.${character.id}.blurb`)}
                  </span>
                </label>
              );
            })}
          </fieldset>
        </section>

        <section aria-labelledby="setup-title" className="welcome__section">
          <h2 id="setup-title">{t('welcome.setup')}</h2>

          <LanguageSelector id="welcome-language" />

          <div className="field">
            <label htmlFor="font-select" className="field__label-row">
              {t('welcome.readingFont')}
              <Tooltip
                label={`${t('welcome.moreInfo')}: ${t('welcome.readingFont')}`}
                content={
                  <>
                    <strong>{t('welcome.help.font')}</strong>
                    <ul className="tooltip__list">
                      {FONT_OPTIONS.map((o) => (
                        <li key={o}>
                          <strong>{t(`welcome.fonts.${o}`)}</strong> —{' '}
                          {t(`welcome.fontDesc.${o}`)}
                        </li>
                      ))}
                    </ul>
                  </>
                }
              />
            </label>
            <select
              id="font-select"
              value={preferences.font}
              onChange={(e) =>
                setPreference('font', e.target.value as FontChoice)
              }
            >
              {FONT_OPTIONS.map((o) => (
                <option key={o} value={o}>
                  {t(`welcome.fonts.${o}`)}
                </option>
              ))}
            </select>
          </div>

          <div className="field">
            <label htmlFor="theme-select" className="field__label-row">
              {t('welcome.colourTheme')}
              {help('theme')}
            </label>
            <select
              id="theme-select"
              value={preferences.theme}
              onChange={(e) =>
                setPreference('theme', e.target.value as ThemeChoice)
              }
            >
              {THEME_OPTIONS.map((o) => (
                <option key={o} value={o}>
                  {t(`welcome.themes.${o}`)}
                </option>
              ))}
            </select>
          </div>

          <div className="field">
            <label htmlFor="text-size-select" className="field__label-row">
              {t('welcome.textSize')}
              {help('textSize')}
            </label>
            <select
              id="text-size-select"
              value={preferences.textSize}
              onChange={(e) =>
                setPreference('textSize', e.target.value as TextSize)
              }
            >
              {TEXT_SIZE_OPTIONS.map((o) => (
                <option key={o} value={o}>
                  {t(`welcome.sizes.${o}`)}
                </option>
              ))}
            </select>
          </div>

          <div className="field field--switch">
            <input
              id="reduce-motion"
              type="checkbox"
              checked={preferences.reduceMotion}
              onChange={(e) => setPreference('reduceMotion', e.target.checked)}
            />
            <label htmlFor="reduce-motion">{t('welcome.reduceMotion')}</label>
            {help('reduceMotion')}
          </div>

          <div className="field field--switch">
            <input
              id="classic-mode"
              type="checkbox"
              checked={preferences.classicMode}
              onChange={(e) => setPreference('classicMode', e.target.checked)}
            />
            <label htmlFor="classic-mode">{t('welcome.classicMode')}</label>
            {help('classicMode')}
          </div>

          <div className="field field--switch">
            <input
              id="game-theme"
              type="checkbox"
              checked={preferences.gameTheme}
              onChange={(e) => setPreference('gameTheme', e.target.checked)}
            />
            <label htmlFor="game-theme">{t('welcome.gameTheme')}</label>
            {help('gameTheme')}
          </div>

          {preferences.gameTheme && (
            <div className="field field--switch">
              <input
                id="sound-effects"
                type="checkbox"
                checked={preferences.soundEffects}
                onChange={(e) =>
                  setPreference('soundEffects', e.target.checked)
                }
              />
              <label htmlFor="sound-effects">
                {t('welcome.soundEffects')}
              </label>
              {help('soundEffects')}
            </div>
          )}

          <div className="welcome__reset">
            <button
              type="button"
              ref={resetButtonRef}
              className="button button--ghost"
              onClick={() => setConfirmingReset(true)}
            >
              {t('welcome.reset')}
            </button>
          </div>
        </section>

        <button
          type="button"
          className="button button--primary welcome__enter"
          onClick={() => {
            setPreference('onboarded', true);
            onEnter();
          }}
        >
          {t('welcome.enter')}
        </button>
      </div>

      {confirmingReset && (
        <div
          className="modal-overlay"
          onClick={(e) => {
            if (e.target === e.currentTarget) closeConfirm();
          }}
        >
          <div
            role="alertdialog"
            aria-modal="true"
            aria-labelledby={dialogTitleId}
            aria-describedby={dialogBodyId}
            className="modal"
            onKeyDown={(e) => {
              if (e.key === 'Escape') closeConfirm();
            }}
          >
            <h2 id={dialogTitleId} className="modal__title">
              {t('welcome.resetConfirmTitle')}
            </h2>
            <p id={dialogBodyId} className="modal__body">
              {t('welcome.resetConfirmBody')}
            </p>
            <div className="modal__actions">
              <button
                type="button"
                className="button button--ghost"
                onClick={closeConfirm}
              >
                {t('welcome.resetCancel')}
              </button>
              <button
                type="button"
                ref={confirmButtonRef}
                className="button button--primary"
                onClick={handleReset}
              >
                {t('welcome.resetConfirm')}
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="visually-hidden" role="status" aria-live="polite">
        {resetAnnouncement}
      </div>
    </main>
  );
}
