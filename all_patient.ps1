$PYTHON_EXE = "?"
$SCRIPT_PATH = "?"
$FOLDER_PATH = "?"

if (-not (Test-Path $FOLDER_PATH))
{
    Write-Host "Errore: La cartella $FOLDER_PATH non esiste" -ForegroundColor Red
    exit 1
}

$folders = Get-ChildItem -Path $FOLDER_PATH -Directory

if ($folders.Count -eq 0)
{
    Write-Host "Nessuna cartella trovata in $FOLDER_PATH" -ForegroundColor Yellow
    exit 0
}

Write-Host "Trovate $($folders.Count) cartelle da processare" -ForegroundColor Cyan
Write-Host ""

foreach ($folder in $folders)
{
    $folderName = $folder.Name

    Write-Host "Processando: $folderName" -ForegroundColor Yellow

    & $PYTHON_EXE $SCRIPT_PATH $folderName

    if ($LASTEXITCODE -eq 0)
    {
        Write-Host "Completato: $folderName" -ForegroundColor Green
    }
    else
    {
        Write-Host "Errore durante elaborazione di: $folderName (Exit code: $LASTEXITCODE)" -ForegroundColor Red
    }

    Write-Host "---"
    Write-Host ""
}

Write-Host "Elaborazione completata!" -ForegroundColor Green
