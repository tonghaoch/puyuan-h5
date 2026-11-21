import { computed, ref, watch } from 'vue'

export const walkPreviewEnabled =
  (import.meta.env.DEV || import.meta.env.MODE === 'location-preview') &&
  new URLSearchParams(window.location.search).get('preview') === 'walk'

export function useWalkPreview(motion: () => boolean) {
  const path = [
    [852, 752],
    [926, 726],
    [994, 706],
    [1074, 685],
  ] as const
  const stepsPerSegment = 6
  const last = (path.length - 1) * stepsPerSegment
  const step = ref(0)
  const paused = ref(false)
  const point = computed(() => {
    const along = last - Math.abs(last - step.value)
    const segment = Math.min(path.length - 2, Math.floor(along / stepsPerSegment))
    const fraction = along / stepsPerSegment - segment
    const from = path[segment]!,
      to = path[segment + 1]!
    return { x: from[0] + (to[0] - from[0]) * fraction, y: from[1] + (to[1] - from[1]) * fraction }
  })
  function advance() {
    step.value = (step.value + 1) % (last * 2)
  }
  watch(
    () => motion() && !paused.value,
    (running, _, cleanup) => {
      if (!running) return
      const timer = window.setInterval(advance, 900)
      cleanup(() => window.clearInterval(timer))
    },
    { immediate: true },
  )
  const action = computed(() =>
    !motion() ? '模拟走一步' : paused.value ? '继续模拟步行' : '暂停模拟步行',
  )
  function toggle() {
    if (motion()) paused.value = !paused.value
    else advance()
  }
  return { point, action, toggle }
}
