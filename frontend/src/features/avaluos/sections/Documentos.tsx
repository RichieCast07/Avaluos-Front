import { useEffect, useState } from 'react'
import { api, descargar } from '../../../lib/api'
import { mxn } from '../../../lib/util'

export function Documentos({ id, guardarYa }: any) {
  const [docs, setDocs] = useState<any[]>([])
  const [ocupado, setOcupado] = useState('')
  const [error, setError] = useState('')
  const cargar = () => api(`/avaluos/${id}/documentos`).then(setDocs)
  useEffect(() => { cargar() }, [id])
  async function generar(formato: 'pdf' | 'xlsx') {
    setError(''); setOcupado(formato)
    try { await guardarYa(); const d = await api(`/avaluos/${id}/documentos`, { body: { formato } }); await cargar(); await descargar(d.id, d.nombre) }
    catch (e: any) { setError(e.message) } finally { setOcupado('') }
  }
  return (
    <>
      <h2>Documentos</h2>
      <p className="nota">Cada vez que generas un archivo se guarda una nueva versión en el historial con los datos que tenía el avalúo en ese momento.</p>
      <div className="fila">
        <button className="btn" disabled={!!ocupado} onClick={() => generar('pdf')}>{ocupado === 'pdf' ? 'Generando PDF…' : 'Generar PDF'}</button>
        <button className="btn" disabled={!!ocupado} onClick={() => generar('xlsx')}>{ocupado === 'xlsx' ? 'Generando Excel…' : 'Generar Excel'}</button>
      </div>
      {error && <div className="error">{error}</div>}
      <h3>Historial</h3>
      <table className="lista"><thead><tr><th>Archivo</th><th>Tipo</th><th>Versión</th><th>Valor</th><th>Fecha</th><th></th></tr></thead><tbody>
        {docs.map((d) => (
          <tr key={d.id}><td>{d.nombre}</td><td>{d.formato.toUpperCase()}</td><td>v{d.version}</td><td>{mxn(d.valor)}</td>
            <td>{new Date(d.created_at + 'Z').toLocaleString('es-MX')}</td>
            <td><button className="btn sec chico" onClick={() => descargar(d.id, d.nombre)}>Descargar</button></td></tr>
        ))}
        {!docs.length && <tr><td colSpan={6} className="nota">Aún no se ha generado ningún documento.</td></tr>}
      </tbody></table>
    </>
  )
}
