import { MAX_COMPARABLES } from '../../../lib/limites'
import { n0, n2, mxn } from '../../../lib/util'
import { Campo, Cel } from '../components/Campos'
import { Factores } from '../components/Factores'
import { useE } from '../context'

export function MercadoInmuebles() {
  const { data, calc, add, quitar } = useE()
  const items = data.comparables_inmuebles.items
  const k = calc.inmuebles
  return (
    <>
      <h2>Enfoque comparativo de mercado</h2>
      <div className="rejilla"><Campo label="Nivel de oferta observado" p="comparables_inmuebles.nivel_oferta" tipo="select" opciones={['MUY ALTA', 'ALTA', 'MEDIA', 'MEDIA BAJA', 'BAJA', 'NULA']} /></div>
      <h3>Inmuebles similares en venta</h3>
      <div className="tabla-scroll"><table className="edit"><thead><tr><th>#</th><th>Dirección</th><th>Teléfono</th><th>Liga</th><th>Constr. m²</th><th>Terreno m²</th><th>Oferta $</th><th></th></tr></thead><tbody>
        {items.map((_: any, i: number) => (
          <tr key={i}><td>{i + 1}</td>
            <td><Cel p={`comparables_inmuebles.items.${i}.direccion`} /></td><td><Cel p={`comparables_inmuebles.items.${i}.telefono`} /></td>
            <td><Cel p={`comparables_inmuebles.items.${i}.liga`} /></td>
            <td><Cel corto p={`comparables_inmuebles.items.${i}.constr`} /></td><td><Cel corto p={`comparables_inmuebles.items.${i}.terreno`} /></td>
            <td><Cel p={`comparables_inmuebles.items.${i}.oferta`} /></td>
            <td><button className="btn sec chico" onClick={() => quitar('comparables_inmuebles.items', i)}>✕</button></td></tr>
        ))}
      </tbody></table></div>
      <button className="btn sec chico" disabled={items.length >= MAX_COMPARABLES} title={items.length >= MAX_COMPARABLES ? 'El formato de Excel no admite más renglones' : ''} onClick={() => add('comparables_inmuebles.items', { direccion: '', telefono: '', liga: '', constr: '', terreno: '', oferta: '', neg: '0.95', ubic: '1', calid: '1', edo: '1', otro: '1' })}>+ Agregar comparable</button>
      <h3>Factores de homologación</h3>
      <div className="tabla-scroll"><table className="edit"><thead><tr><th>#</th><th>$/m²</th><th>NEG.</th><th>UBIC.</th><th>SUP.</th><th>CALID.</th><th>EDO. CONS.</th><th>OTRO</th><th>FRe</th><th>$/m² homologado</th></tr></thead><tbody>
        {items.map((_: any, i: number) => { const f = k.filas[i]; return (
          <tr key={i}><td>{i + 1}</td><td className="res">{f ? n0(f.pm2) : ''}</td>
            <td><Cel corto p={`comparables_inmuebles.items.${i}.neg`} /></td><td><Cel corto p={`comparables_inmuebles.items.${i}.ubic`} /></td>
            <td className="res">{f ? n2(f.f_sup) : ''}</td>
            {['calid', 'edo', 'otro'].map((c) => <td key={c}><Cel corto p={`comparables_inmuebles.items.${i}.${c}`} /></td>)}
            <td className="res">{f ? n2(f.fre) : ''}</td><td className="res">{f ? mxn(f.homologado) : ''}</td></tr>) })}
      </tbody></table></div>
      <div className="rejilla"><Campo label="Monto adicional a considerar ($)" p="comparables_inmuebles.monto_adicional" tipo="num" /></div>
      <p>Valor homologado {mxn(k.valor_homologado)} → en N.R. <b>{mxn(k.en_nr)}/m²</b> × {data.terreno.construccion || 0} m² = {mxn(k.subtotal)}<br />
        <b>Valor comparativo de mercado: {mxn(k.valor_mercado)}</b></p>
      <Factores notas="comparables_inmuebles.notas" items={[['neg', 'Negociación'], ['ubic', 'Ubicación'], ['sup', 'Superficie'], ['calid', 'Calidad'], ['edo', 'Estado de conservación'], ['otro', 'Otro']]} />
    </>
  )
}
