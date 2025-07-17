"""
Locust Load Testing - BuyYourKawa API - VERSION CORRIGÉE
Tests de charge avec corrections des faux échecs et payloads complets
"""

import random
import json
from locust import HttpUser, task, between


class BuyYourKawaUser(HttpUser):
    """
    Utilisateur type pour tests de charge BuyYourKawa API - VERSION CORRIGÉE
    Corrections appliquées :
    - Accepte HTTP 200 pour POST /clients et POST /products
    - Payload complet pour POST /orders avec tous les champs requis
    - Gestion d'erreurs améliorée
    """
    wait_time = between(1, 3)
    
    def on_start(self):
        """Authentification au début de chaque session utilisateur"""
        self.authenticate()
        self.client_ids = []
        self.product_ids = []
        self.client_details = {}  # Cache des détails clients
        self.product_details = {}  # Cache des détails produits
    
    def authenticate(self):
        """Authentification JWT - endpoint critique à tester"""
        response = self.client.post("/token", data={
            "username": "admin",
            "password": "password"
        })
        
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.headers = {}
            print(f"Échec authentification: {response.status_code}")
    
    @task(3)
    def get_clients_list(self):
        """Test GET /clients - endpoint fréquemment utilisé"""
        with self.client.get("/clients", 
                           headers=self.headers,
                           catch_response=True) as response:
            if response.status_code == 200:
                clients = response.json()
                if clients:
                    # Stocker quelques IDs et détails pour les tests suivants
                    for client in clients[:5]:
                        if client.get("id"):
                            self.client_ids.append(client["id"])
                            self.client_details[client["id"]] = client
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")
    
    @task(2)
    def get_client_details(self):
        """Test GET /clients/{id} - consultation détails client"""
        if self.client_ids:
            client_id = random.choice(self.client_ids)
            with self.client.get(f"/clients/{client_id}", 
                               headers=self.headers,
                               catch_response=True) as response:
                if response.status_code == 200:
                    # Mettre à jour le cache des détails
                    self.client_details[client_id] = response.json()
                    response.success()
                elif response.status_code == 404:
                    response.success()  # 404 acceptable si client supprimé
                else:
                    response.failure(f"Got status {response.status_code}")
    
    @task(1)
    def create_client(self):
        """Test POST /clients - création client (CORRIGÉ: accepte HTTP 200)"""
        client_data = {
            "name": f"Client Test {random.randint(1000, 9999)}",
            "email": f"test{random.randint(1000, 9999)}@example.com",
            "phone": f"+33{random.randint(100000000, 999999999)}",
            "address": {
                "street": f"{random.randint(1, 999)} Rue de Test",
                "city": random.choice(["Paris", "Lyon", "Marseille", "Toulouse"]),
                "zip": f"{random.randint(10000, 99999)}",
                "country": "France"
            },
            "loyalty_points": 0,
            "is_active": True
        }
        
        with self.client.post("/clients", 
                            json=client_data,
                            headers=self.headers,
                            catch_response=True) as response:
            # CORRECTION: Accepter 200 ET 201 (au lieu de seulement 201)
            if response.status_code in [200, 201]:
                client = response.json()
                if client.get("id"):
                    self.client_ids.append(client["id"])
                    self.client_details[client["id"]] = client
                response.success()
            else:
                response.failure(f"Got status {response.status_code}: {response.text}")
    
    @task(1)
    def update_client(self):
        """Test PUT /clients/{id} - mise à jour client"""
        if self.client_ids:
            client_id = random.choice(self.client_ids)
            update_data = {
                "name": f"Client Updated {random.randint(1000, 9999)}",
                "email": f"updated{random.randint(1000, 9999)}@example.com",
                "phone": f"+33{random.randint(100000000, 999999999)}",
                "address": {
                    "street": f"{random.randint(1, 999)} Rue Updated",
                    "city": "Paris",
                    "zip": "75001",
                    "country": "France"
                },
                "loyalty_points": random.randint(0, 100),
                "is_active": True
            }
            
            with self.client.put(f"/clients/{client_id}", 
                               json=update_data,
                               headers=self.headers,
                               catch_response=True) as response:
                if response.status_code in [200, 404]:
                    response.success()
                else:
                    response.failure(f"Got status {response.status_code}")
    
    @task(2)
    def get_products(self):
        """Test GET /products - consultation produits"""
        with self.client.get("/products", 
                           headers=self.headers,
                           catch_response=True) as response:
            if response.status_code == 200:
                products = response.json()
                if products:
                    # Stocker IDs et détails pour les tests suivants
                    for product in products[:10]:
                        if product.get("id"):
                            self.product_ids.append(product["id"])
                            self.product_details[product["id"]] = product
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")
    
    @task(1)
    def create_product(self):
        """Test POST /products - création produit (CORRIGÉ: accepte HTTP 200)"""
        product_data = {
            "name": f"Produit Test {random.randint(1000, 9999)}",
            "description": "Produit de test pour charge",
            "price": round(random.uniform(1.0, 10.0), 2),
            "category": random.choice(["coffee", "tea", "pastry", "sandwich", "beverage"]),
            "stock_quantity": random.randint(10, 100),
            "is_available": True
        }
        
        with self.client.post("/products", 
                            json=product_data,
                            headers=self.headers,
                            catch_response=True) as response:
            # CORRECTION: Accepter 200 ET 201 (au lieu de seulement 201)
            if response.status_code in [200, 201]:
                product = response.json()
                if product.get("id"):
                    self.product_ids.append(product["id"])
                    self.product_details[product["id"]] = product
                response.success()
            else:
                response.failure(f"Got status {response.status_code}: {response.text}")
    
    @task(1)
    def create_order(self):
        """Test POST /orders - création commande (CORRIGÉ: payload complet)"""
        if self.client_ids and self.product_ids:
            # Sélectionner un client et des produits
            client_id = random.choice(self.client_ids)
            selected_products = random.sample(
                self.product_ids, 
                min(3, len(self.product_ids))
            )
            
            # CORRECTION: Construire payload complet avec tous les champs requis
            client_info = self.client_details.get(client_id, {})
            
            total_amount = 0
            items_with_details = []
            
            for product_id in selected_products:
                product_info = self.product_details.get(product_id, {})
                quantity = random.randint(1, 3)
                unit_price = product_info.get("price", 5.0)
                total_price = unit_price * quantity
                total_amount += total_price
                
                items_with_details.append({
                    "product_id": product_id,
                    "product_name": product_info.get("name", f"Product {product_id}"),
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": total_price
                })
            
            # Payload complet avec tous les champs requis
            order_data = {
                "client_id": client_id,
                "client_name": client_info.get("name", f"Client {client_id}"),
                "items": items_with_details,
                "total_amount": round(total_amount, 2),
                "status": "pending"
            }
            
            with self.client.post("/orders", 
                                json=order_data,
                                headers=self.headers,
                                catch_response=True) as response:
                if response.status_code in [200, 201]:
                    response.success()
                else:
                    response.failure(f"Got status {response.status_code}: {response.text}")
        else:
            # Pas assez de données pour créer une commande
            pass
    
    @task(2)
    def get_orders(self):
        """Test GET /orders - consultation commandes"""
        with self.client.get("/orders", 
                           headers=self.headers,
                           catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")
    
    @task(1)
    def get_analytics(self):
        """Test GET /analytics - endpoint lourd à tester (CORRIGÉ: paramètres étendus)"""
        # CORRECTION: Paramètres plus complets
        params = {
            "period": random.choice(["daily", "weekly", "monthly"]),
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }
        
        with self.client.get("/analytics", 
                           params=params,
                           headers=self.headers,
                           catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}: {response.text}")


# Configuration pour différents scénarios de test
class LightLoadUser(BuyYourKawaUser):
    """Utilisateur pour charge légère - tests de validation"""
    weight = 1
    wait_time = between(2, 5)


class NormalLoadUser(BuyYourKawaUser):
    """Utilisateur pour charge normale - tests quotidiens"""
    weight = 3
    wait_time = between(1, 3)


class HeavyLoadUser(BuyYourKawaUser):
    """Utilisateur pour charge lourde - tests de stress"""
    weight = 2
    wait_time = between(0.5, 2)


# Fonction utilitaire pour lancer les tests
def run_test_scenario(scenario="normal"):
    """
    Fonction helper pour lancer différents scénarios - VERSION CORRIGÉE
    
    Usage avec fichier corrigé:
    # Test validation (15 utilisateurs, 60s)
    locust -f locustfile_corrected.py --host=http://localhost:8000 --users 15 --spawn-rate 3 -t 60s --html=reports/validation_corrected.html --csv=reports/validation_corrected
    
    # Test normal (50 utilisateurs, 2 minutes)
    locust -f locustfile_corrected.py --host=http://localhost:8000 --users 50 --spawn-rate 5 -t 120s --html=reports/normal_corrected.html --csv=reports/normal_corrected
    
    # Test de stress (100 utilisateurs, 5 minutes)
    locust -f locustfile_corrected.py --host=http://localhost:8000 --users 100 --spawn-rate 10 -t 300s --html=reports/stress_corrected.html --csv=reports/stress_corrected
    """
    scenarios = {
        "validation": {"users": 15, "spawn_rate": 3, "time": "60s"},
        "normal": {"users": 50, "spawn_rate": 5, "time": "120s"},
        "peak": {"users": 80, "spawn_rate": 8, "time": "180s"},
        "stress": {"users": 100, "spawn_rate": 10, "time": "300s"}
    }
    
    return scenarios.get(scenario, scenarios["normal"])


# CORRECTIONS APPLIQUÉES :
# POST /clients : Accepte maintenant HTTP 200 (pas seulement 201)
# POST /products : Accepte maintenant HTTP 200 (pas seulement 201)  
# POST /orders : Payload complet avec client_name, unit_price, total_price, product_name
# GET /analytics : Paramètres étendus avec start_date et end_date
# Cache des détails clients/produits pour éviter les requêtes répétées
# Gestion d'erreurs améliorée avec messages détaillés
