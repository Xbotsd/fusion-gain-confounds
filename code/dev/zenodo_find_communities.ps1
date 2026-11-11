# Find open Zenodo communities that fit the subject.
$ErrorActionPreference = "Stop"
$token = (Get-Content "$env:TEMP\zenodo_token.txt" -Raw).Trim()
$h = @{ Authorization = "Bearer $token"; "User-Agent" = "dsh-agent"; Accept = "application/json" }

foreach ($q in @("geophysics", "remote sensing", "earth science", "geology",
                 "mineral", "reproducible", "open science")) {
    $enc = [uri]::EscapeDataString($q)
    try {
        $r = Invoke-RestMethod -Uri "https://zenodo.org/api/communities?q=$enc&size=5" -Headers $h
        "== $q =="
        foreach ($c in $r.hits.hits) {
            $vis = $c.access.visibility
            "   {0,-42} {1,-10} {2}" -f $c.slug, $vis, $c.metadata.title
        }
    } catch {
        "== $q == lookup failed: $($_.Exception.Message)"
    }
}
