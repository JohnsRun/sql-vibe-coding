[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$InputFile,

    [Parameter(Mandatory = $false)]
    [string]$OutputFile,

    [Parameter(Mandatory = $false)]
    [string]$CssFile,

    [Parameter(Mandatory = $false)]
    [string]$Title
)

$ErrorActionPreference = 'Stop'

function Resolve-AbsolutePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $false)]
        [string]$BasePath = (Get-Location).Path
    )

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return [System.IO.Path]::GetFullPath($Path)
    }

    return [System.IO.Path]::GetFullPath((Join-Path $BasePath $Path))
}

function Get-MarkdownTitle {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath
    )

    $lines = Get-Content -Path $FilePath -Encoding UTF8
    foreach ($line in $lines) {
        if ($line -match '^#{1,6}\s+(.+?)\s*$') {
            return $Matches[1].Trim()
        }
    }

    return [System.IO.Path]::GetFileNameWithoutExtension($FilePath)
}

try {
    $repoRoot = Resolve-AbsolutePath -Path '..' -BasePath $PSScriptRoot

    if ([string]::IsNullOrWhiteSpace($InputFile)) {
        $InputFile = Join-Path $repoRoot '03Test/01test-case.md'
    }
    $InputFile = Resolve-AbsolutePath -Path $InputFile -BasePath $repoRoot

    if (-not (Test-Path -Path $InputFile -PathType Leaf)) {
        Write-Error "Input markdown file not found: $InputFile"
        exit 1
    }

    if ([string]::IsNullOrWhiteSpace($OutputFile)) {
        $outputName = [System.IO.Path]::GetFileNameWithoutExtension($InputFile) + '.html'
        $OutputFile = Join-Path ([System.IO.Path]::GetDirectoryName($InputFile)) $outputName
    }
    $OutputFile = Resolve-AbsolutePath -Path $OutputFile -BasePath $repoRoot

    if ([string]::IsNullOrWhiteSpace($CssFile)) {
        $CssFile = Join-Path $repoRoot '02Development_Zone/styles/business.css'
    }
    $CssFile = Resolve-AbsolutePath -Path $CssFile -BasePath $repoRoot

    if (-not (Test-Path -Path $CssFile -PathType Leaf)) {
        Write-Error "CSS file not found: $CssFile"
        exit 1
    }

    $pandoc = Get-Command -Name 'pandoc' -ErrorAction SilentlyContinue
    if (-not $pandoc) {
        Write-Host 'pandoc is required but not installed.' -ForegroundColor Red
        Write-Host 'Install on macOS with: brew install pandoc' -ForegroundColor Yellow
        exit 2
    }

    $outputDir = [System.IO.Path]::GetDirectoryName($OutputFile)
    if (-not (Test-Path -Path $outputDir -PathType Container)) {
        New-Item -Path $outputDir -ItemType Directory -Force | Out-Null
    }

    if ([string]::IsNullOrWhiteSpace($Title)) {
        $Title = Get-MarkdownTitle -FilePath $InputFile
    }

    # Read CSS content for embedding
    $cssContent = Get-Content -Path $CssFile -Raw -Encoding UTF8

    $pandocArgs = @(
        '--from', 'markdown',
        '--to', 'html5',
        '--standalone',
        '--metadata', "title=$Title",
        '--output', $OutputFile,
        $InputFile
    )

    & $pandoc.Path @pandocArgs
    $exitCode = $LASTEXITCODE

    if ($exitCode -ne 0) {
        Write-Error "pandoc failed with exit code $exitCode"
        exit $exitCode
    }

    # Post-process: embed CSS content and convert mermaid code blocks
    $htmlContent = Get-Content -Path $OutputFile -Raw -Encoding UTF8

    # Embed CSS content directly into HTML with additional code block styling
    $additionalCss = @"
/* Code block styling for pandoc-generated content */
div.sourceCode {
    background: #111827 !important;
    border: 1px solid #334e68 !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    overflow-x: auto !important;
}
pre.sourceCode {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
}
code.sourceCode {
    background: transparent !important;
    color: #e5edf5 !important;
    border: none !important;
    padding: 0 !important;
}
"@
    $styledCss = "<style>`n$cssContent`n$additionalCss`n</style>"
    $htmlContent = $htmlContent -replace '(?i)</head>', "$styledCss`n</head>"

    # Convert mermaid code blocks to Mermaid-renderable divs
    $htmlContent = [regex]::Replace(
        $htmlContent,
        '(?s)<pre[^>]*class="[^"]*mermaid[^"]*"[^>]*>\s*<code[^>]*>(.*?)</code>\s*</pre>',
        [System.Text.RegularExpressions.MatchEvaluator] {
            param($m)
            $inner = $m.Groups[1].Value.Trim()
            $inner = $inner -replace '&lt;',  '<' `
                            -replace '&gt;',  '>' `
                            -replace '&amp;', '&' `
                            -replace '&quot;', '"' `
                            -replace '&#39;', "'"
            return "<div class=`"mermaid`">$inner</div>"
        }
    )

    # Remove duplicate h1 title if it immediately follows the header block
    $htmlContent = [regex]::Replace(
        $htmlContent,
        '(?s)(<header[^>]*>.*?</header>)\s*<h1[^>]*id="[^"]*"[^>]*>[^<]*</h1>',
        '$1'
    )

    $mermaidJs   = '<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>'
    $mermaidInit = '<script>mermaid.initialize({ startOnLoad: true, theme: "default" });</script>'
    $htmlContent = $htmlContent -replace '(?i)</body>', "$mermaidJs`n$mermaidInit`n</body>"

    Set-Content -Path $OutputFile -Value $htmlContent -Encoding UTF8

    Write-Host "HTML generated: $OutputFile" -ForegroundColor Green
    exit 0
}
catch {
    Write-Error "Conversion failed: $($_.Exception.Message)"
    exit 99
}
