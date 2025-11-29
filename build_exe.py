import PyInstaller.__main__
import os

# Get the absolute path to the script and assets
script_dir = os.path.dirname(os.path.abspath(__file__))
app_script = os.path.join(script_dir, 'PC client', 'orca_deck_app.py')
assets_dir = os.path.join(script_dir, 'assets')

print(f"Building executable with arguments:")
print(app_script)
print(f"--name=ORCA DECK")
print(f"--onefile")
print(f"--windowed")
print(f"--add-data={assets_dir};assets")
print(f"--collect-all=customtkinter")
print(f"--clean")
print(f"--noconfirm")

PyInstaller.__main__.run([
    app_script,
    '--name=ORCA DECK',
    '--onefile',
    '--windowed',
    f'--add-data={assets_dir};assets',
    '--collect-all=customtkinter',
    '--clean',
    '--noconfirm'
])
