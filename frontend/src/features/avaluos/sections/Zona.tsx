import { Campo } from '../components/Campos'

export function Zona() {
  return (
    <>
      <h2>Características urbanas</h2>
      <div className="rejilla">
        <Campo label="Construcción dominante" p="zona.construccion_dominante" />
        <Campo label="Densidad de población" p="zona.densidad" />
        <Campo label="Contaminación ambiental" p="zona.contaminacion" />
        <Campo label="Uso de suelo permitido" p="zona.uso_suelo" />
        <Campo label="Índice de saturación (%)" p="zona.saturacion" tipo="num" />
        <Campo label="Vías de acceso e importancia" p="zona.vias_acceso" tipo="area" />
        <Campo label="Servicios públicos" p="zona.servicios" tipo="area" />
        <Campo label="Equipamiento urbano" p="zona.equipamiento" tipo="area" />
      </div>
    </>
  )
}
