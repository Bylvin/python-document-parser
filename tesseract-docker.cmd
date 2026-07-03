@echo off
REM Wrapper yang dipanggil Docling sebagai `tesseract`. Meneruskan semua argumen
REM ke scripts\tesseract_via_docker.py (path host -> container + docker exec).
REM %~dp0 = folder tempat .cmd ini berada (root project, dengan trailing backslash).
python "%~dp0scripts\tesseract_via_docker.py" %*
