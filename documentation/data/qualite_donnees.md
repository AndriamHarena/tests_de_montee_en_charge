# 1. Qualité des Données

## 1.1 Types de Données Manipulées

Ce document identifie les types de données manipulées par notre plateforme BuyYourKawa, leurs formats, contraintes et normes appliquées pour l'ensemble des 10 routes API.

### 1.1.1 Données Clients

| Champ               | Type    | Contraintes                             | Norme/Format            |
|---------------------|---------|----------------------------------------|-------------------------|
| client_id           | UUID    | non null, unique                       | RFC 4122               |
| name                | string  | non null, min 2 chars, max 100 chars   | UTF-8                  |
| email               | string  | non null, regex validation             | RFC 5322               |
| phone               | string  | non null, regex validation             | E.164 (format international) |
| loyalty_points      | integer | non null, >= 0                        | Entier positif         |
| is_active           | boolean | non null, default true                | true/false             |
| created_at          | datetime| non null, auto-generated               | ISO 8601               |
| updated_at          | datetime| non null, auto-updated                 | ISO 8601               |
| street              | string  | non null, max 200 chars                | UTF-8                  |
| city                | string  | non null, max 100 chars                | UTF-8                  |
| zip                 | string  | non null, max 20 chars                 | Alphanumérique         |
| country             | string  | non null, max 100 chars                | ISO 3166-1             |

### 1.1.2 Données Produits

| Champ               | Type    | Contraintes                             | Norme/Format            |
|---------------------|---------|----------------------------------------|-------------------------|
| product_id          | UUID    | non null, unique                       | RFC 4122               |
| name                | string  | non null, min 1 char, max 200 chars    | UTF-8                  |
| description         | string  | optional, max 1000 chars               | UTF-8                  |
| price               | decimal | non null, > 0, max 2 decimals          | Monétaire (EUR)        |
| category            | enum    | non null, valeurs prédéfinies          | ProductCategory        |
| stock_quantity      | integer | non null, >= 0                        | Entier positif         |
| is_available        | boolean | non null, default true                | true/false             |
| created_at          | datetime| non null, auto-generated               | ISO 8601               |
| updated_at          | datetime| non null, auto-updated                 | ISO 8601               |

**Catégories de produits** : `coffee`, `tea`, `pastry`, `sandwich`, `beverage`, `accessory`

### 1.1.3 Données Commandes

| Champ               | Type    | Contraintes                             | Norme/Format            |
|---------------------|---------|----------------------------------------|-------------------------|
| order_id            | UUID    | non null, unique                       | RFC 4122               |
| client_id           | UUID    | non null, foreign key                  | RFC 4122               |
| client_name         | string  | non null, max 100 chars                | UTF-8                  |
| total_amount        | decimal | non null, > 0, max 2 decimals          | Monétaire (EUR)        |
| status              | enum    | non null, valeurs prédéfinies          | OrderStatus            |
| notes               | string  | optional, max 500 chars                | UTF-8                  |
| created_at          | datetime| non null, auto-generated               | ISO 8601               |
| updated_at          | datetime| non null, auto-updated                 | ISO 8601               |

**Statuts de commande** : `pending`, `confirmed`, `preparing`, `ready`, `delivered`, `cancelled`

### 1.1.4 Données Articles de Commande

| Champ               | Type    | Contraintes                             | Norme/Format            |
|---------------------|---------|----------------------------------------|-------------------------|
| product_id          | UUID    | non null, foreign key                  | RFC 4122               |
| product_name        | string  | non null, max 200 chars                | UTF-8                  |
| quantity            | integer | non null, > 0                          | Entier positif         |
| unit_price          | decimal | non null, > 0, max 2 decimals          | Monétaire (EUR)        |
| total_price         | decimal | non null, > 0, max 2 decimals          | Monétaire (EUR)        |

### 1.1.5 Données Analytics

| Champ               | Type    | Contraintes                             | Norme/Format            |
|---------------------|---------|----------------------------------------|-------------------------|
| period              | enum    | non null, valeurs prédéfinies          | today/week/month/year  |
| total_sales         | decimal | non null, >= 0, max 2 decimals         | Monétaire (EUR)        |
| total_orders        | integer | non null, >= 0                        | Entier positif         |
| total_clients       | integer | non null, >= 0                        | Entier positif         |
| avg_order_value     | decimal | non null, >= 0, max 2 decimals         | Monétaire (EUR)        |
| top_products        | array   | liste des produits les plus vendus     | JSON Array             |
| generated_at        | datetime| non null, auto-generated               | ISO 8601               |

## 1.2 Formats d'Échange et Encodage

### API REST

- **Format de requête/réponse**: JSON
- **Encodage**: UTF-8
- **Content-Type**: application/json

### Exemples de Payloads

#### 1.2.1 Création Client

```json
{
  "name": "John Doe",
  "email": "john.doe@buyyourkawa.fr",
  "phone": "+33123456789",
  "loyalty_points": 150,
  "is_active": true,
  "address": {
    "street": "123 Rue de la Paix",
    "city": "Paris",
    "zip": "75001",
    "country": "France"
  }
}
```

#### 1.2.2 Création Produit

```json
{
  "name": "Espresso Traditionnel",
  "description": "Café espresso italien authentique",
  "price": 2.50,
  "category": "coffee",
  "stock_quantity": 100,
  "is_available": true
}
```

#### 1.2.3 Création Commande

```json
{
  "client_id": "123e4567-e89b-12d3-a456-426614174000",
  "client_name": "John Doe",
  "items": [
    {
      "product_id": "987fcdeb-51a2-43d7-b789-123456789abc",
      "product_name": "Espresso Traditionnel",
      "quantity": 2,
      "unit_price": 2.50,
      "total_price": 5.00
    },
    {
      "product_id": "456def78-9abc-12de-f345-678901234567",
      "product_name": "Croissant Beurre",
      "quantity": 1,
      "unit_price": 1.80,
      "total_price": 1.80
    }
  ],
  "total_amount": 6.80,
  "status": "pending",
  "notes": "Sans sucre pour l'espresso"
}
```

#### 1.2.4 Réponse Analytics

```json
{
  "period": "week",
  "total_sales": 1250.75,
  "total_orders": 89,
  "total_clients": 45,
  "avg_order_value": 14.05,
  "top_products": [
    {
      "product_id": "987fcdeb-51a2-43d7-b789-123456789abc",
      "name": "Espresso Traditionnel",
      "quantity_sold": 156,
      "revenue": 390.00
    },
    {
      "product_id": "456def78-9abc-12de-f345-678901234567",
      "name": "Cappuccino",
      "quantity_sold": 98,
      "revenue": 372.40
    }
  ],
  "generated_at": "2024-01-15T10:30:00Z"
}
```

## 1.3 Validation et Conformité

### Niveau API

- Validation automatique via Pydantic/FastAPI
- Sanitisation des entrées avant stockage
- Transformation des formats (ex: numéros de téléphone en format E.164)

### Niveau Base de Données

- Contraintes d'intégrité (clés primaires, clés étrangères)
- Indexes pour optimisation des requêtes
- Triggers pour maintenir created_at/updated_at
