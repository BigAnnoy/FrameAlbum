"""
导入 API 功能测试 (pytest版本)
测试 api_server.py 中的导入相关 API 端点
"""

import json
from unittest.mock import patch, MagicMock
from pathlib import Path

import pytest


class TestAPIImport:
    """测试导入相关 API 端点"""
    
    @patch('backend.api_server.get_import_manager')
    def test_start_import_valid(self, mock_get_import_manager, client):
        """测试有效的导入请求"""
        # 模拟导入管理器
        mock_import_manager = MagicMock()
        mock_get_import_manager.return_value = mock_import_manager
        
        # 测试有效的导入请求
        with patch('backend.api_server.Path.exists') as mock_exists:
            with patch('backend.api_server.Path.is_dir') as mock_is_dir:
                mock_exists.return_value = True
                mock_is_dir.return_value = True
                
                response = client.post(
                    '/api/import/start',
                    data=json.dumps({
                        'source_path': '/source/path',
                        'target_path': '/target/path',
                        'import_mode': 'copy',
                        'skip_source_duplicates': False,
                        'skip_target_duplicates': False
                    }),
                    content_type='application/json'
                )
                
                assert response.status_code == 200
                
                data = json.loads(response.data)
                assert 'status' in data
                assert data['status'] == 'started'
                assert 'import_id' in data
                
                # 验证调用
                mock_import_manager.create_import.assert_called_once()
                mock_import_manager.start_import_async.assert_called_once()
    
    def test_start_import_invalid_mode(self, client):
        """测试无效的导入模式"""
        with patch('backend.api_server.Path.exists') as mock_exists:
            with patch('backend.api_server.Path.is_dir') as mock_is_dir:
                mock_exists.return_value = True
                mock_is_dir.return_value = True
                
                response = client.post(
                    '/api/import/start',
                    data=json.dumps({
                        'source_path': '/source/path',
                        'target_path': '/target/path',
                        'import_mode': 'invalid_mode'
                    }),
                    content_type='application/json'
                )
                
                assert response.status_code == 200
                
                # 无效模式应该回退到 'copy'
                data = json.loads(response.data)
                assert data['status'] == 'started'
    
    @patch('backend.api_server.get_import_manager')
    def test_import_progress(self, mock_get_import_manager, client):
        """测试获取导入进度"""
        # 模拟导入管理器返回进度
        mock_import_manager = MagicMock()
        mock_progress = {
            'status': 'processing',
            'progress': 50,
            'total_files': 100,
            'processed_files': 50
        }
        mock_import_manager.get_progress_dict.return_value = mock_progress
        mock_get_import_manager.return_value = mock_import_manager
        
        response = client.get('/api/import/progress/import_123')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data == mock_progress
        
        # 测试不存在的导入任务
        mock_import_manager.get_progress_dict.return_value = None
        
        response = client.get('/api/import/progress/non_existent')
        
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'error' in data
    
    @patch('backend.api_server.get_import_manager')
    def test_cancel_import(self, mock_get_import_manager, client):
        """测试取消导入"""
        # 模拟导入管理器
        mock_import_manager = MagicMock()
        mock_progress = MagicMock()
        mock_import_manager.get_progress.return_value = mock_progress
        mock_get_import_manager.return_value = mock_import_manager
        
        response = client.post('/api/import/cancel/import_123')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'cancelled'
        
        # 验证调用
        mock_import_manager.cancel_import.assert_called_once_with('import_123')
        
        # 测试不存在的导入任务
        mock_import_manager.get_progress.return_value = None
        
        response = client.post('/api/import/cancel/non_existent')
        
        assert response.status_code == 404
    
    @patch('backend.api_server.get_import_manager')
    def test_pause_import(self, mock_get_import_manager, client):
        """测试暂停导入"""
        # 模拟导入管理器
        mock_import_manager = MagicMock()
        mock_progress = MagicMock()
        mock_import_manager.get_progress.return_value = mock_progress
        mock_get_import_manager.return_value = mock_import_manager
        
        response = client.post('/api/import/pause/import_123')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'paused'
        
        # 验证调用
        mock_import_manager.pause_import.assert_called_once_with('import_123')
    
    @patch('backend.api_server.get_import_manager')
    def test_resume_import(self, mock_get_import_manager, client):
        """测试继续导入"""
        # 模拟导入管理器
        mock_import_manager = MagicMock()
        mock_progress = MagicMock()
        mock_import_manager.get_progress.return_value = mock_progress
        mock_get_import_manager.return_value = mock_import_manager
        
        response = client.post('/api/import/resume/import_123')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'processing'
        
        # 验证调用
        mock_import_manager.resume_import.assert_called_once_with('import_123')
    
    @patch('backend.api_server._perform_import_check')
    def test_check_import_path(self, mock_perform_import_check, client):
        """测试检查导入路径"""
        # 模拟检查结果
        mock_result = {
            'status': 'valid',
            'source_path': '/source/path',
            'media_count': 10,
            'total_size': 1024 * 1024 * 100,
            'total_size_mb': 100.0
        }
        mock_perform_import_check.return_value = mock_result
        
        # 测试有效的源路径
        with patch('backend.api_server.Path.exists') as mock_exists:
            with patch('backend.api_server.Path.is_dir') as mock_is_dir:
                mock_exists.return_value = True
                mock_is_dir.return_value = True
                
                response = client.post(
                    '/api/import/check',
                    data=json.dumps({'source_path': '/source/path'}),
                    content_type='application/json'
                )
                
                assert response.status_code == 200
                
                data = json.loads(response.data)
                assert data == mock_result
        
        # 测试无效的源路径（不存在）
        with patch('backend.api_server.Path.exists') as mock_exists:
            mock_exists.return_value = False
            
            response = client.post(
                '/api/import/check',
                data=json.dumps({'source_path': '/invalid/path'}),
                content_type='application/json'
            )
            
            assert response.status_code == 404
    
    def test_check_import_path_missing_param(self, client):
        """测试缺少源路径参数的导入检查请求"""
        response = client.post(
            '/api/import/check',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert '缺少 source_path 参数' in data['error']
    
    @patch('backend.api_server._import_check_tasks')
    @patch('backend.api_server._import_check_lock')
    def test_get_import_check_progress(self, mock_import_check_lock, mock_import_check_tasks, client):
        """测试获取导入检查进度"""
        # 模拟任务存在
        task_id = 'check_123'
        mock_task = {
            'check_id': task_id,
            'status': 'running',
            'progress': 50,
            'stage': 'scanning',
            'detail': '扫描中...',
            'error': None
        }
        
        # 模拟锁和任务字典
        mock_lock = MagicMock()
        mock_import_check_lock.__enter__.return_value = mock_lock
        mock_import_check_tasks.get.return_value = mock_task
        
        response = client.get(f'/api/import/check/progress/{task_id}')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['check_id'] == task_id
        assert data['status'] == 'running'
        assert data['progress'] == 50
        
        # 测试任务不存在
        mock_import_check_tasks.get.return_value = None
        
        response = client.get('/api/import/check/progress/non_existent')
        
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'error' in data
    
    @patch('backend.api_server.get_config_manager')
    def test_delete_files_valid(self, mock_get_config_manager, client):
        """测试有效的文件删除请求"""
        # 模拟配置管理器
        mock_config_manager = MagicMock()
        mock_config_manager.get_album_path.return_value = '/album/path'
        mock_get_config_manager.return_value = mock_config_manager
        
        # 模拟文件存在且在允许的目录内
        with patch('backend.api_server.Path.exists') as mock_exists:
            with patch('backend.api_server.Path.is_file') as mock_is_file:
                with patch('backend.api_server.Path.is_dir') as mock_is_dir:
                    mock_exists.return_value = True
                    mock_is_file.return_value = True
                    mock_is_dir.return_value = False
                    
                    # 模拟 Path.unlink
                    with patch('backend.api_server.Path.unlink') as mock_unlink:
                        mock_unlink.return_value = None
                        
                        response = client.post(
                            '/api/files/delete',
                            data=json.dumps({'paths': ['/album/path/file.jpg']}),
                            content_type='application/json'
                        )
                        
                        assert response.status_code == 200
                        
                        data = json.loads(response.data)
                        assert data['status'] == 'completed'
                        assert data['deleted_count'] == 1
                        assert data['failed_count'] == 0
    
    def test_delete_files_missing_param(self, client):
        """测试缺少 paths 参数的删除请求"""
        response = client.post(
            '/api/files/delete',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert '请提供要删除的文件路径列表' in data['error']
    
    def test_delete_files_empty_list(self, client):
        """测试空文件列表的删除请求"""
        response = client.post(
            '/api/files/delete',
            data=json.dumps({'paths': []}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert '没有要删除的文件' in data['error']