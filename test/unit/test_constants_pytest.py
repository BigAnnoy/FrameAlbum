"""
常量定义模块测试 (pytest版本)
测试 constants.py 中的所有常量
"""

from backend.constants import VIDEO_FORMATS, IMAGE_FORMATS, MEDIA_FORMATS


def test_video_formats_not_empty():
    """测试视频格式集合不为空"""
    assert len(VIDEO_FORMATS) > 0


def test_image_formats_not_empty():
    """测试图片格式集合不为空"""
    assert len(IMAGE_FORMATS) > 0


def test_media_formats_combination():
    """测试媒体格式集合是视频和图片格式的并集"""
    assert MEDIA_FORMATS == VIDEO_FORMATS | IMAGE_FORMATS


def test_common_video_formats():
    """测试常见视频格式是否包含在集合中"""
    common_video_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    for fmt in common_video_formats:
        assert fmt in VIDEO_FORMATS


def test_common_image_formats():
    """测试常见图片格式是否包含在集合中"""
    common_image_formats = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
    for fmt in common_image_formats:
        assert fmt in IMAGE_FORMATS


def test_format_lowercase():
    """测试所有格式都是小写"""
    for fmt in VIDEO_FORMATS:
        assert fmt == fmt.lower()
    
    for fmt in IMAGE_FORMATS:
        assert fmt == fmt.lower()
    
    for fmt in MEDIA_FORMATS:
        assert fmt == fmt.lower()


def test_no_overlap_between_formats():
    """测试视频格式和图片格式没有重叠"""
    assert VIDEO_FORMATS.isdisjoint(IMAGE_FORMATS)


def test_formats_are_frozenset():
    """测试格式集合是frozenset类型"""
    assert isinstance(VIDEO_FORMATS, frozenset)
    assert isinstance(IMAGE_FORMATS, frozenset)
    assert isinstance(MEDIA_FORMATS, frozenset)
