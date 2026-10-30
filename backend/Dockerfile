# El PDF se genera imprimiendo el Excel con LibreOffice (sin ventana)
FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends libreoffice-calc fonts-liberation fonts-dejavu-core fonts-urw-base35 fontconfig \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV PYTHONUNBUFFERED=1 DATA_DIR=/data HOME=/tmp
# Railway define $PORT; en local cae a 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
