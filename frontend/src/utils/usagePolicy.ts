export const USAGE_POLICY_TITLE = 'CypherGameBuy使用规范'
export const USAGE_POLICY_TXT_URL = '/policy/CypherGameBuy使用规范.txt'
export const USAGE_POLICY_OPEN_EVENT = 'cypher-usage-policy:open'
const USAGE_POLICY_TITLE_MAP: Record<string, string> = {
  'zh-CN': 'CypherGameBuy使用规范',
  'zh-TW': 'CypherGameBuy使用規範',
  en: 'CypherGameBuy Usage Policy',
  ja: 'CypherGameBuy利用規範',
  ko: 'CypherGameBuy 이용 규정',
  th: 'นโยบายการใช้งาน CypherGameBuy',
  vi: 'Quy định sử dụng CypherGameBuy',
  fr: "Règles d'utilisation de CypherGameBuy",
  de: 'Nutzungsrichtlinie für CypherGameBuy',
}
const USAGE_POLICY_TXT_URL_MAP: Record<string, string> = {
  'zh-CN': '/policy/CypherGameBuy使用规范.txt',
  'zh-TW': '/policy/cyphergamebuy-usage-policy.zh-TW.txt',
  en: '/policy/cyphergamebuy-usage-policy.en.txt',
  ja: '/policy/cyphergamebuy-usage-policy.ja.txt',
  ko: '/policy/cyphergamebuy-usage-policy.ko.txt',
  th: '/policy/cyphergamebuy-usage-policy.th.txt',
  vi: '/policy/cyphergamebuy-usage-policy.vi.txt',
  fr: '/policy/cyphergamebuy-usage-policy.fr.txt',
  de: '/policy/cyphergamebuy-usage-policy.de.txt',
}

const normalizeUsagePolicyLocale = (locale?: string): string => {
  const raw = String(locale || '').trim().toLowerCase()
  if (!raw) return 'zh-CN'
  if (raw.startsWith('zh')) {
    if (raw.includes('tw') || raw.includes('hk') || raw.includes('hant')) return 'zh-TW'
    return 'zh-CN'
  }
  if (raw.startsWith('en')) return 'en'
  if (raw.startsWith('ja')) return 'ja'
  if (raw.startsWith('ko')) return 'ko'
  if (raw.startsWith('th')) return 'th'
  if (raw.startsWith('vi')) return 'vi'
  if (raw.startsWith('fr')) return 'fr'
  if (raw.startsWith('de')) return 'de'
  return 'zh-CN'
}

export const resolveUsagePolicyTitle = (locale?: string): string => {
  const normalizedLocale = normalizeUsagePolicyLocale(locale)
  return USAGE_POLICY_TITLE_MAP[normalizedLocale] || USAGE_POLICY_TITLE
}

export const resolveUsagePolicyTxtUrl = (locale?: string): string => {
  const normalizedLocale = normalizeUsagePolicyLocale(locale)
  return USAGE_POLICY_TXT_URL_MAP[normalizedLocale] || USAGE_POLICY_TXT_URL
}

export type UsagePolicyScene = 'ai_generation' | 'publish' | 'chat' | 'share' | 'generic'

export interface UsagePolicyViolation {
  scene: UsagePolicyScene
  category: string
  reason: string
  keyword: string
  excerpt: string
}

export class UsagePolicyViolationError extends Error {
  violation: UsagePolicyViolation

  constructor(violation: UsagePolicyViolation) {
    super(buildViolationMessage(violation))
    this.name = 'UsagePolicyViolationError'
    this.violation = violation
  }
}

type UsagePolicyRuleGroup = {
  category: string
  reason: string
  keywords: string[]
  regexes?: RegExp[]
}

const SCENE_LABEL_MAP: Record<UsagePolicyScene, string> = {
  ai_generation: 'AI生成',
  publish: '发布内容',
  chat: '聊天内容',
  share: '分享内容',
  generic: '提交内容',
}

