@echo off
pyside6-uic main.ui > modules\ui_main.py
pyside6-rcc resources.qrc -o modules\resources_rc.py
chcp 437 > nul
powershell -Command "(gc modules\ui_main.py) -replace 'import resources_rc', 'from . resources_rc import *' | Out-File -encoding ascii modules\ui_main.py"
