import { useEffect, useState } from 'react'
import { api, urlArchivo } from '../../lib/api'
import { MAX_EXPERIENCIA } from '../../lib/limites'

export function Configuracion() {
  const [c, setC] = useState<any>(null)
  const [msg, setMsg] = useState('')
  const cargar = () => api('/configuracion').then(setC)
  useEffect(() => { cargar() }, [])
  if (!c) return <p className="cargando">Cargando…</p>

  const set = (k: string, v: any) => setC({ ...c, [k]: v })
  const setV = (k: string, v: any) => setC({ ...c, valuador: { ...c.valuador, [k]: v } })
  async function guardar() {
    await api('/configuracion', { method: 'PUT', body: c })
    setMsg('Guardado ✓'); setTimeout(() => setMsg(''), 2500)
  }
  async function subir(seccion: string, file?: File) {
    if (!file) return
    const fd = new FormData(); fd.append('seccion', seccion); fd.append('archivo', file)
    await api('/configuracion/archivo', { form: fd }); cargar()
  }
  return (
    <>
      <div className="encabezado-pagina">
        <div><h1>Empresa y valuador</h1><p className="nota">Salen en el Anexo 2 (datos del valuador) de cada avalúo. El logotipo y el encabezado ya vienen en el formato de Excel.</p></div>
        <span className="espacio" /><span className="guardado">{msg}</span><button className="btn" onClick={guardar}>Guardar cambios</button>
      </div>
      <div className="tarjeta rejilla">
        <div className="campo"><label>Perito valuador</label><input value={c.valuador.nombre} onChange={(e) => setV('nombre', e.target.value)} /></div>
        <div className="campo"><label>Maestría</label><input value={c.valuador.maestria} onChange={(e) => setV('maestria', e.target.value)} /></div>
        <div className="campo"><label>Cédula profesional</label><input value={c.valuador.cedula} onChange={(e) => setV('cedula', e.target.value)} /></div>
        <div className="campo ancho"><label>Experiencia (un párrafo por renglón, máximo {MAX_EXPERIENCIA})</label>
          <textarea rows={7} value={(c.valuador.experiencia || []).join('\n')} onChange={(e) => setV('experiencia', e.target.value.split('\n').slice(0, MAX_EXPERIENCIA))} /></div>
      </div>
      <div className="tarjeta fila" style={{ gap: 40 }}>
        {(['cedula'] as const).map((s) => (
          <div key={s} style={{ minWidth: 220 }}>
            <h3>Imagen de la cédula</h3>
            {c.archivos?.[s] ? <img src={urlArchivo(c.archivos[s])} className="vista-previa" /> : <p className="nota">Sin imagen: se usa la que trae el formato</p>}
            <input type="file" accept="image/*" onChange={(e) => subir(s, e.target.files?.[0])} />
          </div>
        ))}
      </div>
    </>
  )
}
