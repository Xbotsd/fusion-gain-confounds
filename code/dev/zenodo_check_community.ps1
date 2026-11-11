# Check whether the inclusion request was accepted and how the record now looks.
$ErrorActionPreference = "Stop"
$token = (Get-Content "$env:TEMP\zenodo_token.txt" -Raw).Trim()
$h = @{ Authorization = "Bearer $token"; "User-Agent" = "dsh-agent"; Accept = "application/json" }

$rec = Invoke-RestMethod -Uri "https://zenodo.org/api/records/24130421" -Headers $h
"record status    : $($rec.status)  version $($rec.metadata.version)"
"communities      : " + (($rec.parent.communities | ForEach-Object { "$($_.id) ($($_.slug))" }) -join ", ")
"description chars: $($rec.metadata.description.Length)"
"description start: $($rec.metadata.description.Substring(0, 90))..."

try {
    $req = Invoke-RestMethod -Uri "https://zenodo.org/api/requests/e7e1bfb0-077a-4e6a-ae67-afe47854c6b0" -Headers $h
    "request status   : $($req.status)   is_open: $($req.is_open)   closed: $($req.is_closed)"
} catch {
    "request status   : unknown ($($_.Exception.Message))"
}
