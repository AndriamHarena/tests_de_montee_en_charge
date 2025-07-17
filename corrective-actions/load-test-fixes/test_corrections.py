"""
Script de validation des corrections Locust
Teste manuellement les endpoints pour vérifier les status codes réels
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_authentication():
    """Test d'authentification"""
    print("🔐 Test authentification...")
    try:
        response = requests.post(f"{BASE_URL}/token", data={
            "username": "admin",
            "password": "password"
        })
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"✅ Authentification réussie - Token obtenu")
            return {"Authorization": f"Bearer {token}"}
        else:
            print(f"❌ Échec authentification: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erreur authentification: {e}")
        return None

def test_post_clients(headers):
    """Test POST /clients - vérifier le status code réel"""
    print("\n👤 Test POST /clients...")
    
    client_data = {
        "name": f"Test Client {datetime.now().strftime('%H%M%S')}",
        "email": f"test{datetime.now().strftime('%H%M%S')}@example.com",
        "phone": "+33123456789",
        "address": {
            "street": "123 Rue de Test",
            "city": "Paris",
            "zip": "75001",
            "country": "France"
        },
        "loyalty_points": 0,
        "is_active": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/clients", json=client_data, headers=headers)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text[:200]}...")
        
        if response.status_code in [200, 201]:
            client = response.json()
            client_id = client.get("id")
            print(f"✅ POST /clients réussi - ID: {client_id}")
            return client_id
        else:
            print(f"❌ POST /clients échoué: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erreur POST /clients: {e}")
        return None

def test_post_products(headers):
    """Test POST /products - vérifier le status code réel"""
    print("\n📦 Test POST /products...")
    
    product_data = {
        "name": f"Test Product {datetime.now().strftime('%H%M%S')}",
        "description": "Produit de test",
        "price": 5.99,
        "category": "coffee",
        "stock_quantity": 100,
        "is_available": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/products", json=product_data, headers=headers)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text[:200]}...")
        
        if response.status_code in [200, 201]:
            product = response.json()
            product_id = product.get("id")
            print(f"✅ POST /products réussi - ID: {product_id}")
            return product_id
        else:
            print(f"❌ POST /products échoué: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erreur POST /products: {e}")
        return None

def test_post_orders(headers, client_id, product_id):
    """Test POST /orders avec payload complet"""
    print("\n🛒 Test POST /orders...")
    
    if not client_id or not product_id:
        print("❌ Impossible de tester POST /orders - client_id ou product_id manquant")
        return None
    
    # Payload complet avec tous les champs requis
    order_data = {
        "client_id": client_id,
        "client_name": f"Test Client {client_id}",
        "items": [
            {
                "product_id": product_id,
                "product_name": f"Test Product {product_id}",
                "quantity": 2,
                "unit_price": 5.99,
                "total_price": 11.98
            }
        ],
        "total_amount": 11.98,
        "status": "pending"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/orders", json=order_data, headers=headers)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text[:200]}...")
        
        if response.status_code in [200, 201]:
            order = response.json()
            order_id = order.get("id")
            print(f"✅ POST /orders réussi - ID: {order_id}")
            return order_id
        else:
            print(f"❌ POST /orders échoué: {response.status_code}")
            print(f"📄 Erreur détaillée: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erreur POST /orders: {e}")
        return None

def test_get_analytics(headers):
    """Test GET /analytics avec paramètres"""
    print("\n📈 Test GET /analytics...")
    
    params = {
        "period": "daily",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/analytics", params=params, headers=headers)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print(f"✅ GET /analytics réussi")
            return True
        else:
            print(f"❌ GET /analytics échoué: {response.status_code}")
            print(f"📄 Erreur détaillée: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur GET /analytics: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 VALIDATION DES CORRECTIONS LOCUST")
    print("=" * 50)
    
    # Test d'authentification
    headers = test_authentication()
    if not headers:
        print("❌ Impossible de continuer sans authentification")
        sys.exit(1)
    
    # Tests des endpoints
    client_id = test_post_clients(headers)
    product_id = test_post_products(headers)
    order_id = test_post_orders(headers, client_id, product_id)
    analytics_ok = test_get_analytics(headers)
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    results = {
        "POST /clients": "✅ OK" if client_id else "❌ ÉCHEC",
        "POST /products": "✅ OK" if product_id else "❌ ÉCHEC", 
        "POST /orders": "✅ OK" if order_id else "❌ ÉCHEC",
        "GET /analytics": "✅ OK" if analytics_ok else "❌ ÉCHEC"
    }
    
    for endpoint, status in results.items():
        print(f"{endpoint}: {status}")
    
    success_count = sum(1 for result in [client_id, product_id, order_id, analytics_ok] if result)
    print(f"\n🎯 Score: {success_count}/4 endpoints fonctionnels")
    
    if success_count == 4:
        print("✅ Tous les tests passent ! Les corrections sont validées.")
        print("🚀 Vous pouvez maintenant utiliser locustfile_corrected.py")
    else:
        print("⚠️ Certains tests échouent. Vérifiez l'API et les corrections.")

if __name__ == "__main__":
    main()
