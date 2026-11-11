# Look at candidate communities before adding the record to one.
$ErrorActionPreference = "Stop"
$token = (Get-Content "$env:TEMP\zenodo_token.txt" -Raw).Trim()
$h = @{ Authorization = "Bearer $token"; "User-Agent" = "dsh-agent"; Accept = "application/json" }

foreach ($slug in @("remote-sensing", "mineralogy", "ubcgif", "dgg")) {
    try {
        $c = Invoke-RestMethod -Uri "https://zenodo.org/api/communities/$slug" -Headers $h
        $desc = ($c.metadata.description -replace "<[^>]+>", "" -replace "\s+", " ")
        if ($desc.Length -gt 220) { $desc = $desc.Substring(0, 220) + "..." }
        "== $slug ($($c.metadata.title)) =="
        "   visibility : $($c.access.visibility)   members: $($c.metadata.curation_policy.Length) char policy"
        "   about      : $desc"
    } catch {
        "== $slug == not accessible: $($_.Exception.Message)"
    }
}

# search a few more terms
foreach ($q in @("airborne", "hyperspectral", "thermal infrared", "geochemistry", "exploration")) {
    $enc = [uri]::EscapeDataString($q)
    try {
        $r = Invoke-RestMethod -Uri "https://zenodo.org/api/communities?q=$enc&size=4" -Headers $h
        "-- $q --"
        foreach ($c in $r.hits.hits) { "   {0,-38} {1,-9} {2}" -f $c.slug, $c.access.visibility, $c.metadata.title }
    } catch { "-- $q -- lookup failed" }
}
