import { promises as fs } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');
const distDir = path.join(projectRoot, 'dist');
const messagesDir = path.join(projectRoot, 'src', 'i18n', 'messages');
const publicDir = path.join(projectRoot, 'public');

const FALLBACK_LOCALE = 'en';
const SITE_NAME = 'CYPHER GAME BUY';
const SUPPORTED_LOCALES = ['en', 'zh-CN', 'zh-TW', 'ja', 'ko', 'th', 'vi', 'fr', 'de'];
const STATIC_SEO_ROUTES = [
  '/',
  '/games',
  '/articles',
  '/recharge',
  '/about',
  '/contact',
  '/customer-service',
  '/recharge-guide',
  '/cg-wiki',
  '/tavern',
  '/novel-story',
  '/plaza',
];
const PRE_RENDER_SEO_START = '<!-- PRE_RENDER_SEO_START -->';
const PRE_RENDER_SEO_END = '<!-- PRE_RENDER_SEO_END -->';

const HREFLANG_MAP = {
  'zh-CN': 'zh-Hans',
  'zh-TW': 'zh-Hant',
};

const DEFAULT_DESCRIPTION =
  'Professional game recharge and news platform with multilingual experience.';
const DEFAULT_KEYWORDS = 'game recharge,game news,topup,multilingual website';

const SEO_ROUTE_BLOCKLIST_PATTERNS = [
  /^\/profile$/i,
  /^\/register$/i,
  /^\/login$/i,
  /^\/forgot-password$/i,
  /^\/password-reset\//i,
  /^\/activate\//i,
  /^\/search$/i,
  /^\/translation-demo$/i,
  /^\/i18n-demo$/i,
  /^\/cors-test$/i,
  /^\/404$/i,
];

const normalizeRoute = (rawRoute) => {
  const route = String(rawRoute || '').trim();
  if (!route || route === '/') return '/';
  const withSlash = route.startsWith('/') ? route : `/${route}`;
  return withSlash.endsWith('/') ? withSlash.slice(0, -1) : withSlash;
};

const resolveRouteTitleKey = (route) => {
  if (route === '/') return 'home';
  if (route === '/games') return 'games';
  if (route.startsWith('/games/')) return 'gameDetail';
  if (route === '/articles') return 'articles';
  if (route.startsWith('/articles/')) return 'articleDetail';
  if (route === '/customer-service') return 'customerService';
  if (route === '/about') return 'about';
  if (route === '/contact') return 'contact';
  if (route === '/recharge') return 'recharge';
  if (route === '/recharge-guide') return 'rechargeGuide';
  if (route === '/cg-wiki') return 'cgWiki';
  if (route === '/tavern') return 'tavern';
  if (route === '/novel-story') return 'novelStory';
  if (route === '/plaza') return 'plaza';
  return 'default';
};

const decodeXmlEntities = (value) =>
  String(value || '')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'")
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>');

const stripLocalePrefix = (pathname, locales) => {
  const normalizedPath = normalizeRoute(pathname);
  if (normalizedPath === '/') return '/';

  const sortedLocales = [...locales].sort((a, b) => b.length - a.length);
  for (const locale of sortedLocales) {
    const localeRoot = `/${locale}`;
    if (normalizedPath === localeRoot) return '/';
    if (normalizedPath.startsWith(`${localeRoot}/`)) {
      return normalizeRoute(normalizedPath.slice(localeRoot.length));
    }
  }

  return normalizedPath;
};

const shouldSkipSeoRoute = (route) => {
  if (!route || !route.startsWith('/')) return true;
  if (route.includes('//')) return true;
  if (/\.(xml|txt|json|js|css|ico|png|jpe?g|webp|svg)$/i.test(route)) return true;
  return SEO_ROUTE_BLOCKLIST_PATTERNS.some((pattern) => pattern.test(route));
};

