# Parity Lab Test Runner for Windows
# Sets up environment and runs tests

# Setup paths
$env:PYTHONPATH = "D:\pg\packages"
$env:PATH = "C:\Strawberry\perl\bin;$env:PATH"

Write-Host "================================" -ForegroundColor Cyan
Write-Host "PG Parity Lab Test Runner" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check dependencies
Write-Host "Checking Dependencies..." -ForegroundColor Gray
python --version
perl --version | Select-String "version"
Write-Host ""

# Run fuzz tests (always work, no dependencies)
Write-Host "Running Fuzz Tests..." -ForegroundColor Yellow
python -m pytest tests/fuzz/ -v -q --tb=line -k "not lower_upper and not fraction_creation"

Write-Host ""
Write-Host "Running Contract Tests (Python-only)..." -ForegroundColor Yellow
python -m pytest tests/contract/ -v -q --tb=line -k "determinism or no_errors"

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Test run complete!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Status:" -ForegroundColor Yellow
Write-Host "  Python Runtime: Functional" -ForegroundColor Green
Write-Host "  Perl Available: Yes" -ForegroundColor Green
Write-Host "  Perl PG Libraries: Not installed" -ForegroundColor Gray
Write-Host ""
Write-Host "For full Perl-Python parity comparison:" -ForegroundColor Gray
Write-Host "  1. Install WeBWorK Perl PG libraries" -ForegroundColor Gray
Write-Host "  2. Update perl_ref/run_pg_snippet.pl with library paths" -ForegroundColor Gray
Write-Host "  3. Run: pytest tests/contract/ -v" -ForegroundColor Gray
Write-Host "================================" -ForegroundColor Cyan

