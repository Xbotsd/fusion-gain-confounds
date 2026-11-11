# Step 3: publish the deposition (irreversible) and read back both DOIs.
$ErrorActionPreference = "Stop"
$token = (Get-Content "$env:TEMP\zenodo_token.txt" -Raw).Trim()
$id = (Get-Content "$env:TEMP\zenodo_deposition_id.txt" -Raw).Trim()
$h = @{
    Authorization = "Bearer $token"
    "User-Agent"  = "dsh-agent"
    Accept        = "application/json"
}

$before = Invoke-RestMethod -Uri "https://zenodo.org/api/deposit/depositions/$id" -Headers $h
"files attached: $($before.files.Count)"
$before.files | ForEach-Object { "  - $($_.filename)  $([math]::Round($_.filesize / 1MB, 1)) MB" }

try {
    $pub = Invoke-RestMethod -Uri "https://zenodo.org/api/deposit/depositions/$id/actions/publish" `
        -Headers $h -Method Post -Body ([System.Text.Encoding]::UTF8.GetBytes("{}")) `
        -ContentType "application/json"
} catch {
    "PUBLISH FAILED: $($_.Exception.Message)"
    $r = $_.Exception.Response
    if ($r) {
        $sr = New-Object System.IO.StreamReader($r.GetResponseStream())
        $sr.ReadToEnd()
    }
    exit 3
}

"state        : $($pub.state)"
"submitted    : $($pub.submitted)"
"DOI          : $($pub.doi)"
"concept DOI  : $($pub.conceptdoi)"
"record url   : $($pub.links.html)"
"record api   : $($pub.links.self)"
$pub.doi | Set-Content "$env:TEMP\zenodo_doi.txt"
$pub.conceptdoi | Set-Content "$env:TEMP\zenodo_concept_doi.txt"
