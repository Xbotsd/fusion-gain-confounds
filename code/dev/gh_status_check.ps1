# Releases, tags and CI status of the renamed repository.
$ErrorActionPreference = "Stop"
$probe = "protocol=https`nhost=github.com`n`n"
$filled = $probe | git credential fill 2>$null
$token = ($filled | Select-String '^password=').Line -replace '^password=', ''
$h = @{ Authorization = "token $token"; "User-Agent" = "dsh-agent"; Accept = "application/vnd.github+json" }
$repo = "Xbotsd/fusion-gain-confounds"

$r = Invoke-RestMethod -Uri "https://api.github.com/repos/$repo" -Headers $h
"name      : $($r.full_name)"
"public    : $(-not $r.private)"
"licence   : $($r.license.spdx_id)"
"head      : $($r.default_branch) / pushed $($r.pushed_at)"

try {
    $rel = Invoke-RestMethod -Uri "https://api.github.com/repos/$repo/releases" -Headers $h
    if ($rel.Count -eq 0) { "releases  : none" }
    else { "releases  : " + (($rel | ForEach-Object { "$($_.tag_name) ($($_.published_at))" }) -join ", ") }
} catch { "releases  : lookup failed" }

try {
    $runs = Invoke-RestMethod -Uri "https://api.github.com/repos/$repo/actions/runs?per_page=5" -Headers $h
    if ($runs.total_count -eq 0) { "ci runs   : none yet" }
    else {
        foreach ($w in $runs.workflow_runs) {
            "ci run    : $($w.name) $($w.head_sha.Substring(0,7)) -> $($w.conclusion) ($($w.status))"
        }
    }
} catch { "ci runs   : lookup failed: $($_.Exception.Message)" }
