# Final verification of the public repository state.
$ErrorActionPreference = "Stop"
$probe = "protocol=https`nhost=github.com`n`n"
$filled = $probe | git credential fill 2>$null
$token = ($filled | Select-String '^password=').Line -replace '^password=', ''
$h = @{ Authorization = "token $token"; "User-Agent" = "dsh-agent"; Accept = "application/vnd.github+json" }

$repo = Invoke-RestMethod -Uri "https://api.github.com/repos/Xbotsd/ivanpah-fusion-benchmark" -Headers $h
"name        : $($repo.full_name)"
"public      : $(-not $repo.private)"
"licence     : $($repo.license.spdx_id)"
"description : $($repo.description)"
"topics      : $($repo.topics -join ', ')"
"pushed_at   : $($repo.pushed_at)"

$commit = Invoke-RestMethod -Uri "https://api.github.com/repos/Xbotsd/ivanpah-fusion-benchmark/commits/main" -Headers $h
"head        : $($commit.sha.Substring(0,7))  $($commit.commit.message.Split("`n")[0])"
"commits     : " + (Invoke-RestMethod -Uri "https://api.github.com/repos/Xbotsd/ivanpah-fusion-benchmark/commits?per_page=100" -Headers $h).Count

$tree = Invoke-RestMethod -Uri "https://api.github.com/repos/Xbotsd/ivanpah-fusion-benchmark/git/trees/main?recursive=1" -Headers $h
$blobs = $tree.tree | Where-Object { $_.type -eq "blob" }
"files       : $($blobs.Count)"
"  code/     : $(($blobs | Where-Object { $_.path -like 'code/*' }).Count)"
"  docs/     : $(($blobs | Where-Object { $_.path -like 'docs/*' }).Count)"
"  processed/: $(($blobs | Where-Object { $_.path -like 'processed/*' }).Count)"
"size        : $([math]::Round(($blobs | Measure-Object -Property size -Sum).Sum / 1MB, 1)) MB of file content"
