# Edit the published record's metadata in place, then publish the edit.
# Safety: if the draft comes back with a different record id (i.e. a new version),
# delete it and abort before touching anything.
$ErrorActionPreference = "Stop"
$token = (Get-Content "$env:TEMP\zenodo_token.txt" -Raw).Trim()
$h = @{ Authorization = "Bearer $token"; "User-Agent" = "dsh-agent"; Accept = "application/json" }
$id = 24130421

$draft = Invoke-RestMethod -Uri "https://zenodo.org/api/records/$id/draft" -Headers $h -Method Post `
    -Body ([System.Text.Encoding]::UTF8.GetBytes("{}")) -ContentType "application/json"
"draft id      : $($draft.id)"
"draft version : $($draft.metadata.version)"

if ($draft.id -ne $id) {
    "ABORT: editing would create a new version ($($draft.id)); deleting the draft."
    Invoke-RestMethod -Uri "https://zenodo.org/api/records/$($draft.id)/draft" -Headers $h -Method Delete | Out-Null
    exit 4
}

$desc = @"
Reproducible airborne multi-modal mineral-exploration benchmark over the Ivanpah-Clark Mountain area (Nevada-California), built from public data: USGS airborne radiometrics (295,943 samples, 2019-2020), real ASTER L1T thermal infrared (five emissivity bands, 2006-10-18, retrieved by normalisation TES), real USGS aeromagnetics and the USGS SIM 3206 surficial geologic map. Airborne EM is synthetic and labelled as such, because no measured airborne EM exists over this footprint.

The benchmark separates two confounds that inflate reported fusion gains. (1) Target circularity: the clay proxy is derived from the gamma channels being inverted. (2) An underdetermined inversion: three gamma channels for five mineral unknowns give rank 3, so appending any channel changes conditioning before it adds information. Five inert channels with the true ASTER response rows recover 69-98% of the F1 gain and a geological AUC at least as high as the real cube's, while a model-free four-substrate test that never uses the response matrix keeps a smaller real gain (+0.179 balanced accuracy, 95% CI [0.120, 0.241], 20/20 repeats).

Contents of the archive: code (40 scripts, eight stages), the manuscript (Markdown and Word), all result JSON/CSV files, the figure sources, the audit and validation outputs, and a manifest with SHA-256 hashes. Raw third-party data and the derived cubes are not redistributed; they are rebuilt by the documented preparation stage.

Reproduce with: python code/run_all.py prepare && python code/run_all.py. The public repository is https://github.com/Xbotsd/fusion-gain-confounds.
"@

$body = @{ metadata = @{ description = $desc } } | ConvertTo-Json -Depth 5
$bytes = [System.Text.Encoding]::UTF8.GetBytes($body)
try {
    $patched = Invoke-RestMethod -Uri "https://zenodo.org/api/records/$id/draft" -Headers $h -Method Patch `
        -Body $bytes -ContentType "application/json"
    "patched description, length $($patched.metadata.description.Length) chars"
} catch {
    "PATCH FAILED: $($_.Exception.Message)"
    $r = $_.Exception.Response
    if ($r) {
        $sr = New-Object System.IO.StreamReader($r.GetResponseStream())
        $sr.ReadToEnd()
    }
    exit 5
}

try {
    $pub = Invoke-RestMethod -Uri "https://zenodo.org/api/records/$id/draft/actions/publish" -Headers $h -Method Post `
        -Body ([System.Text.Encoding]::UTF8.GetBytes("{}")) -ContentType "application/json"
    "published     : id $($pub.id)  version $($pub.metadata.version)  doi $($pub.doi)"
} catch {
    "PUBLISH FAILED: $($_.Exception.Message)"
    $r = $_.Exception.Response
    if ($r) {
        $sr = New-Object System.IO.StreamReader($r.GetResponseStream())
        $sr.ReadToEnd()
    }
    exit 6
}
