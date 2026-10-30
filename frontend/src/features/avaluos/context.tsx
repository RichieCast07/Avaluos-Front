import { createContext, useContext } from 'react'

export type EditorCtx = {
  data: any
  calc: any
  set: (ruta: string, valor: any) => void
  add: (ruta: string, fila: any) => void
  quitar: (ruta: string, i: number) => void
}
export const C = createContext<EditorCtx>(null as any)
export const useE = () => useContext(C)
