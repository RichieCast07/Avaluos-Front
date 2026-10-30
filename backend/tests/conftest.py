import os
import tempfile

# La configuracion se lee al importar la app: se prepara antes
_tmp = tempfile.mkdtemp()
os.environ["DATA_DIR"] = _tmp
os.environ.pop("DATABASE_URL", None)
os.environ["ADMIN_EMAIL"] = "admin@test.local"
os.environ["ADMIN_PASSWORD"] = "clave-de-prueba"

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def admin(client):
    r = client.post("/api/login", json={"email": "admin@test.local", "password": "clave-de-prueba"})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['token']}"}
