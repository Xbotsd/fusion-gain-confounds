# Wait briefly for the CI run on the current head, then report.
$ErrorActionPreference = "Stop"
$probe = "protocol=https`nhost=github.com`n`n"
$filled = $probe | git credential fill 2>$null
$token = ($filled | Select-String '^password=').Line -replace '^password=', ''
$h = @{ Authorization = "token $token"; "User-Agent" = "dsh-agent"; Accept = "application/vnd.github+json" }
$repo = "Xbotsd/fusion-gain-confounds"

for ($i = 0; $i -lt 12; $i++) {
    $runs = Invoke-RestMethod -Uri "https://api.github.com/repos/$repo/actions/runs?per_page=3" -Headers $h
    $head = $runs.workflow_runs[0]
    if ($head.status -eq "completed") {
        "head run : $($head.head_sha.Substring(0,7)) -> $($head.conclusion)"
        break
    }
    Start-Sleep -Seconds 20
    if ($i -eq 11) { "head run : still $($head.status)" }
}
