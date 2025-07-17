#!/usr/bin/env python3
"""
Script automatisé pour lancer les tests de charge Locust
Génère les rapports HTML et CSV pour validation du plan d'actions correctives
"""

import subprocess
import time
import os
import json
from datetime import datetime

# Configuration des tests pour validation du plan d'actions
TEST_SCENARIOS = {
    "validation": {
        "users": 15,
        "spawn_rate": 3,
        "duration": "60s",
        "description": "Test de validation - charge légère (baseline)"
    },
    "normal": {
        "users": 30,
        "spawn_rate": 5,
        "duration": "120s",
        "description": "Test normal - charge quotidienne (référence)"
    },
    "peak": {
        "users": 50,
        "spawn_rate": 8,
        "duration": "180s",
        "description": "Test de pointe - charge élevée (SLA critique)"
    },
    "stress": {
        "users": 100,
        "spawn_rate": 10,
        "duration": "300s",
        "description": "Test de stress - limite système (point de rupture)"
    }
}

def run_locust_test(scenario_name, host="http://localhost:8000"):
    """
    Lance un test Locust pour un scénario donné et génère les rapports
    """
    scenario = TEST_SCENARIOS[scenario_name]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Noms des fichiers de sortie
    html_report = f"reporting/{scenario_name}_{timestamp}.html"
    csv_report = f"reporting/{scenario_name}_{timestamp}"
    
    # Commande Locust avec tous les paramètres nécessaires
    cmd = [
        "locust",
        "-f", "locustfile.py",
        "--host", host,
        "--users", str(scenario["users"]),
        "--spawn-rate", str(scenario["spawn_rate"]),
        "-t", scenario["duration"],
        "--html", html_report,
        "--csv", csv_report,
        "--headless",
        "--print-stats"
    ]
    
    print(f"🚀 Lancement du test '{scenario_name}': {scenario['description']}")
    print(f"   👥 Utilisateurs: {scenario['users']} | ⚡ Spawn rate: {scenario['spawn_rate']} | ⏱️ Durée: {scenario['duration']}")
    print(f"   📊 Rapport HTML: {html_report}")
    print(f"   📈 Rapport CSV: {csv_report}")
    print(f"   🔄 Commande: {' '.join(cmd)}")
    
    try:
        # Lancer le test avec affichage en temps réel
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Afficher la sortie en temps réel
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"   📊 {output.strip()}")
        
        # Attendre la fin du processus
        return_code = process.poll()
        
        if return_code == 0:
            print(f"✅ Test '{scenario_name}' terminé avec succès")
            return True, html_report, csv_report
        else:
            stderr = process.stderr.read()
            print(f"❌ Test '{scenario_name}' échoué (code: {return_code}):")
            print(f"   {stderr}")
            return False, None, None
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Test '{scenario_name}' interrompu (timeout)")
        return False, None, None
    except Exception as e:
        print(f"💥 Erreur lors du test '{scenario_name}': {e}")
        return False, None, None

def check_api_health(host="http://localhost:8000"):
    """
    Vérifie que l'API est accessible et fonctionnelle avant de lancer les tests
    """
    try:
        import requests
        
        # Test de base - documentation
        response = requests.get(f"{host}/docs", timeout=5)
        if response.status_code != 200:
            print(f"❌ Documentation API non accessible (status: {response.status_code})")
            return False
        
        # Test d'authentification
        auth_response = requests.post(f"{host}/token", 
                                    data={"username": "admin", "password": "password"},
                                    timeout=5)
        if auth_response.status_code != 200:
            print(f"❌ Authentification échouée (status: {auth_response.status_code})")
            return False
        
        print("✅ API accessible et fonctionnelle")
        return True
        
    except ImportError:
        print("⚠️ Module 'requests' non installé, vérification basique seulement")
        return True
    except Exception as e:
        print(f"❌ Impossible de joindre l'API: {e}")
        print("💡 Assurez-vous que l'API est démarrée: python -m uvicorn main:app --reload --port 8000")
        return False

