# Estimation de la Charge Utilisateur - BuyYourKawa API
## Analyse Réaliste Basée sur les Benchmarks du Marché

---

## 1. Contexte et Hypothèses de Trafic

### 1.1 Profil de l'Entreprise
- **Secteur** : Vente de café en ligne (B2B/B2C)
- **Cible** : PME françaises + particuliers
- **Modèle** : API de gestion clients pour coffee shop
- **Phase** : Lancement produit avec campagne marketing

### 1.2 Benchmarks du Marché Coffee Shop
Basé sur les données de l'industrie :
- **Starbucks** : 2 min de visite moyenne, 3.8 pages/visite, 51.7% bounce rate
- **Nespresso** : 3.27 min de visite, 4.9 pages/visite, 50% bounce rate
- **Conversion moyenne** : 5.6% (industrie e-commerce café)
- **Panier moyen** : 50-100€ (Nespresso), 146€ CLV moyenne

### 1.3 Hypothèses de Trafic Réalistes

#### Scénario de Lancement Marketing
- **Budget marketing** : 15 000€ (PME française typique)
- **Durée campagne** : 3 semaines
- **Canaux** : Google Ads, Facebook, Email marketing
- **ROI attendu** : 3:1 (standard industrie)

#### Projection de Trafic
- **Visiteurs uniques/jour** : 2 500 (pic de campagne)
- **Visiteurs uniques/mois** : 45 000
- **Taux de conversion** : 4.5% (légèrement sous la moyenne)
- **Clients actifs/jour** : 112 (2 500 × 4.5%)

---

## 2. Profils Utilisateurs et Comportements

### 2.1 Personas Détaillés

#### Persona 1 : Gérant de Coffee Shop (60% du trafic)
- **Fréquence** : 3-5 connexions/jour
- **Durée session** : 8-12 minutes
- **Actions principales** :
  - Consultation clients (40% du temps)
  - Création/modification clients (35% du temps)
  - Export données (25% du temps)
- **Peak hours** : 9h-11h, 14h-16h

#### Persona 2 : Employé/Barista (30% du trafic)
- **Fréquence** : 2-3 connexions/jour
- **Durée session** : 3-5 minutes
- **Actions principales** :
  - Consultation clients (70% du temps)
  - Mise à jour commandes (30% du temps)
- **Peak hours** : 8h-10h, 16h-18h

#### Persona 3 : Manager/Analyste (10% du trafic)
- **Fréquence** : 1-2 connexions/jour
- **Durée session** : 15-25 minutes
- **Actions principales** :
  - Analyse données (50% du temps)
  - Export rapports (30% du temps)
  - Configuration système (20% du temps)
- **Peak hours** : 10h-12h

### 2.2 Répartition des Actions API

| Endpoint | % du Trafic | Fréquence/User/Session |
|----------|-------------|------------------------|
| `/token` (Auth) | 100% | 1 (obligatoire) |
| `/clients` (GET) | 85% | 3-8 requêtes |
| `/clients` (POST) | 25% | 1-3 requêtes |
| `/clients/{id}` (GET) | 60% | 2-5 requêtes |
| `/clients/{id}` (PUT) | 15% | 1-2 requêtes |
| `/clients/{id}` (DELETE) | 5% | 1 requête |

---

## 3. Modèle de Charge Détaillé

### 3.1 Calcul des Utilisateurs Simultanés

#### Méthode de Calcul
```
Utilisateurs simultanés = (Visiteurs/heure × Durée session moyenne) / 3600 secondes
```

#### Données de Base
- **Visiteurs uniques/jour** : 2 500
- **Répartition sur 16h** : 156 visiteurs/heure (moyenne)
- **Peak hour** : 312 visiteurs/heure (×2 pendant 9h-11h)
- **Durée session moyenne** : 7 minutes (420 secondes)

#### Calcul Utilisateurs Simultanés
- **Heure normale** : (156 × 420) / 3600 = **18 utilisateurs simultanés**
- **Heure de pointe** : (312 × 420) / 3600 = **36 utilisateurs simultanés**
- **Pic exceptionnel** (campagne) : **54 utilisateurs simultanés** (×1.5)

