import { randomBytes } from 'node:crypto'
import { preview } from 'vite'

export async function startPhonePreview(host, port) {
  const base = `/preview/${randomBytes(24).toString('hex')}/`
  const server = await preview({
    configFile: false,
    base,
    appType: 'mpa',
    build: { outDir: 'dist-review' },
    preview: { host, port, strictPort: true, open: false },
    plugins: [
      {
        name: 'private-phone-preview',
        configurePreviewServer(server) {
          server.middlewares.use((request, response, next) => {
            response.setHeader('Referrer-Policy', 'no-referrer')
            response.setHeader('Cache-Control', 'no-store')
            if (request.url?.startsWith(base)) return next()
            response.writeHead(404).end()
          })
        },
      },
    ],
  })
  return { server, url: new URL(`http://${host}:${server.httpServer.address().port}${base}`) }
}
