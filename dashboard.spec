# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('Questions.xlsx', '.'),
        ('Chat Data Numeric.xlsx', '.'),
        ('Chat Data Text.xlsx', '.')
    ],
    hiddenimports=[
        'pandas',
        'numpy',
        'plotly',
        'dash',
        'dash_bootstrap_components',
        'openpyxl',
        'flask',
        'werkzeug',
        'jinja2',
        'itsdangerous',
        'click',
        'dash_html_components',
        'dash_core_components',
        'dash_table',
        'plotly.graph_objects',
        'plotly.express',
        're',
        'json',
        'datetime',
        'webbrowser'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='dashboard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
) 