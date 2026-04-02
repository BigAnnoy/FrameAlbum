# 前端模块化架构

## 概述

FrameAlbum 前端已重构为 ES Modules 模块化架构，提升了代码的可维护性、可扩展性和可测试性。

## 目录结构

```
frontend/modules/
├── index.js              # 主入口文件
├── utils/                # 工具模块
│   ├── index.js         # 工具模块索引
│   ├── formatters.js    # 格式化工具
│   └── async.js         # 异步工具
├── api/                  # API模块
│   ├── index.js         # API模块索引
│   ├── client.js        # HTTP客户端
│   ├── album.js         # 相册API
│   ├── settings.js      # 设置API
│   └── health.js        # 健康检查API
├── core/                 # 核心模块（预留）
└── components/           # 组件模块（预留）
```

## 快速开始

### 导入模块

使用 ES Modules 语法导入模块：

```javascript
// 方式1：从主入口导入
import { utils, api } from './modules/index.js';

// 方式2：直接导入特定模块
import { formatFileSize, debounce } from './modules/utils/index.js';
import * as albumApi from './modules/api/album.js';
```

## 模块说明

### 工具模块 (utils)

#### formatters.js - 格式化工具

```javascript
import { formatFileSize, formatDateTime, formatDate } from './modules/utils/formatters.js';

// 格式化文件大小
formatFileSize(1024);              // "1 KB"
formatFileSize(1048576);           // "1 MB"

// 格式化日期时间
formatDateTime('2024-01-01T12:00:00');  // "2024/1/1 12:00:00"

// 格式化日期
formatDate('2024-01-01T12:00:00');       // "2024/1/1"
```

#### async.js - 异步工具

```javascript
import { delay, debounce, throttle } from './modules/utils/async.js';

// 延迟函数
await delay(1000);  // 等待1秒

// 防抖函数
const debouncedFn = debounce(() => {
    console.log('执行防抖函数');
}, 300);

// 节流函数
const throttledFn = throttle(() => {
    console.log('执行节流函数');
}, 500);
```

### API模块 (api)

#### client.js - HTTP客户端

```javascript
import { get, post, put, del } from './modules/api/client.js';

// GET 请求
const data = await get('/endpoint', { param: 'value' });

// POST 请求
const result = await post('/endpoint', { key: 'value' });

// PUT 请求
const updated = await put('/endpoint', { key: 'new value' });

// DELETE 请求
const deleted = await del('/endpoint');
```

#### album.js - 相册API

```javascript
import * as albumApi from './modules/api/album.js';

// 获取相册统计信息
const stats = await albumApi.getAlbumStats();

// 获取目录树
const tree = await albumApi.getAlbumTree();

// 获取照片列表
const photos = await albumApi.getPhotos('/path/to/album');
```

#### settings.js - 设置API

```javascript
import * as settingsApi from './modules/api/settings.js';

// 获取相册路径
const albumPath = await settingsApi.getAlbumPath();

// 设置相册路径
const result = await settingsApi.setAlbumPath('/new/album/path');
```

#### health.js - 健康检查API

```javascript
import * as healthApi from './modules/api/health.js';

// 健康检查
const health = await healthApi.health();

// 测试API
const test = await healthApi.test();
```

## 迁移指南

### 从旧代码迁移

#### 1. 替换全局变量

**旧代码：**
```javascript
window.API.getAlbumStats();
window.APIUtils.formatFileSize(1024);
```

**新代码：**
```javascript
import * as albumApi from './modules/api/album.js';
import { formatFileSize } from './modules/utils/formatters.js';

albumApi.getAlbumStats();
formatFileSize(1024);
```

#### 2. 保持向后兼容

为了平滑迁移，您可以创建一个兼容性层：

```javascript
// compatibility.js
import { utils, api } from './modules/index.js';

// 保持旧的全局变量可用
window.API = {
    getAlbumStats: api.album.getAlbumStats,
    getAlbumTree: api.album.getAlbumTree,
    getPhotos: api.album.getPhotos,
    getAlbumPath: api.settings.getAlbumPath,
    setAlbumPath: api.settings.setAlbumPath,
    health: api.health.health,
    test: api.health.test,
    // ... 其他API
};

window.APIUtils = {
    formatFileSize: utils.formatFileSize,
    formatDateTime: utils.formatDateTime,
    formatDate: utils.formatDate,
    delay: utils.delay,
    debounce: utils.debounce,
    throttle: utils.throttle,
};
```

### 在 HTML 中使用

要在浏览器中使用 ES Modules，需要在 script 标签中添加 `type="module"`：

```html
<script type="module">
    import { utils, api } from './modules/index.js';
    
    // 使用模块
    const stats = await api.album.getAlbumStats();
    console.log(utils.formatFileSize(stats.total_size));
</script>
```

## 最佳实践

### 1. 按需导入

只导入您需要的函数，避免导入整个模块：

```javascript
// ✅ 好的做法
import { formatFileSize } from './modules/utils/formatters.js';

// ❌ 避免的做法
import * as allUtils from './modules/utils/index.js';
```

### 2. 错误处理

始终处理 API 调用的错误：

```javascript
try {
    const stats = await api.album.getAlbumStats();
    // 处理成功
} catch (error) {
    console.error('获取统计信息失败:', error);
    // 处理错误
}
```

### 3. 使用 async/await

使用 async/await 语法，避免 Promise 链：

```javascript
// ✅ 好的做法
async function loadData() {
    const stats = await api.album.getAlbumStats();
    const tree = await api.album.getAlbumTree();
    return { stats, tree };
}

// ❌ 避免的做法
function loadData() {
    return api.album.getAlbumStats()
        .then(stats => {
            return api.album.getAlbumTree()
                .then(tree => ({ stats, tree }));
        });
}
```

## 开发规范

### 1. 模块命名

- 使用小写字母和连字符（kebab-case）
- 文件名应清晰表达模块用途

### 2. 导出方式

- 使用命名导出（named exports）而非默认导出（default export）
- 在 index.js 中统一导出

### 3. 文档注释

为公共函数添加 JSDoc 注释：

```javascript
/**
 * 格式化文件大小
 * @param {number} bytes - 文件大小（字节）
 * @returns {string} 格式化后的文件大小
 */
export function formatFileSize(bytes) {
    // 实现
}
```

## 扩展指南

### 添加新的工具模块

1. 在 `utils/` 目录创建新文件
2. 导出函数
3. 在 `utils/index.js` 中重新导出

### 添加新的API模块

1. 在 `api/` 目录创建新文件
2. 导入 client 模块
3. 实现 API 函数
4. 在 `api/index.js` 中重新导出

## 技术栈

- **ES Modules (ESM)** - 原生模块化系统
- **Fetch API** - 网络请求
- **Async/Await** - 异步编程

## 浏览器支持

ES Modules 支持以下浏览器：
- Chrome 61+
- Firefox 60+
- Safari 11+
- Edge 16+

## 常见问题

### Q: 如何在旧代码和新架构之间切换？

A: 使用兼容性层，保持全局变量可用，逐步迁移代码。

### Q: 模块加载失败怎么办？

A: 确保：
1. 使用了 `type="module"` 属性
2. 文件路径正确
3. 服务器支持 MIME 类型 `application/javascript`

### Q: 如何测试模块？

A: 使用支持 ESM 的测试框架，如 Jest 或 Vitest。

## 更新日志

### v1.0.0 (2026-03-31)
- 初始版本
- 实现基础工具模块
- 实现 API 模块
- 创建模块化架构
