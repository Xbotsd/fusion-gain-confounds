# Check whether the stored GitHub credential can authenticate, without printing it.
$ErrorActionPreference = "Stop"

$probe = "protocol=https`nhost=github.com`n`n"
$filled = $probe | git credential fill 2>$null
$user = ($filled | Select-String '^username=').Line -replace '^username=', ''
$token = ($filled | Select-String '^password=').Line -replace '^password=', ''

if (-not $token) {
    "NO CREDENTIAL: git credential fill returned no password"
    exit 2
}
"username : $user"
"token    : <hidden, $($token.Length) chars>"

$headers = @{
    Authorization          = "token $token"
    "User-Agent"           = "dsh-agent"
    Accept                 = "application/vnd.github+json"
}

try {
    $me = Invoke-RestMethod -Uri "https://api.github.com/user" -Headers $headers -Method Get
    "authenticated as : $($me.login)  (id $($me.id))"
} catch {
    "API AUTH FAILED : $($_.Exception.Message)"
    exit 3
}

# what can this token do?
$resp = Invoke-WebRequest -Uri "https://api.github.com/user" -Headers $headers -Method Get
"scopes header    : $($resp.Headers['x-oauth-scopes'])"
"rate remaining   : $($resp.Headers['x-ratelimit-remaining'])"

# does the target repository already exist?
try {
    $repo = Invoke-RestMethod -Uri "https://api.github.com/repos/Xbotsd/fusion-gain-confounds" -Headers $headers
    "repo exists      : $($repo.full_name)  private=$($repo.private)"
} catch {
    "repo lookup      : $($_.Exception.Message)"
}
