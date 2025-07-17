import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Configuration du test
export let options = {
  stages: [
    { duration: '30s', target: 10 },  // Montée progressive
    { duration: '60s', target: 10 },  // Maintien
    { duration: '30s', target: 0 },   // Descente
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000'], // 95% des requêtes < 1s
    http_req_failed: ['rate<0.05'],    // Moins de 5% d'erreurs
  },
};

// Métriques personnalisées
const errorRate = new Rate('errors');

// Configuration de base
const BASE_URL = 'http://localhost:8000';
let authToken = '';

// Données de test
const testClient = {
  nom: 'Client Test K6',
  email: `test-k6-${Date.now()}@example.com`,
  telephone: '+33123456789'
};

const testProduct = {
  nom: 'Café Test K6',
  description: 'Café de test pour k6',
  prix: 4.50,
  categorie: 'coffee',
  stock: 100
};

export function setup() {
  // Authentification initiale
  const authResponse = http.post(`${BASE_URL}/token`, {
    username: 'admin',
    password: 'secret123'
  });
  
  if (authResponse.status === 200) {
    const token = JSON.parse(authResponse.body).access_token;
    console.log('✅ Authentification réussie');
    return { token: token };
  } else {
    console.log('❌ Échec authentification');
    return { token: null };
  }
}

export default function(data) {
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': data.token ? `Bearer ${data.token}` : ''
  };

  // Test 1: Création d'un client
  const clientResponse = http.post(`${BASE_URL}/clients`, JSON.stringify(testClient), {
    headers: headers
  });
  
  const clientSuccess = check(clientResponse, {
    'Client créé avec succès': (r) => r.status === 200 || r.status === 201,
    'Temps de réponse client < 500ms': (r) => r.timings.duration < 500,
  });
  
  if (!clientSuccess) {
    errorRate.add(1);
    console.log(`❌ Erreur création client: ${clientResponse.status}`);
  }

  sleep(0.5);

  // Test 2: Récupération des clients
  const getClientsResponse = http.get(`${BASE_URL}/clients`, { headers: headers });
  
  const getClientsSuccess = check(getClientsResponse, {
    'Liste clients récupérée': (r) => r.status === 200,
    'Temps de réponse liste < 300ms': (r) => r.timings.duration < 300,
  });
  
  if (!getClientsSuccess) {
    errorRate.add(1);
  }

  sleep(0.5);

  // Test 3: Création d'un produit
  const productResponse = http.post(`${BASE_URL}/products`, JSON.stringify(testProduct), {
    headers: headers
  });
  
  const productSuccess = check(productResponse, {
    'Produit créé avec succès': (r) => r.status === 200 || r.status === 201,
    'Temps de réponse produit < 500ms': (r) => r.timings.duration < 500,
  });
  
  if (!productSuccess) {
    errorRate.add(1);
  }

  sleep(0.5);

  // Test 4: Récupération des produits
  const getProductsResponse = http.get(`${BASE_URL}/products`, { headers: headers });
  
  check(getProductsResponse, {
    'Liste produits récupérée': (r) => r.status === 200,
    'Temps de réponse produits < 300ms': (r) => r.timings.duration < 300,
  });

  sleep(0.5);

  // Test 5: Analytics (si disponible)
  if (data.token) {
    const analyticsResponse = http.get(`${BASE_URL}/analytics?period=day&limit=10`, {
      headers: headers
    });
    
    check(analyticsResponse, {
      'Analytics récupérées': (r) => r.status === 200,
      'Temps de réponse analytics < 800ms': (r) => r.timings.duration < 800,
    });
  }

  sleep(1);
}

export function teardown(data) {
  console.log('🏁 Test k6 terminé');
  console.log(`Token utilisé: ${data.token ? 'Oui' : 'Non'}`);
}
