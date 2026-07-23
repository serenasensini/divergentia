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
  const { preferences, setPreference } = usePreferences();
  const { t } = useI18n();

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
                    {character.blurb}
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
            <label htmlFor="font-select">{t('welcome.readingFont')}</label>
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
            <label htmlFor="theme-select">{t('welcome.colourTheme')}</label>
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
            <label htmlFor="text-size-select">{t('welcome.textSize')}</label>
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
          </div>

          <div className="field field--switch">
            <input
              id="classic-mode"
              type="checkbox"
              checked={preferences.classicMode}
              onChange={(e) => setPreference('classicMode', e.target.checked)}
            />
            <label htmlFor="classic-mode">{t('welcome.classicMode')}</label>
          </div>

          <div className="field field--switch">
            <input
              id="game-theme"
              type="checkbox"
              checked={preferences.gameTheme}
              onChange={(e) => setPreference('gameTheme', e.target.checked)}
            />
            <label htmlFor="game-theme">{t('welcome.gameTheme')}</label>
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
            </div>
          )}
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
    </main>
  );
}
