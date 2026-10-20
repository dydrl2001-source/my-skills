$ErrorActionPreference = 'Stop'
$runtimeRoot = if ($env:VIDEO_READER_HOME) { $env:VIDEO_READER_HOME } else { Join-Path $env:LOCALAPPDATA 'CodexVideoReader' }
$videoPython = Join-Path $runtimeRoot 'venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $videoPython)) {
    throw 'Video Reader runtime is missing. Run setup.ps1 -PythonPath <Python 3.12 executable> first.'
}
& $videoPython (Join-Path $PSScriptRoot 'run.py') @args
exit $LASTEXITCODE
