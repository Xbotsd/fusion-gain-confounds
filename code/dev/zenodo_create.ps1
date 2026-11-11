# Step 1b: create the deposition with an explicitly encoded JSON body.
$ErrorActionPreference = "Stop"
$token = (Get-Content "$env:TEMP\zenodo_token.txt" -Raw).Trim()
$h = @{
    Authorization = "Bearer $token"
    "User-Agent"  = "dsh-agent"
    Accept        = "application/json"
}

$meta = @{
    metadata = @{
        upload_type        = "software"
        title              = "Two confounds in reported fusion gains for airborne mineral exploration"
        version            = "1.0.0"
        publication_date   = (Get-Date -Format "yyyy-MM-dd")
        description        = "Reproducible airborne multi-modal mineral-exploration benchmark on real USGS radiometrics (Ivanpah-Clark Mountain, NV-CA, 2019-2020), real ASTER L1T thermal infrared, real aeromagnetics and the USGS SIM 3206 geologic map, with a documented synthetic EM augmentation. It separates target circularity from the conditioning effect of an underdetermined inversion, and provides a model-free information test that conditioning cannot fake. Code, results and manuscript are in the repository."
        access_right       = "open"
        license            = "mit"
        creators           = @(
            @{
                name        = "Xu, Yudong"
                affiliation = "Heilongjiang University of Science and Technology, Harbin, China"
                orcid       = "0009-0002-3231-0444"
            }
        )
        keywords           = @(
            "airborne geophysics", "gamma-ray spectrometry", "ASTER thermal infrared",
            "multi-modal fusion", "identifiability", "reproducible benchmark",
            "mineral exploration"
        )
        related_identifiers = @(
            @{
                identifier    = "https://github.com/Xbotsd/fusion-gain-confounds"
                relation      = "isSupplementTo"
                resource_type = "software"
            }
        )
        language           = "eng"
    }
} | ConvertTo-Json -Depth 8

$bytes = [System.Text.Encoding]::UTF8.GetBytes($meta)
try {
    $dep = Invoke-RestMethod -Uri "https://zenodo.org/api/deposit/depositions" -Headers $h `
        -Method Post -Body $bytes -ContentType "application/json"
    "deposition id : $($dep.id)"
    "state         : $($dep.state)"
    "html          : $($dep.links.html)"
    "bucket        : $($dep.links.bucket)"
    $dep.id | Set-Content "$env:TEMP\zenodo_deposition_id.txt"
    $dep.links.bucket | Set-Content "$env:TEMP\zenodo_bucket.txt"
} catch {
    "CREATE FAILED: $($_.Exception.Message)"
    $r = $_.Exception.Response
    if ($r) {
        $sr = New-Object System.IO.StreamReader($r.GetResponseStream())
        $sr.ReadToEnd()
    }
    exit 3
}
