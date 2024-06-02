@REM D:\VSCodeProjects\MoneyPrinter2\mp\Scripts\pyinstaller.exe -y -D main.py -n app --collect-all paddleocr --collect-all paddle --collect-all pyclipper --collect-all shapely --collect-all skimage --collect-all concurrent --collect-all imgaug -i money.ico
pyinstaller -y -D main.py -n app --collect-all paddleocr --collect-all paddle --collect-all pyclipper --collect-all shapely --collect-all skimage --collect-all concurrent --collect-all imgaug -i money.ico
pyarmor gen -O obfdist --pack dist/app/app.exe main.py
xcopy Tesseract-OCR dist\app\Tesseract-OCR /E /I /Y
copy runfile\conf.ini dist\app\conf.ini /Y
xcopy runfile\paddleocr dist\app\paddleocr /E /I /Y