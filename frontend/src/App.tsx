import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { Privado } from './components/Shell'
import { Login } from './features/auth/Login'
import { Lista } from './features/avaluos/Lista'
import Editor from './features/avaluos/Editor'
import { Usuarios } from './features/admin/Usuarios'
import { Configuracion } from './features/admin/Configuracion'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Privado>{() => <Lista />}</Privado>} />
        <Route path="/avaluo/:id" element={<Privado>{() => <Editor />}</Privado>} />
        <Route path="/usuarios" element={<Privado soloAdmin>{() => <Usuarios />}</Privado>} />
        <Route path="/configuracion" element={<Privado soloAdmin>{() => <Configuracion />}</Privado>} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  )
}
