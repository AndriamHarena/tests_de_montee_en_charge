import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';

// Métriques personnalisées
const authErrors = new Counter('auth_errors');
const validationErrors = new Counter('validation_errors');
const successRate = new Rate('success_rate');
const responseTime = new Trend('response_time');

// Configuration du test de validation
export const options = {
    stages: [
        { duration: '30s', target: 5 },   // Montée douce
        { duration: '60s', target: 10 },  // Maintien validation
        { duration: '30s', target: 0 },   // Descente
    ],
    thresholds: {
        http_req_duration: ['p(95)<1000'],
        http_req_failed: ['rate<0.05'],
        success_rate: ['rate>0.95'],
        auth_errors: ['count<5'],
        validation_errors: ['count<10']
    }
};

let authToken = '';

export function setup() {
    console.log('Configuration du test de validation k6');
    
    // Authentification initiale
    const authResponse = http.post('http://localhost:8000/token', {
        username: 'admin',
        password: 'secret123'
    }, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    
    if (authResponse.status === 200) {
        const token = JSON.parse(authResponse.body).access_token;
        console.log('Authentification réussie pour setup');
        return { token: token };
    } else {
        console.error('Échec authentification setup');
        return { token: null };
    }
}

export default function(data) {
    const baseUrl = 'http://localhost:8000';
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${data.token}`
    };
    
    // Test 1: Validation de l'authentification
    const authResponse = http.post(`${baseUrl}/token`, {
        username: 'admin',
        password: 'secret123'
    }, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    
    const authSuccess = check(authResponse, {
        'Auth: Status 200': (r) => r.status === 200,
        'Auth: Token présent': (r) => JSON.parse(r.body).access_token !== undefined,
        'Auth: Temps < 500ms': (r) => r.timings.duration < 500
    });
    
    if (!authSuccess) {
        authErrors.add(1);
    }
    
    // Test 2: Validation création client
    const clientData = {
        name: `Client-Test-${__VU}-${__ITER}`,
        email: `test${__VU}${__ITER}@validation.com`,
        phone: `+33${Math.floor(Math.random() * 1000000000)}`
    };
    
    const clientResponse = http.post(`${baseUrl}/clients`, JSON.stringify(clientData), { headers });
    
    const clientSuccess = check(clientResponse, {
        'Client: Status 200 ou 201': (r) => r.status === 200 || r.status === 201,
        'Client: ID présent': (r) => JSON.parse(r.body).id !== undefined,
        'Client: Nom correct': (r) => JSON.parse(r.body).name === clientData.name,
        'Client: Email correct': (r) => JSON.parse(r.body).email === clientData.email
    });
    
    if (!clientSuccess) {
        validationErrors.add(1);
    }
    
    // Test 3: Validation récupération clients
    const getClientsResponse = http.get(`${baseUrl}/clients`, { headers });
    
    const getClientsSuccess = check(getClientsResponse, {
        'Get Clients: Status 200': (r) => r.status === 200,
        'Get Clients: Liste présente': (r) => Array.isArray(JSON.parse(r.body)),
        'Get Clients: Temps < 300ms': (r) => r.timings.duration < 300
    });
    
    // Test 4: Validation création produit
    const productData = {
        name: `Produit-Test-${__VU}-${__ITER}`,
        price: Math.floor(Math.random() * 50) + 5,
        category: ['coffee', 'tea', 'pastry'][Math.floor(Math.random() * 3)],
        description: `Description produit test ${__VU}-${__ITER}`
    };
    
    const productResponse = http.post(`${baseUrl}/products`, JSON.stringify(productData), { headers });
    
    const productSuccess = check(productResponse, {
        'Product: Status 200 ou 201': (r) => r.status === 200 || r.status === 201,
        'Product: ID présent': (r) => JSON.parse(r.body).id !== undefined,
        'Product: Prix correct': (r) => JSON.parse(r.body).price === productData.price
    });
    
    if (!productSuccess) {
        validationErrors.add(1);
    }
    
    // Test 5: Validation analytics
    const analyticsResponse = http.get(`${baseUrl}/analytics`, { headers });
    
    const analyticsSuccess = check(analyticsResponse, {
        'Analytics: Status 200': (r) => r.status === 200,
        'Analytics: Données présentes': (r) => {
            const body = JSON.parse(r.body);
            return body.total_clients !== undefined && body.total_products !== undefined;
        }
    });
    
    // Calcul du taux de succès global
    const globalSuccess = authSuccess && clientSuccess && getClientsSuccess && productSuccess && analyticsSuccess;
    successRate.add(globalSuccess ? 1 : 0);
    responseTime.add(authResponse.timings.duration + clientResponse.timings.duration + getClientsResponse.timings.duration);
    
    sleep(1);
}

export function teardown(data) {
    console.log('Nettoyage du test de validation k6');
}

export function handleSummary(data) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    
    return {
        [`k6-tests/results/validation-${timestamp}.json`]: JSON.stringify(data, null, 2),
        [`k6-tests/results/validation-${timestamp}.html`]: htmlReport(data),
        'stdout': textSummary(data, { indent: ' ', enableColors: true })
    };
}

function htmlReport(data) {
    const timestamp = new Date().toLocaleString('fr-FR');
    
    return `
<!DOCTYPE html>
<html>
<head>
    <title>Rapport de Validation k6 - BuyYourKawa</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #2196F3; color: white; padding: 20px; border-radius: 5px; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }
        .metric-card { background: #f5f5f5; padding: 15px; border-radius: 5px; border-left: 4px solid #2196F3; }
        .success { border-left-color: #4CAF50; }
        .warning { border-left-color: #FF9800; }
        .error { border-left-color: #F44336; }
        .value { font-size: 24px; font-weight: bold; color: #333; }
        .label { color: #666; font-size: 14px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Rapport de Validation k6</h1>
        <p>API BuyYourKawa - ${timestamp}</p>
    </div>
    
    <div class="metrics">
        <div class="metric-card success">
            <div class="value">${data.metrics.http_reqs.values.count}</div>
            <div class="label">Requêtes Totales</div>
        </div>
        
        <div class="metric-card ${data.metrics.http_req_failed.values.rate < 0.05 ? 'success' : 'error'}">
            <div class="value">${(data.metrics.http_req_failed.values.rate * 100).toFixed(2)}%</div>
            <div class="label">Taux d'Échec</div>
        </div>
        
        <div class="metric-card ${data.metrics.http_req_duration.values.p95 < 1000 ? 'success' : 'warning'}">
            <div class="value">${data.metrics.http_req_duration.values.p95.toFixed(0)}ms</div>
            <div class="label">Temps Réponse P95</div>
        </div>
        
        <div class="metric-card ${data.metrics.success_rate?.values.rate > 0.95 ? 'success' : 'error'}">
            <div class="value">${((data.metrics.success_rate?.values.rate || 0) * 100).toFixed(2)}%</div>
            <div class="label">Taux de Succès</div>
        </div>
    </div>
    
    <h2>Détails des Métriques</h2>
    <pre>${JSON.stringify(data.metrics, null, 2)}</pre>
</body>
</html>`;
}

function textSummary(data, options) {
    return `
RAPPORT DE VALIDATION k6 - BuyYourKawa
=========================================

Métriques Principales:
- Requêtes totales: ${data.metrics.http_reqs.values.count}
- Taux d'échec: ${(data.metrics.http_req_failed.values.rate * 100).toFixed(2)}%
- Temps réponse P95: ${data.metrics.http_req_duration.values.p95.toFixed(0)}ms
- Taux de succès: ${((data.metrics.success_rate?.values.rate || 0) * 100).toFixed(2)}%

Validation: ${data.metrics.http_req_failed.values.rate < 0.05 ? 'RÉUSSIE' : 'ÉCHOUÉE'}
`;
}
