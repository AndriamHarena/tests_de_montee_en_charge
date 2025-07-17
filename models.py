# models.py
from pydantic import BaseModel, EmailStr, Field
from pydantic import field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
import re

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class ProductCategory(str, Enum):
    COFFEE = "coffee"
    TEA = "tea"
    PASTRY = "pastry"
    SANDWICH = "sandwich"
    BEVERAGE = "beverage"
    ACCESSORY = "accessory"

class Address(BaseModel):
    street: str = Field(..., min_length=2, max_length=100, description="Adresse de rue")
    city: str = Field(..., min_length=2, max_length=50, description="Ville")
    zip: str = Field(..., min_length=5, max_length=10, description="Code postal")
    country: str = Field(default="France", min_length=2, max_length=50, description="Pays")

    @field_validator('zip')
    def validate_zip(cls, v):
        # Validation pour les codes postaux français (5 chiffres)
        if not re.match(r'^\d{5}$', v):
            raise ValueError('Code postal invalide. Doit contenir 5 chiffres.')
        return v

class Client(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=2, max_length=100, description="Nom complet du client")
    email: EmailStr = Field(..., description="Email valide selon RFC 5322")
    phone: str = Field(..., min_length=10, max_length=20, description="Numéro de téléphone")
    address: Address
    loyalty_points: int = Field(default=0, ge=0, description="Points de fidélité")
    is_active: bool = Field(default=True, description="Client actif")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator('phone')
    def validate_phone(cls, v):
        # Validation pour les numéros de téléphone français
        if not re.match(r'^\+?33[1-9]\d{8}$', v):
            raise ValueError('Numéro de téléphone invalide. Format : +33XYYYYYYY')
        return v

class Product(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=2, max_length=100, description="Nom du produit")
    description: str = Field(..., min_length=10, max_length=500, description="Description du produit")
    price: float = Field(..., gt=0, le=100, description="Prix en euros")
    category: ProductCategory = Field(..., description="Catégorie du produit")
    is_available: bool = Field(default=True, description="Produit disponible")
    stock_quantity: int = Field(default=0, ge=0, description="Quantité en stock")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator('price')
    def validate_price(cls, v):
        # Prix avec 2 décimales maximum
        return round(v, 2)

class OrderItem(BaseModel):
    product_id: str = Field(..., description="ID du produit")
    product_name: str = Field(..., description="Nom du produit")
    quantity: int = Field(..., gt=0, le=20, description="Quantité commandée")
    unit_price: float = Field(..., gt=0, description="Prix unitaire")
    total_price: float = Field(..., gt=0, description="Prix total de la ligne")

class Order(BaseModel):
    id: Optional[str] = None
    client_id: str = Field(..., description="ID du client")
    client_name: str = Field(..., description="Nom du client")
    items: List[OrderItem] = Field(..., min_items=1, description="Articles commandés")
    total_amount: float = Field(..., gt=0, description="Montant total")
    status: OrderStatus = Field(default=OrderStatus.PENDING, description="Statut de la commande")
    notes: Optional[str] = Field(None, max_length=500, description="Notes spéciales")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator('total_amount')
    def validate_total_amount(cls, v):
        return round(v, 2)

class Analytics(BaseModel):
    period: str = Field(..., description="Période d'analyse")
    total_orders: int = Field(..., ge=0, description="Nombre total de commandes")
    total_revenue: float = Field(..., ge=0, description="Chiffre d'affaires total")
    average_order_value: float = Field(..., ge=0, description="Panier moyen")
    top_products: List[dict] = Field(..., description="Produits les plus vendus")
    client_count: int = Field(..., ge=0, description="Nombre de clients")
    generated_at: datetime = Field(default_factory=datetime.now, description="Date de génération")

class Inventory(BaseModel):
    product_id: str = Field(..., description="ID du produit")
    product_name: str = Field(..., description="Nom du produit")
    current_stock: int = Field(..., ge=0, description="Stock actuel")
    min_stock: int = Field(..., ge=0, description="Stock minimum")
    max_stock: int = Field(..., ge=0, description="Stock maximum")
    last_restock: Optional[datetime] = Field(None, description="Dernier réapprovisionnement")
    needs_restock: bool = Field(..., description="Besoin de réapprovisionnement")

class StockMovement(BaseModel):
    id: Optional[str] = None
    product_id: str = Field(..., description="ID du produit")
    movement_type: str = Field(..., pattern="^(in|out|adjustment)$", description="Type de mouvement")
    quantity: int = Field(..., description="Quantité (positive ou négative)")
    reason: str = Field(..., min_length=3, max_length=200, description="Raison du mouvement")
    created_at: Optional[datetime] = None
    created_by: str = Field(..., description="Utilisateur qui a effectué le mouvement")
