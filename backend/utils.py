"""
工具函数模块
提供项目中共用的辅助函数，避免多处重复实现
"""

import hashlib
import logging
from pathlib import Path
from typing import Optional, Union

logger = logging.getLogger(__name__)


def compute_md5(path: Union[str, Path], chunk_size: int = 1024 * 1024) -> Optional[str]:
    """计算文件 MD5 哈希值

    Args:
        path: 文件路径（str 或 Path）
        chunk_size: 读取块大小，默认 1MB

    Returns:
        32 位小写十六进制 MD5 字符串，失败时返回 None
    """
    try:
        hasher = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logger.error(f"计算 MD5 失败 [{path}]: {e}")
        return None
