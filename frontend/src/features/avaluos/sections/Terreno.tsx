import { Campo, Cel } from '../components/Campos'
import { SubirUna } from '../components/SubirUna'

export function Terreno({ archivos, recargarFotos, id }: any) {
  return (
    <>
      <h2>Terreno</h2>
      <div className="rejilla">
        <Campo label="Tramos de calle, calles transversales y orientación" p="terreno.tramos" tipo="area" />
        <Campo label="Linderos y colindancias según (escritura)" p="terreno.escritura" tipo="area" />
      </div>
      <table className="edit"><thead><tr><th>Orientación</th><th>Medida (m)</th><th>Colinda con</th></tr></thead><tbody>
        {['norte', 'sur', 'oriente', 'poniente'].map((k) => (
          <tr key={k}><td style={{ textTransform: 'capitalize' }}>{k}</td><td><Cel p={`terreno.${k}.medida`} corto /></td><td><Cel p={`terreno.${k}.colinda`} /></td></tr>
        ))}
      </tbody></table>
      <div className="rejilla">
        <Campo label="Área del terreno (m²)" p="terreno.superficie" tipo="num" />
        <Campo label="Área de construcción (m²)" p="terreno.construccion" tipo="num" />
        <Campo label="Indiviso (%)" p="terreno.indiviso" tipo="num" />
        <Campo label="Topografía y configuración" p="terreno.topografia" />
        <Campo label="Número de frentes" p="terreno.frentes" />
        <Campo label="Características panorámicas" p="terreno.panoramicas" />
        <Campo label="Densidad habitacional" p="terreno.densidad_hab" />
        <Campo label="Intensidad de construcción" p="terreno.intensidad" />
        <Campo label="Servidumbre y/o restricciones" p="terreno.servidumbre" />
      </div>
      <h3>Georreferencia</h3>
      <div className="rejilla">
        <Campo label="Longitud W" p="terreno.longitud" /><Campo label="Latitud N" p="terreno.latitud" /><Campo label="Altitud (msnm)" p="terreno.altitud" />
      </div>
      <h3>Croquis de localización</h3>
      <div className="fila">
        <SubirUna id={id} seccion="macro" titulo="Macro" archivos={archivos} recargar={recargarFotos} />
        <SubirUna id={id} seccion="micro" titulo="Micro" archivos={archivos} recargar={recargarFotos} />
      </div>
    </>
  )
}
