#!/usr/bin/env python3
"""
FFmpeg 自动下载脚本
==================
自动检测当前平台（Windows / macOS / Linux），下载对应的 FFmpeg 静态编译版，
解压后放置到 backend/ffmpeg_binaries/ 目录，供应用程序直接使用。

用法：
    python scripts/download_ffmpeg.py

特性：
    - 幂等：已存在可执行文件则跳过，不重复下载
    - 带下载进度显示
    - 仅使用 Python 标准库，无额外依赖
    - 自动验证：下载后运行 ffmpeg -version 确认可用

下载源：
    - Windows : https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
    - macOS   : https://evermeet.cx/ffmpeg/  (两个独立 zip)
    - Linux   : https://johnvansickle.com/ffmpeg/  (tar.xz)
"""

import os
import sys
import platform
import subprocess
import tempfile
import zipfile
import tarfile
import shutil
import glob
import socket
from pathlib import Path
from urllib.request import urlretrieve, urlopen
from urllib.error import URLError, HTTPError

# Windows 控制台默认 GBK 编码，强制切换为 UTF-8，避免 print 崩溃
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# 全局下载超时（秒）：避免网络卡死时脚本挂起
socket.setdefaulttimeout(120)

# ── 路径定义 ────────────────────────────────────────────────────────────────
SCRIPT_DIR   = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
BIN_DIR      = PROJECT_ROOT / "backend" / "ffmpeg_binaries"

# ── 下载源配置 ───────────────────────────────────────────────────────────────
WINDOWS_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

# macOS: 从 evermeet.cx 获取最新版本号后构建 URL（两个独立文件）
MACOS_BASE_URL    = "https://evermeet.cx/ffmpeg"
MACOS_FFMPEG_URL  = f"{MACOS_BASE_URL}/getrelease/ffmpeg/zip"
MACOS_FFPROBE_URL = f"{MACOS_BASE_URL}/getrelease/ffprobe/zip"

# Linux: 静态编译版（根据架构选择）
LINUX_ARCH_MAP = {
    "x86_64"  : "amd64",
    "aarch64" : "arm64",
    "armv7l"  : "armhf",
}
LINUX_BASE_URL = "https://johnvansickle.com/ffmpeg/releases"


# ── 工具函数 ─────────────────────────────────────────────────────────────────

def _progress_hook(block_num: int, block_size: int, total_size: int):
    """urlretrieve 进度回调，显示下载进度条"""
    if total_size <= 0:
        downloaded = block_num * block_size
        print(f"\r  已下载 {downloaded / 1024 / 1024:.1f} MB ...", end="", flush=True)
        return
    downloaded = min(block_num * block_size, total_size)
    pct = downloaded / total_size * 100
    bar_len = 40
    filled = int(bar_len * downloaded / total_size)
    bar = "█" * filled + "░" * (bar_len - filled)
    size_mb = total_size / 1024 / 1024
    done_mb = downloaded / 1024 / 1024
    print(f"\r  [{bar}] {pct:5.1f}%  {done_mb:.1f}/{size_mb:.1f} MB", end="", flush=True)
    if downloaded >= total_size:
        print()  # 换行


def _is_executable(path: Path) -> bool:
    """检查文件是否存在且可执行"""
    if not path.exists():
        return False
    if sys.platform == "win32":
        return path.stat().st_size > 1024 * 1024  # > 1 MB 视为有效
    return os.access(path, os.X_OK) and path.stat().st_size > 1024 * 1024


def _set_executable(path: Path):
    """给文件添加可执行权限（Unix 平台）"""
    if sys.platform != "win32":
        path.chmod(path.stat().st_mode | 0o755)


