import { usePreferences, type Language } from '../state/preferences';
import { useI18n } from '../state/i18n';

const LANGUAGES: Language[] = ['en', 'it'];

/**
 * Compact language switcher bound to the persisted `language` preference.
 * Changing it re-renders the whole app in the chosen language.
 */
export function LanguageSelector({ id = 'language-select' }: { id?: string }) {
  const { preferences, setPreference } = usePreferences();
  const { t } = useI18n();

  return (
    <div className="field field--inline">
      <label htmlFor={id}>{t('language.label')}</label>
      <select
        id={id}
        value={preferences.language}
        onChange={(e) => setPreference('language', e.target.value as Language)}
      >
        {LANGUAGES.map((lang) => (
          <option key={lang} value={lang}>
            {t(`language.${lang}`)}
          </option>
        ))}
      </select>
    </div>
  );
}

