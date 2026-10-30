import { getIn } from '../../../lib/util'
import { useE } from '../context'

export function Factores({ items, notas }: { items: [string, string][]; notas: string }) {
  const { data, set } = useE()
  return (
    <details style={{ marginTop: 10 }}>
      <summary>Descripción de los factores utilizados</summary>
      <div className="rejilla" style={{ marginTop: 8 }}>
        {items.map(([k, n]) => (
          <div className="campo ancho" key={k}><label>{n}</label>
            <textarea style={{ minHeight: 44 }} value={getIn(data, `${notas}.${k}`) ?? ''} onChange={(e) => set(`${notas}.${k}`, e.target.value)} /></div>
        ))}
      </div>
    </details>
  )
}
