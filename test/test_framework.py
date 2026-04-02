"""
简单的测试框架验证
"""


def test_pytest_works():
    """验证pytest是否正常工作"""
    assert 1 + 1 == 2


def test_temp_dir_fixture(temp_dir):
    """验证temp_dir fixture"""
    assert temp_dir.exists()
    assert temp_dir.is_dir()


def test_import_backend():
    """验证可以导入backend模块"""
    from backend import constants
    assert hasattr(constants, 'MEDIA_FORMATS')