def analyze_results(csv_file):
    """
    Analyse rapide des résultats CSV pour validation
    """
    try:
        if not os.path.exists(f"{csv_file}_stats.csv"):
            return None
        
        with open(f"{csv_file}_stats.csv", 'r') as f:
            lines = f.readlines()
            if len(lines) < 2:
                return None
            
            # Parser la ligne des stats agrégées
            stats_line = lines[-1]  # Dernière ligne = agrégé
            parts = stats_line.split(',')
            
            if len(parts) >= 8:
                return {
                    "requests": int(parts[2]),
                    "failures": int(parts[3]),
                    "avg_response_time": float(parts[5]),
                    "failure_rate": (int(parts[3]) / int(parts[2]) * 100) if int(parts[2]) > 0 else 0
                }
    except Exception as e:
        print(f"⚠️ Erreur lors de l'analyse des résultats: {e}")
    
    return None

def main():
    """
    Fonction principale - lance tous les tests et génère le rapport de validation
    """
    print("🔧 BuyYourKawa API - Tests de Charge pour Plan d'Actions Correctives")
    print("=" * 70)
    print("📋 Objectif: Valider les métriques avant/après optimisations")
    print("🎯 Seuils: Temps < 200ms, Échecs < 2%, Disponibilité > 99%")
    print("=" * 70)
    
    # Créer le dossier de rapports s'il n'existe pas
    os.makedirs("reporting", exist_ok=True)
    
    # Vérifier que l'API est accessible
    if not check_api_health():
        return
    
    # Lancer les tests dans l'ordre croissant de charge
    test_results = {}
    
    for scenario_name in ["validation", "normal", "peak", "stress"]:
        print(f"\n{'='*25} {scenario_name.upper()} {'='*25}")
        
        success, html_report, csv_report = run_locust_test(scenario_name)
        
        # Analyser les résultats
        analysis = analyze_results(csv_report) if csv_report else None
        
        test_results[scenario_name] = {
            "success": success,
            "html_report": html_report,
            "csv_report": csv_report,
            "analysis": analysis
        }
        
        if success and analysis:
            print(f"📊 Résultats rapides:")
            print(f"   📈 Requêtes totales: {analysis['requests']}")
            print(f"   ❌ Échecs: {analysis['failures']} ({analysis['failure_rate']:.1f}%)")
            print(f"   ⏱️ Temps moyen: {analysis['avg_response_time']:.0f}ms")
            print(f"   📄 Rapport détaillé: {html_report}")
            
            # Validation des seuils
            if analysis['avg_response_time'] > 200:
                print(f"   ⚠️ SEUIL DÉPASSÉ: Temps de réponse > 200ms")
            if analysis['failure_rate'] > 2:
                print(f"   ⚠️ SEUIL DÉPASSÉ: Taux d'échec > 2%")
        
        # Pause entre les tests pour éviter la surcharge
        if scenario_name != "stress":
            print("⏳ Pause de 15 secondes avant le test suivant...")
            time.sleep(15)
    
    # Résumé final avec validation des seuils
    print("\n" + "="*70)
    print("📋 RÉSUMÉ DES TESTS - VALIDATION PLAN D'ACTIONS")
    print("="*70)
    
    for scenario, result in test_results.items():
        status = "✅ SUCCÈS" if result["success"] else "❌ ÉCHEC"
        print(f"{scenario.ljust(12)} : {status}")
        
        if result["success"] and result["analysis"]:
            analysis = result["analysis"]
            print(f"             📊 {analysis['requests']} req | ❌ {analysis['failure_rate']:.1f}% échecs | ⏱️ {analysis['avg_response_time']:.0f}ms")
            print(f"             📄 {result['html_report']}")
            
            # Validation des seuils critiques
            if analysis['avg_response_time'] > 500:
                print(f"             🚨 CRITIQUE: Temps > 500ms")
            elif analysis['avg_response_time'] > 200:
                print(f"             ⚠️ ATTENTION: Temps > 200ms")
            
            if analysis['failure_rate'] > 5:
                print(f"             🚨 CRITIQUE: Échecs > 5%")
            elif analysis['failure_rate'] > 2:
                print(f"             ⚠️ ATTENTION: Échecs > 2%")
    
    print("\n🎯 Tests terminés !")
    print("💡 Consultez les rapports HTML détaillés dans le dossier 'reporting/'")
    print("📊 Utilisez ces métriques pour valider l'efficacité du plan d'actions correctives")

if __name__ == "__main__":
    main()
