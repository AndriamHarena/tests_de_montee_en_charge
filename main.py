from fastapi import FastAPI, HTTPException, Depends, Request, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from prometheus_client import Counter, Histogram, generate_latest
from models import (
    Client, Address, Product, Order, OrderItem, Analytics, 
    Inventory, StockMovement, OrderStatus, ProductCategory
)
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
import jwt
import random

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

app = FastAPI(
    title="BuyYourKawa API",
    description="API de gestion complète pour coffee shop",
    version="2.0.0"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Prometheus metrics
REQUEST_COUNT = Counter('request_count', 'Total number of requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency', ['method', 'endpoint'])
REQUEST_SUCCESS = Counter('request_success', 'Number of successful requests', ['method', 'endpoint'])
REQUEST_FAILURE = Counter('request_failure', 'Number of failed requests', ['method', 'endpoint'])

# Bases de données simulées en mémoire
clients_db = []
products_db = []
orders_db = []
stock_movements_db = []

# Données de test initiales
def init_sample_data():
    # Produits de base
    sample_products = [
        Product(id="1", name="Espresso", description="Café espresso traditionnel", price=2.50, category=ProductCategory.COFFEE, stock_quantity=100),
        Product(id="2", name="Cappuccino", description="Café avec mousse de lait", price=3.80, category=ProductCategory.COFFEE, stock_quantity=80),
        Product(id="3", name="Croissant", description="Viennoiserie française", price=1.90, category=ProductCategory.PASTRY, stock_quantity=50),
        Product(id="4", name="Thé Earl Grey", description="Thé noir aromatisé", price=2.20, category=ProductCategory.TEA, stock_quantity=60),
        Product(id="5", name="Sandwich Jambon", description="Sandwich jambon beurre", price=4.50, category=ProductCategory.SANDWICH, stock_quantity=30)
    ]
    products_db.extend(sample_products)

init_sample_data()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    method = request.method
    endpoint = request.url.path
    REQUEST_COUNT.labels(method, endpoint).inc()
    with REQUEST_LATENCY.labels(method, endpoint).time():
        response = await call_next(request)
        if 200 <= response.status_code < 300:
            REQUEST_SUCCESS.labels(method, endpoint).inc()
        else:
            REQUEST_FAILURE.labels(method, endpoint).inc()
    return response

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(username: str, password: str):
    # Simulation d'authentification simple
    if username == "admin" and password == "password":
        return {"username": username, "role": "admin"}
    return None

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ============================================================================
# ROUTE 1: Authentification
# ============================================================================
@app.post("/token", tags=["Authentication"])
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authentification et génération de token JWT"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

# ============================================================================
# ROUTES 2-5: Gestion des clients (CRUD)
# ============================================================================
@app.post("/clients", response_model=Client, tags=["Clients"])
def create_client(client: Client, token: str = Depends(oauth2_scheme)):
    """Créer un nouveau client"""
    current_user = get_current_user(token)
    client.id = str(uuid.uuid4())
    client.created_at = datetime.now()
    client.updated_at = datetime.now()
    clients_db.append(client)
    return client

@app.get("/clients", response_model=List[Client], tags=["Clients"])
def get_clients(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), token: str = Depends(oauth2_scheme)):
    """Récupérer la liste des clients avec pagination"""
    current_user = get_current_user(token)
    return clients_db[skip:skip + limit]

@app.get("/clients/{client_id}", response_model=Client, tags=["Clients"])
def get_client(client_id: str, token: str = Depends(oauth2_scheme)):
    """Récupérer un client spécifique"""
    current_user = get_current_user(token)
    client = next((c for c in clients_db if c.id == client_id), None)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@app.put("/clients/{client_id}", response_model=Client, tags=["Clients"])
def update_client(client_id: str, client: Client, token: str = Depends(oauth2_scheme)):
    """Mettre à jour un client"""
    current_user = get_current_user(token)
    stored_client = next((c for c in clients_db if c.id == client_id), None)
    if not stored_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Mise à jour des champs
    stored_client.name = client.name
    stored_client.email = client.email
    stored_client.phone = client.phone
    stored_client.address = client.address
    stored_client.loyalty_points = client.loyalty_points
    stored_client.is_active = client.is_active
    stored_client.updated_at = datetime.now()
    return stored_client

