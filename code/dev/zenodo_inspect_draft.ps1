# Inspect the edit draft so the PUT body matches what the server expects.
$ErrorActionPreference = "Stop"
$token = (Get-Content "$env:TEMP\zenodo_token.txt" -Raw).Trim()
$h = @{ Authorization = "Bearer $token"; "User-Agent" = "dsh-agent"; Accept = "application/json" }
$d = Invoke-RestMethod -Uri "https://zenodo.org/api/records/24130421/draft" -Headers $h

"top-level keys : " + (($d.PSObject.Properties.Name) -join ", ")
"metadata keys  : " + (($d.metadata.PSObject.Properties.Name) -join ", ")
"files.enabled  : $($d.files.enabled)"
"access         : $($d.access | ConvertTo-Json -Compress)"
"custom_fields  : $($d.custom_fields | ConvertTo-Json -Compress)"
"status         : $($d.status)"
"is_published   : $($d.is_published)"
$d | ConvertTo-Json -Depth 6 | Set-Content "$env:TEMP\zenodo_draft.json" -Encoding UTF8
"dump written to %TEMP%\zenodo_draft.json"
