@ECHO OFF
pip install pyinstaller
python -m PyInstaller WMATA_Account.py --onefile
cd .\dist
move "WMATA_Account.exe" ./..
cd ..
RD /S /Q .\dist
del .\WMATA_Account.spec
RD /S /Q .\build