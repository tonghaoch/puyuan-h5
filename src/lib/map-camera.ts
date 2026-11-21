export interface Camera {
  x: number
  y: number
  scale: number
}
export const SCENE = { width: 1520, height: 1240 }
export const MEADOW_MARGIN = 1600
export const ZOOM_STEP = 1.25
export function zoomRange(width: number, height: number) {
  const initial = Math.max(0.22, Math.min(width / 1120, (height - 160) / 1040))
  return { initial, min: initial / ZOOM_STEP, max: initial * 4 }
}
export function cameraBounds() {
  const margin = MEADOW_MARGIN
  return { left: -margin, top: -margin, right: SCENE.width + margin, bottom: SCENE.height + margin }
}
function clampAxis(position: number, viewport: number, start: number, end: number, scale: number) {
  const min = viewport - end * scale
  const max = -start * scale
  return min > max ? (min + max) / 2 : Math.max(min, Math.min(max, position))
}
export function clampCamera(camera: Camera, width: number, height: number): Camera {
  const { min, max } = zoomRange(width, height)
  const scale = Math.max(min, Math.min(max, camera.scale))
  const bounds = cameraBounds()
  return {
    scale,
    x: clampAxis(camera.x, width, bounds.left, bounds.right, scale),
    y: clampAxis(camera.y, height, bounds.top, bounds.bottom, scale),
  }
}
export function zoomAt(
  camera: Camera,
  factor: number,
  x: number,
  y: number,
  width: number,
  height: number,
): Camera {
  const { min, max } = zoomRange(width, height)
  const scale = Math.max(min, Math.min(max, camera.scale * factor))
  const ratio = scale / camera.scale
  return clampCamera(
    { scale, x: x - (x - camera.x) * ratio, y: y - (y - camera.y) * ratio },
    width,
    height,
  )
}
export function visibleScene(camera: Camera, width: number, height: number, overscan = 100) {
  return {
    left: -camera.x / camera.scale - overscan,
    top: -camera.y / camera.scale - overscan,
    right: (width - camera.x) / camera.scale + overscan,
    bottom: (height - camera.y) / camera.scale + overscan,
  }
}
