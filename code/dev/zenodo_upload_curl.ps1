# Step 2b: upload with curl.exe (handles large bodies and TLS better than Invoke-RestMethod).
$ErrorActionPreference = "Stop"
$token = (Get-Content "$env:TEMP\zenodo_token.txt" -Raw).Trim()
$bucket = (Get-Content "$env:TEMP\zenodo_bucket.txt" -Raw).Trim()
$zip = "$env:TEMP\fusion-gain-confounds-1.0.0.zip"
$uri = "$bucket/fusion-gain-confounds-1.0.0.zip"

$curl = (Get-Command curl.exe -ErrorAction SilentlyContinue).Source
if (-not $curl) { $curl = (Get-Command curl -ErrorAction SilentlyContinue).Source }
"curl: $curl"

$args = @(
    "-sS", "-X", "PUT",
    "-H", "Authorization: Bearer $token",
    "-H", "Content-Type: application/octet-stream",
    "--data-binary", "@$zip",
    "-w", "`nHTTP %{http_code}`n",
    $uri
)
$out = & $curl @args
$out | Select-Object -Last 3