const collectRoutesFromSitemap = async (locales, siteOrigin) => {
  const routes = new Set();
  const sitemapPath = path.join(publicDir, 'sitemap.xml');

  try {
    const sitemapRaw = await fs.readFile(sitemapPath, 'utf8');
    const locMatches = sitemapRaw.matchAll(/<loc>([\s\S]*?)<\/loc>/gi);

    for (const match of locMatches) {
      const locValue = decodeXmlEntities(match[1]).trim();
      if (!locValue) continue;

      try {
        const url = new URL(locValue, siteOrigin);
        const route = stripLocalePrefix(url.pathname, locales);
        if (!shouldSkipSeoRoute(route)) {
          routes.add(route);
        }
      } catch {
        // Ignore malformed loc entries.
      }
    }
  } catch {
    // Missing sitemap.xml is acceptable; static route fallback still works.
  }

  return routes;
};

const toHreflang = (locale) => HREFLANG_MAP[locale] || locale.toLowerCase();

const escapeHtml = (value) =>
  String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');

const escapeRegExp = (value) => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

const ensureTrailingSlashRemoved = (value) => String(value || '').replace(/\/+$/, '');

const localizedPath = (locale, route) =>
  route === '/' ? `/${locale}` : `/${locale}${route}`;

const buildTitle = (routeTitle) => {
  const title = String(routeTitle || '').trim();
  if (!title || title === SITE_NAME) return SITE_NAME;
  return `${title} | ${SITE_NAME}`;
};

const setHtmlLang = (html, locale) => {
  if (!/<html\b/i.test(html)) return html;
  return html.replace(/<html\b([^>]*)>/i, (_full, attrs) => {
    if (/\blang\s*=\s*["'][^"']*["']/i.test(attrs)) {
      return `<html${attrs.replace(/\blang\s*=\s*["'][^"']*["']/i, `lang="${escapeHtml(locale)}"`)}>`;
    }
    return `<html lang="${escapeHtml(locale)}"${attrs}>`;
  });
};

const setDocumentTitle = (html, title) => {
  const titleTag = `<title>${escapeHtml(title)}</title>`;
  if (/<title>[\s\S]*?<\/title>/i.test(html)) {
    return html.replace(/<title>[\s\S]*?<\/title>/i, titleTag);
  }
  return html.replace('</head>', `  ${titleTag}\n</head>`);
};

const replaceSeoBlock = (html, seoBlock) => {
  const markerRegex = new RegExp(
    `${escapeRegExp(PRE_RENDER_SEO_START)}[\\s\\S]*?${escapeRegExp(PRE_RENDER_SEO_END)}`,
    'm'
  );
  if (markerRegex.test(html)) {
    return html.replace(markerRegex, seoBlock);
  }
  return html.replace('</head>', `${seoBlock}\n</head>`);
};

const buildSeoBlock = ({
  description,
  keywords,
  canonicalUrl,
  alternateLinks,
}) => {
  const lines = [
    PRE_RENDER_SEO_START,
    `    <meta name="description" content="${escapeHtml(description)}" data-i18n-seo-meta="true">`,
    `    <meta name="keywords" content="${escapeHtml(keywords)}" data-i18n-seo-meta="true">`,
    `    <link rel="canonical" href="${escapeHtml(canonicalUrl)}" data-i18n-seo-link="true">`,
    ...alternateLinks.map(
      (link) =>
        `    <link rel="alternate" hreflang="${escapeHtml(link.hreflang)}" href="${escapeHtml(
          link.href
        )}" data-i18n-seo-link="true">`
    ),
    `    ${PRE_RENDER_SEO_END}`,
  ];
  return lines.join('\n');
};

const readJsonFile = async (filePath) => {
  const raw = await fs.readFile(filePath, 'utf8');
  return JSON.parse(raw);
};

const loadLocales = async () => {
  const entries = await fs.readdir(messagesDir, { withFileTypes: true });
  const localesFromFiles = entries
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name);

  const localeSet = new Set([...SUPPORTED_LOCALES, ...localesFromFiles]);
  return Array.from(localeSet).sort((a, b) => {
    const indexA = SUPPORTED_LOCALES.indexOf(a);
    const indexB = SUPPORTED_LOCALES.indexOf(b);
    if (indexA === -1 && indexB === -1) return a.localeCompare(b);
    if (indexA === -1) return 1;
    if (indexB === -1) return -1;
    return indexA - indexB;
  });
};

