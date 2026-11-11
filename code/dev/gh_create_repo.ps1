# Create the public repository under the authenticated account (token never printed).
$ErrorActionPreference = "Stop"
$probe = "protocol=https`nhost=github.com`n`n"
$filled = $probe | git credential fill 2>$null
$token = ($filled | Select-String '^password=').Line -replace '^password=', ''
$headers = @{
    Authorization        = "token $token"
    "User-Agent"         = "dsh-agent"
    Accept               = "application/vnd.github+json"
}

$body = @{
    name        = "fusion-gain-confounds"
    description = "Two confounds in reported fusion gains for airborne mineral exploration: reproducible benchmark on real USGS radiometrics, real ASTER L1T thermal infrared and USGS SIM 3206 geology"
    homepage    = ""
    private     = $false
    has_issues  = $true
    has_wiki    = $false
    auto_init   = $false
} | ConvertTo-Json

try {
    $repo = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Headers $headers `
        -Method Post -Body $body -ContentType "application/json"
    "CREATED  : $($repo.full_name)"
    "clone url: $($repo.clone_url)"
    "ssh url  : $($repo.ssh_url)"
    "private  : $($repo.private)"
} catch {
    "CREATE FAILED: $($_.Exception.Message)"
    $r = $_.Exception.Response
    if ($r) {
        $sr = New-Object System.IO.StreamReader($r.GetResponseStream())
        $sr.ReadToEnd()
    }
    exit 4
}
