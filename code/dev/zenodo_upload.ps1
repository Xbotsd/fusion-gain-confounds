# Step 2: build the source archive and upload it to the deposition bucket.
$ErrorActionPreference = "Stop"
$token = (Get-Content "$env:TEMP\zenodo_token.txt" -Raw).Trim()
$bucket = (Get-Content "$env:TEMP\zenodo_bucket.txt" -Raw).Trim()
$zip = "$env:TEMP\fusion-gain-confounds-1.0.0.zip"

Push-Location "D:\A_MineralProspecting"
git archive --format=zip --prefix=fusion-gain-confounds-1.0.0/ -o $zip HEAD
Pop-Location
$size = (Get-Item $zip).Length
"archive : $zip  ($([math]::Round($size / 1MB, 1)) MB)"

$h = @{
    Authorization = "Bearer $token"
    "User-Agent"  = "dsh-agent"
}
$uri = "$bucket/fusion-gain-confounds-1.0.0.zip"
$bytes = [System.IO.File]::ReadAllBytes($zip)
try {
    $up = Invoke-RestMethod -Uri $uri -Headers $h -Method Put -Body $bytes `
        -ContentType "application/zip"
    "uploaded: $($up.key)  $($up.size) bytes"
} catch {
    "UPLOAD FAILED: $($_.Exception.Message)"
    $r = $_.Exception.Response
    if ($r) {
        $sr = New-Object System.IO.StreamReader($r.GetResponseStream())
        $sr.ReadToEnd()
    }
    exit 3
}
