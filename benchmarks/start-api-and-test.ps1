# Script de démarrage API et tests automatisés
param(
    [string]$TestType = "validation",  # validation, normal, all
    [switch]$SkipInstall = $false
)

Write-Host "🚀 Démarrage automatisé API + Tests BuyYourKawa" -ForegroundColor Green

# Vérifier si Python est disponible
try {
    $pythonVersion = python --version
    Write-Host "✅ Python détecté: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python non trouvé. Veuillez installer Python." -ForegroundColor Red
    exit 1
}

# Installation des outils si nécessaire
if (-not $SkipInstall) {
    Write-Host "📦 Installation des outils de test..." -ForegroundColor Yellow
    try {
        .\install-tools.ps1
        Write-Host "✅ Outils installés" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Erreur installation, continuons..." -ForegroundColor Yellow
    }
}

# Démarrer l'API en arrière-plan
Write-Host "🔧 Démarrage de l'API BuyYourKawa..." -ForegroundColor Yellow

$apiJob = Start-Job -ScriptBlock {
    Set-Location $args[0]
    python main.py
} -ArgumentList (Get-Location).Path

Write-Host "✅ API démarrée (Job ID: $($apiJob.Id))" -ForegroundColor Green

# Attendre que l'API soit prête
Write-Host "⏳ Attente du démarrage de l'API..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0

do {
    Start-Sleep -Seconds 2
    $attempt++
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -TimeoutSec 3
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ API prête!" -ForegroundColor Green
            break
        }
    } catch {
        Write-Host "⏳ Tentative $attempt/$maxAttempts..." -ForegroundColor Gray
    }
} while ($attempt -lt $maxAttempts)

if ($attempt -ge $maxAttempts) {
    Write-Host "❌ Timeout - API non accessible" -ForegroundColor Red
    Stop-Job $apiJob
    Remove-Job $apiJob
    exit 1
}

# Exécuter les tests
Write-Host "🧪 Lancement des tests..." -ForegroundColor Magenta

try {
    .\run-validation-tests.ps1 -TestType $TestType -SkipApiCheck
    Write-Host "✅ Tests terminés avec succès" -ForegroundColor Green
} catch {
    Write-Host "❌ Erreur lors des tests: $_" -ForegroundColor Red
} finally {
    # Arrêter l'API
    Write-Host "🛑 Arrêt de l'API..." -ForegroundColor Yellow
    Stop-Job $apiJob
    Remove-Job $apiJob
    Write-Host "✅ API arrêtée" -ForegroundColor Green
}

# Afficher les résultats
Write-Host ""
Write-Host "📊 RÉSULTATS DISPONIBLES:" -ForegroundColor Cyan
Write-Host "├── k6-tests\results\" -ForegroundColor White
Write-Host "├── artillery-tests\results\" -ForegroundColor White
Write-Host "└── comparison-results\" -ForegroundColor White
Write-Host ""
Write-Host "💡 Prochaines étapes:" -ForegroundColor Yellow
Write-Host "   1. Analyser les rapports HTML dans artillery-tests\results\" -ForegroundColor White
Write-Host "   2. Examiner les métriques JSON/CSV dans k6-tests\results\" -ForegroundColor White
Write-Host "   3. Consulter le rapport de comparaison dans comparison-results\" -ForegroundColor White
