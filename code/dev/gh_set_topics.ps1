# Add topics and re-verify the repository metadata.
$ErrorActionPreference = "Stop"
$probe = "protocol=https`nhost=github.com`n`n"
$filled = $probe | git credential fill 2>$null
$token = ($filled | Select-String '^password=').Line -replace '^password=', ''
$h = @{
    Authorization = "token $token"
    "User-Agent"  = "dsh-agent"
    Accept        = "application/vnd.github.mercy-preview+json"
}

$topics = @(
    "geophysics", "remote-sensing", "aster", "gamma-ray-spectrometry",
    "mineral-exploration", "multi-modal-fusion", "reproducible-research",
    "benchmark", "identifiability", "thermal-infrared"
) | ConvertTo-Json
try {
    $r = Invoke-RestMethod -Uri "https://api.github.com/repos/Xbotsd/ivanpah-fusion-benchmark/topics" `
        -Headers $h -Method Put -Body (@{ names = ($topics | ConvertFrom-Json) } | ConvertTo-Json) `
        -ContentType "application/json"
    "topics set: " + ($r.names -join ", ")
} catch {
    "topics failed: $($_.Exception.Message)"
}

$h2 = @{ Authorization = "token $token"; "User-Agent" = "dsh-agent"; Accept = "application/vnd.github+json" }
$repo = Invoke-RestMethod -Uri "https://api.github.com/repos/Xbotsd/ivanpah-fusion-benchmark" -Headers $h2
"license   : $($repo.license.spdx_id) / $($repo.license.name)"
"head      : $($repo.pushed_at)"
"size_kb   : $($repo.size)"
