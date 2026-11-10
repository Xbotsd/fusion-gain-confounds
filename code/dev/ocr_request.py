"""OCR the request screenshot using Windows.Media.Ocr (needs pywin32-free approach).

Uses PowerShell script generated on the fly; falls back to reporting failure.
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
IMG = ROOT / "raw" / "request_20261107.png"

PS = r'''
param([string]$OutFile)
$path = "IMGPATH"
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType=WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Foundation, ContentType=WindowsRuntime]
$null = [Windows.Storage.StorageFile, Windows.Foundation, ContentType=WindowsRuntime]
Function Await($WinRtTask, $ResultType) {
    $asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
    $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
    $netTask = $asTask.Invoke($null, @($WinRtTask))
    $netTask.Wait(-1) | Out-Null
    $netTask.Result
}
$file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($path)) ([Windows.Storage.StorageFile])
$stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
$decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
$bmp = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
$ocrEngine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
$result = Await ($ocrEngine.RecognizeAsync($bmp)) ([Windows.Media.Ocr.OcrResult])
$result.Text | Out-File -FilePath $OutFile -Encoding utf8
'''.replace("IMGPATH", str(IMG))


def main():
    script = ROOT / "raw" / "ocr_req.ps1"
    script.write_text(PS, encoding="utf-8-sig")
    outfile = ROOT / "raw" / "ocr_result.txt"
    try:
        r = subprocess.run(
            ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", str(script),
             "-OutFile", str(outfile)],
            capture_output=True, timeout=120)
        print("rc:", r.returncode)
    except Exception as exc:  # noqa: BLE001
        print(f"powershell failed: {exc}")
        return
    if outfile.exists():
        print(outfile.read_text(encoding="utf-8", errors="replace"))
    else:
        print("no output file; stderr:", r.stderr[:300] if r.stderr else b"")


if __name__ == "__main__":
    main()
