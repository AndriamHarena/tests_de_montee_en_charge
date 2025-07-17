# Script d'exécution des benchmarks
param(
    [string]$Tool = "all",  # all, k6, artillery, locust
    [string]$Test = "basic", # basic, stress
    [switch]$SkipApiCheck = $false
)

Write-Host "Lancement des benchmarks BuyYourKawa" -ForegroundColor Green
Write-Host "Outil: $Tool | Test: $Test" -ForegroundColor Cyan

# Vérifier que l'API est démarrée
if (-not $SkipApiCheck) {
    Write-Host "Vérification de l'API..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "API BuyYourKawa accessible" -ForegroundColor Green
        }
    } catch {
        Write-Host "API non accessible. Démarrez l'API avec: python main.py" -ForegroundColor Red
        exit 1
    }
}

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"

# Fonction pour exécuter k6
function Run-K6Tests {
    param($TestType)
    
    Write-Host "Exécution des tests k6 ($TestType)..." -ForegroundColor Yellow
    
    $scriptPath = "k6-tests\$TestType-test.js"
    $outputPath = "k6-tests\results\k6-$TestType-$timestamp"
    
    if (Test-Path $scriptPath) {
        try {
            k6 run --out json="$outputPath.json" --out csv="$outputPath.csv" $scriptPath
            Write-Host "Test k6 $TestType terminé" -ForegroundColor Green
            Write-Host "Résultats: $outputPath.*" -ForegroundColor Cyan
        } catch {
            Write-Host "Erreur k6 $TestType : $_" -ForegroundColor Red
        }
    } else {
        Write-Host "Script k6 non trouvé: $ScriptPath" -ForegroundColor Red
    }
}

# Fonction pour exécuter Artillery
function Run-ArtilleryTests {
    param($TestType)
    
    Write-Host "Exécution des tests Artillery ($TestType)..." -ForegroundColor Yellow
    
    $scriptPath = "artillery-tests\$TestType-test.yml"
    $outputPath = "artillery-tests\results\artillery-$TestType-$timestamp.json"
    
    if (Test-Path $scriptPath) {
        try {
            artillery run --output $outputPath $scriptPath
            Write-Host "Test Artillery $TestType terminé" -ForegroundColor Green
            Write-Host "Résultats disponibles dans:" -ForegroundColor Yellow
            
            # Générer rapport HTML
            $htmlOutput = $outputPath.Replace(".json", ".html")
            artillery report --output $htmlOutput $outputPath
            Write-Host "Rapport HTML: $htmlOutput" -ForegroundColor Cyan
        } catch {
            Write-Host "Erreur Artillery $TestType : $_" -ForegroundColor Red
        }
    } else {
        Write-Host "Script Artillery non trouvé: $ScriptPath" -ForegroundColor Red
    }
}

# Fonction pour exécuter Locust (référence)
function Run-LocustTests {
    param($TestType)
    
    Write-Host "Exécution des tests Locust ($TestType)..." -ForegroundColor Yellow
    
    $scriptPath = "..\corrective-actions\load-test-fixes\locustfile_corrected.py"
    $outputPath = "comparison-results\locust-$TestType-$timestamp"
    
    if (Test-Path $scriptPath) {
        try {
            if ($TestType -eq "basic") {
                $users = 15
                $duration = "60s"
            } else {
                $users = 100
                $duration = "300s"
            }
            
            locust -f $scriptPath --host=http://localhost:8000 --users $users --spawn-rate 5 -t $duration --html="$outputPath.html" --csv="$outputPath" --headless
            Write-Host "Test Locust $TestType terminé" -ForegroundColor Green
            Write-Host "Résultats: $outputPath.*" -ForegroundColor Cyan
        } catch {
            Write-Host "Erreur Locust $TestType : $_" -ForegroundColor Red
        }
    } else {
        Write-Host "Script Locust non trouvé: $ScriptPath" -ForegroundColor Red
    }
}

# Exécution selon les paramètres
switch ($Tool.ToLower()) {
    "k6" {
        Run-K6Tests $Test
    }
    "artillery" {
        Run-ArtilleryTests $Test
    }
    "locust" {
        Run-LocustTests $Test
    }
    "all" {
        Write-Host "Exécution de tous les outils..." -ForegroundColor Magenta
        
        # Séquence d'exécution avec pauses
        Run-K6Tests $Test
        Start-Sleep -Seconds 10
        
        Run-ArtilleryTests $Test
        Start-Sleep -Seconds 10
        
        Run-LocustTests $Test
        
        Write-Host "Benchmarks terminés!" -ForegroundColor Green
        Write-Host "Consultez les dossiers results/ pour les résultats détaillés" -ForegroundColor Cyan
    }
    default {
        Write-Host "Outil non reconnu: $Tool" -ForegroundColor Red
        Write-Host "Outils disponibles: k6, artillery, locust, all" -ForegroundColor Yellow
    }
}

# Génération du rapport de comparaison
if ($Tool -eq "all") {
    Write-Host "Génération du rapport de comparaison..." -ForegroundColor Yellow
    
    $comparisonReport = @"
# Rapport de Comparaison - $timestamp

## Résumé des Tests
- **Date**: $(Get-Date)
- **Type de test**: $Test
- **API**: BuyYourKawa (http://localhost:8000)

## Résultats par Outil

### k6
- Fichiers: k6-tests/results/k6-$Test-$timestamp.*
- Performance: [À analyser]
- Facilité d'utilisation: [À évaluer]

### Artillery
- Fichiers: artillery-tests/results/artillery-$Test-$timestamp.*
- Performance: [À analyser]
- Facilité d'utilisation: [À évaluer]

### Locust
- Fichiers: comparison-results/locust-$Test-$timestamp.*
- Performance: [À analyser]
- Facilité d'utilisation: [À évaluer]

## Analyse Comparative
[À compléter après analyse des résultats]

## Recommandations
[À définir selon les résultats]
"@
    
    $comparisonReport | Out-File -FilePath "comparison-results\comparison-$timestamp.md" -Encoding UTF8
    Write-Host "Rapport de comparaison créé: comparison-results\comparison-$timestamp.md" -ForegroundColor Green
}
