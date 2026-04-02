"""
导入管理器单元测试 (pytest版本)
测试导入管理器的核心功能
"""

import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from backend.import_manager import get_import_manager, FileConflict, ImportStatus


@pytest.fixture
def temp_source_dir():
    """创建临时源目录fixture"""
    temp_dir = tempfile.mkdtemp()
    
    # 创建测试文件
    with open(os.path.join(temp_dir, "test_photo_1.jpg"), "w") as f:
        f.write("dummy photo 1 content")
    
    with open(os.path.join(temp_dir, "test_photo_2.jpg"), "w") as f:
        f.write("dummy photo 2 content")
    
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_target_dir():
    """创建临时目标目录fixture"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def import_manager():
    """创建导入管理器fixture"""
    return get_import_manager()


def test_import_manager_initialization():
    """测试导入管理器初始化"""
    manager = get_import_manager()
    assert manager is not None


def test_create_import(import_manager, temp_source_dir, temp_target_dir):
    """测试创建导入任务"""
    import_id = "test_import_123"
    
    import_manager.create_import(import_id, temp_source_dir, temp_target_dir)
    
    # 验证导入任务已创建
    progress = import_manager.get_progress(import_id)
    assert progress is not None
    assert progress.import_id == import_id


def test_get_progress_non_existent(import_manager):
    """测试获取不存在的导入任务进度"""
    progress = import_manager.get_progress("non_existent_import")
    assert progress is None


def test_get_progress_dict(import_manager, temp_source_dir, temp_target_dir):
    """测试获取导入任务进度字典"""
    import_id = "test_import_456"
    import_manager.create_import(import_id, temp_source_dir, temp_target_dir)
    
    progress_dict = import_manager.get_progress_dict(import_id)
    assert progress_dict is not None
    assert isinstance(progress_dict, dict)
    assert 'import_id' in progress_dict
    assert progress_dict['import_id'] == import_id


def test_cancel_import(import_manager, temp_source_dir, temp_target_dir):
    """测试取消导入任务"""
    import_id = "test_import_789"
    import_manager.create_import(import_id, temp_source_dir, temp_target_dir)
    
    result = import_manager.cancel_import(import_id)
    assert result is None
    
    # 验证导入任务仍可访问
    progress = import_manager.get_progress(import_id)
    assert progress is not None

def test_cancel_non_existent_import(import_manager):
    """测试取消不存在的导入任务"""
    result = import_manager.cancel_import("non_existent_import")
    assert result is None

def test_pause_import(import_manager, temp_source_dir, temp_target_dir):
    """测试暂停导入任务"""
    import_id = "test_import_101"
    import_manager.create_import(import_id, temp_source_dir, temp_target_dir)
    
    result = import_manager.pause_import(import_id)
    assert result is None
    
    # 验证导入任务仍可访问
    progress = import_manager.get_progress(import_id)
    assert progress is not None

def test_resume_import(import_manager, temp_source_dir, temp_target_dir):
    """测试继续导入任务"""
    import_id = "test_import_202"
    import_manager.create_import(import_id, temp_source_dir, temp_target_dir)
    
    result = import_manager.pause_import(import_id)
    assert result is None
    
    result = import_manager.resume_import(import_id)
    assert result is None
    
    # 验证导入任务仍可访问
    progress = import_manager.get_progress(import_id)
    assert progress is not None


def test_file_conflict_enum():
    """测试文件冲突枚举"""
    # 测试枚举值存在且正确
    assert FileConflict.NONE.value == "none"
    assert FileConflict.MD5_DUPLICATE.value == "md5"
    assert FileConflict.NAME_DUPLICATE.value == "name"
    
    # 测试枚举类型
    assert isinstance(FileConflict.NONE, FileConflict)
    assert isinstance(FileConflict.MD5_DUPLICATE, FileConflict)
    assert isinstance(FileConflict.NAME_DUPLICATE, FileConflict)


def test_file_conflict_values():
    """测试文件冲突枚举值"""
    # 测试所有枚举值
    conflict_values = [item.value for item in FileConflict]
    assert "none" in conflict_values
    assert "md5" in conflict_values
    assert "name" in conflict_values

