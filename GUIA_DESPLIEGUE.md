# Guía de despliegue: Vercel (frontend) + Railway (backend)

```
Navegador ──► Vercel (React)  ──API──►  Railway (FastAPI + LibreOffice)  ──► PostgreSQL (Railway)
                                                │
                                                └─ Volume /data (fotos, Excel y PDF generados)
```

Tu Excel (`backend/app/assets/plantilla_avaluo.xlsx`) es la **plantilla**: la web escribe los datos en sus celdas
y el PDF se obtiene imprimiendo ese mismo archivo con LibreOffice, así que el PDF respeta el formato original.
El frontend necesita la URL del backend (`VITE_API_URL`) y el backend la de Vercel (`FRONTEND_URL`, solo para CORS).
Hay que desplegar en este orden.

## 0. Subir el código a GitHub
```bash
cd avaluos-web
git init && git add . && git commit -m "Sistema de avalúos"
# crea un repositorio en GitHub y súbelo (git remote add origin ... && git push -u origin main)
```

## 1. Backend en Railway
1. Railway → **New Project → Deploy from GitHub repo** → elige el repositorio.
2. En el servicio: **Settings → Source → Root Directory = `backend`**. Railway detecta el `Dockerfile` y `railway.json`.
3. **Agregar PostgreSQL**: en el proyecto, **New → Database → Add PostgreSQL**.
4. **Agregar el Volume** (el disco de Railway se borra en cada despliegue; aquí viven fotos, PDF y Excel):
   servicio → **Settings → Volumes → Add Volume → Mount path `/data`**.
5. **Variables** del servicio del backend:

   | Variable | Valor |
   |---|---|
   | `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` (referencia al plugin; el nombre del plugin puede variar) |
   | `SECRET_KEY` | cadena larga aleatoria (`openssl rand -hex 32`) |
   | `ADMIN_EMAIL` / `ADMIN_PASSWORD` | primer administrador (se crea solo la primera vez) |
   | `DATA_DIR` | `/data` |
   | `FRONTEND_URL` | la URL de Vercel (paso 2). Puedes dejar una temporal y corregirla después |
   | `FRONTEND_REGEX` | opcional, para previews de Vercel: `https://.*\.vercel\.app` |

6. **Settings → Networking → Generate Domain**. Anota la URL (`https://xxxx.up.railway.app`) y comprueba
   que `https://xxxx.up.railway.app/salud` responde `{"ok":true}`.

> Recomendado: al menos 1 GB de RAM en el servicio (LibreOffice convierte el PDF). La primera conversión tarda unos segundos.

## 2. Frontend en Vercel
1. Vercel → **Add New → Project** → importa el mismo repositorio.
2. **Root Directory = `frontend`**. Framework: Vite (build `npm run build`, salida `dist`).
3. **Environment Variables**: `VITE_API_URL` = URL pública de Railway, **sin diagonal final**.
4. Deploy. `frontend/vercel.json` ya redirige todas las rutas a `index.html` (necesario para `/avaluo/3`…).
5. Copia la URL final de Vercel y ponla en `FRONTEND_URL` del backend en Railway (Railway redespliega solo).

## 3. Primer uso
1. Abre la URL de Vercel e inicia sesión con `ADMIN_EMAIL` / `ADMIN_PASSWORD`.
2. **Empresa y valuador**: revisa nombre, maestría, cédula y experiencia (hasta 5 párrafos). El logotipo y el encabezado ya vienen en el Excel.
3. **Usuarios**: crea las cuentas de los valuadores (el rol *valuador* captura y genera documentos; solo el *administrador* elimina avalúos y edita usuarios/empresa).
4. Prueba con **Crear ejemplo → 10. Documentos → Generar PDF / Excel**.

## Problemas frecuentes
| Síntoma | Causa y solución |
|---|---|
| El login dice "Failed to fetch" | `VITE_API_URL` mal escrita o `FRONTEND_URL` no coincide exactamente con el dominio de Vercel (CORS). Revisa ambas, sin diagonal final. |
| "Generar PDF" tarda y falla | Revisa los logs de Railway. Casi siempre es poca RAM (LibreOffice). Sube el plan o la memoria del servicio. |
| Las fotos desaparecen tras un despliegue | Falta el Volume en `/data` o `DATA_DIR` no apunta a él. |
| `/avaluo/3` da 404 en Vercel | Falta `vercel.json` (viene en `frontend/`) o el Root Directory no es `frontend`. |
| Cambié `VITE_API_URL` y no se nota | Las variables `VITE_*` se incrustan al compilar: haz **Redeploy** en Vercel. |

## Desarrollo local
```bash
# backend (Python 3.12+)
cd backend && pip install -r requirements.txt   # y LibreOffice instalado (soffice) para el PDF
uvicorn app.main:app --reload            # http://localhost:8000  (SQLite en ../data)
python -m pytest                          # pruebas del cálculo y de la API

# frontend
cd frontend && npm install && npm run dev # http://localhost:5173 (usa el proxy /api → 8000)
```
Con `docker compose up` se levanta backend (con LibreOffice) + PostgreSQL.

## Límites del formato de Excel
La plantilla tiene renglones fijos; la web no deja pasar de ahí: **4** comparables de terreno, **4** de inmuebles,
**3** construcciones, **5** instalaciones especiales, **6** fotos de anexo y **5** párrafos de experiencia.
Para ampliar alguno hay que agregar renglones en el Excel y ajustar `domain/plantillas.py` y `infrastructure/plantilla_avaluo.py`.

## Si cambias la plantilla
Reemplaza `backend/app/assets/plantilla_avaluo.xlsx` conservando las celdas que se llenan (están listadas en
`infrastructure/plantilla_avaluo.py`) y corre `python -m pytest`: las pruebas comparan el valor que recalcula el Excel contra el del sistema.