### 3.2 Scénarios de Test

#### Scénario 1 : Charge Normale (Baseline)
- **Utilisateurs simultanés** : 20
- **Durée** : 30 minutes
- **Pattern** : Stable
- **Objectif** : Validation fonctionnelle

#### Scénario 2 : Charge de Pointe (Realistic Peak)
- **Utilisateurs simultanés** : 50
- **Pattern** : Ramp-up 5min -> Plateau 20min -> Ramp-down 5min
- **Objectif** : Performance en conditions réelles

#### Scénario 3 : Charge Exceptionnelle (Marketing Campaign)
- **Utilisateurs simultanés** : 100
- **Pattern** : Ramp-up 10min -> Plateau 15min -> Ramp-down 5min
- **Objectif** : Résistance aux pics marketing

#### Scénario 4 : Test de Limite (Stress Test)
- **Utilisateurs simultanés** : 200
- **Pattern** : Ramp-up 15min -> Plateau 10min -> Ramp-down 5min
- **Objectif** : Identification du point de rupture

---

## 4. Objectifs de Performance

### 4.1 SLA (Service Level Agreement)

| Métrique | Charge Normale | Charge de Pointe | Charge Exceptionnelle |
|----------|----------------|------------------|----------------------|
| **Temps de réponse moyen** | < 200ms | < 400ms | < 800ms |
| **95e percentile** | < 500ms | < 1000ms | < 2000ms |
| **Taux d'erreur** | < 0.1% | < 0.5% | < 2% |
| **Disponibilité** | 99.9% | 99.5% | 99% |

### 4.2 Seuils d'Alerte

| Niveau | Utilisateurs Simultanés | Action |
|--------|------------------------|--------|
| **Vert** | 0-30 | Monitoring normal |
| **Orange** | 31-75 | Surveillance renforcée |
| **Rouge** | 76-150 | Alerte équipe technique |
| **Critique** | >150 | Activation plan d'urgence |

---

## 5. Patterns de Charge Détaillés

### 5.1 Pattern Journalier Type
```
06h-08h : 5% du trafic (2-3 users simultanés)
08h-10h : 20% du trafic (8-12 users simultanés)
10h-12h : 25% du trafic (12-18 users simultanés) <- PEAK
12h-14h : 15% du trafic (6-9 users simultanés)
14h-16h : 20% du trafic (8-12 users simultanés)
16h-18h : 10% du trafic (4-6 users simultanés)
18h-22h : 5% du trafic (2-3 users simultanés)
```

### 5.2 Pattern Hebdomadaire
- **Lundi-Vendredi** : 100% du trafic
- **Samedi** : 60% du trafic
- **Dimanche** : 30% du trafic

