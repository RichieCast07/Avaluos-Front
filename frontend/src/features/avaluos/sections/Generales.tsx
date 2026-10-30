import { Campo } from '../components/Campos'

export function Generales() {
  return (
    <>
      <h2>Datos generales</h2>
      <div className="rejilla">
        <Campo label="Fecha del avalúo" p="fecha" tipo="fecha" />
        <Campo label="Propietario del inmueble" p="generales.propietario" />
        <Campo label="Solicitante" p="generales.solicitante" />
        <Campo label="Bien que se avalúa" p="generales.bien" />
        <Campo label="Régimen de propiedad" p="generales.regimen" />
        <Campo label="Propósito del avalúo" p="generales.proposito" />
        <Campo label="Uso del avalúo" p="generales.uso" />
      </div>
      <h3>Ubicación del inmueble</h3>
      <div className="rejilla">
        <Campo label="Calle" p="inmueble.calle" /><Campo label="Número" p="inmueble.numero" />
        <Campo label="Colonia" p="inmueble.colonia" /><Campo label="Municipio" p="inmueble.municipio" />
        <Campo label="Código postal" p="inmueble.cp" /><Campo label="Estado y país" p="inmueble.estado" />
        <Campo label="Cuenta predial" p="inmueble.cuenta_predial" /><Campo label="Cuenta de agua" p="inmueble.cuenta_agua" />
      </div>
    </>
  )
}
