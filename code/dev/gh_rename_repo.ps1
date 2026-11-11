# Rename the repository so the name carries the paper's thesis.
$ErrorActionPreference = "Stop"
$probe = "protocol=https`nhost=github.com`n`n"
$filled = $probe | git credential fill 2>$null
$token = ($filled | Select-String '^password=').Line -replace '^password=', ''
$h = @{ Authorization = "token $token"; "User-Agent" = "dsh-agent"; Accept = "application/vnd.github+json" }

$body = @{ name = "fusion-gain-confounds" } | ConvertTo-Json
$repo = Invoke-RestMethod -Uri "https://api.github.com/repos/Xbotsd/ivanpah-fusion-benchmark" `
    -Headers $h -Method Patch -Body $body -ContentType "application/json"
"renamed : $($repo.full_name)"
"url     : $($repo.html_url)"
"clone   : $($repo.clone_url)"
