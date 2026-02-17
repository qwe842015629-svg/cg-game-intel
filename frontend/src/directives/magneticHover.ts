import type { DirectiveBinding, ObjectDirective } from 'vue'
import { isLiteMotionMode } from '../utils/motionMode'

type MagneticBinding =
  | number
  | {
      strength?: number
      max?: number
    }

interface MagneticOptions {
  strength: number
  max: number
}

const defaultOptions: MagneticOptions = {
  strength: 0.12,
  max: 8,
}

const cleanupMap = new WeakMap<HTMLElement, () => void>()

const prefersReducedMotion = () =>
  typeof window !== 'undefined' &&
  typeof window.matchMedia === 'function' &&
  window.matchMedia('(prefers-reduced-motion: reduce)').matches

const supportsFinePointer = () =>
  typeof window !== 'undefined' &&
  typeof window.matchMedia === 'function' &&
  window.matchMedia('(hover: hover) and (pointer: fine)').matches

const resolveOptions = (binding: DirectiveBinding<MagneticBinding>): MagneticOptions => {
  if (typeof binding.value === 'number') {
    return {
      ...defaultOptions,
      max: Math.max(3, Number(binding.value)),
    }
  }

  const raw = binding.value || {}
  return {
    strength: Number(raw.strength ?? defaultOptions.strength),
    max: Math.max(3, Number(raw.max ?? defaultOptions.max)),
  }
}

export const magneticHoverDirective: ObjectDirective<HTMLElement, MagneticBinding> = {
  mounted(el, binding) {
    if (prefersReducedMotion() || !supportsFinePointer()) {
      return
    }

    const options = resolveOptions(binding)
    const liteMode = isLiteMotionMode()
    const tunedStrength = liteMode ? options.strength * 0.58 : options.strength
    const tunedMax = liteMode ? Math.min(8, options.max * 0.62) : options.max
    const follow = liteMode ? 0.2 : 0.16
    const settleEpsilon = 0.05
    const centerDeadzone = 4.5

    el.classList.add('magnetic-hover')
    el.classList.toggle('magnetic-lite', liteMode)

    let currentX = 0
    let currentY = 0
    let targetX = 0
    let targetY = 0
    let rafId: number | null = null
    let hovering = false

    const applyTranslate = (x: number, y: number) => {
      ;(el.style as CSSStyleDeclaration & { translate?: string }).translate = `${x.toFixed(2)}px ${y.toFixed(2)}px`
    }

    const runFrame = () => {
      currentX += (targetX - currentX) * follow
      currentY += (targetY - currentY) * follow

      if (Math.abs(targetX - currentX) < settleEpsilon) currentX = targetX
      if (Math.abs(targetY - currentY) < settleEpsilon) currentY = targetY

      applyTranslate(currentX, currentY)

      const settled = Math.abs(targetX - currentX) < settleEpsilon && Math.abs(targetY - currentY) < settleEpsilon
      if (settled && !hovering) {
        rafId = null
        return
      }

      rafId = window.requestAnimationFrame(runFrame)
    }

    const ensureAnimation = () => {
      if (rafId !== null) return
      rafId = window.requestAnimationFrame(runFrame)
    }

    const onMove = (event: MouseEvent) => {
      hovering = true
      const rect = el.getBoundingClientRect()
      const centerX = rect.left + rect.width / 2
      const centerY = rect.top + rect.height / 2
      const offsetX = event.clientX - centerX
      const offsetY = event.clientY - centerY

      const inDeadzone = Math.abs(offsetX) < centerDeadzone && Math.abs(offsetY) < centerDeadzone
      const nextX = inDeadzone ? 0 : Math.max(-tunedMax, Math.min(tunedMax, offsetX * tunedStrength))
      const nextY = inDeadzone ? 0 : Math.max(-tunedMax, Math.min(tunedMax, offsetY * tunedStrength))

      if (Math.abs(nextX - targetX) < 0.08 && Math.abs(nextY - targetY) < 0.08) {
        return
      }

      targetX = nextX
      targetY = nextY
      ensureAnimation()
    }

    const onLeave = () => {
      hovering = false
      targetX = 0
      targetY = 0
      ensureAnimation()
    }

    el.addEventListener('mousemove', onMove)
    el.addEventListener('mouseleave', onLeave)

    cleanupMap.set(el, () => {
      el.removeEventListener('mousemove', onMove)
      el.removeEventListener('mouseleave', onLeave)
      if (rafId !== null) {
        window.cancelAnimationFrame(rafId)
        rafId = null
      }
      ;(el.style as CSSStyleDeclaration & { translate?: string }).translate = '0 0'
      el.classList.remove('magnetic-lite')
    })
  },
  unmounted(el) {
    const cleanup = cleanupMap.get(el)
    if (cleanup) {
      cleanup()
      cleanupMap.delete(el)
    }
  },
}
