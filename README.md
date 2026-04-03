<h1 align="center">📷 FrameAlbum</h1>
<h3 align="center">本地照片管理器 · 隐私零泄露 · 按日期自动整理</h3>


<p align="center">
  <img src="https://img.shields.io/badge/版本-v0.1-gold?style=flat-square" />
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python" />
  <img src="https://img.shields.io/badge/PyWebView-6.1+-green?style=flat-square" />
  <img src="https://img.shields.io/badge/Flask-2.3+-red?style=flat-square&logo=flask" />
  <img src="https://img.shields.io/badge/许可证-MIT-lightgrey?style=flat-square" />
</p>

---

## ✨ 功能亮点

| 功能 | 说明 |
|------|------|
| 🗂 **智能时间线整理** | 读取 EXIF 拍摄时间，自动归档至 `YYYY/YYYY-MM/` 目录 |
| 🔍 **两阶段去重** | (文件大小 + EXIF 时间) 预筛 → MD5 精确比对，减少 I/O |
| ▶️ **视频原生播放** | HTTP Range 支持 Seek，自动提取时长/分辨率/编码信息 |
| 🖼 **特殊格式预览** | HEIC / TIFF / BMP 自动转 JPEG 缩略图，无格式障碍 |
| ☑️ **多选批量操作** | 长按 / 勾选框进入多选，一键批量删除含确认弹窗 |
| ⏸ **可暂停异步导入** | 多线程 + 实时进度轮询，随时暂停/继续 |
| 📋/✂️ **复制或移动** | 导入时弹窗二选一，复制保留源文件，移动删除源文件 |
| 🖱 **右键菜单 + 快捷键** | 右键预览/打开/删除；← → 翻页；ESC 关闭 |
| 🔒 **完全本地运行** | 数据不离机，无任何云端依赖 |

---

## 🚀 快速开始

### 方式一：下载 EXE（推荐）

前往 [GitHub Releases](https://github.com/BigAnnoy/FrameAlbum/releases) 下载最新版本的 `FrameAlbum.exe`，双击即可运行，无需安装任何依赖。

### 方式二：从源码运行

**环境要求**
- Python 3.8+
- Windows / macOS / Linux

**安装依赖**
```bash
git clone https://github.com/BigAnnoy/FrameAlbum.git
cd FrameAlbum
pip install -r requirements.txt
```

**启动**
```bash
python src/FrameAlbum.py
```

首次启动会引导选择相册存储目录。

### FFmpeg（可选，视频功能）

视频缩略图和元数据提取需要 FFmpeg。

**自动下载（推荐）**
```bash
python scripts/download_ffmpeg.py
```

脚本自动检测平台，下载静态编译版（约 70MB）到 `backend/ffmpeg_binaries/`，无需手动配置。

**手动安装**
```bash
# Windows
winget install ffmpeg

# macOS
brew install ffmpeg

# Linux
sudo apt install ffmpeg
```

> 未安装 FFmpeg 时图片功能完全正常，视频显示占位图标。

---

## 📁 目录结构

```
FrameAlbum/
├── src/
│   └── FrameAlbum.py              # 主入口（PyWebView 窗口 + Flask 启动）
├── backend/
│   ├── __init__.py
│   ├── api_server.py              # Flask REST API（25+ 端点）
│   ├── config_manager.py          # 配置管理
│   ├── database.py                # SQLAlchemy 数据模型
│   ├── import_manager.py          # 异步导入逻辑（MD5 去重）
│   ├── thumbnail_manager.py       # 缩略图生成与缓存
│   ├── video_processor.py         # FFmpeg 视频处理
│   └── ffmpeg_binaries/           # FFmpeg（可选，自动下载）
├── frontend/
│   ├── index.html                 # 单页应用入口
│   ├── css/                       # 样式
│   ├── modules/                   # 模块化 JS
│   │   ├── api/                   # API 客户端
│   │   ├── app/                   # 应用层
│   │   ├── components/            # UI 组件
│   │   └── utils/                 # 工具函数
│   └── *.svg                      # 图标资源
├── docs/                          # 文档
├── scripts/
│   └── download_ffmpeg.py         # FFmpeg 下载脚本
├── FrameAlbum.spec                # PyInstaller 打包配置
├── requirements.txt
└── README.md
```

整理后的媒体文件结构：

```
相册目录/
└── 2024/
    └── 2024-03/
        ├── 20240315_143022_001.jpg
        ├── 20240315_143022_002.jpg   ← 同秒连拍自动序号
        └── 20240316_091500_001.mp4
```

---

## 🏗 技术栈

| 层 | 技术 |
|----|------|
| 窗口层 | [PyWebView](https://pywebview.flowrl.com/) 6.1+ |
| 后端 API | Flask 2.3+ · Flask-CORS |
| 数据库 | SQLite · SQLAlchemy |
| 图像处理 | Pillow 10+ · pillow-heif |
| 视频处理 | FFmpeg（可选） |
| 前端 | 原生 HTML / CSS / JavaScript（零框架依赖） |

---

## 📋 核心 API

```
GET  /api/health                  # 服务健康检查
GET  /api/album/stats              # 统计信息（照片数/视频数/时间跨度）
GET  /api/album/tree               # 目录树
GET  /api/album/photos?path=...   # 照片列表（含 thumbnail/preview/url）
GET  /api/album/thumbnail?path=... # 缩略图（带缓存）
GET  /api/album/preview?path=...   # HEIC 等特殊格式 JPEG 预览
POST /api/import/check             # 导入预检（MD5 去重 + 统计）
POST /api/import/start             # 启动异步导入
GET  /api/import/progress/<id>    # 实时进度
POST /api/import/pause/<id>       # 暂停导入
POST /api/import/resume/<id>       # 继续导入
POST /api/import/cancel/<id>       # 取消导入
POST /api/files/delete             # 批量删除文件
GET/PUT /api/settings/album-path    # 相册路径管理
```

---

## 🗒 更新日志

见 [CHANGELOG.md](CHANGELOG.md)

---

## 📄 许可证

[MIT License](LICENSE) © 2026
