call .venv\Scripts\activate

python -m nuitka --file-version=1.0.0 --standalone --no-pyi-file --jobs=8 --clean-cache=all --lto=yes --plugin-enable=tk-inter,upx --upx-binary=upx.exe --windows-icon-from-ico=link.ico --windows-console-mode=disable --output-filename=connect.exe --include-data-file=icon.png=icon.png main.py

pause