def _verify_ffmpeg(ffmpeg_path: Path, ffprobe_path: Path):
    """运行 ffmpeg -version 验证安装"""
    print("\n── 验证安装 ────────────────────────────────")
    for binary, path in [("ffmpeg", ffmpeg_path), ("ffprobe", ffprobe_path)]:
        try:
            result = subprocess.run(
                [str(path), "-version"],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                first_line = result.stdout.splitlines()[0]
                print(f"  ✅ {binary}: {first_line}")
            else:
                print(f"  ❌ {binary}: 验证失败 - {result.stderr.splitlines()[0] if result.stderr else '未知错误'}")
        except Exception as e:
            print(f"  ❌ {binary}: 运行出错 - {e}")


def _download_file(url: str, dest: Path, desc: str = ""):
    """下载文件到指定路径"""
    label = desc or dest.name
    print(f"  下载 {label}")
    print(f"  来源: {url}")
    try:
        urlretrieve(url, str(dest), reporthook=_progress_hook)
    except (URLError, HTTPError) as e:
        raise RuntimeError(f"下载失败: {e}") from e


# ── Windows 下载逻辑 ─────────────────────────────────────────────────────────

def download_windows():
    """下载并安装 Windows 版 FFmpeg"""
    _exe = ".exe"
    ffmpeg_dest  = BIN_DIR / f"ffmpeg{_exe}"
    ffprobe_dest = BIN_DIR / f"ffprobe{_exe}"

    if _is_executable(ffmpeg_dest) and _is_executable(ffprobe_dest):
        print("  ✅ ffmpeg.exe 和 ffprobe.exe 已存在，跳过下载。")
        print("     如需强制重新下载，请先手动删除上述文件再运行此脚本。")
        return ffmpeg_dest, ffprobe_dest

    # 使用 mkdtemp + finally 手动清理，避免 Windows 上 TemporaryDirectory 清理时
    # 因 exe 句柄未释放而报 PermissionError
    tmpdir = tempfile.mkdtemp()
    try:
        zip_path = Path(tmpdir) / "ffmpeg.zip"
        _download_file(WINDOWS_URL, zip_path, "ffmpeg-essentials.zip (约 80MB)")

        print("  解压中 ...")
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmpdir)

        # zip 内有版本号目录，如 ffmpeg-8.1-essentials_build/bin/ffmpeg.exe
        found_ffmpeg  = glob.glob(os.path.join(tmpdir, "**", "bin", "ffmpeg.exe"),  recursive=True)
        found_ffprobe = glob.glob(os.path.join(tmpdir, "**", "bin", "ffprobe.exe"), recursive=True)

        if not found_ffmpeg or not found_ffprobe:
            raise RuntimeError("解压后未找到 ffmpeg.exe / ffprobe.exe，ZIP 包结构可能已变化")

        BIN_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(found_ffmpeg[0],  ffmpeg_dest)
        shutil.copy2(found_ffprobe[0], ffprobe_dest)
        print(f"  已复制到 {BIN_DIR}")
    finally:
        # ignore_errors=True：Windows 偶发句柄残留时静默跳过，临时目录重启后自动清理
        shutil.rmtree(tmpdir, ignore_errors=True)

    return ffmpeg_dest, ffprobe_dest


# ── macOS 下载逻辑 ────────────────────────────────────────────────────────────

def download_macos():
    """下载并安装 macOS 版 FFmpeg（两个独立 zip）"""
    ffmpeg_dest  = BIN_DIR / "ffmpeg"
    ffprobe_dest = BIN_DIR / "ffprobe"

    if _is_executable(ffmpeg_dest) and _is_executable(ffprobe_dest):
        print("  ✅ ffmpeg 和 ffprobe 已存在，跳过下载。")
        return ffmpeg_dest, ffprobe_dest

    BIN_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        for name, url in [("ffmpeg", MACOS_FFMPEG_URL), ("ffprobe", MACOS_FFPROBE_URL)]:
            zip_path = Path(tmpdir) / f"{name}.zip"
            _download_file(url, zip_path, f"{name} (macOS 静态版)")

            print(f"  解压 {name} ...")
            # 每个 zip 用独立子目录，避免 ffmpeg/ffprobe 同名文件互相覆盖
            extract_dir = Path(tmpdir) / name
            extract_dir.mkdir()
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(extract_dir)

            # evermeet.cx 的包解压后直接是可执行文件（无子目录）
            candidates = list(extract_dir.rglob(name))
            found = next((p for p in candidates if p.is_file()), None)
            if not found:
                raise RuntimeError(f"解压后未找到 {name}，包结构可能已变化")

            dest = BIN_DIR / name
            shutil.copy2(found, dest)
            _set_executable(dest)

    print(f"  ✅ 已复制到 {BIN_DIR}")
    return ffmpeg_dest, ffprobe_dest