# ============================================================================
# ROUTES 6-7: Gestion des produits
# ============================================================================
@app.get("/products", response_model=List[Product], tags=["Products"])
def get_products(category: Optional[ProductCategory] = None, available_only: bool = True, token: str = Depends(oauth2_scheme)):
    """Récupérer la liste des produits avec filtres"""
    current_user = get_current_user(token)
    filtered_products = products_db
    
    if category:
        filtered_products = [p for p in filtered_products if p.category == category]
    if available_only:
        filtered_products = [p for p in filtered_products if p.is_available and p.stock_quantity > 0]
    
    return filtered_products

@app.post("/products", response_model=Product, tags=["Products"])
def create_product(product: Product, token: str = Depends(oauth2_scheme)):
    """Créer un nouveau produit"""
    current_user = get_current_user(token)
    product.id = str(uuid.uuid4())
    product.created_at = datetime.now()
    product.updated_at = datetime.now()
    products_db.append(product)
    return product

# ============================================================================
# ROUTES 8-9: Gestion des commandes
# ============================================================================
@app.post("/orders", response_model=Order, tags=["Orders"])
def create_order(order: Order, token: str = Depends(oauth2_scheme)):
    """Créer une nouvelle commande"""
    current_user = get_current_user(token)
    
    # Vérifier que le client existe
    client = next((c for c in clients_db if c.id == order.client_id), None)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Vérifier la disponibilité des produits
    for item in order.items:
        product = next((p for p in products_db if p.id == item.product_id), None)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.stock_quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")
    
    # Créer la commande
    order.id = str(uuid.uuid4())
    order.created_at = datetime.now()
    order.updated_at = datetime.now()
    orders_db.append(order)
    
    # Mettre à jour les stocks
    for item in order.items:
        product = next((p for p in products_db if p.id == item.product_id), None)
        product.stock_quantity -= item.quantity
    
    return order

@app.get("/orders", response_model=List[Order], tags=["Orders"])
def get_orders(status: Optional[OrderStatus] = None, client_id: Optional[str] = None, token: str = Depends(oauth2_scheme)):
    """Récupérer les commandes avec filtres"""
    current_user = get_current_user(token)
    filtered_orders = orders_db
    
    if status:
        filtered_orders = [o for o in filtered_orders if o.status == status]
    if client_id:
        filtered_orders = [o for o in filtered_orders if o.client_id == client_id]
    
    return filtered_orders

# ============================================================================
# ROUTE 10: Analytics et reporting
# ============================================================================
@app.get("/analytics", response_model=Analytics, tags=["Analytics"])
def get_analytics(period: str = Query("today", pattern="^(today|week|month|year)$"), token: str = Depends(oauth2_scheme)):
    """Récupérer les analytics de vente"""
    current_user = get_current_user(token)
    
    # Calculs simulés basés sur les données
    total_orders = len(orders_db)
    total_revenue = sum(order.total_amount for order in orders_db)
    average_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    # Top produits (simulation)
    product_sales = {}
    for order in orders_db:
        for item in order.items:
            if item.product_name not in product_sales:
                product_sales[item.product_name] = 0
            product_sales[item.product_name] += item.quantity
    
    top_products = [
        {"name": name, "quantity_sold": qty} 
        for name, qty in sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
    
    return Analytics(
        period=period,
        total_orders=total_orders,
        total_revenue=total_revenue,
        average_order_value=average_order_value,
        top_products=top_products,
        client_count=len(clients_db)
    )

# ============================================================================
# ROUTE BONUS: Métriques Prometheus
# ============================================================================
@app.get("/metrics", tags=["Monitoring"])
def metrics():
    """Métriques Prometheus pour monitoring"""
    return generate_latest()

# ============================================================================
# DÉMARRAGE DE L'APPLICATION
# ============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
