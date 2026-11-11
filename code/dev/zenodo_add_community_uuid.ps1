# Get the community's UUID and retry the inclusion request with it.
$ErrorActionPreference = "Stop"
$token = (Get-Content "$env:TEMP\zenodo_token.txt" -Raw).Trim()
$h = @{ Authorization = "Bearer $token"; "User-Agent" = "dsh-agent"; Accept = "application/json" }
$id = 24130421

$c = Invoke-RestMethod -Uri "https://zenodo.org/api/communities/remote-sensing" -Headers $h
"community id   : $($c.id)"
"community slug : $($c.slug)"
"visibility     : $($c.access.visibility)"

$body = @{ receiver = $c.id; type = "community-inclusion" } | ConvertTo-Json
try {
    $r = Invoke-RestMethod -Uri "https://zenodo.org/api/records/$id/communities" -Headers $h `
        -Method Post -Body ([System.Text.Encoding]::UTF8.GetBytes($body)) -ContentType "application/json"
    "request : $($r | ConvertTo-Json -Compress -Depth 5)"
} catch {
    "FAILED: $($_.Exception.Message)"
    $resp = $_.Exception.Response
    if ($resp) {
        $sr = New-Object System.IO.StreamReader($resp.GetResponseStream())
        $sr.ReadToEnd()
    }
}
