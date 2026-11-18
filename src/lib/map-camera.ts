export interface Camera {
  x: number
  y: number
  scale: number
}
export const SCENE = { width: 1520, height: 1240 }
export const MIN_SCALE = 0.22
export const MAX_SCALE = 1.8
export function clampCamera(camera: Camera, width: number, height: number): Camera {
  const scale = Math.max(MIN_SCALE, Math.min(MAX_SCALE, camera.scale))
  const padding = 90
  const minX = Math.min(padding, width - SCENE.width * scale - padding)
  const maxX = Math.max(-padding, width - SCENE.width * scale + padding)
  const minY = Math.min(padding, height - SCENE.height * scale - padding)
  const maxY = Math.max(-padding, height - SCENE.height * scale + padding)
  return {
    scale,
    x: Math.max(minX, Math.min(maxX, camera.x)),
    y: Math.max(minY, Math.min(maxY, camera.y)),
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
  const scale = Math.max(MIN_SCALE, Math.min(MAX_SCALE, camera.scale * factor))
  const ratio = scale / camera.scale
  return clampCamera(
    { scale, x: x - (x - camera.x) * ratio, y: y - (y - camera.y) * ratio },
    width,
    height,
  )
}
