import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../../lib/api'
import { mxn } from '../../lib/util'

type Fila = { id: number; folio: string; titulo: string; propietario: string; estado: string; valor: number; updated_at: string; documentos: number }

export function Lista() {
  const nav = useNavigate()
  const [filas, setFilas] = useState<Fila[]>([])
  const [q, setQ] = useState('')
  const [error, setError] = useState('')

  const cargar = () => api('/avaluos?q=' + encodeURIComponent(q)).then(setFilas).catch((e) => setError(e.message))
  useEffect(() => { const t = setTimeout(cargar, 250); return () => clearTimeout(t) }, [q])

  async function nuevo(ejemplo = false, duplicar_de?: number) {
    const a = await api('/avaluos', { body: { ejemplo, duplicar_de } })
    nav(`/avaluo/${a.id}`)
  }
  async function borrar(f: Fila) {
    if (!confirm(`¿Eliminar el avalúo ${f.folio}? Se borran también sus Excel y PDF.`)) return
    try { await api(`/avaluos/${f.id}`, { method: 'DELETE' }); cargar() } catch (e: any) { setError(e.message) }
  }

  return (
    <>
      <div className="encabezado-pagina">
        <div>
          <h1>Historial de avalúos</h1>
          <p className="nota">{filas.length} {filas.length === 1 ? 'avalúo' : 'avalúos'}</p>
        </div>
        <span className="espacio" />
        <input className="buscar" placeholder="Buscar por folio o dirección" value={q} onChange={(e) => setQ(e.target.value)} />
        <button className="btn sec" onClick={() => nuevo(true)} title="Crea un avalúo con datos de prueba (José Mariano Jiménez 614)">Crear ejemplo</button>
        <button className="btn" onClick={() => nuevo(false)}>+ Nuevo avalúo</button>
      </div>
      {error && <div className="error">{error}</div>}
      <div className="tarjeta sin-relleno">
        <table className="lista">
          <thead><tr><th>Folio</th><th>Inmueble</th><th>Propietario</th><th className="r">Valor</th><th>Estado</th><th>Docs</th><th>Actualizado</th><th></th></tr></thead>
          <tbody>
            {filas.map((f) => (
              <tr key={f.id}>
                <td><Link to={`/avaluo/${f.id}`}><b>{f.folio}</b></Link></td>
                <td>{f.titulo}</td>
                <td>{f.propietario}</td>
                <td className="r">{f.valor ? mxn(f.valor) : '—'}</td>
                <td><span className={'etiqueta ' + f.estado}>{f.estado}</span></td>
                <td>{f.documentos}</td>
                <td>{new Date(f.updated_at + 'Z').toLocaleString('es-MX', { dateStyle: 'medium', timeStyle: 'short' })}</td>
                <td className="acciones">
                  <button className="btn sec chico" onClick={() => nav(`/avaluo/${f.id}`)}>Abrir</button>
                  <button className="btn sec chico" onClick={() => nuevo(false, f.id)}>Duplicar</button>
                  <button className="btn sec chico peligro" onClick={() => borrar(f)}>Eliminar</button>
                </td>
              </tr>
            ))}
            {!filas.length && <tr><td colSpan={8} className="vacio">Todavía no hay avalúos. Crea uno nuevo o prueba con el ejemplo.</td></tr>}
          </tbody>
        </table>
      </div>
    </>
  )
}
