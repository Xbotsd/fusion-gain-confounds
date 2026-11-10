@echo off
REM A_MineralProspecting pipeline launcher.
REM Forwards all arguments to run_all.py using an interpreter that has
REM numpy/scipy/GDAL (the `geo` conda environment). Any Python >= 3.9 can
REM launch this script; run_all.py resolves the right interpreter itself.

setlocal
set "ROOT=%~dp0"
python "%ROOT%code\run_all.py" %*
endlocal
