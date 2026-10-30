import { useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../../lib/api'
import { getIn, setIn, mxn } from '../../lib/util'
import { C, type EditorCtx } from './context'
import { Generales } from './sections/Generales'
import { Zona } from './sections/Zona'
import { Terreno } from './sections/Terreno'
import { Construccion } from './sections/Construccion'
import { MercadoTerreno } from './sections/MercadoTerreno'
import { Costos } from './sections/Costos'
import { MercadoInmuebles } from './sections/MercadoInmuebles'
import { Fotos } from './sections/Fotos'
import { Conclusion } from './sections/Conclusion'
import { Documentos } from './sections/Documentos'

const PASOS: [string, string][] = [['generales', '1. Datos generales'], ['zona', '2. Zona'], ['terreno', '3. Terreno'], ['construccion', '4. Construcción'],
  ['mterreno', '5. Mercado del terreno'], ['costos', '6. Enfoque de costos'], ['minmuebles', '7. Mercado de inmuebles'], ['fotos', '8. Fotografías'],
  ['conclusion', '9. Conclusión'], ['documentos', '10. Documentos (PDF / Excel)']]

export default function Editor() {
  const { id } = useParams()
  const [data, setData] = useState<any>(null)
  const [calc, setCalc] = useState<any>(null)
  const [meta, setMeta] = useState<any>({})
  const [archivos, setArchivos] = useState<any[]>([])
  const [paso, setPaso] = useState('generales')
  const [estado, setEstado] = useState('')
  const sucio = useRef(false)
  const ultimo = useRef<any>(null)
  const timer = useRef<any>(null)
  const estadoAv = useRef('borrador')

  const cargar = () => api(`/avaluos/${id}`).then((a) => { setData(a.data); setCalc(a.calc); setMeta(a); setArchivos(a.archivos); estadoAv.current = a.estado })
  const recargarFotos = () => api(`/avaluos/${id}`).then((a) => setArchivos(a.archivos))
  useEffect(() => { cargar() }, [id])

  async function guardarYa() {
    clearTimeout(timer.current)
    if (!sucio.current) return
    sucio.current = false
    setEstado('Guardando…')
    try {
      const r = await api(`/avaluos/${id}`, { method: 'PUT', body: { data: ultimo.current, estado: estadoAv.current } })
      setCalc(r.calc); setMeta((m: any) => ({ ...m, titulo: r.titulo })); setEstado('Guardado ✓')
    } catch (e: any) { sucio.current = true; setEstado('Error al guardar: ' + e.message) }
  }
  useEffect(() => {
    ultimo.current = data
    if (!data || !sucio.current) return
    setEstado('Cambios sin guardar…')
    clearTimeout(timer.current)
    timer.current = setTimeout(guardarYa, 700)
    return () => clearTimeout(timer.current)
  }, [data])

  if (!data || !calc) return <p>Cargando…</p>
  const ctx: EditorCtx = {
    data, calc,
    set: (p, v) => { sucio.current = true; setData((d: any) => setIn(d, p, v)) },
    add: (p, fila) => { sucio.current = true; setData((d: any) => setIn(d, p, [...getIn(d, p), fila])) },
    quitar: (p, i) => { sucio.current = true; setData((d: any) => setIn(d, p, getIn(d, p).filter((_: any, j: number) => j !== i))) },
  }
  const cambiarEstado = async (e: string) => { estadoAv.current = e; setMeta((m: any) => ({ ...m, estado: e })); sucio.current = true; await guardarYa() }

  return (
    <C.Provider value={ctx}>
      <div className="fila" style={{ marginBottom: 12 }}>
        <Link to="/">← Historial</Link>
        <h1 style={{ margin: 0 }}>{meta.folio} · {meta.titulo}</h1>
        <span className="espacio" /><span className="guardado">{estado}</span>
      </div>
      <div className="editor">
        <div className="pasos tarjeta" style={{ padding: 6 }}>
          {PASOS.map(([k, n]) => <button key={k} className={paso === k ? 'act' : ''} onClick={() => setPaso(k)}>{n}</button>)}
        </div>
        <div className="tarjeta">
          {paso === 'generales' && <Generales />}
          {paso === 'zona' && <Zona />}
          {paso === 'terreno' && <Terreno id={id} archivos={archivos} recargarFotos={recargarFotos} />}
          {paso === 'construccion' && <Construccion />}
          {paso === 'mterreno' && <MercadoTerreno />}
          {paso === 'costos' && <Costos />}
          {paso === 'minmuebles' && <MercadoInmuebles />}
          {paso === 'fotos' && <Fotos id={id} archivos={archivos} recargar={recargarFotos} />}
          {paso === 'conclusion' && <Conclusion estado={meta.estado} setEstado={cambiarEstado} />}
          {paso === 'documentos' && <Documentos id={id} guardarYa={guardarYa} />}
          <div className="fila" style={{ marginTop: 20 }}>
            {PASOS.findIndex(([k]) => k === paso) > 0 && <button className="btn sec" onClick={() => setPaso(PASOS[PASOS.findIndex(([k]) => k === paso) - 1][0])}>← Anterior</button>}
            <span className="espacio" />
            {PASOS.findIndex(([k]) => k === paso) < PASOS.length - 1 && <button className="btn" onClick={() => setPaso(PASOS[PASOS.findIndex(([k]) => k === paso) + 1][0])}>Siguiente →</button>}
          </div>
        </div>
        <div className="resumen tarjeta">
          <h2>Resumen</h2>
          <dl>
            <dt>V.N.R. terreno</dt><dd>{mxn(calc.terreno.vnr)}/m²</dd>
            <dt>Valor físico</dt><dd>{mxn(calc.costos.valor_fisico)}</dd>
            <dt>En N.R. construcción</dt><dd>{mxn(calc.inmuebles.en_nr)}/m²</dd>
            <dt>Valor comparativo de mercado</dt><dd>{mxn(calc.conclusion.valor_mercado)}</dd>
            <dt>Valor de comercialización</dt><dd className="grande">{mxn(calc.conclusion.valor)}</dd>
          </dl>
        </div>
      </div>
    </C.Provider>
  )
}
