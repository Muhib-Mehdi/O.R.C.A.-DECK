import PyInstaller.__main__
import os

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_SCRIPT = os.path.join(BASE_DIR, "PC client", "orca_deck_app.py")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# PyInstaller arguments
args = [
    APP_SCRIPT,
    '--name=ORCA DECK',
    '--onefile',
    '--windowed',
    f'--add-data={ASSETS_DIR}{os.pathsep}assets',
    '--collect-all=customtkinter',
    '--clean',
    '--noconfirm',
]

print("Building executable with arguments:")
for arg in args:
    print(arg)

PyInstaller.__main__.run(args)
