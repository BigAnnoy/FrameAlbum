#!/usr/bin/env python3
"""
FFmpeg集成测试脚本
验证视频处理器功能是否正常工作
使用本地集成的FFmpeg二进制文件
"""

import os
import sys
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from backend.video_processor import VideoProcessor
    logger.info("✅ 成功导入VideoProcessor模块")
except ImportError as e:
    logger.error(f"❌ 导入VideoProcessor模块失败: {e}")
    sys.exit(1)

def main():
    """测试FFmpeg集成功能"""
    logger.info("开始测试FFmpeg集成...")
    
    # 检查FFmpeg是否可用
    logger.info("检查FFmpeg是否可用...")
    if VideoProcessor.is_ffmpeg_available():
        logger.info("✅ FFmpeg已可用 (本地集成)")
    else:
        logger.warning("⚠️  FFmpeg不可用")
    
    # 测试视频处理器功能
    test_video_path = Path(__file__).parent.parent / "test_data" / "test_video.mp4"
    if test_video_path.exists():
        logger.info(f"测试视频文件: {test_video_path}")
        
        # 测试元数据提取
        logger.info("测试视频元数据提取...")
        metadata = VideoProcessor.extract_metadata(str(test_video_path))
        if metadata:
            logger.info(f"✅ 元数据提取成功: {metadata}")
        else:
            logger.warning("⚠️  元数据提取失败")
        
        # 测试缩略图生成
        logger.info("测试视频缩略图生成...")
        thumbnail_path = Path(__file__).parent.parent / "test_data" / "test_thumbnail.jpg"
        success = VideoProcessor.generate_thumbnail(str(test_video_path), str(thumbnail_path))
        if success and thumbnail_path.exists():
            logger.info(f"✅ 缩略图生成成功: {thumbnail_path}")
            logger.info(f"缩略图大小: {thumbnail_path.stat().st_size} 字节")
            # 清理测试文件
            thumbnail_path.unlink(missing_ok=True)
        else:
            logger.warning("⚠️  缩略图生成失败")
    else:
        logger.warning(f"⚠️  测试视频文件不存在: {test_video_path}")
        logger.warning("请将测试视频文件命名为test_video.mp4并放在test_data目录下")
    
    logger.info("FFmpeg集成测试完成!")

if __name__ == "__main__":
    main()
