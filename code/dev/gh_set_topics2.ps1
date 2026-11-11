# Retry setting topics with an explicit JSON body.
$ErrorActionPreference = "Stop"
$probe = "protocol=https`nhost=github.com`n`n"
$filled = $probe | git credential fill 2>$null
$token = ($filled | Select-String '^password=').Line -replace '^password=', ''
$h = @{
    Authorization = "token $token"
    "User-Agent"  = "dsh-agent"
    Accept        = "application/vnd.github+json"
}
$body = '{"names":["geophysics","remote-sensing","aster","gamma-ray-spectrometry","mineral-exploration","multi-modal-fusion","reproducible-research","benchmark","identifiability","thermal-infrared"]}'
try {
    $r = Invoke-RestMethod -Uri "https://api.github.com/repos/Xbotsd/fusion-gain-confounds/topics" `
        -Headers $h -Method Put -Body $body -ContentType "application/json; charset=utf-8"
    "topics set: " + ($r.names -join ", ")
} catch {
    "topics failed: $($_.Exception.Message)"
    $resp = $_.Exception.Response
    if ($resp) {
        $sr = New-Object System.IO.StreamReader($resp.GetResponseStream())
        $sr.ReadToEnd()
    }
}
