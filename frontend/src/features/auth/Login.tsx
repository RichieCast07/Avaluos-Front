import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, setToken } from '../../lib/api'

export function Login() {
  const nav = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(false)

  async function entrar(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setCargando(true)
    try {
      const r = await api('/login', { body: { email, password } })
      setToken(r.token)
      nav('/')
    } catch (er: any) {
      setError(er.message)
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="login-pagina">
      <aside className="login-marca">
        <div className="login-logo">A+</div>
        <h1>Sistema de avalúos</h1>
        <p>Captura, calcula y emite avalúos inmobiliarios en un solo lugar, con historial de PDF y Excel por cada inmueble.</p>
        <ul>
          <li>Cálculo automático de factores de homologación</li>
          <li>PDF listo para entregar, sin desacomodos</li>
          <li>Historial de versiones por avalúo</li>
        </ul>
      </aside>
      <main className="login-forma">
        <form onSubmit={entrar}>
          <h2>Iniciar sesión</h2>
          <p className="nota">Ingresa con tu cuenta de la inmobiliaria.</p>
          <label htmlFor="email">Correo electrónico</label>
          <input id="email" type="email" autoComplete="username" value={email} onChange={(e) => setEmail(e.target.value)} autoFocus required />
          <label htmlFor="pw">Contraseña</label>
          <input id="pw" type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          {error && <div className="error" role="alert">{error}</div>}
          <button className="btn grande" disabled={cargando}>{cargando ? 'Entrando…' : 'Entrar'}</button>
        </form>
      </main>
    </div>
  )
}