const USAGE_POLICY_RULES: UsagePolicyRuleGroup[] = [
  {
    category: '国家与公共安全',
    reason: '涉及危害国家安全或公共安全内容',
    keywords: [
      '颠覆国家政权',
      '分裂国家',
      '恐怖袭击',
      '制作炸弹',
      '爆炸物教程',
      '枪支弹药交易',
      'extremist attack',
      'bomb making guide',
      'terror attack',
    ],
    regexes: [
      /\b(?:buy|sell|trade)\s+(?:guns?|firearms?|explosives?)\b/i,
      /\b(?:how to|guide to)\s+(?:make|build)\s+(?:a\s+)?bomb\b/i,
    ],
  },
  {
    category: '色情低俗',
    reason: '涉及色情、淫秽或未成年人不当性内容',
    keywords: [
      '淫秽',
      '色情',
      '软色情',
      '裸聊',
      '约炮',
      '性交易',
      '未成年色情',
      'child porn',
      'sexual service',
      'explicit sexual content',
    ],
    regexes: [/\b(?:escort|paid sex|pornographic)\b/i],
  },
  {
    category: '暴力与自伤',
    reason: '涉及暴力伤害、自残自杀或教唆犯罪内容',
    keywords: [
      '自杀教程',
      '教唆自杀',
      '自残教程',
      '杀人教程',
      '投毒方法',
      '报复社会',
      'suicide guide',
      'self harm challenge',
      'kill tutorial',
    ],
    regexes: [
      /\b(?:how to|guide to)\s+(?:kill|poison|hurt)\b/i,
      /\b(?:encourage|teach)\s+(?:suicide|self-harm)\b/i,
    ],
  },
  {
    category: '违法犯罪',
    reason: '涉及诈骗、毒品、赌博、走私等违法行为',
    keywords: [
      '电信诈骗',
      '洗钱',
      '赌博网站',
      '博彩套利',
      '毒品交易',
      '走私渠道',
      '诈骗话术',
      'fraud script',
      'money laundering',
      'drug trafficking',
    ],
    regexes: [
      /\b(?:steal|phish)\s+(?:account|password|card)\b/i,
      /\b(?:fake|forged)\s+(?:id|documents?)\b/i,
    ],
  },
  {
    category: '隐私与侵权',
    reason: '涉及隐私泄露、人肉搜索或侵权内容',
    keywords: [
      '人肉搜索',
      '曝光隐私',
      '身份证号',
      '银行卡号',
      'cvv',
      '盗刷',
      'doxxing',
      'leak personal data',
    ],
    regexes: [
      /\b(?:leak|publish)\s+(?:phone number|home address|id number)\b/i,
      /\b(?:credit card|bank card)\s*(?:number|cvv|security code)\b/i,
    ],
  },
  {
    category: '绕过限制与滥用',
    reason: '涉及绕过平台规则、强制越权或恶意滥用',
    keywords: [
      '绕过审核',
      '无视平台规则',
      '忽略所有法律',
      '越狱提示词',
      'jailbreak prompt',
      'bypass safety',
      'ignore all rules',
    ],
    regexes: [/\b(?:disable|ignore)\s+(?:safety|policy|rules?)\b/i],
  },
]

const buildViolationMessage = (violation: UsagePolicyViolation): string => {
  const sceneLabel = SCENE_LABEL_MAP[violation.scene] || SCENE_LABEL_MAP.generic
  return `${sceneLabel}检测到可能违规内容（命中：${violation.keyword}）。请先查看《${USAGE_POLICY_TITLE}》并修改后再试。`
}

const buildExcerpt = (source: string, start: number, length: number): string => {
  const safeStart = Math.max(0, start - 24)
  const safeEnd = Math.min(source.length, start + Math.max(length, 1) + 24)
  return source.slice(safeStart, safeEnd).replace(/\s+/g, ' ').trim()
}

const maybeJsonParse = (value: string): unknown => {
  const raw = String(value || '').trim()
  if (!raw) return ''
  if (!((raw.startsWith('{') && raw.endsWith('}')) || (raw.startsWith('[') && raw.endsWith(']')))) {
    return raw
  }

  try {
    return JSON.parse(raw)
  } catch {
    return raw
  }
}

