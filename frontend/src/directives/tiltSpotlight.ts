import type { DirectiveBinding, ObjectDirective } from 'vue'
import { isLiteMotionMode } from '../utils/motionMode'

type TiltBinding =
  | number
  | {
      max?: number
      scale?: number
      perspective?: number
    }

interface TiltOptions {
  max: number
  scale: number
  perspective: number
}

const defaultOptions: TiltOptions = {
  max: 3.2,
  scale: 1.004,
  perspective: 900,
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

const resolveOptions = (binding: DirectiveBinding<TiltBinding>): TiltOptions => {
  if (typeof binding.value === 'number') {
    return {
      ...defaultOptions,
      max: Math.max(2, Number(binding.value)),
    }
  }

  const raw = binding.value || {}
  return {
    max: Math.max(2, Number(raw.max ?? defaultOptions.max)),
    scale: Number(raw.scale ?? defaultOptions.scale),
    perspective: Math.max(500, Number(raw.perspective ?? defaultOptions.perspective)),
  }
}

const setVars = (el: HTMLElement, options: TiltOptions, rx: number, ry: number, scale: number, spotX: number, spotY: number) => {
  el.style.setProperty('--tilt-rx', `${rx.toFixed(2)}deg`)
  el.style.setProperty('--tilt-ry', `${ry.toFixed(2)}deg`)
  el.style.setProperty('--tilt-scale', `${scale}`)
  el.style.setProperty('--tilt-perspective', `${options.perspective}px`)
  el.style.setProperty('--spot-x', `${spotX.toFixed(1)}%`)
  el.style.setProperty('--spot-y', `${spotY.toFixed(1)}%`)
}

export const tiltSpotlightDirective: ObjectDirective<HTMLElement, TiltBinding> = {
  mounted(el, binding) {
    if (prefersReducedMotion() || !supportsFinePointer() || isLiteMotionMode()) return

    const options = resolveOptions(binding)
    const follow = 0.16
    const settleEpsilon = 0.035
    const centerDeadzone = 0.07

    el.classList.add('tilt-interactive')
    setVars(el, options, 0, 0, 1, 50, 50)

    let targetRx = 0
    let targetRy = 0
    let targetSpotX = 50
    let targetSpotY = 50

    let currentRx = 0
    let currentRy = 0
    let currentSpotX = 50
    let currentSpotY = 50

    let hovering = false
    let rafId: number | null = null

    const runFrame = () => {
      currentRx += (targetRx - currentRx) * follow
      currentRy += (targetRy - currentRy) * follow
      currentSpotX += (targetSpotX - currentSpotX) * follow
      currentSpotY += (targetSpotY - currentSpotY) * follow

      if (Math.abs(targetRx - currentRx) < settleEpsilon) currentRx = targetRx
      if (Math.abs(targetRy - currentRy) < settleEpsilon) currentRy = targetRy
      if (Math.abs(targetSpotX - currentSpotX) < settleEpsilon * 10) currentSpotX = targetSpotX
      if (Math.abs(targetSpotY - currentSpotY) < settleEpsilon * 10) currentSpotY = targetSpotY

      const scale = hovering ? options.scale : 1
      setVars(el, options, currentRx, currentRy, scale, currentSpotX, currentSpotY)

      const settled =
        Math.abs(targetRx - currentRx) < settleEpsilon &&
        Math.abs(targetRy - currentRy) < settleEpsilon &&
        Math.abs(targetSpotX - currentSpotX) < settleEpsilon * 10 &&
        Math.abs(targetSpotY - currentSpotY) < settleEpsilon * 10

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
      const rect = el.getBoundingClientRect()
      const px = (event.clientX - rect.left) / rect.width
      const py = (event.clientY - rect.top) / rect.height

      let nx = px * 2 - 1
      let ny = py * 2 - 1
      if (Math.abs(nx) < centerDeadzone) nx = 0
      if (Math.abs(ny) < centerDeadzone) ny = 0

      targetRy = nx * options.max
      targetRx = -ny * options.max
      targetSpotX = px * 100
      targetSpotY = py * 100

      ensureAnimation()
    }

    const onEnter = () => {
      hovering = true
      el.classList.add('tilt-active')
      ensureAnimation()
    }

    const onLeave = () => {
      hovering = false
      el.classList.remove('tilt-active')
      targetRx = 0
      targetRy = 0
      targetSpotX = 50
      targetSpotY = 50
      ensureAnimation()
    }

    el.addEventListener('mousemove', onMove)
    el.addEventListener('mouseenter', onEnter)
    el.addEventListener('mouseleave', onLeave)

    cleanupMap.set(el, () => {
      el.removeEventListener('mousemove', onMove)
      el.removeEventListener('mouseenter', onEnter)
      el.removeEventListener('mouseleave', onLeave)
      if (rafId !== null) {
        window.cancelAnimationFrame(rafId)
        rafId = null
      }
      el.classList.remove('tilt-interactive', 'tilt-active')
      setVars(el, options, 0, 0, 1, 50, 50)
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
