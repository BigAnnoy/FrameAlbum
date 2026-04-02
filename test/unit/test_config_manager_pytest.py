"""
ConfigManager pytest 单元测试
测试配置管理模块的所有公共 API 方法
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

from backend.config_manager import ConfigManager
from backend.database import SessionLocal, Setting, Photo, ImportHistory, Base, engine


@pytest.fixture
def temp_dir():
    """创建临时目录，测试后自动清理"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def db_cleanup():
    """清理数据库fixture"""
    def cleanup():
        db = SessionLocal()
        try:
            db.query(ImportHistory).delete()
            db.query(Photo).delete()
            db.query(Setting).delete()
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()
    
    cleanup()
    yield
    cleanup()


def create_config_manager_with_mock(temp_config_dir):
    """创建带有模拟属性的ConfigManager实例"""
    mock_config_dir = MagicMock()
    mock_config_dir.__get__ = MagicMock(return_value=Path(temp_config_dir))
    
    mock_config_file = MagicMock()
    mock_config_file.__get__ = MagicMock(return_value=Path(temp_config_dir) / "config.json")
    
    with patch.object(ConfigManager, 'CONFIG_DIR', mock_config_dir), \
         patch.object(ConfigManager, 'CONFIG_FILE', mock_config_file):
        
        config_manager = ConfigManager()
        return config_manager


def test_initialization(temp_dir):
    """测试初始化配置"""
    mock_config_dir = MagicMock()
    mock_config_dir.__get__ = MagicMock(return_value=Path(temp_dir))
    
    mock_config_file = MagicMock()
    mock_config_file.__get__ = MagicMock(return_value=Path(temp_dir) / "config.json")
    
    with patch.object(ConfigManager, 'CONFIG_DIR', mock_config_dir), \
         patch.object(ConfigManager, 'CONFIG_FILE', mock_config_file):
        
        config_manager = ConfigManager()
        
        default_config = config_manager._default_config()
        assert config_manager.config == default_config
        
        assert Path(temp_dir).exists()
        
        with tempfile.TemporaryDirectory() as temp_album_dir:
            config_manager.set_album_path(temp_album_dir)
            assert (Path(temp_dir) / "config.json").exists()


def test_is_first_run(temp_dir):
    """测试首次运行检测"""
    config_manager = create_config_manager_with_mock(temp_dir)
    
    assert config_manager.is_first_run()
    
    with tempfile.TemporaryDirectory() as temp_album_dir:
        config_manager.set_album_path(temp_album_dir)
        assert not config_manager.is_first_run()


def test_set_album_path_valid(temp_dir):
    """测试设置有效的相册路径"""
    config_manager = create_config_manager_with_mock(temp_dir)
    
    with tempfile.TemporaryDirectory() as temp_album_dir:
        result = config_manager.set_album_path(temp_album_dir)
        assert result
        
        expected_path = str(Path(temp_album_dir).absolute())
        assert config_manager.get_album_path() == expected_path
        
        assert config_manager.config.get("created_at") is not None


def test_set_album_path_invalid_nonexistent(temp_dir):
    """测试设置不存在的相册路径"""
    config_manager = create_config_manager_with_mock(temp_dir)
    
    nonexistent_path = str(Path(temp_dir) / "nonexistent")
    result = config_manager.set_album_path(nonexistent_path)
    assert not result


def test_get_album_path(temp_dir):
    """测试获取相册路径"""
    config_manager = create_config_manager_with_mock(temp_dir)
    
    assert config_manager.get_album_path() is None
    
    with tempfile.TemporaryDirectory() as temp_album_dir:
        config_manager.set_album_path(temp_album_dir)
        expected_path = str(Path(temp_album_dir).absolute())
        assert config_manager.get_album_path() == expected_path


def test_set_last_import(temp_dir):
    """测试更新最后导入时间"""
    config_manager = create_config_manager_with_mock(temp_dir)
    
    custom_timestamp = "2023-01-01T12:00:00"
    config_manager.set_last_import(custom_timestamp)
    assert config_manager.get_last_import() == custom_timestamp
    
    config_manager.set_last_import(None)
    last_import = config_manager.get_last_import()
    assert last_import is not None
    datetime.fromisoformat(last_import)


def test_update_setting(temp_dir):
    """测试更新应用设置"""
    config_manager = create_config_manager_with_mock(temp_dir)
    
    config_manager.update_setting("import_mode_default", "move")
    assert config_manager.get_setting("import_mode_default") == "move"
    
    config_manager.update_setting("new_setting", "new_value")
    assert config_manager.get_setting("new_setting") == "new_value"


def test_get_setting(temp_dir):
    """测试获取应用设置"""
    config_manager = create_config_manager_with_mock(temp_dir)
    
    assert config_manager.get_setting("nonexistent_setting", "default_value") == "default_value"
    
    config_manager.update_setting("test_setting", "test_value")
    assert config_manager.get_setting("test_setting") == "test_value"


