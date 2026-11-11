# Add to a community through the InvenioRDM endpoint instead of the legacy one.
$ErrorActionPreference = "Stop"
$token = (Get-Content "$env:TEMP\zenodo_token.txt" -Raw).Trim()
$h = @{ Authorization = "Bearer $token"; "User-Agent" = "dsh-agent"; Accept = "application/json" }
$id = 24130421

$rec = Invoke-RestMethod -Uri "https://zenodo.org/api/records/$id" -Headers $h
"state : $($rec.status)  version $($rec.metadata.version)"

$body = @{ receiver = "remote-sensing"; type = "community-inclusion" } | ConvertTo-Json
try {
    $r = Invoke-RestMethod -Uri "https://zenodo.org/api/records/$id/communities" -Headers $h `
        -Method Post -Body ([System.Text.Encoding]::UTF8.GetBytes($body)) -ContentType "application/json"
    "request created : $($r | ConvertTo-Json -Compress -Depth 4)"
} catch {
    "REQUEST FAILED: $($_.Exception.Message)"
    $resp = $_.Exception.Response
    if ($resp) { (New-Object System.IO.StreamReader($resp.GetResponseStream())).ReadToEnd() }
}
