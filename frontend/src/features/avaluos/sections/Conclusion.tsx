import { mxn } from '../../../lib/util'
import { Campo } from '../components/Campos'
import { useE } from '../context'

export function Conclusion({ setEstado, estado }: any) {
  const { data, calc, set } = useE()
  return (
    <>
      <h2>Conclusión del avalúo</h2>
      <div className="rejilla">
        <div className="campo"><label>Valor de comercialización basado en</label>
          <select value={data.conclusion.valor_conclusion} onChange={(e) => set('conclusion.valor_conclusion', e.target.value)}>
            <option value="mercado">Valor comparativo de mercado</option><option value="fisico">Valor físico (costos)</option><option value="promedio">Promedio de ambos</option></select></div>
        <Campo label="Vigencia (meses)" p="conclusion.vigencia_meses" tipo="num" />
        <Campo label="Declaración 1" p="conclusion.declaraciones.0" tipo="area" />
        <Campo label="Declaración 2" p="conclusion.declaraciones.1" tipo="area" />
        <Campo label="Comentarios generales, supuestos y condiciones limitantes" p="conclusion.comentarios" tipo="area" />
      </div>
      <div className="total-caja">
        <div>Valor comparativo de mercado: <b>{mxn(calc.conclusion.valor_mercado)}</b></div>
        <div>Valor físico o V.N.R.: <b>{mxn(calc.conclusion.valor_fisico)}</b></div>
        <div style={{ fontSize: 20, marginTop: 8 }}>Valor de comercialización: <b style={{ color: 'var(--rojo)' }}>{mxn(calc.conclusion.valor)}</b></div>
        <div className="nota">{calc.conclusion.letras}</div>
      </div>
      <div className="fila"><span>Estado del avalúo:</span>
        <button className={'btn chico' + (estado === 'borrador' ? '' : ' sec')} onClick={() => setEstado('borrador')}>Borrador</button>
        <button className={'btn chico' + (estado === 'final' ? '' : ' sec')} onClick={() => setEstado('final')}>Final</button></div>
    </>
  )
}