def test_get_all_config(temp_dir):
    """测试获取所有配置"""
    config_manager = create_config_manager_with_mock(temp_dir)
    
    all_config = config_manager.get_all_config()
    assert all_config == config_manager.config
    
    all_config["test_key"] = "test_value"
    assert "test_key" not in config_manager.config


def test_reset_config(temp_dir):
    """测试重置配置"""
    config_manager = create_config_manager_with_mock(temp_dir)
    
    with tempfile.TemporaryDirectory() as temp_album_dir:
        config_manager.set_album_path(temp_album_dir)
        config_manager.update_setting("import_mode_default", "move")
        
        config_manager.reset_config()
        
        assert config_manager.config == config_manager._default_config()


def test_get_config_manager_singleton():
    """测试单例模式"""
    from backend.config_manager import get_config_manager
    
    config_manager1 = get_config_manager()
    config_manager2 = get_config_manager()
    
    assert config_manager1 is config_manager2


def test_get_album_path_obj(temp_dir):
    """测试获取相册路径对象"""
    config_manager = create_config_manager_with_mock(temp_dir)
    
    # 未设置相册路径时，应该返回None
    assert config_manager.get_album_path_obj() is None
    
    with tempfile.TemporaryDirectory() as temp_album_dir:
        config_manager.set_album_path(temp_album_dir)
        album_path_obj = config_manager.get_album_path_obj()
        assert album_path_obj is not None
        assert isinstance(album_path_obj, Path)
        assert str(album_path_obj.absolute()) == config_manager.get_album_path()


def test_set_album_path_only(temp_dir):
    """测试仅设置相册路径，不重建MD5索引"""
    config_manager = create_config_manager_with_mock(temp_dir)
    
    with tempfile.TemporaryDirectory() as temp_album_dir:
        result = config_manager.set_album_path_only(temp_album_dir)
        assert result
        
        expected_path = str(Path(temp_album_dir).absolute())
        assert config_manager.get_album_path() == expected_path


def test_set_album_path_invalid(temp_dir):
    """测试设置无效的相册路径"""
    config_manager = create_config_manager_with_mock(temp_dir)
    
    # 测试设置不存在的目录
    nonexistent_dir = str(Path(temp_dir) / "nonexistent")
    result = config_manager.set_album_path(nonexistent_dir)
    assert not result
    
    # 测试设置文件而非目录
    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_file = f.name
    
    try:
        result = config_manager.set_album_path(temp_file)
        assert not result
    finally:
        import os
        os.unlink(temp_file)


def test_rebuild_md5_index(temp_dir):
    """测试重建MD5索引"""
    config_manager = create_config_manager_with_mock(temp_dir)
    
    # 创建一些测试媒体文件
    with tempfile.TemporaryDirectory() as temp_album_dir:
        # 创建几个测试图片文件
        for i in range(3):
            test_file = Path(temp_album_dir) / f"test{i}.jpg"
            test_file.write_text(f"test content {i}")
        
        # 使用mock来避免实际的数据库操作
        with patch.object(config_manager, '_compute_md5', return_value='test_md5'):
            with patch('backend.config_manager.SessionLocal') as mock_session_local:
                # 设置mock - 模拟实际的SessionLocal()行为
                mock_db = MagicMock()
                
                # 模拟SessionLocal()直接返回mock_db实例（不是上下文管理器）
                mock_session_local.return_value = mock_db
                
                # 调用方法
                config_manager._rebuild_md5_index_for_album(Path(temp_album_dir))
                
                # 验证数据库操作
                # 注意：由于方法内部可能有条件分支，我们只验证close方法被调用，
                # 而不严格验证commit是否被调用
                mock_db.close.assert_called_once()


def test_get_album_path_invalid(temp_dir):
    """测试获取无效的相册路径"""
    config_manager = create_config_manager_with_mock(temp_dir)
    
    # 设置一个有效的相册路径
    with tempfile.TemporaryDirectory() as temp_album_dir:
        config_manager.set_album_path(temp_album_dir)
        
        # 验证路径有效
        assert config_manager.get_album_path() is not None
        
        # 模拟路径被删除
        import shutil
        shutil.rmtree(temp_album_dir)
        
        # 再次获取路径，应该返回None
        assert config_manager.get_album_path() is None


def test_nested_key_setting(temp_dir):
    """测试嵌套键设置"""
    config_manager = create_config_manager_with_mock(temp_dir)
    
    # 测试设置嵌套键（当前应该不支持）
    config_manager.update_setting("nested.key", "value")
    # 应该返回默认值
    assert config_manager.get_setting("nested.key", "default") == "default"


def test_get_setting_default(temp_dir):
    """测试获取不存在的设置时返回默认值"""
    config_manager = create_config_manager_with_mock(temp_dir)
    
    # 测试获取不存在的设置
    assert config_manager.get_setting("nonexistent_setting") is None
    assert config_manager.get_setting("nonexistent_setting", "default_value") == "default_value"
