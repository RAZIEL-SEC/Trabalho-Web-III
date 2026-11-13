from fastapi.testclient import TestClient

def test_criar_grupo_e_subgrupo(client_autenticado: TestClient):
    grupo = client_autenticado.post("/classificacoes/grupos", json={"nome": "Alimentação"})
    assert grupo.status_code == 201
    grupo_id = grupo.json()["id"]
    subgrupo = client_autenticado.post("/classificacoes/subgrupos", json={"nome": "Grãos", "grupo_id": grupo_id})
    assert subgrupo.status_code == 201
    assert subgrupo.json()["grupo_id"] == grupo_id
    assert any(g["id"] == grupo_id for g in client_autenticado.get("/classificacoes/grupos").json())
    assert any(s["id"] == subgrupo.json()["id"] for s in client_autenticado.get(f"/classificacoes/subgrupos?grupo_id={grupo_id}").json())

def test_item_pode_ser_associado_a_subgrupo(client_autenticado: TestClient):
    grupo = client_autenticado.post("/classificacoes/grupos", json={"nome": "Alimentação"}).json()
    subgrupo = client_autenticado.post("/classificacoes/subgrupos", json={"nome": "Grãos", "grupo_id": grupo["id"]}).json()
    item = client_autenticado.post("/itens", json={"nome": "Arroz", "unidade": "kg", "subgrupo_id": subgrupo["id"]})
    assert item.status_code == 201
    assert item.json()["subgrupo_id"] == subgrupo["id"]

def test_nao_desativa_subgrupo_com_itens_ativos(client_autenticado: TestClient):
    grupo = client_autenticado.post("/classificacoes/grupos", json={"nome": "Alimentação"}).json()
    subgrupo = client_autenticado.post("/classificacoes/subgrupos", json={"nome": "Grãos", "grupo_id": grupo["id"]}).json()
    item = client_autenticado.post("/itens", json={"nome": "Arroz", "unidade": "kg", "subgrupo_id": subgrupo["id"]})
    assert item.status_code == 201
    response = client_autenticado.delete(f"/classificacoes/subgrupos/{subgrupo['id']}")
    assert response.status_code == 409
