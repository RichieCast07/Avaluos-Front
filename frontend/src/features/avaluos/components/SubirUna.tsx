import { api, urlArchivo } from '../../../lib/api'

export function SubirUna({ id, seccion, titulo, archivos, recargar }: any) {
  const actual = archivos.find((f: any) => f.seccion === seccion)
  async function subir(file?: File) {
    if (!file) return
    const fd = new FormData(); fd.append('seccion', seccion); fd.append('archivo', file)
    await api(`/avaluos/${id}/archivos`, { form: fd }); recargar()
  }
  return (
    <div className="foto" style={{ width: 230 }}>
      <b style={{ fontSize: 13 }}>{titulo}</b>
      {actual ? <img src={urlArchivo(actual.id)} /> : <p className="nota">Sin imagen</p>}
      <input type="file" accept="image/*" onChange={(e) => subir(e.target.files?.[0])} />
    </div>
  )
}
