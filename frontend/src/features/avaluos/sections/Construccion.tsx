import { Campo } from '../components/Campos'

const ELEMENTOS: [string, string][] = [
  ['cimientos', 'Cimientos'], ['estructura', 'Estructura'], ['muros', 'Muros'], ['entrepisos', 'Entrepisos'], ['techos', 'Techos'],
  ['azoteas', 'Azoteas'], ['bardas', 'Bardas'], ['aplanados_int', 'Aplanados interiores'], ['aplanados_ext', 'Aplanados exteriores'],
  ['techos_acab', 'Techos (acabado)'], ['lambrines', 'Lambrines'], ['pisos', 'Pisos'], ['escaleras', 'Escaleras'], ['pintura', 'Pintura'],
  ['recubrimientos', 'Recubrimientos especiales'], ['carpinteria', 'Carpintería'], ['hidraulicas', 'Instalaciones hidráulicas y sanitarias'],
  ['electricas', 'Instalaciones eléctricas'], ['puertas', 'Puertas y ventanerías'], ['herreria', 'Herrería'], ['vidrieria', 'Vidriería'],
  ['cerrajeria', 'Cerrajería'], ['fachada', 'Fachada'], ['especiales', 'Instalaciones especiales, accesorios y obras complementarias'],
]

export function Construccion() {
  return (
    <>
      <h2>Descripción del inmueble</h2>
      <div className="rejilla">
        <Campo label="Uso actual" p="descripcion.uso_actual" tipo="area" />
        <Campo label="Calidad y clasificación" p="descripcion.calidad" />
        <Campo label="Número de niveles" p="descripcion.niveles" />
        <Campo label="Edad aproximada (años)" p="descripcion.edad" tipo="num" />
        <Campo label="Vida útil remanente (años)" p="descripcion.vida_remanente" tipo="num" />
        <Campo label="Vida total (años)" p="descripcion.vida_total" tipo="num" />
        <Campo label="Estado de conservación" p="descripcion.conservacion" />
        <Campo label="Unidades rentables" p="descripcion.unidades_rentables" />
      </div>
      <h3>Elementos de la construcción</h3>
      <div className="rejilla">
        {ELEMENTOS.map(([k, n]) => <Campo key={k} label={n} p={`descripcion.elementos.${k}`} tipo="area" />)}
      </div>
    </>
  )
}
