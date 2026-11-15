$ErrorActionPreference = 'Stop'
$rootPath = if ($env:SHC_KNOWLEDGE_ROOT) { $env:SHC_KNOWLEDGE_ROOT } else { $PSScriptRoot }
$rustCompiler = Join-Path $env:USERPROFILE '.cargo\bin\rustc.exe'
python -m unittest discover -s $rootPath -p test_pipeline.py -v
if ($LASTEXITCODE -ne 0) { throw 'Evidence tests failed' }
& $rustCompiler --edition 2021 --target i686-pc-windows-gnu (Join-Path $rootPath 'scripts\viewport_original_compare.rs') -o (Join-Path $rootPath 'viewport-compare.exe')
if ($LASTEXITCODE -ne 0) { throw 'Rust build failed' }
$livePath = (Get-Content -LiteralPath (Join-Path $rootPath 'evidence\latest-live.txt') -Raw).Trim()
& (Join-Path $rootPath 'viewport-compare.exe') $livePath
if ($LASTEXITCODE -ne 0) { throw 'Original comparison failed' }
python (Join-Path $rootPath 'pipeline.py') index
if ($LASTEXITCODE -ne 0) { throw 'Index validation failed' }
