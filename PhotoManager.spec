# -*- mode: python ; coding: utf-8 -*-
"""
FrameAlbum v0.1 - PyInstaller 打包配置
生成：dist/FrameAlbum/ 文件夹（包含 FrameAlbum.exe）

打包命令：
    pyinstaller PhotoManager.spec --clean

输出目录：dist/FrameAlbum/
"""

import sys
from pathlib import Path

# ─── 路径定义 ───────────────────────────────────────────────
ROOT = Path(SPECPATH)  # 项目根目录（spec 文件所在目录）

import importlib.util, site
def _pkg_dir(name):
    """动态获取已安装包的目录路径"""
    spec = importlib.util.find_spec(name)
    if spec and spec.origin:
        return str(Path(spec.origin).parent)
    for sp in site.getsitepackages():
        p = Path(sp) / name
        if p.exists():
            return str(p)
    raise RuntimeError(f"Cannot find package: {name}")

block_cipher = None

# ─── 数据文件（随 exe 一起打包的非 Python 文件）──────────────
datas = [
    # 前端静态资源（整个目录）
    (str(ROOT / 'frontend'), 'frontend'),
    # pillow_heif 插件数据（动态路径）
    (_pkg_dir('pillow_heif'), 'pillow_heif'),
]

# 如果 ffmpeg_binaries 目录存在，一并打包（与 video_processor.py / check_ffmpeg() 路径对齐）
ffmpeg_dir = ROOT / 'backend' / 'ffmpeg_binaries'
if ffmpeg_dir.exists():
    datas.append((str(ffmpeg_dir), 'backend/ffmpeg_binaries'))

# ─── 隐藏导入（PyInstaller 静态分析可能遗漏的模块）────────────
hiddenimports = [
    # Flask 相关
    'flask',
    'flask_cors',
    'werkzeug',
    'werkzeug.serving',
    'werkzeug.routing',
    'werkzeug.exceptions',
    'jinja2',
    'jinja2.ext',
    'click',
    # SQLAlchemy
    'sqlalchemy',
    'sqlalchemy.dialects.sqlite',
    'sqlalchemy.orm',
    'sqlalchemy.ext.declarative',
    # Pillow
    'PIL',
    'PIL.Image',
    'PIL.ExifTags',
    'PIL.ImageOps',
    # pillow_heif
    'pillow_heif',
    # python-dateutil
    'dateutil',
    'dateutil.parser',
    # tkinter（文件夹选择对话框）
    'tkinter',
    'tkinter.filedialog',
    # 标准库补充
    'email',
    'email.mime',
    'email.mime.text',
    'html.parser',
    # pywebview
    'webview',
    'webview.platforms',
    'webview.platforms.winforms',
    # Windows Toast 桌面通知（可选依赖，打包时预声明）
    'win10toast',
    'win10toast.notification',
    'threading',
]

# ─── 需要排除的模块（减小体积）────────────────────────────────
excludes = [
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'IPython',
    'notebook',
    'jupyter',
    'test',
    'unittest',
    'setuptools',
    'pkg_resources',
    'pip',
    # 额外精简（v0.1 新增）
    'tkinter.test',
    'distutils',
    'doctest',
    'pydoc',
    'xmlrpc',
    'curses',
    'lib2to3',
    'turtledemo',
    'turtle',
    'idlelib',
    '_pydev_bundle',
    'pydevd',
    'pdb',
    'profile',
    'pstats',
    'cProfile',
    'difflib',
    'ftplib',
    'imaplib',
    'smtplib',
    'poplib',
    'nntplib',
    'telnetlib',
    'msilib',
    'antigravity',
]

# ─── Analysis ──────────────────────────────────────────────
a = Analysis(
    [str(ROOT / 'src' / 'FrameAlbum.py')],  # 入口文件
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],  # pywebview 自带 __pyinstaller hook，无需额外指定
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# ─── PYZ（Python 字节码归档）──────────────────────────────────
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

# ─── EXE ────────────────────────────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # 二进制文件放到 COLLECT/BUNDLE，不内嵌
    name='FrameAlbum',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,          # 开启 UPX 压缩（如果系统有 upx 命令）
    console=False,     # 不显示控制台窗口（GUI 模式）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='docs/icon.ico',  # 图标文件路径
)

if sys.platform == 'darwin':
    # macOS 平台：生成 .app 包
    app = BUNDLE(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        name='FrameAlbum.app',
        icon='docs/icon.icns',  # macOS 图标文件
        bundle_identifier='com.framealbum.app',  # Bundle ID
        info_plist={
            'NSHighResolutionCapable': 'True',
            'CFBundleShortVersionString': '0.4.0',
            'CFBundleVersion': '0.4.0',
        },
    )
else:
    # Windows/Linux 平台：生成文件夹模式，将所有文件收集到 dist/FrameAlbum/
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        # upx_exclude：保护关键动态库不被 UPX 压坏
        upx_exclude=[
            'vcruntime140.dll',
            'vcruntime140_1.dll',
            'msvcp140.dll',
            'python3*.dll',
            'webview2loader.dll',
            'WebView2Loader.dll',
        ],
        name='FrameAlbum',
    )
