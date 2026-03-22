import { createI18n } from "vue-i18n";
import { locales, type LocaleCode } from "./locales";
import { normalizeLocaleCode, resolveInitialLocale } from "./locale-utils";

type MessageNode = Record<string, any>;
type MessageModule = { default: MessageNode };
type MessageLoader = () => Promise<MessageModule>;

const FALLBACK_LOCALE: LocaleCode = "en";

const messages: Record<string, MessageNode> = {};
const loadedStructuredLocales = new Set<LocaleCode>();
const localeLoadTasks = new Map<LocaleCode, Promise<void>>();

const isPlainObject = (value: unknown): value is MessageNode => {
  return typeof value === "object" && value !== null && !Array.isArray(value);
};

const deepMerge = (target: MessageNode, source: MessageNode): MessageNode => {
  Object.entries(source).forEach(([key, value]) => {
    if (isPlainObject(value)) {
      const current = isPlainObject(target[key]) ? target[key] : {};
      target[key] = deepMerge({ ...current }, value);
      return;
    }

    target[key] = value;
  });

  return target;
};

const messageLoaders = import.meta.glob("./messages/*/*.json") as Record<
  string,
  MessageLoader
>;

const getLocaleModulePaths = (locale: LocaleCode): string[] => {
  const prefix = `./messages/${locale}/`;
  return Object.keys(messageLoaders).filter((path) => path.startsWith(prefix));
};

const loadStructuredLocaleMessages = async (locale: LocaleCode): Promise<void> => {
  if (loadedStructuredLocales.has(locale)) return;

  const ongoing = localeLoadTasks.get(locale);
  if (ongoing) {
    await ongoing;
    return;
  }

  const task = (async () => {
    const baseMessages = i18n.global.getLocaleMessage(locale) as MessageNode;
    const merged = { ...baseMessages };
    const modulePaths = getLocaleModulePaths(locale);

    for (const path of modulePaths) {
      const module = await messageLoaders[path]();
      const payload = (module?.default ?? {}) as MessageNode;
      deepMerge(merged, payload);
    }

    i18n.global.setLocaleMessage(locale, merged);
    loadedStructuredLocales.add(locale);
  })().finally(() => {
    localeLoadTasks.delete(locale);
  });

  localeLoadTasks.set(locale, task);
  await task;
};

Object.keys(locales).forEach((key) => {
  const localeCode = key as LocaleCode;
  messages[localeCode] = {
    ...(locales[localeCode].translations as MessageNode),
  };
});

export const i18n = createI18n({
  legacy: false,
  locale: resolveInitialLocale(),
  fallbackLocale: FALLBACK_LOCALE,
  messages,
  globalInjection: true,
  missingWarn: false,
  fallbackWarn: false,
});

export const ensureLocaleMessages = async (rawLocale: unknown): Promise<LocaleCode> => {
  const locale = normalizeLocaleCode(rawLocale);
  const localesToLoad =
    locale === FALLBACK_LOCALE ? [locale] : [FALLBACK_LOCALE, locale];

  for (const item of localesToLoad) {
    await loadStructuredLocaleMessages(item);
  }

  return locale;
};

export default i18n;
