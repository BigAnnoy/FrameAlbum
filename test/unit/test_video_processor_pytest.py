"""
VideoProcessor 单元测试 (pytest版本)
测试视频处理模块的所有公共 API 方法
"""

import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, call

import pytest

from backend.video_processor import VideoProcessor


@pytest.fixture
def temp_dir():
    """创建临时目录fixture"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def video_paths(temp_dir):
    """创建测试视频文件路径fixture"""
    video_path = str(temp_dir / "test_video.mp4")
    output_path = str(temp_dir / "output.jpg")
    
    with open(video_path, 'w') as f:
        f.write("dummy video content")
    
    return video_path, output_path


def test_is_ffmpeg_available_true():
    """测试FFmpeg可用的情况"""
    with patch.object(VideoProcessor, 'is_ffmpeg_available', return_value=True):
        assert VideoProcessor.is_ffmpeg_available() is True


def test_is_ffmpeg_available_false():
    """测试FFmpeg不可用的情况"""
    with patch.object(VideoProcessor, 'is_ffmpeg_available', return_value=False):
        assert VideoProcessor.is_ffmpeg_available() is False


@patch.object(VideoProcessor, 'is_ffmpeg_available', return_value=True)
@patch('subprocess.run')
def test_run_ffmpeg_command_success(mock_run, mock_is_available, video_paths):
    """测试成功执行FFmpeg命令的情况"""
    video_path, output_path = video_paths
    
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_run.return_value = mock_result
    
    with patch('backend.video_processor.FFMPEG_PATH', str(Path("ffmpeg.exe"))):
        args = ["-i", video_path, "-vframes", "1", output_path]
        result = VideoProcessor._run_ffmpeg_command(args)
        
        assert result is True
        mock_run.assert_called_once()


@patch.object(VideoProcessor, 'is_ffmpeg_available', return_value=True)
@patch('subprocess.run')
def test_run_ffmpeg_command_failure(mock_run, mock_is_available, video_paths):
    """测试执行FFmpeg命令失败的情况"""
    video_path, output_path = video_paths
    
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stderr = "Error occurred"
    mock_run.return_value = mock_result
    
    with patch('backend.video_processor.FFMPEG_PATH', str(Path("ffmpeg.exe"))):
        args = ["-i", video_path, "-vframes", "1", output_path]
        result = VideoProcessor._run_ffmpeg_command(args)
        
        assert result is False


@patch.object(VideoProcessor, 'is_ffmpeg_available', return_value=True)
@patch.object(VideoProcessor, '_run_ffmpeg_command', return_value=True)
def test_generate_thumbnail_success(mock_run_command, mock_is_available, video_paths):
    """测试成功生成视频缩略图的情况"""
    video_path, output_path = video_paths
    
    result = VideoProcessor.generate_thumbnail(video_path, output_path)
    
    assert result is True
    mock_run_command.assert_called_once()


@patch.object(VideoProcessor, 'is_ffmpeg_available', return_value=True)
@patch.object(VideoProcessor, '_run_ffmpeg_command', return_value=False)
def test_generate_thumbnail_failure(mock_run_command, mock_is_available, video_paths):
    """测试生成视频缩略图失败的情况"""
    video_path, output_path = video_paths
    
    result = VideoProcessor.generate_thumbnail(video_path, output_path)
    
    assert result is False


@patch.object(VideoProcessor, 'is_ffmpeg_available', return_value=False)
def test_generate_thumbnail_ffmpeg_not_available(mock_is_available, video_paths):
    """测试FFmpeg不可用时生成视频缩略图的情况"""
    video_path, output_path = video_paths
    
    result = VideoProcessor.generate_thumbnail(video_path, output_path)
    
    assert result is False


@patch.object(VideoProcessor, 'is_ffmpeg_available', return_value=True)
@patch('subprocess.run')
def test_extract_metadata_success(mock_run, mock_is_available, video_paths):
    """测试成功提取视频元数据的情况"""
    video_path, _ = video_paths
    
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
    
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = json.dumps(mock_output)
    mock_run.return_value = mock_result
    
    with patch('backend.video_processor.FFPROBE_PATH', str(Path("ffprobe.exe"))):
        metadata = VideoProcessor.extract_metadata(video_path)
        
        assert metadata is not None
        assert metadata["duration"] == 10.0
        assert metadata["width"] == 1920
        assert metadata["height"] == 1080
        assert metadata["codec"] == "h264"
        assert metadata["bit_rate"] == 5000000
        assert metadata["frame_rate"] == "30/1"
        assert metadata["format"] == "mp4"
        assert metadata["size"] == 10000000


@patch.object(VideoProcessor, 'is_ffmpeg_available', return_value=True)
@patch('subprocess.run')
def test_extract_metadata_failure(mock_run, mock_is_available, video_paths):
    """测试提取视频元数据失败的情况"""
    video_path, _ = video_paths
    
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stderr = "Error occurred"
    mock_run.return_value = mock_result
    
    with patch('backend.video_processor.FFPROBE_PATH', str(Path("ffprobe.exe"))):
        metadata = VideoProcessor.extract_metadata(video_path)
        
        assert metadata is None


@patch.object(VideoProcessor, 'is_ffmpeg_available', return_value=False)
def test_extract_metadata_ffmpeg_not_available(mock_is_available, video_paths):
    """测试FFmpeg不可用时提取视频元数据的情况"""
    video_path, _ = video_paths
    
    metadata = VideoProcessor.extract_metadata(video_path)
    
    assert metadata is None


@patch.object(VideoProcessor, 'is_ffmpeg_available', return_value=True)
@patch.object(VideoProcessor, '_run_ffmpeg_command', return_value=True)
def test_transcode_video_success(mock_run_command, mock_is_available, video_paths, temp_dir):
    """测试成功转码视频的情况"""
    video_path, _ = video_paths
    output_path = str(temp_dir / "output.mp4")
    
    result = VideoProcessor.transcode_video(video_path, output_path)
    
    assert result is True
    mock_run_command.assert_called_once()


@patch.object(VideoProcessor, 'is_ffmpeg_available', return_value=True)
@patch.object(VideoProcessor, 'extract_metadata')
def test_get_video_duration_success(mock_extract_metadata, mock_is_available, video_paths):
    """测试成功获取视频时长的情况"""
    video_path, _ = video_paths
    
    mock_extract_metadata.return_value = {
        "duration": 10.0,
        "width": 1920,
        "height": 1080
    }
    
    duration = VideoProcessor.get_video_duration(video_path)
    
    assert duration == 10.0


@patch.object(VideoProcessor, 'is_ffmpeg_available', return_value=True)
@patch.object(VideoProcessor, 'extract_metadata')
def test_get_video_duration_failure(mock_extract_metadata, mock_is_available, video_paths):
    """测试获取视频时长失败的情况"""
    video_path, _ = video_paths
    
    mock_extract_metadata.return_value = None
    
    duration = VideoProcessor.get_video_duration(video_path)
    
    assert duration is None
