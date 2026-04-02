#!/usr/bin/env python3
"""
测试相册统计功能
用于定位统计信息获取失败的问题
"""

import sys
import os
from pathlib import Path

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from backend.api_server import get_album_stats, get_album_path

# 测试获取相册路径
print("=== 测试相册路径 ===")
album_path = get_album_path()
print(f"相册路径: {album_path}")

# 测试获取统计信息
print("\n=== 测试统计信息 ===")
try:
    stats = get_album_stats()
    print(f"统计信息: {stats}")
    if stats:
        print(f"总文件数: {stats.get('total_files')}")
        print(f"总大小: {stats.get('total_size_mb')} MB")
        print(f"年份数: {len(stats.get('years', {}))}")
    else:
        print("❌ 统计信息获取失败")
except Exception as e:
    print(f"❌ 异常: {e}")
    import traceback
    traceback.print_exc()

# 测试遍历目录
print("\n=== 测试目录遍历 ===")
try:
    if album_path:
        album_path_obj = Path(album_path)
        print(f"目录存在: {album_path_obj.exists()}")
        print(f"是目录: {album_path_obj.is_dir()}")
        
        print("\n目录内容:")
        for item in album_path_obj.iterdir():
            print(f"  {item.name} ({'目录' if item.is_dir() else '文件'})")
    else:
        print("❌ 相册路径为空")
except Exception as e:
    print(f"❌ 遍历目录异常: {e}")
    import traceback
    traceback.print_exc()
