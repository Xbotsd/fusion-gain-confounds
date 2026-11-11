# Add the record to the open "remote-sensing" community, keeping the metadata.
$ErrorActionPreference = "Stop"
$token = (Get-Content "$env:TEMP\zenodo_token.txt" -Raw).Trim()
$h = @{ Authorization = "Bearer $token"; "User-Agent" = "dsh-agent"; Accept = "application/json" }
$id = 24130421

function Show-Error($e) {
    "FAILED: $($e.Exception.Message)"
    $r = $e.Exception.Response
    if ($r) { (New-Object System.IO.StreamReader($r.GetResponseStream())).ReadToEnd() }
}

$dep = Invoke-RestMethod -Uri "https://zenodo.org/api/deposit/depositions/$id" -Headers $h
"current communities : " + (($dep.metadata.communities | ForEach-Object { $_.identifier }) -join ", ")

$body = @{
    metadata = @{
        upload_type         = "software"
        title               = $dep.metadata.title
        version             = $dep.metadata.version
        publication_date    = $dep.metadata.publication_date
        description         = $dep.metadata.description
        access_right        = "open"
        license             = "mit"
        language            = "eng"
        creators            = $dep.metadata.creators
        keywords            = $dep.metadata.keywords
        related_identifiers = $dep.metadata.related_identifiers
        communities         = @(@{ identifier = "remote-sensing" })
    }
} | ConvertTo-Json -Depth 8

try {
    $upd = Invoke-RestMethod -Uri "https://zenodo.org/api/deposit/depositions/$id" -Headers $h `
        -Method Put -Body ([System.Text.Encoding]::UTF8.GetBytes($body)) -ContentType "application/json"
    "requested community : " + (($upd.metadata.communities | ForEach-Object { "$($_.identifier)/$($_.state)" }) -join ", ")
} catch { Show-Error $_; exit 5 }

try {
    $pub = Invoke-RestMethod -Uri "https://zenodo.org/api/deposit/depositions/$id/actions/publish" -Headers $h `
        -Method Post -Body ([System.Text.Encoding]::UTF8.GetBytes("{}")) -ContentType "application/json"
    "published : doi $($pub.doi)  states " + (($pub.metadata.communities | ForEach-Object { "$($_.identifier)/$($_.state)" }) -join ", ")
} catch { Show-Error $_; exit 6 }
