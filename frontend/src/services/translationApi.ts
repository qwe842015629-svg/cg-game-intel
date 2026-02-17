import { buildApiUrl } from '../api/base'

export interface TranslateRequest {
  text: string
  targetLanguage: string
  sourceLanguage?: string
}

export interface TranslateBatchRequest {
  texts: string[]
  targetLanguage: string
}

export interface TranslateMultiRequest {
  text: string
  targetLanguages: string[]
}

export interface Language {
  code: string
  name: string
  native_name: string
}

export interface TranslationStats {
  available: number
  used: number
  message: string
}

export async function translateText(
  text: string,
  targetLanguage: string,
  sourceLanguage?: string
): Promise<string> {
  try {
    const response = await fetch(buildApiUrl('/translate/'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text,
        targetLanguage,
        sourceLanguage,
      }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || '翻译失败')
    }

    const data = await response.json()
    return data.translatedText
  } catch (error) {
    console.error('Translation error:', error)
    throw error
  }
}

export async function translateBatch(
  texts: string[],
  targetLanguage: string
): Promise<string[]> {
  try {
    const response = await fetch(buildApiUrl('/translate/batch/'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        texts,
        targetLanguage,
      }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || '批量翻译失败')
    }

    const data = await response.json()
    return data.translatedTexts
  } catch (error) {
    console.error('Batch translation error:', error)
    throw error
  }
}

export async function translateMultiLanguage(
  text: string,
  targetLanguages: string[]
): Promise<Record<string, string>> {
  try {
    const response = await fetch(buildApiUrl('/translate/multi/'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text,
        targetLanguages,
      }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || '多语言翻译失败')
    }

    const data = await response.json()
    return data.translations
  } catch (error) {
    console.error('Multi-language translation error:', error)
    throw error
  }
}

export async function getSupportedLanguages(): Promise<Language[]> {
  try {
    const response = await fetch(buildApiUrl('/translate/languages/'))

    if (!response.ok) {
      throw new Error('获取语言列表失败')
    }

    const data = await response.json()
    return data.languages
  } catch (error) {
    console.error('Get languages error:', error)
    throw error
  }
}

export async function getTranslationStats(): Promise<TranslationStats> {
  try {
    const response = await fetch(buildApiUrl('/translate/stats/'))

    if (!response.ok) {
      throw new Error('获取统计信息失败')
    }

    const data = await response.json()
    return {
      available: data.available,
      used: data.used,
      message: data.message,
    }
  } catch (error) {
    console.error('Get stats error:', error)
    throw error
  }
}

export async function autoTranslateLocales(
  sourceTexts: Record<string, string>,
  targetLanguage: string
): Promise<Record<string, string>> {
  const keys = Object.keys(sourceTexts)
  const values = Object.values(sourceTexts)

  try {
    const translatedValues = await translateBatch(values, targetLanguage)

    const result: Record<string, string> = {}
    keys.forEach((key, index) => {
      result[key] = translatedValues[index]
    })

    return result
  } catch (error) {
    console.error('Auto translate locales error:', error)
    throw error
  }
}
