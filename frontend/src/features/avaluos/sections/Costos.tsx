import { MAX_CONSTRUCCIONES, MAX_ESPECIALES } from '../../../lib/limites'
import { n2, mxn, num } from '../../../lib/util'
import { Campo, Cel } from '../components/Campos'
import { useE } from '../context'

export function Costos() {
  const { data, calc, set, add, quitar } = useE()
  const k = calc.costos
  const sugerir = () => {
    const r = num(data.descripcion.vida_remanente), t = num(data.descripcion.vida_total)
    if (!t) return alert('Captura vida útil remanente y vida total en "Descripción".')
    const v = (r / t).toFixed(2)
    data.costos.construcciones.forEach((_: any, i: number) => set(`costos.construcciones.${i}.demerito`, v))
  }
  return (
    <>
      <h2>Enfoque de costos</h2>
      <h3>a) Del terreno</h3>
      <div className="rejilla">
        <Campo label="Coeficiente" p="costos.terreno_coef" tipo="num" />
        <Campo label="Motivo del coeficiente" p="costos.terreno_motivo" />
      </div>
      <p>V.N.R. del terreno {mxn(calc.terreno.vnr)}/m² × {data.terreno.superficie || 0} m² × coef. = <b>{mxn(k.valor_terreno)}</b>. Con indiviso: <b>{mxn(k.terreno_sub)}</b></p>
      <h3>b) De las construcciones</h3>
      <div className="tabla-scroll"><table className="edit"><thead><tr><th>Uso o destino</th><th>Área m²</th><th>V.R.N. unitario $</th><th>Factor de demérito</th><th>V.N.R. unitario</th><th>Valor parcial</th><th></th></tr></thead><tbody>
        {data.costos.construcciones.map((_: any, i: number) => (
          <tr key={i}><td><Cel p={`costos.construcciones.${i}.uso`} /></td><td><Cel corto p={`costos.construcciones.${i}.area`} /></td>
            <td><Cel p={`costos.construcciones.${i}.vrn`} /></td><td><Cel corto p={`costos.construcciones.${i}.demerito`} /></td>
            <td className="res">{mxn(k.construcciones[i]?.vnr)}</td><td className="res">{mxn(k.construcciones[i]?.valor)}</td>
            <td><button className="btn sec chico" onClick={() => quitar('costos.construcciones', i)}>✕</button></td></tr>
        ))}
      </tbody></table></div>
      <div className="fila">
        <button className="btn sec chico" disabled={data.costos.construcciones.length >= MAX_CONSTRUCCIONES} title={data.costos.construcciones.length >= MAX_CONSTRUCCIONES ? 'El formato de Excel no admite más renglones' : ''} onClick={() => add('costos.construcciones', { uso: '', area: '', vrn: '', demerito: '' })}>+ Agregar construcción</button>
        <button className="btn sec chico" onClick={sugerir} title="Vida útil remanente ÷ vida total">Sugerir demérito por vida útil</button>
      </div>
      <p>Subtotal construcciones: <b>{mxn(k.construccion_sub)}</b></p>
      <h3>c) Instalaciones especiales, elementos accesorios y obras complementarias</h3>
      <div className="tabla-scroll"><table className="edit"><thead><tr><th>Concepto</th><th>Unidad</th><th>Cantidad</th><th>V.R.N. unitario $</th><th>Factor de demérito</th><th>Valor parcial</th><th></th></tr></thead><tbody>
        {data.costos.especiales.map((_: any, i: number) => (
          <tr key={i}><td><Cel p={`costos.especiales.${i}.concepto`} /></td><td><Cel corto p={`costos.especiales.${i}.unidad`} /></td>
            <td><Cel corto p={`costos.especiales.${i}.cantidad`} /></td><td><Cel p={`costos.especiales.${i}.vrn`} /></td>
            <td><Cel corto p={`costos.especiales.${i}.demerito`} /></td><td className="res">{mxn(k.especiales[i]?.valor)}</td>
            <td><button className="btn sec chico" onClick={() => quitar('costos.especiales', i)}>✕</button></td></tr>
        ))}
      </tbody></table></div>
      <button className="btn sec chico" disabled={data.costos.especiales.length >= MAX_ESPECIALES} title={data.costos.especiales.length >= MAX_ESPECIALES ? 'El formato de Excel no admite más renglones' : ''} onClick={() => add('costos.especiales', { concepto: '', unidad: 'm2', cantidad: '', vrn: '', demerito: '1' })}>+ Agregar concepto</button>
      <p>Subtotal instalaciones (con indiviso): <b>{mxn(k.especiales_sub)}</b></p>
      <div className="total-caja">
        <b>Valor físico o V.N.R. (a + b + c): {mxn(k.valor_fisico)}</b>
        <div className="nota">Terreno {n2(k.participacion.terreno)}% · Construcción {n2(k.participacion.construccion)}% · Instalaciones {n2(k.participacion.instalaciones)}%</div>
      </div>
    </>
  )
}
