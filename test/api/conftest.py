"""
API集成测试配置文件
提供Flask应用和测试客户端fixture
"""

import pytest
from backend.api_server import app as flask_app


@pytest.fixture
def app():
    """Flask应用fixture"""
    flask_app.config['TESTING'] = True
    yield flask_app


@pytest.fixture
def client(app):
    """测试客户端fixture"""
    return app.test_client()