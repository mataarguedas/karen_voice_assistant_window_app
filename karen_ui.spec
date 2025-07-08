# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['karen_ui.py'],
    pathex=[],
    binaries=[],
    datas=[('hey_karen_en.ppn', '.'), ('hey_karen_es.ppn', '.'), ('porcupine_params_es.pv', '.'), ('karenCirclePic.PNG', '.'), ('karenPic.jpeg', '.'), ('voice_indicator.png', '.'), ('venvKUI\\Lib\\site-packages\\pvporcupine\\resources', 'pvporcupine\\resources'), ('venvKUI\\Lib\\site-packages\\pvporcupine\\lib\\windows\\amd64', 'pvporcupine\\lib\\windows\\amd64'), ('C:\\Users\\Emma~\\karenUI\\venvKUI\\Lib\\site-packages\\pvporcupine\\lib\\common', 'pvporcupine\\lib\\common')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='karen_ui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
