# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Define data files to include (only embed assets, not data)
datas = [
    ('assets', 'assets'),
]

# Define hidden imports (only what we actually need)
hiddenimports = [
    'PyQt5.QtCore',
    'PyQt5.QtGui', 
    'PyQt5.QtWidgets',
    'keyboard',
    'PIL',
    'PIL.Image',
    'PIL.ImageQt',
    'pystray',
    'src',
    'src.system_tray',
    'src.core',
    'src.core.constants',
    'src.core.utils',
    'src.ui',
    'src.ui.main_window',
    'src.ui.drawing_area',
    'src.ui.draggable_list',
    'src.ui.screenshot_selector',
    'src.ui.styles',
]

# Exclude unnecessary modules to reduce size
excludes = [
    'pandas',
    'numpy',
    'matplotlib',
    'scipy',
    'sklearn',
    'tensorflow',
    'torch',
    'transformers',
    'notebook',
    'jupyter',
    'IPython',
    'tkinter',
    'test',
    'unittest',
    '_testcapi',
    '_testimportmultiple',
    'doctest',
    'pdb',
    'profile',
    'pstats',
    'trace',
    'difflib',
    'ctypes.test',
    'lib2to3',
    'turtledemo',
]

a = Analysis(
    ['main.py'],
    pathex=['.', 'src'],  # Add current dir and src to Python path
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SnapTrace',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,  # Disable strip since tool not found
    upx=True,    # Use UPX compression
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for windowed app (no console)
    disable_windowing_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/logo.ico',  # Application icon
)
