export const getIn = (o: any, path: string): any => path.split('.').reduce((a, k) => (a == null ? a : a[k]), o)

// copia inmutable con el valor puesto en la ruta ("terreno.norte.medida", "comparables_terreno.items.0.sup")
export function setIn(o: any, path: string, v: any): any {
  const [k, ...resto] = path.split('.')
  const copia: any = Array.isArray(o) ? [...o] : { ...o }
  copia[k] = resto.length ? setIn(o?.[k] ?? {}, resto.join('.'), v) : v
  return copia
}

const f0 = new Intl.NumberFormat('es-MX', { maximumFractionDigits: 0 })
const f2 = new Intl.NumberFormat('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
export const n0 = (x: number | null | undefined) => (x == null ? '' : f0.format(x))
export const n2 = (x: number | null | undefined) => (x == null ? '' : f2.format(x))
export const mxn = (x: number | null | undefined) => (x == null ? '' : '$ ' + f0.format(x))
export const num = (v: any) => { const n = parseFloat(String(v ?? '').replace(/,/g, '')); return isNaN(n) ? 0 : n }
