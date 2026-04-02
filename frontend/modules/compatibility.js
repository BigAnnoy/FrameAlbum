/**
 * 兼容性层
 * 保持旧的全局变量可用，实现平滑迁移
 */

import { utils, api, components } from './index.js';

// 保持旧的全局 API 变量可用
window.API = {
    // 相册 API
    getAlbumStats: api.album.getAlbumStats,
    getAlbumTree: api.album.getAlbumTree,
    getPhotos: api.album.getPhotos,
    
    // 设置 API
    getAlbumPath: api.settings.getAlbumPath,
    setAlbumPath: api.settings.setAlbumPath,
    
    // 健康检查 API
    health: api.health.health,
    test: api.health.test,
    
    // 导入 API
    checkImportPath: api.importApi.checkImportPath,
    startImport: api.importApi.startImport,
    getImportProgress: api.importApi.getImportProgress,
    cancelImport: api.importApi.cancelImport,
    pauseImport: api.importApi.pauseImport,
    resumeImport: api.importApi.resumeImport,
    
    // 基础 HTTP 方法
    get: api.client.get,
    post: api.client.post,
    put: api.client.put,
    delete: api.client.del,
};

// 小写别名
window.api = window.API;

// 保持旧的全局 APIUtils 变量可用
window.APIUtils = {
    // 格式化工具
    formatFileSize: utils.formatFileSize,
    formatDateTime: utils.formatDateTime,
    formatDate: utils.formatDate,
    
    // 异步工具
    delay: utils.delay,
    debounce: utils.debounce,
    throttle: utils.throttle,
};

// 保持旧的全局 AlbumBrowser 变量可用（使用单例模式）
let albumBrowserInstance = null;
window.AlbumBrowser = new Proxy({}, {
    get(target, prop) {
        if (!albumBrowserInstance) {
            albumBrowserInstance = new components.AlbumBrowser();
        }
        if (typeof albumBrowserInstance[prop] === 'function') {
            return albumBrowserInstance[prop].bind(albumBrowserInstance);
        }
        return albumBrowserInstance[prop];
    },
    set(target, prop, value) {
        if (!albumBrowserInstance) {
            albumBrowserInstance = new components.AlbumBrowser();
        }
        albumBrowserInstance[prop] = value;
        return true;
    }
});

// 保持旧的全局 SettingsDialog 变量可用（使用单例模式）
let settingsDialogInstance = null;
window.SettingsDialog = new Proxy({}, {
    get(target, prop) {
        if (!settingsDialogInstance) {
            settingsDialogInstance = new components.SettingsDialog();
        }
        if (typeof settingsDialogInstance[prop] === 'function') {
            return settingsDialogInstance[prop].bind(settingsDialogInstance);
        }
        return settingsDialogInstance[prop];
    },
    set(target, prop, value) {
        if (!settingsDialogInstance) {
            settingsDialogInstance = new components.SettingsDialog();
        }
        settingsDialogInstance[prop] = value;
        return true;
    }
});

// 保持旧的全局 ImportDialog 变量可用（使用单例模式）
let importDialogInstance = null;
window.ImportDialog = new Proxy({}, {
    get(target, prop) {
        if (!importDialogInstance) {
            importDialogInstance = new components.ImportDialog();
        }
        if (typeof importDialogInstance[prop] === 'function') {
            return importDialogInstance[prop].bind(importDialogInstance);
        }
        return importDialogInstance[prop];
    },
    set(target, prop, value) {
        if (!importDialogInstance) {
            importDialogInstance = new components.ImportDialog();
        }
        importDialogInstance[prop] = value;
        return true;
    }
});

// 保持旧的全局 PhotoSelection 变量可用
window.PhotoSelection = components.PhotoSelection;

// 保持旧的全局 InitializationScreen 类和实例可用
window.InitializationScreen = components.InitializationScreen;

// 创建全局初始化屏幕实例
if (!window.initScreen) {
    // 等待 DOM 准备就绪后再创建实例
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.initScreen = new components.InitializationScreen();
            console.log('[compatibility.js] ✅ DOM 就绪后创建全局 initScreen 实例');
        });
    } else {
        window.initScreen = new components.InitializationScreen();
        console.log('[compatibility.js] ✅ 创建全局 initScreen 实例');
    }
}

// 保持旧的全局 I18n 变量可用
window.I18n = utils.i18n;

console.log('✅ 兼容性层已加载，旧的全局变量 API、APIUtils、I18n、AlbumBrowser、SettingsDialog、ImportDialog、PhotoSelection 和 InitializationScreen 仍然可用');
