$port = 8000
$root = "D:\Projects\LifeKernel\workspace"
Write-Host "Starting server at http://localhost:$port/tools/jsonl_viewer.html"
python -m http.server $port --directory $root
