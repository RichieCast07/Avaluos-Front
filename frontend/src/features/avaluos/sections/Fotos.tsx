import { api, urlArchivo } from '../../../lib/api'
import { MAX_FOTOS_ANEXO } from '../../../lib/limites'
import { SubirUna } from '../components/SubirUna'

export function Fotos({ id, archivos, recargar }: any) {
  const anexo = archivos.filter((f: any) => f.seccion === 'anexo')
  async function subir(files: FileList | null) {
    if (!files) return
    const cupo = MAX_FOTOS_ANEXO - anexo.length
    for (const file of Array.from(files).slice(0, Math.max(cupo, 0))) { const fd = new FormData(); fd.append('seccion', 'anexo'); fd.append('archivo', file); await api(`/avaluos/${id}/archivos`, { form: fd }) }
    recargar()
  }
  async function quitar(f: any) { await api(`/archivos/${f.id}`, { method: 'DELETE' }); recargar() }
  return (
    <>
      <h2>Fotografías</h2>
      <div className="fila"><SubirUna id={id} seccion="portada" titulo="Foto de portada" archivos={archivos} recargar={recargar} /></div>
      <h3>Anexo 1. Reporte fotográfico</h3>
      <p className="nota">El formato tiene lugar para {MAX_FOTOS_ANEXO} fotos ({anexo.length} de {MAX_FOTOS_ANEXO}). Se acomodan en el orden en que las subas.</p>
      <input type="file" accept="image/*" multiple disabled={anexo.length >= MAX_FOTOS_ANEXO} onChange={(e) => subir(e.target.files)} />
      <div className="fotos" style={{ marginTop: 12 }}>
        {anexo.map((f: any) => (
          <div className="foto" key={f.id}><img src={urlArchivo(f.id)} />
            <button className="btn sec chico" style={{ marginTop: 6 }} onClick={() => quitar(f)}>Quitar</button></div>
        ))}
      </div>
    </>
  )
}
