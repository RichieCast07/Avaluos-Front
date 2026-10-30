# Sistema de avalúos

Captura de avalúos inmobiliarios en web, con cálculo automático, historial y generación de **Excel** (se llena tu formato original) y **PDF** (se imprime ese mismo Excel, sin descuadres).

- **frontend/** React + TypeScript (Vite) → Vercel
- **backend/** FastAPI + SQLAlchemy + PostgreSQL → Railway
- Despliegue paso a paso: [GUIA_DESPLIEGUE.md](GUIA_DESPLIEGUE.md)

## Arquitectura del backend (capas)
```
app/
  domain/          reglas de negocio puras: calculo del avaluo, cantidad con letra, plantillas (sin web ni BD)
  infrastructure/  modelos SQLAlchemy, repositorios, almacenamiento en disco, llenado de la plantilla de Excel (`plantilla_avaluo`, `xlsx_editor`) y conversión a PDF con LibreOffice
  services/        casos de uso: avaluos, archivos, documentos, usuarios, empresa, seguridad
  api/             FastAPI: dependencias, esquemas y routers delgados (sin logica de negocio)
  config.py        configuracion por variables de entorno
tests/             pruebas del calculo (contra el Excel original) y de la API
```
Regla de dependencias: `api → services → infrastructure → domain`; el dominio no importa nada de las otras capas.

## Frontend
```
src/
  lib/           cliente de la API y utilidades
  components/    estructura comun (cabecera, rutas protegidas)
  features/
    auth/        login
    avaluos/     historial, editor (una seccion por archivo)
    admin/       usuarios, empresa y valuador
```
