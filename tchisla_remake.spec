# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['tchisla_remake.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
a.datas += [("tchisla_remake_icon.ico", "D:\\Programs\\Jupyter\\tkinter\\my_tchisla\\tchisla_remake_icon.ico", "DATA"),
("Laura Shigihara - Loonboon.mp3", "D:\\Programs\\Jupyter\\tkinter\\my_tchisla\\Laura Shigihara - Loonboon.mp3", "DATA")]
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='tchisla_remake',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon="D:\\Programs\\Jupyter\\tkinter\\my_tchisla\\tchisla_remake_icon.ico" )