const loadSeoMessages = async (locales) => {
  const output = {};

  for (const locale of locales) {
    const seoPath = path.join(messagesDir, locale, 'seo.json');
    try {
      const payload = await readJsonFile(seoPath);
      output[locale] = payload?.seo || {};
    } catch {
      output[locale] = {};
    }
  }

  return output;
};

const resolveSeoValue = (seoByLocale, locale) => {
  const fallback = seoByLocale[FALLBACK_LOCALE] || {};
  const current = seoByLocale[locale] || {};
  return {
    defaultDescription: current.defaultDescription || fallback.defaultDescription || DEFAULT_DESCRIPTION,
    defaultKeywords: current.defaultKeywords || fallback.defaultKeywords || DEFAULT_KEYWORDS,
    routeTitles: {
      ...(fallback.routeTitles || {}),
      ...(current.routeTitles || {}),
    },
  };
};

const createPageHtml = ({
  templateHtml,
  locale,
  route,
  locales,
  seoByLocale,
  siteOrigin,
}) => {
  const seoValues = resolveSeoValue(seoByLocale, locale);
  const titleKey = resolveRouteTitleKey(route);
  const routeTitle = seoValues.routeTitles[titleKey] || seoValues.routeTitles.default || SITE_NAME;
  const title = buildTitle(routeTitle);
  const canonicalPath = localizedPath(locale, route);
  const canonicalUrl = `${siteOrigin}${canonicalPath}`;

  const alternateLinks = locales.map((item) => ({
    hreflang: toHreflang(item),
    href: `${siteOrigin}${localizedPath(item, route)}`,
  }));

  alternateLinks.push({
    hreflang: 'x-default',
    href: `${siteOrigin}${localizedPath(FALLBACK_LOCALE, route)}`,
  });

  const seoBlock = buildSeoBlock({
    description: seoValues.defaultDescription,
    keywords: seoValues.defaultKeywords,
    canonicalUrl,
    alternateLinks,
  });

  let html = templateHtml;
  html = setHtmlLang(html, locale);
  html = setDocumentTitle(html, title);
  html = replaceSeoBlock(html, seoBlock);
  return html;
};

const ensureDistExists = async () => {
  try {
    await fs.access(path.join(distDir, 'index.html'));
  } catch {
    throw new Error('dist/index.html not found. Run "vite build" before prerender.');
  }
};

const writeRouteHtml = async (locale, route, html) => {
  const routeDir = route === '/' ? '' : route.replace(/^\//, '');
  const outputDir = path.join(distDir, locale, routeDir);
  const outputFile = path.join(outputDir, 'index.html');

  await fs.mkdir(outputDir, { recursive: true });
  await fs.writeFile(outputFile, html, 'utf8');
};

const run = async () => {
  await ensureDistExists();

  const siteOrigin = ensureTrailingSlashRemoved(
    process.env.SEO_SITE_ORIGIN || process.env.VITE_SITE_ORIGIN || 'https://www.cyphergamebuy.com'
  );
  const locales = await loadLocales();

  if (!locales.includes(FALLBACK_LOCALE)) {
    throw new Error(`fallback locale "${FALLBACK_LOCALE}" is missing in src/i18n/messages`);
  }

  const normalizedRoutes = new Set(STATIC_SEO_ROUTES.map(normalizeRoute));
  const routesFromSitemap = await collectRoutesFromSitemap(locales, siteOrigin);
  for (const route of routesFromSitemap) {
    normalizedRoutes.add(route);
  }

  const routeList = Array.from(normalizedRoutes).filter((route) => !shouldSkipSeoRoute(route));
  const templateHtml = await fs.readFile(path.join(distDir, 'index.html'), 'utf8');
  const seoByLocale = await loadSeoMessages(locales);

  for (const locale of locales) {
    for (const route of routeList) {
      const html = createPageHtml({
        templateHtml,
        locale,
        route,
        locales,
        seoByLocale,
        siteOrigin,
      });
      await writeRouteHtml(locale, route, html);
      process.stdout.write(`prerendered: ${locale}${route}\n`);
    }
  }
};

run().catch((error) => {
  console.error(`[prerender-seo] ${error?.message || error}`);
  process.exit(1);
});
