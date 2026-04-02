# 启动路径修复总结

## 问题描述

重新组织项目目录后，应用启动时出现两个主要错误：

1. **ModuleNotFoundError: No module named 'api_server'**
   - 原因：`api_server.py` 被移到了 `backend/` 目录，但 `FrameAlbum.py` 无法找到它
   
2. **找不到前端文件错误**
   - 原因：前端文件在 `../frontend` 目录，但路径计算有误

## 修复方案

### 1. 修复 `src/FrameAlbum.py`

添加了项目路径配置，确保可以找到后端模块和前端资源：

```python
# 配置 Python 路径 - 添加项目目录以便导入后端模块
project_root = Path(__file__).parent.parent  # 项目根目录
backend_dir = project_root / 'backend'
frontend_dir = project_root / 'frontend'

# 添加后端目录到 Python 路径
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
```

### 2. 修复 `backend/api_server.py`

添加了当前目录到 Python 路径，确保可以导入同目录的模块：

```python
# 确保当前目录在 Python 路径中（为了导入同目录的模块）
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
```

### 3. 修复方法调用错误

修正了 `FrameAlbum.py` 中对 `ConfigManager` 的错误方法调用：

| 错误方法 | 正确方法 |
|---------|---------|
| `get_created_at()` | `get_all_config()['created_at']` |
| `is_initialized()` | `is_first_run()` |

修改前：
```python
return {
    'album_path': self.config.get_album_path(),
    'created_at': str(self.config.get_created_at()),  # ❌ 不存在
    'last_import': str(self.config.get_last_import()),
    'is_initialized': self.config.is_initialized()  # ❌ 不存在
}
```

修改后：
```python
all_config = self.config.get_all_config()
return {
    'album_path': self.config.get_album_path(),
    'created_at': all_config.get('created_at'),  # ✅ 正确
    'last_import': self.config.get_last_import(),
    'is_first_run': self.config.is_first_run()  # ✅ 正确
}
```

## 验证结果

已创建诊断脚本 `启动测试.py`，运行结果显示所有检查都通过：

```
[OK] backend directory
[OK] frontend directory  
[OK] src directory
[OK] FrameAlbum.py
[OK] api_server.py
[OK] config_manager.py
[OK] index.html
[OK] config_manager.ConfigManager (可正确导入)
[OK] api_server.app (可正确导入)
[OK] PyWebView (可正确导入)
```

## 启动应用

现在可以通过以下任意方式启动应用：

### 方式 1: 直接 Python 命令
```bash
cd c:\Users\IT20240802\Desktop\照片整理
python src\FrameAlbum.py
```

### 方式 2: 使用启动脚本（推荐）
```bash
启动相册.bat
```

### 方式 3: 使用 Python 启动脚本
```bash
python 启动相册.py
```

## 相关文件

| 文件 | 说明 |
|------|------|
| `src/FrameAlbum.py` | 已修复路径配置 |
| `backend/api_server.py` | 已修复路径配置 |
| `启动测试.py` | 诊断脚本 |
| `docs/GETTING_STARTED.md` | 快速开始指南 |

## 技术要点

- Python `sys.path` 用于动态添加模块搜索路径
- 使用 `Path(__file__).parent` 获取当前文件的目录
- `Path.exists()` 验证文件和目录是否存在
- PyWebView 应用加载本地 HTML 文件时需要绝对路径
