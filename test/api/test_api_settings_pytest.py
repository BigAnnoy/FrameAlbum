"""
设置 API 功能测试 (pytest版本)
测试与设置相关的 API 端点
"""

import json
import tempfile
from unittest.mock import patch, MagicMock

import pytest


@patch('backend.api_server.get_config_manager')
def test_get_language_api(mock_get_config_manager, client):
    """测试获取语言偏好 API"""
    # 测试返回中文
    mock_config = MagicMock()
    mock_config.get_setting.return_value = 'zh'
    mock_get_config_manager.return_value = mock_config
    
    response = client.get('/api/settings/language')
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'language' in data
    assert data['language'] == 'zh'
    mock_config.get_setting.assert_called_once_with('language', None)
    
    # 测试返回英文
    mock_config.get_setting.return_value = 'en'
    response = client.get('/api/settings/language')
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['language'] == 'en'
    
    # 测试返回 None
    mock_config.get_setting.return_value = None
    response = client.get('/api/settings/language')
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['language'] is None


@patch('backend.api_server.get_config_manager')
def test_set_language_api_valid(mock_get_config_manager, client):
    """测试设置语言偏好 API（有效语言）"""
    mock_config = MagicMock()
    mock_get_config_manager.return_value = mock_config
    
    # 测试设置中文
    response = client.put(
        '/api/settings/language',
        data=json.dumps({'language': 'zh'}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'status' in data
    assert 'language' in data
    assert data['status'] == 'ok'
    assert data['language'] == 'zh'
    mock_config.update_setting.assert_called_once_with('language', 'zh')
    
    # 测试设置英文
    mock_config.reset_mock()
    response = client.put(
        '/api/settings/language',
        data=json.dumps({'language': 'en'}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'ok'
    assert data['language'] == 'en'
    mock_config.update_setting.assert_called_once_with('language', 'en')


@patch('backend.api_server.get_config_manager')
def test_set_language_api_invalid(mock_get_config_manager, client):
    """测试设置语言偏好 API（无效语言）"""
    mock_config = MagicMock()
    mock_get_config_manager.return_value = mock_config
    
    # 测试无效语言代码
    response = client.put(
        '/api/settings/language',
        data=json.dumps({'language': 'invalid_lang'}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    
    data = json.loads(response.data)
    assert 'error' in data
    assert '不支持的语言代码' in data['error']
    
    # 测试没有提供语言
    response = client.put(
        '/api/settings/language',
        data=json.dumps({}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'ok'
    assert data['language'] == 'zh'  # 默认值
    mock_config.update_setting.assert_called_once_with('language', 'zh')


def test_test_api(client):
    """测试测试 API 端点"""
    response = client.get('/api/test')
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'API 工作正常'
    assert 'timestamp' in data