# ── Linux 下载逻辑 ────────────────────────────────────────────────────────────

def download_linux():
    """下载并安装 Linux 版 FFmpeg (tar.xz 静态编译版)"""
    ffmpeg_dest  = BIN_DIR / "ffmpeg"
    ffprobe_dest = BIN_DIR / "ffprobe"

    if _is_executable(ffmpeg_dest) and _is_executable(ffprobe_dest):
        print("  ✅ ffmpeg 和 ffprobe 已存在，跳过下载。")
        return ffmpeg_dest, ffprobe_dest

    machine = platform.machine()
    arch = LINUX_ARCH_MAP.get(machine)
    if not arch:
        raise RuntimeError(
            f"不支持的 Linux 架构：{machine}\n"
            f"支持的架构：{', '.join(LINUX_ARCH_MAP.keys())}\n"
            f"请手动从 https://johnvansickle.com/ffmpeg/ 下载并放置到 {BIN_DIR}"
        )

    url = f"{LINUX_BASE_URL}/ffmpeg-release-{arch}-static.tar.xz"
    BIN_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        tar_path = Path(tmpdir) / "ffmpeg.tar.xz"
        _download_file(url, tar_path, f"ffmpeg-release-{arch}-static.tar.xz (约 75MB)")

        print("  解压中 ...")
        with tarfile.open(tar_path, "r:xz") as tf:
            tf.extractall(tmpdir)

        found_ffmpeg  = glob.glob(os.path.join(tmpdir, "**", "ffmpeg"),  recursive=True)
        found_ffprobe = glob.glob(os.path.join(tmpdir, "**", "ffprobe"), recursive=True)

        # 排除目录，只取文件
        found_ffmpeg  = [p for p in found_ffmpeg  if os.path.isfile(p)]
        found_ffprobe = [p for p in found_ffprobe if os.path.isfile(p)]

        if not found_ffmpeg or not found_ffprobe:
            raise RuntimeError("解压后未找到 ffmpeg / ffprobe，包结构可能已变化")

        shutil.copy2(found_ffmpeg[0],  ffmpeg_dest)
        shutil.copy2(found_ffprobe[0], ffprobe_dest)
        _set_executable(ffmpeg_dest)
        _set_executable(ffprobe_dest)
        print(f"  ✅ 已复制到 {BIN_DIR}")

    return ffmpeg_dest, ffprobe_dest


# ── 主入口 ────────────────────────────────────────────────────────────────────

def main():
    system = platform.system()

    print("=" * 60)
    print(" FFmpeg 自动下载脚本")
    print("=" * 60)
    print(f"  平台   : {system} ({platform.machine()})")
    print(f"  目标目录: {BIN_DIR}")
    print()

    try:
        if system == "Windows":
            ffmpeg_path, ffprobe_path = download_windows()
        elif system == "Darwin":
            ffmpeg_path, ffprobe_path = download_macos()
        elif system == "Linux":
            ffmpeg_path, ffprobe_path = download_linux()
        else:
            print(f"❌ 不支持的操作系统：{system}")
            print(f"   请手动下载 FFmpeg 并将 ffmpeg/ffprobe 放置到：{BIN_DIR}")
            sys.exit(1)

        _verify_ffmpeg(ffmpeg_path, ffprobe_path)

        print()
        print("=" * 60)
        print(" ✅ FFmpeg 准备完成！现在可以正常使用视频功能。")
        print("=" * 60)

    except RuntimeError as e:
        print(f"\n❌ 下载失败：{e}")
        print(f"\n请手动下载并放置到：{BIN_DIR}")
        print("  Windows : https://www.gyan.dev/ffmpeg/builds/")
        print("  macOS   : https://evermeet.cx/ffmpeg/")
        print("  Linux   : https://johnvansickle.com/ffmpeg/")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 下载已取消。")
        sys.exit(1)


if __name__ == "__main__":
    main()
