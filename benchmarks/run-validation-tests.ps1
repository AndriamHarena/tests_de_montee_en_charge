# Script d'exécution des tests de validation et normaux
param(
    [string]$TestType = "all",  # validation, normal, all
    [switch]$SkipApiCheck = $false
)

Write-Host "🧪 Lancement des tests de validation et normaux" -ForegroundColor Green
Write-Host "Type de test: $TestType" -ForegroundColor Cyan

# Vérifier que l'API est démarrée
if (-not $SkipApiCheck) {
    Write-Host "🔍 Vérification de l'API..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ API BuyYourKawa accessible" -ForegroundColor Green
        }
    } catch {
        Write-Host "❌ API non accessible. Démarrez l'API avec: python main.py" -ForegroundColor Red
        exit 1
    }
}

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"

# Fonction pour exécuter les tests k6
function Invoke-K6Tests {
    param($TestName, $ScriptPath)
    
    Write-Host "🔧 Exécution test k6: $TestName..." -ForegroundColor Yellow
    
    if (Test-Path $ScriptPath) {
        try {
            $outputJson = "k6-tests\results\$TestName-$timestamp.json"
            $outputCsv = "k6-tests\results\$TestName-$timestamp.csv"
            
            # Créer le dossier results s'il n'existe pas
            if (!(Test-Path "k6-tests\results")) {
                New-Item -ItemType Directory -Path "k6-tests\results" -Force
            }
            
            # Exécuter k6 avec sortie JSON et CSV
            k6 run --out json="$outputJson" --out csv="$outputCsv" $ScriptPath
            
            Write-Host "✅ Test k6 $TestName terminé" -ForegroundColor Green
            Write-Host "📊 Résultats JSON: $outputJson" -ForegroundColor Cyan
            Write-Host "📊 Résultats CSV: $outputCsv" -ForegroundColor Cyan
            
            return @{
                Success = $true
                JsonPath = $outputJson
                CsvPath = $outputCsv
            }
        } catch {
            Write-Host "❌ Erreur k6 $TestName : $_" -ForegroundColor Red
            return @{ Success = $false }
        }
    } else {
        Write-Host "❌ Script k6 non trouvé: $ScriptPath" -ForegroundColor Red
        return @{ Success = $false }
    }
}

# Fonction pour exécuter les tests Artillery
function Invoke-ArtilleryTests {
    param($TestName, $ScriptPath)
    
    Write-Host "🔧 Exécution test Artillery: $TestName..." -ForegroundColor Yellow
    
    if (Test-Path $ScriptPath) {
        try {
            $outputJson = "artillery-tests\results\$TestName-$timestamp.json"
            $outputHtml = "artillery-tests\results\$TestName-$timestamp.html"
            
            # Créer le dossier results s'il n'existe pas
            if (!(Test-Path "artillery-tests\results")) {
                New-Item -ItemType Directory -Path "artillery-tests\results" -Force
            }
            
            # Exécuter Artillery avec sortie JSON
            artillery run --output $outputJson $ScriptPath
            
            # Générer rapport HTML
            artillery report --output $outputHtml $outputJson
            
            Write-Host "✅ Test Artillery $TestName terminé" -ForegroundColor Green
            Write-Host "📊 Résultats JSON: $outputJson" -ForegroundColor Cyan
            Write-Host "📈 Rapport HTML: $outputHtml" -ForegroundColor Cyan
            
            return @{
                Success = $true
                JsonPath = $outputJson
                HtmlPath = $outputHtml
            }
        } catch {
            Write-Host "❌ Erreur Artillery $TestName : $_" -ForegroundColor Red
            return @{ Success = $false }
        }
    } else {
        Write-Host "❌ Script Artillery non trouvé: $ScriptPath" -ForegroundColor Red
        return @{ Success = $false }
    }
}