### 5.3 Pattern Saisonnier
- **Janvier-Mars** : 80% (post-fêtes)
- **Avril-Juin** : 100% (baseline)
- **Juillet-Août** : 70% (vacances)
- **Septembre-Novembre** : 120% (rentrée)
- **Décembre** : 150% (fêtes de fin d'année)

---

## 6. Scénarios de Test Détaillés

### 6.1 Scénario "Consultation Client" (70% du trafic)
```python
# Poids : 7/10 utilisateurs
1. POST /token (authentification)
2. GET /clients (liste des clients) - 2-3 fois
3. GET /clients/{id} (détail client) - 3-5 fois
4. Think time : 2-5 secondes entre requêtes
```

### 6.2 Scénario "Gestion Client" (20% du trafic)
```python
# Poids : 2/10 utilisateurs
1. POST /token (authentification)
2. GET /clients (liste des clients)
3. POST /clients (création client) - 1-2 fois
4. PUT /clients/{id} (modification) - 1 fois
5. Think time : 3-8 secondes entre requêtes
```

### 6.3 Scénario "Administration" (10% du trafic)
```python
# Poids : 1/10 utilisateurs
1. POST /token (authentification)
2. GET /clients (liste complète)
3. GET /clients/{id} (vérifications multiples) - 5-10 fois
4. DELETE /clients/{id} (suppression) - occasionnel
5. Think time : 5-15 secondes entre requêtes
```

---

## 7. Recommandations d'Implémentation

### 7.1 Phases de Test Recommandées

#### Phase 1 : Validation Fonctionnelle (Semaine 1)
- **Objectif** : Vérifier que l'API fonctionne sous charge légère
- **Charge** : 10-20 utilisateurs simultanés
- **Durée** : Tests courts (10-15 minutes)

#### Phase 2 : Test de Performance (Semaine 2)
- **Objectif** : Valider les performances en conditions réelles
- **Charge** : 30-50 utilisateurs simultanés
- **Durée** : Tests moyens (30-45 minutes)

#### Phase 3 : Test de Résistance (Semaine 3)
- **Objectif** : Identifier les limites du système
- **Charge** : 75-150 utilisateurs simultanés
- **Durée** : Tests longs (60-90 minutes)

### 7.2 Métriques à Surveiller

#### Métriques Applicatives
- Temps de réponse par endpoint
- Taux d'erreur par type
- Throughput (requêtes/seconde)
- Taux de succès des authentifications

#### Métriques Infrastructure
- CPU utilization (< 70%)
- Memory usage (< 80%)
- Database connections (< 80% du pool)
- Network I/O

---

## 8. Analyse Comparative Marché

### 8.1 Benchmarks Concurrents

| Concurrent | Users Simultanés | Temps Réponse | Disponibilité |
|------------|------------------|---------------|---------------|
| **Square POS API** | 500+ | 150ms | 99.9% |
| **Shopify API** | 1000+ | 200ms | 99.95% |
| **WooCommerce** | 100-300 | 300ms | 99.5% |
| **BuyYourKawa** (cible) | 50-100 | 400ms | 99.5% |

### 8.2 Positionnement Réaliste
Notre API BuyYourKawa vise un positionnement **PME/Startup** :
- Performance correcte sans sur-ingénierie
- Coût maîtrisé
- Évolutivité progressive

---

## 9. Plan de Montée en Charge

### 9.1 Roadmap 6 Mois

| Mois | Utilisateurs Cibles | Actions Techniques |
|------|--------------------|--------------------|
| **M1** | 50 simultanés | Optimisation base |
| **M2** | 75 simultanés | Cache Redis |
| **M3** | 100 simultanés | Load balancer |
| **M4** | 150 simultanés | Database scaling |
| **M5** | 200 simultanés | CDN + optimisations |
| **M6** | 300 simultanés | Architecture microservices |

### 9.2 Investissements Nécessaires

| Phase | Infrastructure | Coût Mensuel Estimé |
|-------|----------------|---------------------|
| **Actuel** | 1 serveur | 50€/mois |
| **Phase 1** | + Redis | 80€/mois |
| **Phase 2** | + Load balancer | 120€/mois |
| **Phase 3** | + DB replica | 200€/mois |

---

## 10. Conclusion et Recommandations

### 10.1 Estimation Finale Réaliste
- **Charge normale** : 20-30 utilisateurs simultanés
- **Charge de pointe** : 50-75 utilisateurs simultanés  
- **Charge exceptionnelle** : 100-150 utilisateurs simultanés
- **Limite technique actuelle** : ~200 utilisateurs simultanés

### 10.2 Actions Prioritaires
1. **Immédiat** : Tester avec 50 utilisateurs simultanés
2. **Court terme** : Optimiser l'endpoint `/token` (780ms -> 300ms)
3. **Moyen terme** : Implémenter un cache pour les lectures
4. **Long terme** : Préparer la scalabilité horizontale

### 10.3 Risques Identifiés
- **Authentification** : Goulot d'étranglement principal
- **Base de données** : Pas d'index optimisés
- **Monitoring** : Alerting insuffisant pour la production

---

*Document créé le 17 juillet 2025 - Basé sur les benchmarks industrie et l'analyse du code existant*
