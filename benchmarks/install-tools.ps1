# Script d'installation des outils de benchmark
# Exécuter en tant qu'administrateur

Write-Host "Installation des outils de tests de charge" -ForegroundColor Green

# Vérifier si Node.js est installé
Write-Host "Vérification de Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "Node.js détecté: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "Node.js non trouvé. Veuillez installer Node.js depuis https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Installer k6
Write-Host "Installation de k6..." -ForegroundColor Yellow
try {
    # Méthode 1: Chocolatey (recommandée)
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        choco install k6 -y
        Write-Host "k6 installé via Chocolatey" -ForegroundColor Green
    } else {
        # Méthode 2: Téléchargement direct
        Write-Host "Chocolatey non trouvé. Téléchargement manuel de k6..." -ForegroundColor Yellow
        $k6Url = "https://github.com/grafana/k6/releases/latest/download/k6-v0.47.0-windows-amd64.zip"
        $k6Path = "$env:TEMP\k6.zip"
        Invoke-WebRequest -Uri $k6Url -OutFile $k6Path
        Expand-Archive -Path $k6Path -DestinationPath "$env:LOCALAPPDATA\k6" -Force
        $env:PATH += ";$env:LOCALAPPDATA\k6"
        Write-Host "k6 installé manuellement" -ForegroundColor Green
    }
} catch {
    Write-Host "Erreur lors de l'installation de k6: $_" -ForegroundColor Red
}

# Installer Artillery
Write-Host "Installation d'Artillery..." -ForegroundColor Yellow
try {
    npm install -g artillery@latest
    Write-Host "Artillery installé" -ForegroundColor Green
} catch {
    Write-Host "Erreur lors de l'installation d'Artillery: $_" -ForegroundColor Red
}

# Vérifier les installations
Write-Host "Vérification des installations..." -ForegroundColor Yellow

try {
    $k6Version = k6 version
    Write-Host "k6: $k6Version" -ForegroundColor Green
} catch {
    Write-Host "k6 non accessible" -ForegroundColor Red
}

try {
    $artilleryVersion = artillery version
    Write-Host "Artillery: $artilleryVersion" -ForegroundColor Green
} catch {
    Write-Host "Artillery non accessible" -ForegroundColor Red
}

# Créer les dossiers de résultats
Write-Host "Création des dossiers de résultats..." -ForegroundColor Yellow
$resultDirs = @(
    "benchmarks\k6-tests\results",
    "benchmarks\artillery-tests\results",
    "benchmarks\comparison-results"
)

foreach ($dir in $resultDirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force
        Write-Host "Dossier créé: $dir" -ForegroundColor Green
    }
}

Write-Host "Installation terminée!" -ForegroundColor Green
Write-Host "Prochaines étapes:" -ForegroundColor Cyan
Write-Host "   1. Démarrer l'API BuyYourKawa: python main.py" -ForegroundColor White
Write-Host "   2. Exécuter les tests: .\run-benchmarks.ps1" -ForegroundColor White
