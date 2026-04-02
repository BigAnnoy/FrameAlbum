/**
 * 应用主程序（模块化版本）
 * 初始化应用，管理全局状态，处理事件
 */

import { utils, api } from '../index.js';

export class App {
    constructor() {
        this.isReady = false;
        this.currentPath = null;
        this.albumTree = null;
        this.albumStats = null;
        this.init();
    }

    /**
     * 应用初始化
     */
    async init() {
        try {
            console.log('🚀 应用初始化中...');
            
            // 0. 等待 PyWebView API 准备就绪（关键步骤）
            if (window.pywebviewReady) {
                console.log('⏳ 等待 PyWebView API 准备就绪...');
                try {
                    await window.pywebviewReady.wait(5000);
                    console.log('✅ PyWebView API 已准备就绪');
                } catch (err) {
                    console.warn('⚠️ PyWebView API 准备超时:', err.message);
                }
            }
            
            // 1. 等待 DOM 准备就绪
            await this.waitForDOM();
            console.log('[init] DOM 已准备就绪');
            
            // 2. 检查是否需要初始化（相册路径是否已设置）
            console.log('[init] 开始检查初始化状态...');
            const needsInitialization = await this.checkInitializationStatus();
            console.log('[init] 初始化状态检查完成，需要初始化:', needsInitialization);
            
            // 检查初始化屏幕和主界面的状态
            const initScreen = document.getElementById('initialization-screen');
            const appContainer = document.querySelector('.app-container');
            console.log('[init] 初始化屏幕元素:', initScreen);
            console.log('[init] 主界面容器元素:', appContainer);
            
            if (needsInitialization) {
                console.log('📋 首次启动，显示初始化屏幕');
                if (window.initScreen) {
                    console.log('✅ 使用全局 initScreen 实例');
                    window.initScreen.init();
                    window.initScreen.show();
                } else {
                    console.warn('⚠️ 全局 initScreen 实例不存在，创建新实例');
                    const initScreen = new InitializationScreen();
                    initScreen.init();
                    initScreen.show();
                }
                if (appContainer) {
                    appContainer.classList.remove('shown');
                    console.log('[init] 主界面已隐藏');
                }
                return;
            } else {
                console.log('✅ 相册已初始化，显示主界面');
                if (appContainer) {
                    appContainer.classList.add('shown');
                    console.log('[init] 主界面已显示');
                }
            }
            
            // 3. 绑定事件
            console.log('[init] 开始绑定事件...');
            this.bindEvents();
            console.log('[init] 事件绑定完成');
            
            // 4. 初始化 UI
            console.log('[init] 开始初始化 UI...');
            this.initUI();
            console.log('[init] UI 初始化完成');
            
            // 5. 加载数据
            console.log('[init] 开始加载初始数据...');
            await this.loadInitialData();
            console.log('[init] 数据加载完成');
            
            this.isReady = true;
            console.log('✅ 应用初始化完成');
            
        } catch (error) {
            console.error('❌ 应用初始化失败:', error);
            console.error('错误堆栈:', error.stack);
            this.showError('应用初始化失败: ' + error.message);
        }
    }

    /**
     * 检查是否需要初始化
     */
    async checkInitializationStatus() {
        console.log('=== 开始检查初始化状态 ===');
        
        try {
            console.log('[checkInitializationStatus] 直接检查相册路径设置...');
            
            const albumPathUrl = 'http://127.0.0.1:5000/api/settings/album-path';
            console.log('[checkInitializationStatus] 直接调用API URL:', albumPathUrl);
            
            const response = await fetch(albumPathUrl);
            console.log('[checkInitializationStatus] API响应状态:', response.status);
            
            if (response.ok) {
                const result = await response.json();
                console.log('[checkInitializationStatus] API响应内容:', result);
                console.log('[checkInitializationStatus] 相册路径值:', result.album_path);
                
                if (result.album_path && result.album_path !== '') {
                    console.log('[checkInitializationStatus] ✅ 相册已初始化，可以显示主界面');
                    return false;
                } else {
                    console.log('[checkInitializationStatus] ⚠️ 相册路径未设置，需要初始化');
                    return true;
                }
            } else {
                console.error('[checkInitializationStatus] ❌ API请求失败，状态码:', response.status);
                return false;
            }
        } catch (error) {
            console.error('[checkInitializationStatus] ❌ 检查初始化状态异常:', error);
            console.error('[checkInitializationStatus] 错误堆栈:', error.stack);
            return false;
        }
    }

