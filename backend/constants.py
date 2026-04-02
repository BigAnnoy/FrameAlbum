"""
常量定义模块
集中管理项目中所有共享常量，避免多处重复定义
"""

# 支持的视频格式（小写扩展名）
VIDEO_FORMATS: frozenset = frozenset({
    '.mp4', '.mkv', '.avi', '.mov', '.wmv',
    '.flv', '.webm', '.m4v', '.mpg', '.mpeg', '.3gp',
})

# 支持的图片格式（小写扩展名）
IMAGE_FORMATS: frozenset = frozenset({
    '.jpg', '.jpeg', '.png', '.bmp', '.gif',
    '.webp', '.tiff', '.ico', '.heic',
})

# 所有支持的媒体格式（图片 + 视频）
MEDIA_FORMATS: frozenset = IMAGE_FORMATS | VIDEO_FORMATS
