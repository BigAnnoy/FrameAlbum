"""
相册相关API测试用例
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch


@patch('backend.api_server.get_album_path')
def test_album_stats(mock_get_album_path, client):
    """测试获取相册统计信息"""
    # 模拟相册路径
    mock_get_album_path.return_value = "/fake/album/path"
    
    response = client.get('/api/album/stats')
    
    # 验证状态码 - 当相册路径不存在时返回500
    assert response.status_code == 500


@patch('backend.api_server.get_album_path')
def test_album_tree(mock_get_album_path, client):
    """测试获取相册目录树"""
    # 模拟相册路径
    mock_get_album_path.return_value = "/fake/album/path"
    
    response = client.get('/api/album/tree')
    
    # 验证状态码 - 当相册路径不存在时返回404
    assert response.status_code == 404


@patch('backend.api_server.get_album_path')
def test_album_photos(mock_get_album_path, client):
    """测试获取指定路径下的照片列表"""
    # 创建临时目录和测试文件
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试图片文件
        test_files = [
            "test1.jpg",
            "test2.png", 
            "test3.mp4"
        ]
        
        for file_name in test_files:
            file_path = Path(temp_dir) / file_name
            file_path.write_text("test content")
        
        # 模拟相册路径
        mock_get_album_path.return_value = temp_dir
        
        # 调用API
        response = client.get(f'/api/album/photos?path={temp_dir}')
        
        # 验证状态码
        assert response.status_code == 200
        
        # 验证响应内容 - 返回的是字典，不是列表
        data = response.get_json()
        assert data is not None
        assert isinstance(data, dict)
        
        # 验证返回的字段
        assert 'photos' in data
        assert isinstance(data['photos'], list)
        
        assert 'count' in data
        assert isinstance(data['count'], int)
        
        assert 'path' in data
        assert isinstance(data['path'], str)
        
        # 验证返回的照片数量
        assert len(data['photos']) == len(test_files)
        
        # 验证照片字段
        if data['photos']:
            photo = data['photos'][0]
            assert 'name' in photo
            assert 'path' in photo
            assert 'size' in photo
            assert 'type' in photo
            assert 'url' in photo
            assert 'thumbnail_url' in photo
            assert 'preview_url' in photo
            assert 'modified' in photo
            assert 'size_mb' in photo


@patch('backend.api_server.get_album_path')
def test_album_photos_nonexistent_path(mock_get_album_path, client):
    """测试获取不存在路径下的照片列表"""
    # 模拟相册路径
    mock_get_album_path.return_value = "/non/existent/path"
    
    # 调用API
    response = client.get('/api/album/photos?path=/non/existent/path')
    
    # 验证状态码
    assert response.status_code == 404
    
    # 验证响应内容
    data = response.get_json()
    assert data is not None
    assert 'error' in data


@patch('backend.api_server.get_album_path')
def test_album_photos_no_path_param(mock_get_album_path, client):
    """测试获取照片列表时不提供path参数"""
    # 模拟相册路径
    mock_get_album_path.return_value = "/test/album/path"
    
    # 调用API，不提供path参数
    response = client.get('/api/album/photos')
    
    # 验证状态码
    assert response.status_code == 400
    
    # 验证响应内容
    data = response.get_json()
    assert data is not None
    assert 'error' in data
    assert '缺少 path 参数' in data['error']