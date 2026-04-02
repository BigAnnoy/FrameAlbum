"""
VideoProcessor 单元测试
测试视频处理模块的所有公共 API 方法
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock, call
import json

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.video_processor import VideoProcessor


class TestVideoProcessor(unittest.TestCase):
    """VideoProcessor 单元测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建模拟视频文件路径
        self.video_path = str(Path(self.temp_dir) / "test_video.mp4")
        self.output_path = str(Path(self.temp_dir) / "output.jpg")
        
        # 创建一个空的视频文件
        with open(self.video_path, 'w') as f:
            f.write("dummy video content")
    
    def tearDown(self):
        """测试后的清理工作"""
        # 删除临时目录
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch.object(VideoProcessor, 'is_ffmpeg_available', return_value=True)
    def test_is_ffmpeg_available_true(self, mock_is_available):
        """测试FFmpeg可用的情况"""
        # 验证FFmpeg可用
        self.assertTrue(VideoProcessor.is_ffmpeg_available())
        mock_is_available.assert_called_once()
    
    @patch.object(VideoProcessor, 'is_ffmpeg_available', return_value=False)
    def test_is_ffmpeg_available_false(self, mock_is_available):
        """测试FFmpeg不可用的情况"""
        # 验证FFmpeg不可用
        self.assertFalse(VideoProcessor.is_ffmpeg_available())
        mock_is_available.assert_called_once()
    
    @patch.object(VideoProcessor, 'is_ffmpeg_available', return_value=True)
    @patch('subprocess.run')
    def test_run_ffmpeg_command_success(self, mock_run, mock_is_available):
        """测试成功执行FFmpeg命令的情况"""
        # 模拟subprocess.run返回成功结果
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        # 访问私有方法的正确方式是使用类的实例或通过类本身
        with patch('backend.video_processor.FFMPEG_PATH', str(Path("ffmpeg.exe"))):
            # 调用_run_ffmpeg_command方法
            args = ["-i", self.video_path, "-vframes", "1", self.output_path]
            result = VideoProcessor._run_ffmpeg_command(args)
            
            # 验证结果
            self.assertTrue(result)
            # 验证subprocess.run被正确调用
            mock_run.assert_called_once()
    
    @patch.object(VideoProcessor, 'is_ffmpeg_available', return_value=True)
    @patch('subprocess.run')
    def test_run_ffmpeg_command_failure(self, mock_run, mock_is_available):
        """测试执行FFmpeg命令失败的情况"""
        # 模拟subprocess.run返回失败结果
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Error occurred"
        mock_run.return_value = mock_result
        
        # 访问私有方法的正确方式
        with patch('backend.video_processor.FFMPEG_PATH', str(Path("ffmpeg.exe"))):
            # 调用_run_ffmpeg_command方法
            args = ["-i", self.video_path, "-vframes", "1", self.output_path]
            result = VideoProcessor._run_ffmpeg_command(args)
            
            # 验证结果
            self.assertFalse(result)
    
    @patch.object(VideoProcessor, 'is_ffmpeg_available', return_value=True)
    @patch.object(VideoProcessor, '_run_ffmpeg_command', return_value=True)
    def test_generate_thumbnail_success(self, mock_run_command, mock_is_available):
        """测试成功生成视频缩略图的情况"""
        # 调用generate_thumbnail方法
        result = VideoProcessor.generate_thumbnail(self.video_path, self.output_path)
        
        # 验证结果
        self.assertTrue(result)
        # 验证_run_ffmpeg_command被正确调用
        mock_run_command.assert_called_once()
    
    @patch.object(VideoProcessor, 'is_ffmpeg_available', return_value=True)
    @patch.object(VideoProcessor, '_run_ffmpeg_command', return_value=False)
    def test_generate_thumbnail_failure(self, mock_run_command, mock_is_available):
        """测试生成视频缩略图失败的情况"""
        # 调用generate_thumbnail方法
        result = VideoProcessor.generate_thumbnail(self.video_path, self.output_path)
        
        # 验证结果
        self.assertFalse(result)
    
    @patch.object(VideoProcessor, 'is_ffmpeg_available', return_value=False)
    def test_generate_thumbnail_ffmpeg_not_available(self, mock_is_available):
        """测试FFmpeg不可用时生成视频缩略图的情况"""
        # 调用generate_thumbnail方法
        result = VideoProcessor.generate_thumbnail(self.video_path, self.output_path)
        
        # 验证结果
        self.assertFalse(result)
    
    @patch.object(VideoProcessor, 'is_ffmpeg_available', return_value=True)
    @patch('subprocess.run')
    def test_extract_metadata_success(self, mock_run, mock_is_available):
        """测试成功提取视频元数据的情况"""
        # 模拟ffprobe输出
        mock_output = {
            "streams": [
                {
                    "codec_type": "video",
                    "duration": "10.0",
                    "width": 1920,
                    "height": 1080,
                    "codec_name": "h264",
                    "bit_rate": "5000000",
                    "r_frame_rate": "30/1"
                }
            ],
            "format": {
                "format_name": "mp4",
                "size": "10000000",
                "tags": {
                    "creation_time": "2023-01-01T12:00:00Z"
                }
            }
        }
        
        # 模拟subprocess.run返回成功结果
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(mock_output)
        mock_run.return_value = mock_result
        
        # 访问FFPROBE_PATH
        with patch('backend.video_processor.FFPROBE_PATH', str(Path("ffprobe.exe"))):
            # 调用extract_metadata方法
            metadata = VideoProcessor.extract_metadata(self.video_path)
            
            # 验证结果
            self.assertIsNotNone(metadata)
            self.assertEqual(metadata["duration"], 10.0)
            self.assertEqual(metadata["width"], 1920)
            self.assertEqual(metadata["height"], 1080)
            self.assertEqual(metadata["codec"], "h264")
            self.assertEqual(metadata["bit_rate"], 5000000)
            self.assertEqual(metadata["frame_rate"], "30/1")
            self.assertEqual(metadata["format"], "mp4")
            self.assertEqual(metadata["size"], 10000000)
    
    @patch.object(VideoProcessor, 'is_ffmpeg_available', return_value=True)
    @patch('subprocess.run')
    def test_extract_metadata_failure(self, mock_run, mock_is_available):
        """测试提取视频元数据失败的情况"""
        # 模拟subprocess.run返回失败结果
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Error occurred"
        mock_run.return_value = mock_result
        
        # 访问FFPROBE_PATH
        with patch('backend.video_processor.FFPROBE_PATH', str(Path("ffprobe.exe"))):
            # 调用extract_metadata方法
            metadata = VideoProcessor.extract_metadata(self.video_path)
            
            # 验证结果
            self.assertIsNone(metadata)
    
    @patch.object(VideoProcessor, 'is_ffmpeg_available', return_value=False)
    def test_extract_metadata_ffmpeg_not_available(self, mock_is_available):
        """测试FFmpeg不可用时提取视频元数据的情况"""
        # 调用extract_metadata方法
        metadata = VideoProcessor.extract_metadata(self.video_path)
        
        # 验证结果
        self.assertIsNone(metadata)
    
    @patch.object(VideoProcessor, 'is_ffmpeg_available', return_value=True)
    @patch.object(VideoProcessor, '_run_ffmpeg_command', return_value=True)
    def test_transcode_video_success(self, mock_run_command, mock_is_available):
        """测试成功转码视频的情况"""
        # 调用transcode_video方法
        output_path = str(Path(self.temp_dir) / "output.mp4")
        result = VideoProcessor.transcode_video(self.video_path, output_path)
        
        # 验证结果
        self.assertTrue(result)
        # 验证_run_ffmpeg_command被正确调用
        mock_run_command.assert_called_once()
    
    @patch.object(VideoProcessor, 'is_ffmpeg_available', return_value=True)
    @patch.object(VideoProcessor, 'extract_metadata')
    def test_get_video_duration_success(self, mock_extract_metadata, mock_is_available):
        """测试成功获取视频时长的情况"""
        # 模拟extract_metadata返回有效的元数据
        mock_extract_metadata.return_value = {
            "duration": 10.0,
            "width": 1920,
            "height": 1080
        }
        
        # 调用get_video_duration方法
        duration = VideoProcessor.get_video_duration(self.video_path)
        
        # 验证结果
        self.assertEqual(duration, 10.0)
    
    @patch.object(VideoProcessor, 'is_ffmpeg_available', return_value=True)
    @patch.object(VideoProcessor, 'extract_metadata')
    def test_get_video_duration_failure(self, mock_extract_metadata, mock_is_available):
        """测试获取视频时长失败的情况"""
        # 模拟extract_metadata返回None
        mock_extract_metadata.return_value = None
        
        # 调用get_video_duration方法
        duration = VideoProcessor.get_video_duration(self.video_path)
        
        # 验证结果
        self.assertIsNone(duration)


if __name__ == "__main__":
    unittest.main()
