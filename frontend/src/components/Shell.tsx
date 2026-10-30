import { useEffect, useState } from 'react'
import { Link, NavLink, Navigate, useNavigate } from 'react-router-dom'
import { api, cerrarSesion, getToken } from '../lib/api'

export type Yo = { id: number; nombre: string; email: string; rol: string }

function Cabecera({ yo }: { yo: Yo }) {
  const nav = useNavigate()
  return (
    <header className="top">
      <Link to="/" className="marca"><span className="marca-logo">A+</span> Avalúos</Link>
      <nav>
        <NavLink to="/" end>Historial</NavLink>
        {yo.rol === 'admin' && <NavLink to="/configuracion">Empresa y valuador</NavLink>}
        {yo.rol === 'admin' && <NavLink to="/usuarios">Usuarios</NavLink>}
      </nav>
      <span className="yo">{yo.nombre}</span>
      <button className="btn sec chico" onClick={() => { cerrarSesion(); nav('/login') }}>Cerrar sesión</button>
    </header>
  )
}

/** Protege una ruta: sin sesion manda al login. Entrega el usuario a su contenido. */
export function Privado({ children, soloAdmin = false }: { children: (yo: Yo) => React.ReactNode; soloAdmin?: boolean }) {
  const [yo, setYo] = useState<Yo | null>(null)
  const [fallo, setFallo] = useState(!getToken())
  useEffect(() => {
    if (!getToken()) return
    api('/me').then(setYo).catch(() => setFallo(true))
  }, [])
  if (fallo) return <Navigate to="/login" replace />
  if (!yo) return <p className="cargando">Cargando…</p>
  if (soloAdmin && yo.rol !== 'admin') return <Navigate to="/" replace />
  return (
    <>
      <Cabecera yo={yo} />
      <div className="contenedor">{children(yo)}</div>
    </>
  )
}
