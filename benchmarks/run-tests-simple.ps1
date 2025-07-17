# Script simple pour lancer les tests
param(
    [string]$TestType = "validation"
)

Write-Host "Demarrage des tests BuyYourKawa" -ForegroundColor Green

# Verifier si l'API est accessible
Write-Host "Verification de l'API..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -TimeoutSec 3
    if ($response.StatusCode -eq 200) {
        Write-Host "API accessible sur http://localhost:8000" -ForegroundColor Green
    }
} catch {
    Write-Host "API non accessible - Demarrage de l'API..." -ForegroundColor Yellow
    
    # Demarrer l'API en arriere-plan
    $apiJob = Start-Job -ScriptBlock {
        Set-Location "c:\Users\andri\Documents\1 - Digital School of Paris\DSP4 Archi O24A (4-5) 2024-2026\Test de montée en charge\-tp-tests-charge"
        python main.py
    }
    
    Write-Host "Attente du demarrage de l'API (30 secondes)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
    
    # Verifier a nouveau
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -TimeoutSec 5
        Write-Host "API demarree avec succes" -ForegroundColor Green
    } catch {
        Write-Host "Erreur: API non accessible apres demarrage" -ForegroundColor Red
        Stop-Job $apiJob -Force
        Remove-Job $apiJob -Force
        exit 1
    }
}

# Creer les dossiers de resultats
New-Item -ItemType Directory -Path "k6-tests\results" -Force | Out-Null
New-Item -ItemType Directory -Path "artillery-tests\results" -Force | Out-Null
New-Item -ItemType Directory -Path "comparison-results" -Force | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"

# Tests k6
Write-Host "Execution des tests k6..." -ForegroundColor Yellow
try {
    if ($TestType -eq "validation" -or $TestType -eq "all") {
        Write-Host "Test k6 validation..." -ForegroundColor Cyan
        k6 run --out json="k6-tests\results\validation-$timestamp.json" --out csv="k6-tests\results\validation-$timestamp.csv" k6-tests\validation-test.js
    }
    
    if ($TestType -eq "normal" -or $TestType -eq "all") {
        Write-Host "Test k6 normal..." -ForegroundColor Cyan
        k6 run --out json="k6-tests\results\basic-$timestamp.json" --out csv="k6-tests\results\basic-$timestamp.csv" k6-tests\basic-test.js
    }
    
    Write-Host "Tests k6 termines" -ForegroundColor Green
} catch {
    Write-Host "Erreur lors des tests k6: $($_.Exception.Message)" -ForegroundColor Red
}

# Tests Artillery
Write-Host "Execution des tests Artillery..." -ForegroundColor Yellow
try {
    if ($TestType -eq "validation" -or $TestType -eq "all") {
        Write-Host "Test Artillery validation..." -ForegroundColor Cyan
        artillery run --output "artillery-tests\results\validation-$timestamp.json" artillery-tests\validation-test.yml
        artillery report --output "artillery-tests\results\validation-$timestamp.html" "artillery-tests\results\validation-$timestamp.json"
    }
    
    if ($TestType -eq "normal" -or $TestType -eq "all") {
        Write-Host "Test Artillery normal..." -ForegroundColor Cyan
        artillery run --output "artillery-tests\results\basic-$timestamp.json" artillery-tests\basic-test.yml
        artillery report --output "artillery-tests\results\basic-$timestamp.html" "artillery-tests\results\basic-$timestamp.json"
    }
    
    Write-Host "Tests Artillery termines" -ForegroundColor Green
} catch {
    Write-Host "Erreur lors des tests Artillery: $($_.Exception.Message)" -ForegroundColor Red
}

# Generer rapport de comparaison
Write-Host "Generation du rapport de comparaison..." -ForegroundColor Yellow
$reportPath = "comparison-results\comparison-$TestType-$timestamp.md"

@"
# Rapport de Comparaison - Tests $TestType
Date: $(Get-Date -Format "dd/MM/yyyy HH:mm:ss")

## Resultats des Tests

### Tests k6
- Fichiers JSON: k6-tests\results\*-$timestamp.json
- Fichiers CSV: k6-tests\results\*-$timestamp.csv

### Tests Artillery  
- Fichiers JSON: artillery-tests\results\*-$timestamp.json
- Fichiers HTML: artillery-tests\results\*-$timestamp.html

## Analyse

Les resultats detailles sont disponibles dans les fichiers generes ci-dessus.
Consultez les rapports HTML Artillery pour une visualisation graphique.

## Prochaines Etapes

1. Analyser les metriques de performance
2. Comparer les temps de reponse k6 vs Artillery
3. Identifier les goulots d'etranglement
4. Documenter les resultats dans le plan d'action
"@ | Out-File -FilePath $reportPath -Encoding UTF8

Write-Host "Rapport genere: $reportPath" -ForegroundColor Green

# Arreter l'API si elle a ete demarree par ce script
if ($apiJob) {
    Write-Host "Arret de l'API..." -ForegroundColor Yellow
    Stop-Job $apiJob -Force
    Remove-Job $apiJob -Force
}

Write-Host "Tests termines avec succes!" -ForegroundColor Green
Write-Host "Resultats disponibles dans:" -ForegroundColor Cyan
Write-Host "- k6-tests\results\" -ForegroundColor White
Write-Host "- artillery-tests\results\" -ForegroundColor White
Write-Host "- comparison-results\" -ForegroundColor White
