param([string]$PythonPath = 'python')
$ErrorActionPreference = 'Stop'
& $PythonPath (Join-Path $PSScriptRoot 'setup.py')
if ($LASTEXITCODE -ne 0) { throw 'Video Reader setup failed. See the preceding output.' }
