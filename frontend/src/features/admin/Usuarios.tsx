import { useEffect, useState } from 'react'
import { api } from '../../lib/api'

const VACIO = { nombre: '', email: '', password: '', rol: 'valuador' }

export function Usuarios() {
  const [us, setUs] = useState<any[]>([])
  const [f, setF] = useState(VACIO)
  const [error, setError] = useState('')
  const cargar = () => api('/usuarios').then(setUs)
  useEffect(() => { cargar() }, [])

  async function crear(e: React.FormEvent) {
    e.preventDefault(); setError('')
    try { await api('/usuarios', { body: f }); setF(VACIO); cargar() } catch (er: any) { setError(er.message) }
  }
  async function alternar(u: any) {
    setError('')
    try { await api(`/usuarios/${u.id}?activo=${!u.activo}`, { method: 'PATCH' }); cargar() } catch (er: any) { setError(er.message) }
  }
  return (
    <>
      <div className="encabezado-pagina"><h1>Usuarios</h1></div>
      {error && <div className="error">{error}</div>}
      <div className="tarjeta sin-relleno">
        <table className="lista">
          <thead><tr><th>Nombre</th><th>Correo</th><th>Rol</th><th>Estado</th><th></th></tr></thead>
          <tbody>{us.map((u) => (
            <tr key={u.id}><td><b>{u.nombre}</b></td><td>{u.email}</td><td>{u.rol === 'admin' ? 'Administrador' : 'Valuador'}</td>
              <td><span className={'etiqueta ' + (u.activo ? 'final' : '')}>{u.activo ? 'Activo' : 'Inactivo'}</span></td>
              <td className="acciones"><button className="btn sec chico" onClick={() => alternar(u)}>{u.activo ? 'Desactivar' : 'Activar'}</button></td></tr>
          ))}</tbody>
        </table>
      </div>
      <form className="tarjeta" onSubmit={crear}>
        <h2>Nuevo usuario</h2>
        <div className="rejilla">
          <div className="campo"><label>Nombre</label><input required value={f.nombre} onChange={(e) => setF({ ...f, nombre: e.target.value })} /></div>
          <div className="campo"><label>Correo</label><input type="email" required value={f.email} onChange={(e) => setF({ ...f, email: e.target.value })} /></div>
          <div className="campo"><label>Contraseña (mínimo 8 caracteres)</label><input type="password" required minLength={8} value={f.password} onChange={(e) => setF({ ...f, password: e.target.value })} /></div>
          <div className="campo"><label>Rol</label><select value={f.rol} onChange={(e) => setF({ ...f, rol: e.target.value })}><option value="valuador">Valuador</option><option value="admin">Administrador</option></select></div>
        </div>
        <p><button className="btn">Crear usuario</button></p>
      </form>
    </>
  )
}
