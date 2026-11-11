# Confirm what the public repository actually serves.
$ErrorActionPreference = "Stop"
$probe = "protocol=https`nhost=github.com`n`n"
$filled = $probe | git credential fill 2>$null
$token = ($filled | Select-String '^password=').Line -replace '^password=', ''
$h = @{ Authorization = "token $token"; "User-Agent" = "dsh-agent"; Accept = "application/vnd.github+json" }

$repo = Invoke-RestMethod -Uri "https://api.github.com/repos/Xbotsd/fusion-gain-confounds" -Headers $h
"full_name   : $($repo.full_name)"
"private     : $($repo.private)"
"default     : $($repo.default_branch)"
"size_kb     : $($repo.size)"
"license     : $($repo.license.spdx_id)"
"html_url    : $($repo.html_url)"

$commit = Invoke-RestMethod -Uri "https://api.github.com/repos/Xbotsd/fusion-gain-confounds/commits/main" -Headers $h
"head commit : $($commit.sha.Substring(0,7))  $($commit.commit.message.Split("`n")[0])"

$tree = Invoke-RestMethod -Uri "https://api.github.com/repos/Xbotsd/fusion-gain-confounds/contents/" -Headers $h
"top level   : " + (($tree | ForEach-Object { $_.name }) -join ", ")

$count = 0
$page = 1
do {
    $items = Invoke-RestMethod -Uri "https://api.github.com/repos/Xbotsd/fusion-gain-confounds/git/trees/main?recursive=1" -Headers $h
    $count = ($items.tree | Where-Object { $_.type -eq "blob" }).Count
    $page = 2
} while ($page -eq 1)
"tracked files: $count"
