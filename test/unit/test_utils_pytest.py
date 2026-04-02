"""
工具函数模块测试 (pytest版本)
测试 utils.py 中的所有公共 API 方法
"""

import tempfile
import shutil
from pathlib import Path

import pytest

from backend.utils import compute_md5


@pytest.fixture
def temp_file():
    """创建临时文件fixture"""
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir) / "test_file.txt"
    
    with open(temp_path, 'w') as f:
        f.write("Hello, World!")
    
    yield temp_path
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def large_temp_file():
    """创建大文件fixture，用于测试分块读取"""
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir) / "large_test_file.bin"
    
    with open(temp_path, 'wb') as f:
        f.write(b'0' * (2 * 1024 * 1024))
    
    yield temp_path
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_compute_md5_success(temp_file):
    """测试成功计算文件MD5"""
    md5_hash = compute_md5(temp_file)
    
    assert md5_hash is not None
    assert isinstance(md5_hash, str)
    assert len(md5_hash) == 32


def test_compute_md5_nonexistent_file():
    """测试计算不存在的文件的MD5"""
    md5_hash = compute_md5("nonexistent_file.txt")
    
    assert md5_hash is None


def test_compute_md5_large_file(large_temp_file):
    """测试计算大文件的MD5"""
    md5_hash = compute_md5(large_temp_file)
    
    assert md5_hash is not None
    assert len(md5_hash) == 32


def test_compute_md5_with_custom_chunk_size(temp_file):
    """测试使用自定义块大小计算MD5"""
    md5_hash = compute_md5(temp_file, chunk_size=512)
    
    assert md5_hash is not None
    assert len(md5_hash) == 32


def test_compute_md5_with_pathlib(temp_file):
    """测试使用Path对象计算MD5"""
    md5_hash = compute_md5(Path(temp_file))
    
    assert md5_hash is not None
    assert len(md5_hash) == 32
