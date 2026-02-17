export type MotionMode = 'standard' | 'lite' | 'reduced'

const MOTION_MODE_ATTR = 'data-motion-mode'
const MOTION_MODE_EVENT = 'app-motion-mode-change'

const supportsMatchMedia = () => typeof window !== 'undefined' && typeof window.matchMedia === 'function'

const prefersReducedMotion = () =>
  supportsMatchMedia() && window.matchMedia('(prefers-reduced-motion: reduce)').matches

const prefersReducedData = () =>
  supportsMatchMedia() && window.matchMedia('(prefers-reduced-data: reduce)').matches

const estimateLowPowerDevice = () => {
  if (typeof navigator === 'undefined') return false

  let score = 0
  const nav = navigator as Navigator & {
    connection?: { saveData?: boolean }
    deviceMemory?: number
  }

  if (nav.connection?.saveData) score += 2
  if (typeof nav.deviceMemory === 'number' && nav.deviceMemory <= 4) score += 1
  if (typeof nav.hardwareConcurrency === 'number' && nav.hardwareConcurrency <= 4) score += 1
  if (prefersReducedData()) score += 1

  return score >= 2
}

export const detectMotionMode = (): MotionMode => {
  if (prefersReducedMotion()) return 'reduced'
  if (estimateLowPowerDevice()) return 'lite'
  return 'standard'
}

const dispatchModeChange = (mode: MotionMode) => {
  if (typeof window === 'undefined') return
  window.dispatchEvent(new CustomEvent(MOTION_MODE_EVENT, { detail: { mode } }))
}

const applyMotionMode = (mode: MotionMode) => {
  if (typeof document === 'undefined') return

  const root = document.documentElement
  const previous = root.getAttribute(MOTION_MODE_ATTR)

  if (previous === mode) return
  root.setAttribute(MOTION_MODE_ATTR, mode)
  dispatchModeChange(mode)
}

export const getCurrentMotionMode = (): MotionMode => {
  if (typeof document !== 'undefined') {
    const mode = document.documentElement.getAttribute(MOTION_MODE_ATTR)
    if (mode === 'standard' || mode === 'lite' || mode === 'reduced') {
      return mode
    }
  }
  return detectMotionMode()
}

export const isLiteMotionMode = () => getCurrentMotionMode() === 'lite'

export const isReducedMotionMode = () => getCurrentMotionMode() === 'reduced'

export const MOTION_MODE_CHANGE_EVENT = MOTION_MODE_EVENT

export const initMotionMode = () => {
  if (!supportsMatchMedia()) return () => {}

  const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  const reducedDataQuery = window.matchMedia('(prefers-reduced-data: reduce)')
  const addQueryListener = (query: MediaQueryList, listener: () => void) => {
    if (typeof query.addEventListener === 'function') {
      query.addEventListener('change', listener)
      return
    }
    query.addListener(listener)
  }
  const removeQueryListener = (query: MediaQueryList, listener: () => void) => {
    if (typeof query.removeEventListener === 'function') {
      query.removeEventListener('change', listener)
      return
    }
    query.removeListener(listener)
  }

  const update = () => {
    applyMotionMode(detectMotionMode())
  }

  update()

  const onChange = () => update()
  const onVisibility = () => update()

  addQueryListener(reducedMotionQuery, onChange)
  addQueryListener(reducedDataQuery, onChange)
  document.addEventListener('visibilitychange', onVisibility)

  return () => {
    removeQueryListener(reducedMotionQuery, onChange)
    removeQueryListener(reducedDataQuery, onChange)
    document.removeEventListener('visibilitychange', onVisibility)
  }
}
