# 配置管理重构计划

## 任务目标

1. **修复 `last_import` 问题** - 导入完成后自动更新时间
2. **配置改用 JSON 存储** - 移除数据库相关代码，提高可读性

## 具体步骤

### 步骤 1: 重构 config_manager.py

**修改内容：**
- 移除 `from .database import get_setting, set_setting` 导入
- 移除 `init_db()` 调用
- 移除 `_migrate_to_database()` 方法
- 移除 `_save_config()` 中的数据库同步代码
- 简化所有方法，只操作 JSON 文件
- 保留内存缓存 `self.config` 提高性能

**涉及的方法：**
- `__init__()` - 移除数据库初始化
- `set_album_path_only()` - 移除数据库写入
- `get_album_path()` - 移除数据库读取
- `set_last_import()` - 移除数据库写入
- `get_last_import()` - 移除数据库读取
- `update_setting()` - 移除数据库写入
- `get_setting()` - 移除数据库读取
- `get_all_config()` - 移除数据库读取
- `reset_config()` - 移除数据库重置

### 步骤 2: 修复 last_import 更新问题

**修改文件：** `backend/import_manager.py`

**修改位置：** `_do_import()` 方法的 `finally` 块中

**添加代码：**
```python
# 导入完成后更新最后导入时间
if progress.status == ImportStatus.COMPLETED:
    from .config_manager import get_config_manager
    config = get_config_manager()
    config.set_last_import()
```

### 步骤 3: 清理 database.py

**可选操作：**
- 保留 `Setting` 表（其他模块可能使用）
- 或完全移除 `Setting` 表及相关函数

### 步骤 4: 测试验证

**测试内容：**
1. 设置相册路径是否正常保存到 JSON
2. 导入完成后 `last_import` 是否更新
3. 设置项是否正常读写
4. 重启应用后配置是否保留

## 文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `backend/config_manager.py` | 修改 | 移除数据库相关代码 |
| `backend/import_manager.py` | 修改 | 添加 last_import 更新 |
| `backend/database.py` | 可选修改 | 清理 Setting 表（可选） |

## 预期结果

1. 配置只存储在 `config.json`，可读性更好
2. 导入完成后自动更新 `last_import` 时间
3. 代码更简洁，减少数据库依赖
