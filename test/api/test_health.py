"""
健康检查API测试用例
"""


def test_health_check(client):
    """测试健康检查API"""
    response = client.get('/api/health')
    
    # 验证状态码
    assert response.status_code == 200
    
    # 验证响应内容
    data = response.get_json()
    assert data is not None
    
    # 验证status字段
    assert 'status' in data
    assert data['status'] == 'ok'
    
    # 验证timestamp字段
    assert 'timestamp' in data
    # 验证timestamp格式（ISO格式）
    from datetime import datetime
    try:
        datetime.fromisoformat(data['timestamp'])
        is_valid_format = True
    except ValueError:
        is_valid_format = False
    assert is_valid_format


def test_health_check_method(client):
    """测试健康检查API只支持GET方法"""
    # 测试POST方法
    response = client.post('/api/health')
    assert response.status_code == 405  # 方法不允许
    
    # 测试PUT方法
    response = client.put('/api/health')
    assert response.status_code == 405  # 方法不允许
    
    # 测试DELETE方法
    response = client.delete('/api/health')
    assert response.status_code == 405  # 方法不允许