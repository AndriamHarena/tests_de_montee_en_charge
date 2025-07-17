# Guide d'Exécution des Tests - Phase 6 Benchmarks

## Démarrage Rapide

### Option 1: Démarrage Automatique (Recommandé)
```powershell
# Démarrer l'API et exécuter les tests de validation
.\start-api-and-test.ps1 -TestType validation

# Démarrer l'API et exécuter tous les tests
.\start-api-and-test.ps1 -TestType all
```

### Option 2: Démarrage Manuel
```powershell
# 1. Installer les outils
.\install-tools.ps1

# 2. Démarrer l'API (dans un autre terminal)
cd ..
python main.py

# 3. Exécuter les tests
.\run-validation-tests.ps1 -TestType validation
```

## Types de Tests Disponibles

### Tests de Validation
- **Objectif** : Vérifier le bon fonctionnement de l'API
- **Durée** : ~2 minutes
- **Charge** : 5-10 utilisateurs simultanés
- **Scripts** :
  - `k6-tests/validation-test.js`
  - `artillery-tests/validation-test.yml`

### Tests Normaux (Basic)
- **Objectif** : Performance en conditions normales
- **Durée** : ~3 minutes
- **Charge** : 15 utilisateurs simultanés
- **Scripts** :
  - `k6-tests/basic-test.js`
  - `artillery-tests/basic-test.yml`

### Tests de Stress
- **Objectif** : Limites de performance
- **Durée** : ~5 minutes
- **Charge** : Jusqu'à 100 utilisateurs simultanés
- **Scripts** :
  - `k6-tests/stress-test.js`
  - `artillery-tests/stress-test.yml`

## Structure des Résultats

```
benchmarks/
├── k6-tests/results/
│   ├── validation-YYYYMMDD-HHMMSS.json
│   ├── validation-YYYYMMDD-HHMMSS.csv
│   ├── basic-YYYYMMDD-HHMMSS.json
│   └── stress-YYYYMMDD-HHMMSS.csv
├── artillery-tests/results/
│   ├── validation-YYYYMMDD-HHMMSS.json
│   ├── validation-YYYYMMDD-HHMMSS.html
│   ├── basic-YYYYMMDD-HHMMSS.html
│   └── stress-YYYYMMDD-HHMMSS.html
└── comparison-results/
    ├── comparison-validation-YYYYMMDD-HHMMSS.md
    └── performance-comparison.md
```

## Commandes Spécifiques

### Tests k6 Uniquement
```powershell
# Test de validation k6
k6 run --out json=k6-tests/results/validation-manual.json k6-tests/validation-test.js

# Test de stress k6
k6 run --out csv=k6-tests/results/stress-manual.csv k6-tests/stress-test.js
```

### Tests Artillery Uniquement
```powershell
# Test de validation Artillery
artillery run --output artillery-tests/results/validation-manual.json artillery-tests/validation-test.yml

# Générer rapport HTML
artillery report --output artillery-tests/results/validation-manual.html artillery-tests/results/validation-manual.json
```

## Analyse des Résultats

### Métriques k6 (JSON/CSV)
- `http_req_duration` : Temps de réponse
- `http_req_failed` : Taux d'échec
- `http_reqs` : Nombre total de requêtes
- `success_rate` : Taux de succès personnalisé

### Métriques Artillery (HTML)
- **Response Time** : P50, P95, P99
- **Request Rate** : Requêtes par seconde
- **Error Rate** : Pourcentage d'erreurs
- **Scenarios** : Détail par scénario

## Seuils de Performance

### Tests de Validation
- **Taux d'échec** : < 5%
- **Temps réponse P95** : < 1000ms
- **Taux de succès** : > 95%

### Tests Normaux
- **Taux d'échec** : < 3%
- **Temps réponse P95** : < 800ms
- **Débit** : > 20 req/s

### Tests de Stress
- **Taux d'échec** : < 10%
- **Temps réponse P95** : < 1500ms
- **Stabilité** : Pas de dégradation brutale

## Dépannage

### Problèmes Courants

#### API non accessible
```powershell
# Vérifier si l'API fonctionne
curl http://localhost:8000/docs

# Redémarrer l'API
python main.py
```

#### k6 non trouvé
```powershell
# Installer k6 via Chocolatey
choco install k6

# Ou télécharger depuis https://k6.io/docs/getting-started/installation/
```

#### Artillery non trouvé
```powershell
# Installer Artillery via npm
npm install -g artillery@latest
```

#### Erreurs d'authentification
- Vérifier que l'utilisateur admin existe
- Credentials par défaut : `admin` / `secret123`

## Checklist Avant Tests

- [ ] Python installé et fonctionnel
- [ ] API BuyYourKawa démarrée sur port 8000
- [ ] k6 installé et accessible
- [ ] Artillery installé et accessible
- [ ] Dossiers results/ créés
- [ ] Aucun autre processus sur port 8000

## Workflow Recommandé

1. **Installation** : `.\install-tools.ps1`
2. **Test rapide** : `.\start-api-and-test.ps1 -TestType validation`
3. **Analyse** : Consulter les rapports HTML Artillery
4. **Tests complets** : `.\run-validation-tests.ps1 -TestType all`
5. **Comparaison** : Lire `comparison-results/comparison-*.md`
6. **Documentation** : Mettre à jour le plan d'action

## Support

En cas de problème :
1. Vérifier les logs de l'API
2. Consulter les messages d'erreur k6/Artillery
3. Vérifier la connectivité réseau
4. Redémarrer l'API si nécessaire
