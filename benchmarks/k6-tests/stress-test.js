import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Configuration du test de stress
export let options = {
  stages: [
    { duration: '2m', target: 50 },   // Montée à 50 users
    { duration: '3m', target: 50 },   // Maintien 50 users
    { duration: '2m', target: 100 },  // Montée à 100 users
    { duration: '3m', target: 100 },  // Maintien 100 users
    { duration: '2m', target: 0 },    // Descente
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% des requêtes < 2s
    http_req_failed: ['rate<0.1'],     // Moins de 10% d'erreurs
    'group_duration{group:::API Workflow}': ['p(95)<3000'],
  },
};

// Métriques personnalisées
const errorRate = new Rate('api_errors');
const apiDuration = new Trend('api_workflow_duration');

const BASE_URL = 'http://localhost:8000';

export function setup() {
  // Test de connectivité
  const healthCheck = http.get(`${BASE_URL}/docs`);
  if (healthCheck.status !== 200) {
    console.log('❌ API non disponible');
    return { apiAvailable: false };
  }
  
  // Authentification
  const authResponse = http.post(`${BASE_URL}/token`, {
    username: 'admin',
    password: 'secret123'
  });
  
  return {
    apiAvailable: true,
    token: authResponse.status === 200 ? JSON.parse(authResponse.body).access_token : null
  };
}

export default function(data) {
  if (!data.apiAvailable) {
    console.log('API non disponible, arrêt du test');
    return;
  }

  const headers = {
    'Content-Type': 'application/json',
    'Authorization': data.token ? `Bearer ${data.token}` : ''
  };

  // Workflow API complet
  const workflowStart = Date.now();

  // 1. Création client
  const clientData = {
    nom: `Client-${__VU}-${__ITER}`,
    email: `client-${__VU}-${__ITER}@test.com`,
    telephone: `+3312345${String(__VU).padStart(4, '0')}`
  };

  const clientResponse = http.post(`${BASE_URL}/clients`, JSON.stringify(clientData), {
    headers: headers
  });

  const clientOk = check(clientResponse, {
    'Client créé': (r) => r.status === 200 || r.status === 201,
  });

  if (!clientOk) {
    errorRate.add(1);
  }

  sleep(0.2);

  // 2. Liste des clients
  const getClientsResponse = http.get(`${BASE_URL}/clients?limit=20`, {
    headers: headers
  });

  check(getClientsResponse, {
    'Liste clients OK': (r) => r.status === 200,
  });

  sleep(0.2);

  // 3. Création produit
  const productData = {
    nom: `Produit-${__VU}-${__ITER}`,
    description: `Produit de test VU${__VU} Iter${__ITER}`,
    prix: Math.round((Math.random() * 10 + 1) * 100) / 100,
    categorie: ['coffee', 'tea', 'pastry'][Math.floor(Math.random() * 3)],
    stock: Math.floor(Math.random() * 100) + 10
  };

  const productResponse = http.post(`${BASE_URL}/products`, JSON.stringify(productData), {
    headers: headers
  });

  const productOk = check(productResponse, {
    'Produit créé': (r) => r.status === 200 || r.status === 201,
  });

  if (!productOk) {
    errorRate.add(1);
  }

  sleep(0.2);

  // 4. Liste des produits
  const getProductsResponse = http.get(`${BASE_URL}/products?limit=20`, {
    headers: headers
  });

  check(getProductsResponse, {
    'Liste produits OK': (r) => r.status === 200,
  });

  sleep(0.2);

  // 5. Création commande (si client et produit créés)
  if (clientOk && productOk) {
    const orderData = {
      client_id: 1, // ID simplifié pour le test
      items: [
        {
          product_id: 1,
          quantite: Math.floor(Math.random() * 3) + 1,
          prix_unitaire: productData.prix
        }
      ],
      total: productData.prix * 2
    };

    const orderResponse = http.post(`${BASE_URL}/orders`, JSON.stringify(orderData), {
      headers: headers
    });

    check(orderResponse, {
      'Commande créée': (r) => r.status === 200 || r.status === 201,
    });
  }

  sleep(0.3);

  // 6. Analytics (si token disponible)
  if (data.token) {
    const analyticsResponse = http.get(`${BASE_URL}/analytics?period=day`, {
      headers: headers
    });

    check(analyticsResponse, {
      'Analytics OK': (r) => r.status === 200,
    });
  }

  // Enregistrer la durée totale du workflow
  const workflowDuration = Date.now() - workflowStart;
  apiDuration.add(workflowDuration);

  sleep(1);
}

export function teardown(data) {
  console.log('🏁 Test de stress k6 terminé');
  console.log(`API disponible: ${data.apiAvailable}`);
  console.log(`Token utilisé: ${data.token ? 'Oui' : 'Non'}`);
}
