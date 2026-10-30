import io


def test_login_incorrecto(client):
    assert client.post("/api/login", json={"email": "admin@test.local", "password": "mal"}).status_code == 401


def test_rutas_exigen_sesion(client):
    assert client.get("/api/avaluos").status_code == 401
    assert client.get("/api/avaluos", headers={"Authorization": "Bearer basura"}).status_code == 401


def test_flujo_completo(client, admin):
    a = client.post("/api/avaluos", json={"ejemplo": True}, headers=admin).json()
    assert a["folio"].startswith("AV-") and a["valor"] == 7_648_000

    # editar y recalcular: otro monto adicional cambia el valor
    d = client.get(f"/api/avaluos/{a['id']}", headers=admin).json()
    d["data"]["comparables_inmuebles"]["monto_adicional"] = "100000"
    r = client.put(f"/api/avaluos/{a['id']}", json={"data": d["data"]}, headers=admin).json()
    assert r["calc"]["conclusion"]["valor"] == 7_748_000

    # busqueda
    assert any(x["id"] == a["id"] for x in client.get("/api/avaluos?q=Mariano", headers=admin).json())

    # excel + historial con versiones
    x1 = client.post(f"/api/avaluos/{a['id']}/documentos", json={"formato": "xlsx"}, headers=admin).json()
    x2 = client.post(f"/api/avaluos/{a['id']}/documentos", json={"formato": "xlsx"}, headers=admin).json()
    assert (x1["version"], x2["version"]) == (1, 2) and x1["nombre"].endswith("_v1.xlsx")
    assert len(client.get(f"/api/avaluos/{a['id']}/documentos", headers=admin).json()) == 2
    f = client.get(f"/api/documentos/{x2['id']}/descargar", headers=admin)
    assert f.status_code == 200 and f.content[:2] == b"PK"

    # duplicar y borrar
    c = client.post("/api/avaluos", json={"duplicar_de": a["id"]}, headers=admin).json()
    assert c["id"] != a["id"]
    assert client.delete(f"/api/avaluos/{a['id']}", headers=admin).status_code == 200
    assert client.get(f"/api/avaluos/{a['id']}", headers=admin).status_code == 404


def test_formato_invalido(client, admin):
    a = client.post("/api/avaluos", json={}, headers=admin).json()
    assert client.post(f"/api/avaluos/{a['id']}/documentos", json={"formato": "doc"}, headers=admin).status_code == 400


def test_subida_solo_imagenes(client, admin):
    a = client.post("/api/avaluos", json={}, headers=admin).json()
    malo = client.post(f"/api/avaluos/{a['id']}/archivos", data={"seccion": "anexo"},
                       files={"archivo": ("x.txt", io.BytesIO(b"hola"), "text/plain")}, headers=admin)
    assert malo.status_code == 400
    bueno = client.post(f"/api/avaluos/{a['id']}/archivos", data={"seccion": "portada"},
                        files={"archivo": ("f.png", io.BytesIO(b"\x89PNG\r\n"), "image/png")}, headers=admin)
    assert bueno.status_code == 200
    # la portada es unica: subir otra reemplaza
    client.post(f"/api/avaluos/{a['id']}/archivos", data={"seccion": "portada"},
                files={"archivo": ("g.png", io.BytesIO(b"\x89PNG\r\n"), "image/png")}, headers=admin)
    assert len(client.get(f"/api/avaluos/{a['id']}", headers=admin).json()["archivos"]) == 1


def test_roles(client, admin):
    r = client.post("/api/usuarios", json={"email": "val@test.local", "nombre": "Valuador", "password": "12345678"}, headers=admin)
    assert r.status_code == 200
    tok = client.post("/api/login", json={"email": "val@test.local", "password": "12345678"}).json()["token"]
    val = {"Authorization": f"Bearer {tok}"}
    assert client.get("/api/usuarios", headers=val).status_code == 403
    assert client.put("/api/configuracion", json={}, headers=val).status_code == 403
    a = client.post("/api/avaluos", json={}, headers=val).json()
    assert client.delete(f"/api/avaluos/{a['id']}", headers=val).status_code == 403  # solo admin borra
    assert client.post("/api/usuarios", json={"email": "val@test.local", "nombre": "x", "password": "12345678"}, headers=admin).status_code == 400
    assert client.post("/api/usuarios", json={"email": "otro@test.local", "nombre": "x", "password": "corta"}, headers=admin).status_code == 400
