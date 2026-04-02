"""
设置相关API测试用例
"""

from unittest.mock import patch
import tempfile
from pathlib import Path


def test_get_album_path(client):
    """测试获取相册路径"""
    response = client.get('/api/settings/album-path')
    
    # 验证状态码
    assert response.status_code == 200
    
    # 验证响应内容
    data = response.get_json()
    assert data is not None
    
    # 验证返回的字段
    assert 'album_path' in data


@patch('backend.api_server.get_config_manager')
def test_put_album_path(mock_get_config_manager, client):
    """测试设置相册路径"""
    # 创建临时目录作为测试相册路径
    with tempfile.TemporaryDirectory() as temp_dir:
        # 模拟配置管理器
        mock_config = mock_get_config_manager.return_value
        mock_config.set_album_path.return_value = True
        
        # 调用API
        response = client.put('/api/settings/album-path', json={'album_path': temp_dir})
        
        # 验证状态码
        assert response.status_code == 200
        
        # 验证响应内容
        data = response.get_json()
        assert data is not None


@patch('backend.api_server.check_ffmpeg')
def test_ffmpeg_status(mock_check_ffmpeg, client):
    """测试获取FFmpeg状态"""
    # 模拟FFmpeg检查结果
    mock_check_ffmpeg.return_value = (True, 'system')
    
    # 调用API
    response = client.get('/api/settings/ffmpeg-status')
    
    # 验证状态码
    assert response.status_code == 200
    
    # 验证响应内容
    data = response.get_json()
    assert data is not None
    
    # 验证返回的字段
    assert 'status' in data
    assert data['status'] == 'available'
    
    assert 'path' in data
    assert data['path'] == 'system'


@patch('backend.api_server.check_ffmpeg')
def test_ffmpeg_status_not_available(mock_check_ffmpeg, client):
    """测试FFmpeg不可用的情况"""
    # 模拟FFmpeg检查结果
    mock_check_ffmpeg.return_value = (False, None)
    
    # 调用API
    response = client.get('/api/settings/ffmpeg-status')
    
    # 验证状态码
    assert response.status_code == 200
    
    # 验证响应内容
    data = response.get_json()
    assert data is not None
    
    # 验证返回的字段
    assert 'status' in data
    assert data['status'] == 'unavailable'
    
    assert 'path' in data
    assert data['path'] is None


def test_get_language(client):
    """测试获取语言设置"""
    response = client.get('/api/settings/language')
    
    # 验证状态码
    assert response.status_code == 200
    
    # 验证响应内容
    data = response.get_json()
    assert data is not None
    
    # 验证返回的字段
    assert 'language' in data
    # 允许language为None
    assert isinstance(data['language'], (str, type(None)))


def test_put_language(client):
    """测试设置语言"""
    # 调用API
    response = client.put('/api/settings/language', json={'language': 'en'})
    
    # 验证状态码
    assert response.status_code == 200
    
    # 验证响应内容
    data = response.get_json()
    assert data is not None
    
    # 验证返回的字段
    assert 'status' in data
    assert data['status'] == 'ok'
    
    assert 'language' in data
    assert data['language'] == 'en'