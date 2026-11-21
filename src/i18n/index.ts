import { computed, ref, watchEffect } from 'vue'
import { matchesSearch } from '../data/catalog'
import ui from './ui.json'
import offsite from './offsite.json'
import catalog from './catalog.json'
import captions from './captions.json'

type Locale = 'zh-CN' | 'en'
type Text = string | number | null | undefined
const storageKey = 'puyuan.language'
const dictionaries: Record<Locale, Record<string, string>> = {
  en: { ...ui, ...offsite, ...catalog },
  'zh-CN': captions,
}

function initialLocale(): Locale {
  try {
    return localStorage.getItem(storageKey) === 'en' ? 'en' : 'zh-CN'
  } catch {
    return 'zh-CN'
  }
}
export const locale = ref<Locale>(initialLocale())
export const languageAction = computed(() =>
  locale.value === 'en' ? 'Switch to Chinese · 中文' : '切换到英文 · English',
)

export function toggleLanguage() {
  locale.value = locale.value === 'en' ? 'zh-CN' : 'en'
  try {
    localStorage.setItem(storageKey, locale.value)
  } catch {
    return
  }
}

function lookup(source: Text, language: Locale): string {
  const key = String(source ?? '')
  return Object.hasOwn(dictionaries[language], key) ? dictionaries[language][key]! : key
}

export function t(source: Text, values?: Record<string, Text>): string {
  const message = lookup(source, locale.value)
  return values
    ? message.replace(/\{(\w+)\}/g, (token, key: string) =>
        Object.hasOwn(values, key) ? lookup(values[key], locale.value) : token,
      )
    : message
}

export function matchesBilingual(query: string, ...fields: string[]) {
  return matchesSearch(query, ...fields, ...fields.map((field) => lookup(field, 'en')))
}

export function syncDocumentLanguage() {
  watchEffect(() => {
    document.documentElement.lang = locale.value
    document.title = t('濮院漫游 · 一入濮院，便是江南')
    document
      .querySelector('meta[name="description"]')
      ?.setAttribute('content', t('循水巷，过石桥，听一曲婉转。濮院古镇地图与游园体验。'))
  })
}
