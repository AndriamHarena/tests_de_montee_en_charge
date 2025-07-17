from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

def get_test_token():
    response = client.post(
        "/token",
        data={"username": "test", "password": "test"}
    )
    return response.json()["access_token"]

def test_token_auth():
    response = client.post(
        "/token",
        data={"username": "test", "password": "test"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_client_creation():
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        "/clients",
        json={
            "name": "Test Client",
            "email": "test@example.com",
            "phone": "+33123456789",
            "address": {
                "street": "123 Rue Test",
                "city": "Paris",
                "zip": "75000",
                "country": "France"
            }
        },
        headers=headers
    )
    assert response.status_code == 200
    assert "id" in response.json()

def test_invalid_phone():
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        "/clients",
        json={
            "name": "Test Client",
            "email": "test@example.com",
            "phone": "123456789",  # Format invalide
            "address": {
                "street": "123 Rue Test",
                "city": "Paris",
                "zip": "75000",
                "country": "France"
            }
        },
        headers=headers
    )
    assert response.status_code == 422
    assert "Format : +33XYYYYYYY" in response.json()["detail"][0]["msg"]

def test_invalid_zip():
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        "/clients",
        json={
            "name": "Test Client",
            "email": "test@example.com",
            "phone": "+33123456789",
            "address": {
                "street": "123 Rue Test",
                "city": "Paris",
                "zip": "750000",  # Format invalide (6 chiffres)
                "country": "France"
            }
        },
        headers=headers
    )
    assert response.status_code == 422
    assert "5 chiffres requis" in response.json()["detail"][0]["msg"]

def test_client_update():
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Créer un client
    response = client.post(
        "/clients",
        json={
            "name": "Test Client",
            "email": "test@example.com",
            "phone": "+33123456789",
            "address": {
                "street": "123 Rue Test",
                "city": "Paris",
                "zip": "75000",
                "country": "France"
            }
        },
        headers=headers
    )
    client_id = response.json()["id"]
    
    # Mettre à jour le client
    response = client.put(
        f"/clients/{client_id}",
        json={
            "name": "Test Client Updated",
            "email": "test_updated@example.com",
            "phone": "+33123456789",
            "address": {
                "street": "123 Rue Test Updated",
                "city": "Paris",
                "zip": "75000",
                "country": "France"
            }
        },
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test Client Updated"

def test_client_delete():
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Créer un client
    response = client.post(
        "/clients",
        json={
            "name": "Test Client",
            "email": "test@example.com",
            "phone": "+33123456789",
            "address": {
                "street": "123 Rue Test",
                "city": "Paris",
                "zip": "75000",
                "country": "France"
            }
        },
        headers=headers
    )
    client_id = response.json()["id"]
    
    # Supprimer le client
    response = client.delete(
        f"/clients/{client_id}",
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Client deleted successfully"
