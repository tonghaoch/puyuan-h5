export async function rasterizeArt(page, source, width, height) {
  const png = await page.evaluate(
    async ({ source, width, height }) => {
      const url = URL.createObjectURL(new Blob([source], { type: 'image/svg+xml' }))
      try {
        const image = new Image()
        image.src = url
        await image.decode()
        const canvas = document.createElement('canvas')
        canvas.width = width
        canvas.height = height
        const context = canvas.getContext('2d', { colorSpace: 'srgb', willReadFrequently: true })
        context.drawImage(image, 0, 0, width, height)
        return canvas.toDataURL('image/png').split(',')[1]
      } finally {
        URL.revokeObjectURL(url)
      }
    },
    { source, width, height },
  )
  return Buffer.from(png, 'base64')
}