    /**
     * 等待 DOM 准备就绪
     */
    waitForDOM() {
        return new Promise(resolve => {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', resolve);
            } else {
                resolve();
            }
        });
    }

    /**
     * 绑定事件处理
     */
    bindEvents() {
        console.log('[bindEvents] 开始绑定事件...');
        
        const btnSettings = document.getElementById('btn-settings');
        if (btnSettings) {
            btnSettings.addEventListener('click', () => {
                console.log('[Event] 点击设置按钮');
                this.showSettingsDialog();
            });
            btnSettings.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.showSettingsDialog();
                }
            });
            console.log('[bindEvents] btn-settings 已绑定');
        }
        
        const btnHelp = document.getElementById('btn-help');
        if (btnHelp) {
            btnHelp.addEventListener('click', () => {
                console.log('[Event] 点击帮助按钮');
                this.showHelp();
            });
            btnHelp.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.showHelp();
                }
            });
            console.log('[bindEvents] btn-help 已绑定');
        }
        
        const btnRefresh = document.getElementById('btn-refresh');
        if (btnRefresh) {
            btnRefresh.addEventListener('click', () => {
                console.log('[Event] 点击刷新按钮');
                this.refresh();
            });
            btnRefresh.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.refresh();
                }
            });
            console.log('[bindEvents] btn-refresh 已绑定');
        }
        
        const btnImport = document.getElementById('btn-import');
        if (btnImport) {
            btnImport.addEventListener('click', () => {
                console.log('[Event] 点击导入按钮');
                this.showImportDialog();
            });
            btnImport.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.showImportDialog();
                }
            });
            console.log('[bindEvents] btn-import 已绑定');
        }

        const btnImportWelcome = document.getElementById('btn-import-welcome');
        if (btnImportWelcome) {
            btnImportWelcome.addEventListener('click', () => {
                this.showImportDialog();
            });
        }
        
        window.addEventListener('resize', utils.debounce(() => {
            this.handleWindowResize();
        }, 200));
        
        this.handleWindowResize();

        ['close-help-dialog', 'close-help-btn'].forEach(id => {
            const btn = document.getElementById(id);
            if (btn) btn.addEventListener('click', () => {
                const dialog = document.getElementById('help-dialog');
                if (dialog) dialog.style.display = 'none';
            });
        });
        const helpDialog = document.getElementById('help-dialog');
        if (helpDialog) {
            helpDialog.addEventListener('click', (e) => {
                if (e.target === helpDialog) helpDialog.style.display = 'none';
            });
        }
        
        console.log('[bindEvents] 事件绑定完成');
    }

    /**
     * 初始化 UI
     */
    initUI() {
        console.log('[initUI] 开始 UI 初始化...');
        
        try {
            if (window.AlbumBrowser && typeof window.AlbumBrowser.init === 'function') {
                console.log('[initUI] 初始化 AlbumBrowser...');
                window.AlbumBrowser.init();
            } else {
                console.warn('[initUI] AlbumBrowser 不可用');
            }
            
            if (window.importDialog) {
                console.log('[initUI] importDialog 实例已初始化');
            } else {
                console.warn('[initUI] importDialog 实例不可用');
            }
            
            if (window.SettingsDialog && typeof window.SettingsDialog.init === 'function') {
                console.log('[initUI] 初始化 SettingsDialog...');
                window.SettingsDialog.init();
            } else {
                console.warn('[initUI] SettingsDialog 不可用');
            }
            
            this.initTheme();

            if (window.I18n) {
                I18n.initLanguage().catch(e => console.warn('[i18n] initLanguage 失败:', e));
            }
            
            console.log('[initUI] UI 初始化完成');
        } catch (error) {
            console.error('[initUI] UI 初始化出错:', error);
            throw error;
        }
    }

    /**
     * 加载初始数据
     */
    async loadInitialData() {
        console.log('[loadInitialData] 开始加载初始数据...');
        try {
            console.log('[loadInitialData] 1️⃣ 测试 API 连接...');
            const health = await api.health.health();
            console.log('[loadInitialData] ✅ API 服务器连接正常:', health);
            
            console.log('[loadInitialData] 2️⃣ 加载相册统计信息...');
            await this.loadAlbumStats();
            console.log('[loadInitialData] ✅ 统计信息加载完成');
            
            console.log('[loadInitialData] ✅ 初始数据加载完成');
        } catch (error) {
            console.error('[loadInitialData] ❌ 加载初始数据失败:', error);
            console.error('[loadInitialData] 错误详情:', error.stack);
            throw error;
        }
    }

    /**
     * 加载相册统计信息
     */
    async loadAlbumStats() {
        try {
            this.albumStats = await api.album.getAlbumStats();
            this.updateStatsUI();
        } catch (error) {
            console.error('加载统计信息失败:', error);
            this.showWarning('无法加载统计信息');
        }
    }

    /**
     * 初始化主题设置
     */
    initTheme() {
        const savedTheme = localStorage.getItem('theme') || 'system';
        this.applyTheme(savedTheme);
        
        const themeSelect = document.getElementById('theme-select');
        if (themeSelect) {
            themeSelect.value = savedTheme;
            themeSelect.addEventListener('change', (e) => {
                this.applyTheme(e.target.value);
            });
        }
    }
    
    /**
     * 应用主题设置
     */
    applyTheme(theme) {
        localStorage.setItem('theme', theme);
        
        let actualTheme = theme;
        if (theme === 'system') {
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            actualTheme = prefersDark ? 'dark' : 'light';
        }
        
        document.documentElement.setAttribute('data-theme', actualTheme);
        
        const themeSelect = document.getElementById('theme-select');
        if (themeSelect) {
            themeSelect.value = theme;
        }
    }

    /**
     * 更新统计 UI
     */
    updateStatsUI() {
        if (!this.albumStats) return;
        
        const totalFilesEl = document.getElementById('stat-total-files');
        if (totalFilesEl) {
            const treeTotal = this.albumTree?.count;
            totalFilesEl.textContent = treeTotal != null ? String(treeTotal) : (this.albumStats.total_files || '0');
        }

        const videoCountEl = document.getElementById('stat-video-count');
        if (videoCountEl) {
            videoCountEl.textContent = this.albumStats.video_count != null
                ? String(this.albumStats.video_count)
                : '0';
        }
        
        const totalSizeEl = document.getElementById('stat-total-size');
        if (totalSizeEl) {
            totalSizeEl.textContent = utils.formatFileSize(this.albumStats.total_size || 0);
        }

        const lastImport = this.albumStats.last_import;
        const lastImportEl = document.getElementById('stat-last-import');
        if (lastImport) {
            try {
                const importDate = new Date(lastImport);
                const formattedDate = importDate.toLocaleString('zh-CN', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                });
                if (lastImportEl) lastImportEl.textContent = formattedDate;
            } catch (e) {
                console.warn('日期格式化失败:', e);
                if (lastImportEl) lastImportEl.textContent = lastImport;
            }
        } else {
            if (lastImportEl) lastImportEl.textContent = '暂无数据';
        }
    }

    /**
     * 处理窗口大小变化
     */
    handleWindowResize() {
        const width = window.innerWidth;
        const appContainer = document.querySelector('.app-container');

        if (!appContainer) return;
        
        if (width < 768) {
            appContainer.classList.add('mobile-layout');
        } else {
            appContainer.classList.remove('mobile-layout');
        }
        
        if (window.AlbumBrowser && window.AlbumBrowser.currentPath) {
            window.AlbumBrowser.renderPhotosWithPagination();
        }
    }

    /**
     * 刷新应用数据
     */
    async refresh() {
        try {
            console.log('🔄 刷新中...');
            await this.loadAlbumStats();
            if (window.AlbumBrowser) {
                await window.AlbumBrowser.loadTree();
            }
            const currentPath = window.AlbumBrowser && window.AlbumBrowser.currentPath;
            if (currentPath) {
                delete window.AlbumBrowser.photosCache[currentPath];
                await window.AlbumBrowser.loadPhotos(currentPath);
            }
            console.log('✅ 刷新完成');
            this.showSuccess('刷新成功');
        } catch (error) {
            console.error('刷新失败:', error);
            this.showError('刷新失败: ' + error.message);
        }
    }

    /**
     * 显示导入对话框
     */
    showImportDialog() {
        if (window.importDialog && typeof window.importDialog.open === 'function') {
            const treeData = (window.AlbumBrowser && window.AlbumBrowser.treeData) || this.albumTree;
            window.importDialog.open(treeData?.path || null);
        } else {
            console.error('[showImportDialog] importDialog 实例不可用');
            alert('导入功能未加载，请刷新页面');
        }
    }

    /**
     * 显示设置对话框
     */
    showSettingsDialog() {
        console.log('[Event] 显示设置对话框');
        if (window.SettingsDialog && typeof window.SettingsDialog.open === 'function') {
            window.SettingsDialog.open();
        } else {
            console.error('SettingsDialog 不可用');
            alert('设置功能未加载，请刷新页面');
        }
    }

    /**
     * 显示帮助
     */
    showHelp() {
        const dialog = document.getElementById('help-dialog');
        if (dialog) {
            dialog.style.display = 'flex';
        }
    }

    /**
     * 显示成功提示
     */
    showSuccess(message) {
        console.log('✅', message);
        this.showNotification(message, 'success');
    }

    /**
     * 显示错误提示
     */
    showError(message) {
        console.error('❌', message);
        this.showNotification(message, 'error');
    }

    /**
     * 显示警告提示
     */
    showWarning(message) {
        console.warn('⚠️', message);
        this.showNotification(message, 'warning');
    }

    /**
     * 显示通知（Toast）
     */
    showNotification(message, type = 'info', duration = 3500) {
        const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
        const container = document.getElementById('toast-container');
        if (!container) {
            console.log(`[${type}] ${message}`);
            return;
        }

        const toast = document.createElement('div');
        toast.className = `toast toast--${type}`;
        toast.textContent = `${icons[type]} ${message}`;
        container.appendChild(toast);

        if (duration > 0) {
            setTimeout(() => {
                toast.style.opacity = '0';
                toast.style.transform = 'translateY(-20px)';
                toast.style.transition = 'opacity 0.3s, transform 0.3s';
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }
    }
}

// 初始化应用
if (typeof window !== 'undefined') {
    console.log('🚀 初始化模块化应用...');
    // 等待 DOM 准备就绪
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            console.log('✅ DOM 就绪，创建 App 实例...');
            window.app = new App();
        });
    } else {
        console.log('✅ DOM 已就绪，创建 App 实例...');
        window.app = new App();
    }
}
