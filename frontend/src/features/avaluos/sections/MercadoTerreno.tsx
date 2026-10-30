import { MAX_COMPARABLES } from '../../../lib/limites'
import { n0, n2, mxn } from '../../../lib/util'
import { Campo, Cel } from '../components/Campos'
import { Factores } from '../components/Factores'
import { useE } from '../context'

export function MercadoTerreno() {
  const { data, calc, add, quitar } = useE()
  const items = data.comparables_terreno.items
  return (
    <>
      <h2>Análisis comparativo de mercado del terreno</h2>
      <div className="rejilla"><Campo label="Nivel de oferta observado" p="comparables_terreno.nivel_oferta" tipo="select" opciones={['MUY ALTA', 'ALTA', 'MEDIA', 'MEDIA BAJA', 'BAJA', 'NULA']} /></div>
      <h3>Terrenos similares en venta</h3>
      <div className="tabla-scroll"><table className="edit"><thead><tr><th>#</th><th>Dirección</th><th>Teléfono</th><th>Liga</th><th>Sup. m²</th><th>Oferta $</th><th></th></tr></thead><tbody>
        {items.map((_: any, i: number) => (
          <tr key={i}><td>{i + 1}</td>
            <td><Cel p={`comparables_terreno.items.${i}.direccion`} /></td><td><Cel p={`comparables_terreno.items.${i}.telefono`} /></td>
            <td><Cel p={`comparables_terreno.items.${i}.liga`} /></td>
            <td><Cel corto p={`comparables_terreno.items.${i}.sup`} /></td><td><Cel p={`comparables_terreno.items.${i}.oferta`} /></td>
            <td><button className="btn sec chico" onClick={() => quitar('comparables_terreno.items', i)}>✕</button></td></tr>
        ))}
      </tbody></table></div>
      <button className="btn sec chico" disabled={items.length >= MAX_COMPARABLES} title={items.length >= MAX_COMPARABLES ? 'El formato de Excel no admite más renglones' : ''} onClick={() => add('comparables_terreno.items', { direccion: '', telefono: '', liga: '', sup: '', oferta: '', neg: '0.98', ubic: '1', zona: '1', forma: '1', otro: '1' })}>+ Agregar comparable</button>
      <h3>Factores de homologación</h3>
      <div className="tabla-scroll"><table className="edit"><thead><tr><th>#</th><th>$/m²</th><th>NEG.</th><th>UBIC.</th><th>ZONA</th><th>FORMA</th><th>SUP.</th><th>OTRO</th><th>FRe</th><th>$/m² homologado</th></tr></thead><tbody>
        {items.map((_: any, i: number) => { const f = calc.terreno.filas[i]; return (
          <tr key={i}><td>{i + 1}</td><td className="res">{f ? n0(f.pm2) : ''}</td>
            {['neg', 'ubic', 'zona', 'forma'].map((k) => <td key={k}><Cel corto p={`comparables_terreno.items.${i}.${k}`} /></td>)}
            <td className="res">{f ? n2(f.f_sup) : ''}</td><td><Cel corto p={`comparables_terreno.items.${i}.otro`} /></td>
            <td className="res">{f ? n2(f.fre) : ''}</td><td className="res">{f ? mxn(f.homologado) : ''}</td></tr>) })}
      </tbody></table></div>
      <p><b>Valor homologado:</b> {mxn(calc.terreno.valor_homologado)} &nbsp; <b>V.N.R. $/m²:</b> {mxn(calc.terreno.vnr)}</p>
      <p className="nota">El factor de superficie se calcula solo: (superficie de la oferta ÷ superficie del terreno)^(1/6). Un factor menor a 1 significa que la oferta es mejor que el bien valuado.</p>
      <Factores notas="comparables_terreno.notas" items={[['neg', 'Negociación'], ['ubic', 'Ubicación'], ['zona', 'Zona'], ['forma', 'Forma'], ['sup', 'Superficie'], ['otro', 'Otro']]} />
    </>
  )
}
