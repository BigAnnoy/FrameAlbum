#!/usr/bin/env python3
"""
重置配置脚本
用于测试初始化屏幕
"""

from backend.config_manager import get_config_manager

# 获取配置管理器
config = get_config_manager()

# 重置配置
print("开始重置配置...")
config.reset_config()
print("配置已重置为默认值")

# 显示当前配置
print("\n当前配置:")
print(f"首次运行: {config.is_first_run()}")
print(f"相册路径: {config.get_album_path()}")
print("\n重置完成，请重新启动应用")
