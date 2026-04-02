#!/usr/bin/env python3
"""
检查配置文件脚本
用于查看当前配置状态
"""

from backend.config_manager import get_config_manager

# 获取配置管理器
config = get_config_manager()

# 显示当前配置
print("=== 配置状态检查 ===")
print(f"配置文件路径: {config.CONFIG_FILE}")
print(f"配置文件存在: {config.CONFIG_FILE.exists()}")
print(f"首次运行: {config.is_first_run()}")
print(f"相册路径: {config.get_album_path()}")
print(f"完整配置: {config.get_all_config()}")

# 检查路径是否存在
album_path = config.get_album_path()
if album_path:
    from pathlib import Path
    path_obj = Path(album_path)
    print(f"\n=== 路径检查 ===")
    print(f"路径存在: {path_obj.exists()}")
    print(f"是目录: {path_obj.is_dir()}")
