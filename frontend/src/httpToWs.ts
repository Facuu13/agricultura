/** Convierte la base HTTP(S) del API en URL WebSocket para `/ws`. */
export function httpBaseToWsUrl(httpBase: string, path = '/ws'): string {
  const b = httpBase.replace(/\/$/, '')
  if (b.startsWith('https://')) {
    return b.replace(/^https/, 'wss') + path
  }
  return b.replace(/^http/, 'ws') + path
}