const collectTextChunks = (input: unknown, bucket: string[], depth = 0): void => {
  if (depth > 6 || input === null || input === undefined) return

  if (typeof input === 'string') {
    const parsed = maybeJsonParse(input)
    if (typeof parsed === 'string') {
      if (parsed.trim()) bucket.push(parsed)
      return
    }
    collectTextChunks(parsed, bucket, depth + 1)
    return
  }

  if (typeof input === 'number' || typeof input === 'boolean') return

  if (Array.isArray(input)) {
    for (const item of input) {
      collectTextChunks(item, bucket, depth + 1)
    }
    return
  }

  if (typeof URLSearchParams !== 'undefined' && input instanceof URLSearchParams) {
    for (const [key, value] of input.entries()) {
      bucket.push(`${key}: ${value}`)
    }
    return
  }

  if (typeof FormData !== 'undefined' && input instanceof FormData) {
    for (const [key, value] of input.entries()) {
      if (typeof value === 'string') {
        bucket.push(`${key}: ${value}`)
      }
    }
    return
  }

  if (typeof Blob !== 'undefined' && input instanceof Blob) return
  if (input instanceof Date) return

  if (typeof input === 'object') {
    for (const [key, value] of Object.entries(input as Record<string, unknown>)) {
      if (typeof value === 'string') {
        bucket.push(`${key}: ${value}`)
      } else {
        collectTextChunks(value, bucket, depth + 1)
      }
    }
  }
}

const detectViolationFromText = (
  sourceText: string,
  scene: UsagePolicyScene,
): UsagePolicyViolation | null => {
  const raw = String(sourceText || '').trim()
  if (!raw) return null

  const normalized = raw.toLowerCase()

  for (const ruleGroup of USAGE_POLICY_RULES) {
    for (const keyword of ruleGroup.keywords) {
      const lowered = keyword.toLowerCase()
      const index = normalized.indexOf(lowered)
      if (index === -1) continue

      return {
        scene,
        category: ruleGroup.category,
        reason: ruleGroup.reason,
        keyword,
        excerpt: buildExcerpt(raw, index, keyword.length),
      }
    }

    for (const regex of ruleGroup.regexes || []) {
      const match = raw.match(regex)
      if (!match || typeof match.index !== 'number') continue
      const keyword = String(match[0] || regex.source)
      return {
        scene,
        category: ruleGroup.category,
        reason: ruleGroup.reason,
        keyword,
        excerpt: buildExcerpt(raw, match.index, keyword.length),
      }
    }
  }

  return null
}

const toPolicyScanText = (input: unknown): string => {
  const bucket: string[] = []
  collectTextChunks(input, bucket)
  return bucket.join('\n').trim().slice(0, 12000)
}

export const findUsagePolicyViolation = (
  input: unknown,
  scene: UsagePolicyScene = 'generic',
): UsagePolicyViolation | null => {
  const scanText = toPolicyScanText(input)
  if (!scanText) return null
  return detectViolationFromText(scanText, scene)
}

export const guardUsagePolicyContent = (
  input: unknown,
  scene: UsagePolicyScene = 'generic',
): void => {
  const violation = findUsagePolicyViolation(input, scene)
  if (!violation) return
  throw new UsagePolicyViolationError(violation)
}

export const isUsagePolicyViolationError = (error: unknown): error is UsagePolicyViolationError => {
  if (!error || typeof error !== 'object') return false
  if (error instanceof UsagePolicyViolationError) return true
  return (error as { name?: string }).name === 'UsagePolicyViolationError'
}

export const openUsagePolicyDialog = (reason?: string): void => {
  if (typeof window === 'undefined') return
  window.dispatchEvent(
    new CustomEvent(USAGE_POLICY_OPEN_EVENT, {
      detail: {
        reason: String(reason || '').trim(),
      },
    }),
  )
}
