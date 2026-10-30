export const API_URL: string = (import.meta.env.VITE_API_URL ?? '').replace(/\/$/, '')

const KEY = 'avaluos_token'
export const getToken = (): string => {
  return localStorage.getItem(KEY) || ''
}
export const setToken = (t: string) => { localStorage.setItem(KEY, t) }
export const cerrarSesion = () => { localStorage.removeItem(KEY) }

export class ApiError extends Error {
  status: number
  constructor(status: number, msg: string) { super(msg); this.status = status }
}

export async function api<T = any>(ruta: string, opts: { method?: string; body?: any; form?: FormData } = {}): Promise<T> {
  const headers: Record<string, string> = {}
  const t = getToken()
  if (t) headers.Authorization = `Bearer ${t}`
  let body: any
  if (opts.form) body = opts.form
  else if (opts.body !== undefined) { headers['Content-Type'] = 'application/json'; body = JSON.stringify(opts.body) }
  const r = await fetch(`${API_URL}/api${ruta}`, { method: opts.method || (body ? 'POST' : 'GET'), headers, body })
  if (!r.ok) {
    let msg = r.statusText
    try { const j = await r.json(); msg = typeof j.detail === 'string' ? j.detail : msg } catch { /* sin cuerpo */ }
    if (r.status === 401 && !location.pathname.startsWith('/login')) { cerrarSesion(); location.href = '/login' }
    throw new ApiError(r.status, msg)
  }
  return r.json()
}

export const urlArchivo = (id: number) => `${API_URL}/api/archivos/${id}/contenido?token=${encodeURIComponent(getToken())}`

export async function descargar(id: number, nombre: string) {
  const r = await fetch(`${API_URL}/api/documentos/${id}/descargar`, { headers: { Authorization: `Bearer ${getToken()}` } })
  if (!r.ok) throw new ApiError(r.status, 'No se pudo descargar')
  const url = URL.createObjectURL(await r.blob())
  const a = document.createElement('a')
  a.href = url; a.download = nombre; a.click()
  URL.revokeObjectURL(url)
}
