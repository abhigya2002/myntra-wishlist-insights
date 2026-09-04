$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
Write-Host "=== pip install ==="
pip install -r requirements.txt
Write-Host "=== build_index ==="
python build_index.py
Write-Host "=== retrieve smoke ==="
python retrieve.py
Write-Host "=== pulse ==="
python pulse.py
Write-Host "=== chat smoke (grounded) ==="
python -c "from chat import answer; r=answer('Why do people add to wishlist intent or bookmark?'); print(r['answer'][:1000]); print('n_sources', len(r['sources'])); print('refused', r['refused'])"
Write-Host "=== chat smoke (refusal) ==="
python -c "from chat import answer; r=answer('Should we raise the wishlist cap to increase sales?'); print(r['answer'][:400]); print('refused', r['refused'])"
Write-Host "=== streamlit import ==="
python -c "import app"
Write-Host "=== done ==="
Get-Item data\index.jsonl, output\pulse-report.md | Format-Table Name, Length
