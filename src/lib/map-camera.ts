export interface Camera {
  x: number
  y: number
  scale: number
}
export type CameraWorld = 'illustration' | 'geographic'
// SCENE remains the original image/geo frame. Exterior space must never shift its coordinates.
export const SCENE = { width: 1520, height: 1240 }
export const MEADOW_MARGIN = 1600
export const MIN_SCALE = 0.22
export const MAX_SCALE = 3
export function cameraBounds(world: CameraWorld) {
  const margin = world === 'illustration' ? MEADOW_MARGIN : 90
  return { left: -margin, top: -margin, right: SCENE.width + margin, bottom: SCENE.height + margin }
}
function clampAxis(position: number, viewport: number, start: number, end: number, scale: number) {
  const min = viewport - end * scale
  const max = -start * scale
  return min > max ? (min + max) / 2 : Math.max(min, Math.min(max, position))
}
export function clampCamera(
  camera: Camera,
  width: number,
  height: number,
  world: CameraWorld = 'illustration',
): Camera {
  const scale = Math.max(
    MIN_SCALE,
    Math.min(world === 'illustration' ? MAX_SCALE : 1.8, camera.scale),
  )
  const bounds = cameraBounds(world)
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
  world: CameraWorld = 'illustration',
): Camera {
  const scale = Math.max(
    MIN_SCALE,
    Math.min(world === 'illustration' ? MAX_SCALE : 1.8, camera.scale * factor),
  )
  const ratio = scale / camera.scale
  return clampCamera(
    { scale, x: x - (x - camera.x) * ratio, y: y - (y - camera.y) * ratio },
    width,
    height,
    world,
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
