import type { DirectiveBinding, ObjectDirective } from 'vue'
import { isLiteMotionMode, isReducedMotionMode } from '../utils/motionMode'

type MotionBinding =
  | number
  | {
      delay?: number
      x?: number
      y?: number
      once?: boolean
      threshold?: number
      rootMargin?: string
    }

interface MotionOptions {
  delay: number
  x: number
  y: number
  once: boolean
  threshold: number
  rootMargin: string
}

const defaultOptions: MotionOptions = {
  delay: 0,
  x: 0,
  y: 18,
  once: true,
  threshold: 0.12,
  rootMargin: '0px 0px -8% 0px',
}

const observerMap = new WeakMap<HTMLElement, IntersectionObserver>()
const optionsKeyMap = new WeakMap<HTMLElement, string>()

const prefersReducedMotion = () =>
  typeof window !== 'undefined' &&
  typeof window.matchMedia === 'function' &&
  window.matchMedia('(prefers-reduced-motion: reduce)').matches

const resolveOptions = (binding: DirectiveBinding<MotionBinding>): MotionOptions => {
  if (typeof binding.value === 'number') {
    return {
      ...defaultOptions,
      delay: Math.max(0, binding.value),
    }
  }

  const raw = binding.value || {}
  return {
    delay: Math.max(0, Number(raw.delay ?? defaultOptions.delay)),
    x: Number(raw.x ?? defaultOptions.x),
    y: Number(raw.y ?? defaultOptions.y),
    once: raw.once ?? defaultOptions.once,
    threshold: Number(raw.threshold ?? defaultOptions.threshold),
    rootMargin: String(raw.rootMargin ?? defaultOptions.rootMargin),
  }
}

const unobserve = (el: HTMLElement) => {
  const observer = observerMap.get(el)
  if (observer) {
    observer.unobserve(el)
    observer.disconnect()
    observerMap.delete(el)
  }
}

const applyMotion = (el: HTMLElement, options: MotionOptions) => {
  const liteMode = isLiteMotionMode()
  const tunedDelay = liteMode ? Math.min(options.delay, 120) : options.delay
  const tunedX = liteMode ? options.x * 0.6 : options.x
  const tunedY = liteMode ? options.y * 0.6 : options.y

  el.style.setProperty('--motion-delay', `${tunedDelay}ms`)
  el.style.setProperty('--motion-enter-x', `${tunedX}px`)
  el.style.setProperty('--motion-enter-y', `${tunedY}px`)
  el.classList.add('motion-reveal')
  el.classList.toggle('motion-lite', liteMode)

  if (prefersReducedMotion() || isReducedMotionMode()) {
    el.classList.add('motion-visible')
    return
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          el.classList.add('motion-visible')
          if (options.once) {
            unobserve(el)
          }
        } else if (!options.once) {
          el.classList.remove('motion-visible')
        }
      })
    },
    {
      threshold: options.threshold,
      rootMargin: options.rootMargin,
    }
  )

  observer.observe(el)
  observerMap.set(el, observer)
}

const buildOptionsKey = (options: MotionOptions) =>
  `${options.delay}|${options.x}|${options.y}|${options.once ? 1 : 0}|${options.threshold}|${options.rootMargin}`

export const motionRevealDirective: ObjectDirective<HTMLElement, MotionBinding> = {
  mounted(el, binding) {
    const options = resolveOptions(binding)
    optionsKeyMap.set(el, buildOptionsKey(options))
    applyMotion(el, options)
  },
  updated(el, binding) {
    const nextOptions = resolveOptions(binding)
    const nextKey = buildOptionsKey(nextOptions)
    const prevKey = optionsKeyMap.get(el)
    if (prevKey === nextKey) {
      return
    }

    optionsKeyMap.set(el, nextKey)
    unobserve(el)
    el.classList.remove('motion-visible')
    applyMotion(el, nextOptions)
  },
  unmounted(el) {
    unobserve(el)
    optionsKeyMap.delete(el)
  },
}
