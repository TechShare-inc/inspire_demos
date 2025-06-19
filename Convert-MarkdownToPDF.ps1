# Convert-MarkdownToPDF.ps1
# This script converts Markdown files to PDF using the provided CSS styling

# Check if the required packages are installed
$pandocInstalled = $null -ne (Get-Command "pandoc" -ErrorAction SilentlyContinue)
$wkhtmltopdfInstalled = $null -ne (Get-Command "wkhtmltopdf" -ErrorAction SilentlyContinue)

if (-not $pandocInstalled -or -not $wkhtmltopdfInstalled) {
    Write-Host "Required software missing. Please install the following:" -ForegroundColor Red
    
    if (-not $pandocInstalled) {
        Write-Host "- Pandoc: https://pandoc.org/installing.html" -ForegroundColor Yellow
    }
    
    if (-not $wkhtmltopdfInstalled) {
        Write-Host "- wkhtmltopdf: https://wkhtmltopdf.org/downloads.html" -ForegroundColor Yellow
    }
    
    exit 1
}

# Get the directory where the script is located
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$docsDir = Join-Path $scriptDir "docs"
$styleDir = Join-Path $scriptDir "style"

# Function to convert a Markdown file to PDF
function Convert-ToPDF {
    param (
        [string]$inputFile,
        [string]$outputFile,
        [string]$styleFile,
        [string]$pageSize = "A4"
    )
    
    $headerHtml = ""
    $footerHtml = ""
    
    # Create PDF using pandoc and wkhtmltopdf
    Write-Host "Converting $inputFile to $outputFile..." -ForegroundColor Cyan
    
    $pandocArgs = @(
        "-f", "markdown",
        "-t", "html",
        "--standalone",
        "--css", $styleFile,
        "-o", $outputFile,
        $inputFile,
        "--pdf-engine=wkhtmltopdf",
        "--pdf-engine-opt=--enable-local-file-access",
        "--pdf-engine-opt=--page-size=$pageSize",
        "--pdf-engine-opt=--margin-top=25",
        "--pdf-engine-opt=--margin-right=20",
        "--pdf-engine-opt=--margin-bottom=30",
        "--pdf-engine-opt=--margin-left=20",
        "--pdf-engine-opt=--footer-spacing=10"
    )
    
    # Run pandoc with the arguments
    try {
        & pandoc $pandocArgs
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Successfully converted $inputFile to $outputFile" -ForegroundColor Green
        } else {
            Write-Host "Error converting $inputFile to $outputFile. Exit code: $LASTEXITCODE" -ForegroundColor Red
        }
    } catch {
        Write-Host "Error: $_" -ForegroundColor Red
    }
}

# Find and convert all Markdown files in the docs directory and subdirectories
$mdFiles = Get-ChildItem -Path $docsDir -Filter "*.md" -Recurse
$styleCssPath = Join-Path $styleDir "style.css"

foreach ($file in $mdFiles) {
    $outputFile = $file.FullName -replace "\.md$", ".pdf"
    Convert-ToPDF -inputFile $file.FullName -outputFile $outputFile -styleFile $styleCssPath
}

Write-Host "All Markdown files have been converted to PDF." -ForegroundColor Green
