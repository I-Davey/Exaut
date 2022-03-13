Title Range: GIT2.PyInstaller_SQL\PICAT_SQL\Py - started ([PICAT_SerMan.xlsm]PICAT_GIT!:339)
ECHO "18/09/10 15:38"
ECHO "PyInstaller SQLD:\PICAT\PICAT_SQL\Py to D:\PICAT" R:342
@REM
@REM
d:
CD D:\PICAT\PICAT_SQL\Py\
@REM
@REM
@REM
pyi-makespec --windowed --onefile --noupx "D:\PICAT\PICAT_SQL\Py\PICAT_SQL.py" 
pyinstaller  --clean PICAT_SQL.spec
@REM
@REM
Copy "D:\PICAT\PICAT_SQL\Py\__pycache__\PICAT_SQL.cpython-36.pyc" /y  "D:\PICAT\PICAT_SQL.pyw"
Copy "D:\PICAT\PICAT_SQL\Py\dist\PICAT_SQL.exe" /y  "D:\PICAT\PICAT_SQL.exe"
Copy "D:\PICAT\PICAT_SQL\Py\PICAT_SQL.py" /y D:\PICAT\
pyi-makespec --windowed --onefile --noupx "D:\PICAT\PICAT_SQL\Py\PICAT_SQL_Generate.py" 
pyinstaller  --clean PICAT_SQL_Generate.spec
@REM
@REM
Copy "D:\PICAT\PICAT_SQL\Py\__pycache__\PICAT_SQL_Generate.cpython-36.pyc" /y  "D:\PICAT\PICAT_SQL_Generate.pyw"
Copy "D:\PICAT\PICAT_SQL\Py\dist\PICAT_SQL_Generate.exe" /y  "D:\PICAT\PICAT_SQL_Generate.exe"
Copy "D:\PICAT\PICAT_SQL\Py\PICAT_SQL_Generate.py" /y D:\PICAT\
Copy "D:\PICAT\PICAT_SQL\Py\PICAT_SQL_*.py" /y D:\PICAT\
@REM
@REM
PAUSE

