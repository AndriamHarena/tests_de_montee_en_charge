# Script de vérification des outils installés
Write-Host "Vérification des outils de benchmark..." -ForegroundColor Green

# Vérifier Python
Write-Host "Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "$pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python non trouvé" -ForegroundColor Red
}

# Vérifier Node.js
Write-Host "Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "Node.js non trouvé" -ForegroundColor Red
}

# Vérifier k6
Write-Host "k6..." -ForegroundColor Yellow
try {
    $k6Version = k6 version
    Write-Host "k6 installé" -ForegroundColor Green
} catch {
    Write-Host "k6 non trouvé - Exécutez: .\install-tools.ps1" -ForegroundColor Red
}

# Vérifier Artillery
Write-Host "Artillery..." -ForegroundColor Yellow
try {
    $artilleryVersion = artillery version
    Write-Host "Artillery $artilleryVersion" -ForegroundColor Green
} catch {
    Write-Host "Artillery non trouvé - Exécutez: npm install -g artillery" -ForegroundColor Red
}

# Vérifier Locust
Write-Host "Locust..." -ForegroundColor Yellow
try {
    $locustVersion = locust --version
    Write-Host "Locust installé" -ForegroundColor Green
} catch {
    Write-Host "Locust non trouvé - Exécutez: pip install locust" -ForegroundColor Red
}

# Vérifier l'API
Write-Host "API BuyYourKawa..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -TimeoutSec 3
    if ($response.StatusCode -eq 200) {
        Write-Host "API accessible sur http://localhost:8000" -ForegroundColor Green
    }
} catch {
    Write-Host "API non accessible - Démarrez avec: python main.py" -ForegroundColor Red
}

# Vérifier les dossiers
Write-Host "Structure des dossiers..." -ForegroundColor Yellow
$requiredDirs = @(
    "k6-tests\results",
    "artillery-tests\results", 
    "comparison-results"
)

foreach ($dir in $requiredDirs) {
    if (Test-Path $dir) {
        Write-Host "$dir" -ForegroundColor Green
    } else {
        Write-Host "$dir manquant" -ForegroundColor Red
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "$dir créé" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "PROCHAINES ÉTAPES:" -ForegroundColor Cyan
Write-Host "1. Si des outils manquent: .\install-tools.ps1" -ForegroundColor White
Write-Host "2. Démarrer l'API: cd .. && python main.py" -ForegroundColor White
Write-Host "3. Lancer les tests: .\run-validation-tests.ps1 -TestType validation" -ForegroundColor White
Write-Host "4. Ou utiliser le script automatique: .\start-api-and-test.ps1" -ForegroundColor White