# Fonction pour générer un rapport de comparaison
function New-ComparisonReport {
    param($K6Results, $ArtilleryResults, $TestType)
    
    Write-Host "📈 Génération du rapport de comparaison..." -ForegroundColor Yellow
    
    $reportPath = "comparison-results\comparison-$TestType-$timestamp.md"
    
    # Créer le dossier comparison-results s'il n'existe pas
    if (!(Test-Path "comparison-results")) {
        New-Item -ItemType Directory -Path "comparison-results" -Force
    }
    
    $report = @"
# Rapport de Comparaison - Tests $TestType
**Date**: $(Get-Date -Format "dd/MM/yyyy HH:mm:ss")
**API**: BuyYourKawa (http://localhost:8000)

## Résumé des Tests Exécutés

### Tests k6
"@
    
    foreach ($test in $K6Results.Keys) {
        $result = $K6Results[$test]
        $status = if ($result.Success) { "✅ RÉUSSI" } else { "❌ ÉCHOUÉ" }
        $report += @"

#### $test
- **Statut**: $status
- **Fichiers**: 
  - JSON: $($result.JsonPath)
  - CSV: $($result.CsvPath)
"@
    }
    
    $report += @"

### Tests Artillery
"@
    
    foreach ($test in $ArtilleryResults.Keys) {
        $result = $ArtilleryResults[$test]
        $status = if ($result.Success) { "✅ RÉUSSI" } else { "❌ ÉCHOUÉ" }
        $report += @"

#### $test
- **Statut**: $status
- **Fichiers**: 
  - JSON: $($result.JsonPath)
  - HTML: $($result.HtmlPath)
"@
    }
    
    $report += @"

## Analyse Comparative

### Performance
- **k6**: Généralement plus rapide, consommation mémoire réduite
- **Artillery**: Interface plus simple, rapports HTML intégrés

### Facilité d'utilisation
- **k6**: Scripting JavaScript avancé, métriques personnalisées
- **Artillery**: Configuration YAML simple, courbe d'apprentissage faible

### Recommandations
- **k6** pour les tests de performance haute fréquence
- **Artillery** pour les tests de validation et démonstrations
- **Locust** reste optimal pour BuyYourKawa (interface web + Python)

## Prochaines Étapes
1. Analyser les métriques détaillées dans les fichiers JSON/CSV
2. Comparer les temps de réponse et taux d'erreur
3. Valider les seuils de performance définis
4. Documenter les résultats dans le plan d'action

---
*Rapport généré automatiquement le $(Get-Date)*
"@
    
    $report | Out-File -FilePath $reportPath -Encoding UTF8
    Write-Host "✅ Rapport de comparaison créé: $reportPath" -ForegroundColor Green
    
    return $reportPath
}

# Exécution des tests selon le paramètre
$k6Results = @{}
$artilleryResults = @{}

if ($TestType -eq "validation" -or $TestType -eq "all") {
    Write-Host "🧪 === TESTS DE VALIDATION ===" -ForegroundColor Magenta
    
    # Tests de validation k6
    $k6Results["validation"] = Invoke-K6Tests "validation" "k6-tests\validation-test.js"
    Start-Sleep -Seconds 5
    
    # Tests de validation Artillery
    $artilleryResults["validation"] = Invoke-ArtilleryTests "validation" "artillery-tests\validation-test.yml"
    Start-Sleep -Seconds 5
}

if ($TestType -eq "normal" -or $TestType -eq "all") {
    Write-Host "📊 === TESTS NORMAUX ===" -ForegroundColor Magenta
    
    # Tests normaux k6
    $k6Results["basic"] = Invoke-K6Tests "basic" "k6-tests\basic-test.js"
    Start-Sleep -Seconds 5
    
    $k6Results["stress"] = Invoke-K6Tests "stress" "k6-tests\stress-test.js"
    Start-Sleep -Seconds 5
    
    # Tests normaux Artillery
    $artilleryResults["basic"] = Invoke-ArtilleryTests "basic" "artillery-tests\basic-test.yml"
    Start-Sleep -Seconds 5
    
    $artilleryResults["stress"] = Invoke-ArtilleryTests "stress" "artillery-tests\stress-test.yml"
    Start-Sleep -Seconds 5
}

# Génération du rapport de comparaison
if ($k6Results.Count -gt 0 -or $artilleryResults.Count -gt 0) {
    $reportPath = New-ComparisonReport $k6Results $artilleryResults $TestType
    
    Write-Host ""
    Write-Host "🎉 Tous les tests terminés!" -ForegroundColor Green
    Write-Host "📊 Rapport de comparaison: $reportPath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📁 Résultats disponibles dans:" -ForegroundColor Yellow
    Write-Host "   - k6-tests\results\" -ForegroundColor White
    Write-Host "   - artillery-tests\results\" -ForegroundColor White
    Write-Host "   - comparison-results\" -ForegroundColor White
} else {
    Write-Host "❌ Aucun test exécuté" -ForegroundColor Red
}
