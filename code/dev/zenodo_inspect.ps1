# Inspect the published record: what is editable, and does a draft exist?
$ErrorActionPreference = "Stop"
$token = (Get-Content "$env:TEMP\zenodo_token.txt" -Raw).Trim()
$h = @{ Authorization = "Bearer $token"; "User-Agent" = "dsh-agent"; Accept = "application/json" }

$rec = Invoke-RestMethod -Uri "https://zenodo.org/api/records/24130421" -Headers $h
"id            : $($rec.id)"
"version       : $($rec.metadata.version)"
"status        : $($rec.status)"
"is_published  : " + ($rec.status -eq "published")
"files         : $($rec.files.Count)"
"communities   : " + (($rec.parent.communities | ForEach-Object { $_.id }) -join ", ")
"metadata keys : " + (($rec.metadata.PSObject.Properties.Name) -join ", ")

# Is there already a draft (edit in progress)?
try {
    $draft = Invoke-RestMethod -Uri "https://zenodo.org/api/records/24130421/draft" -Headers $h
    "draft exists  : id $($draft.id)  version $($draft.metadata.version)"
} catch {
    "draft exists  : none ($($_.Exception.Message))"
}
