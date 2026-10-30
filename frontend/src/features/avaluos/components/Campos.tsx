import { getIn } from '../../../lib/util'
import { useE } from '../context'

export function Campo({ label, p, tipo = 'texto', opciones, ancho }: { label: string; p: string; tipo?: 'texto' | 'num' | 'area' | 'select' | 'fecha'; opciones?: string[]; ancho?: boolean }) {
  const { data, set } = useE()
  const v = getIn(data, p) ?? ''
  return (
    <div className={'campo' + (ancho || tipo === 'area' ? ' ancho' : '')}>
      <label>{label}</label>
      {tipo === 'area' ? <textarea value={v} onChange={(e) => set(p, e.target.value)} />
        : tipo === 'select' ? <select value={v} onChange={(e) => set(p, e.target.value)}>{opciones!.map((o) => <option key={o}>{o}</option>)}</select>
        : <input type={tipo === 'fecha' ? 'date' : 'text'} inputMode={tipo === 'num' ? 'decimal' : undefined} value={v} onChange={(e) => set(p, e.target.value)} />}
    </div>
  )
}

export const Cel = ({ p, corto, placeholder }: { p: string; corto?: boolean; placeholder?: string }) => {
  const { data, set } = useE()
  return <input className={corto ? 'corto' : ''} placeholder={placeholder} value={getIn(data, p) ?? ''} onChange={(e) => set(p, e.target.value)} />
}

// ---------------------------------------------------------------- secciones
