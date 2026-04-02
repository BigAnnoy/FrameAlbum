/**
 * 设置对话框模块（模块化版本）
 * 处理相册路径修改、FFmpeg 检查、缓存清空等
 */

import { api } from '../index.js';

export class SettingsDialog {
    constructor() {
        this.dialog = null;
        this.currentPath = null;
        this.escKeyHandler = null;
    }

    /**
     * 初始化设置对话框
     */
    init() {
        console.log('初始化设置对话框');
        
        this.dialog = document.getElementById('settings-dialog');
        this.bindEvents();
    }

    /**
     * 打开设置对话框
     */
    async open() {
        console.log('打开设置对话框');
        
        if (!this.dialog) {
            this.dialog = document.getElementById('settings-dialog');
            if (!this.dialog) {
                console.error('[SettingsDialog.open] 找不到 settings-dialog 元素');
                return;
            }
        }

        await this.loadSettings();
        
        this.dialog.style.display = 'flex';
        this.dialog.setAttribute('aria-hidden', 'false');
        
        this.bindKeyboardEvents();
        this.focusFirstInteractiveElement();
        document.body.style.overflow = 'hidden';
    }

    /**
     * 关闭设置对话框
     */
    close() {
        console.log('关闭设置对话框');

        if (!this.dialog) return;
        
        this.dialog.style.display = 'none';
        this.dialog.setAttribute('aria-hidden', 'true');
        
        this.unbindKeyboardEvents();
        document.body.style.overflow = 'auto';
    }
    
    /**
     * 绑定键盘事件
     */
    bindKeyboardEvents() {
        this.escKeyHandler = (e) => {
            if (e.key === 'Escape') {
                this.close();
            }
        };
        document.addEventListener('keydown', this.escKeyHandler);
    }
    
    /**
     * 移除键盘事件监听
     */
    unbindKeyboardEvents() {
        if (this.escKeyHandler) {
            document.removeEventListener('keydown', this.escKeyHandler);
            this.escKeyHandler = null;
        }
    }
    
    /**
     * 聚焦到对话框的第一个可交互元素
     */
    focusFirstInteractiveElement() {
        const firstInput = this.dialog.querySelector('input, button, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (firstInput) {
            firstInput.focus();
        }
    }

    /**
     * 加载当前设置
     */
    async loadSettings() {
        try {
            const settingsPath = document.getElementById('settings-album-path');
            if (settingsPath) {
                const response = await api.settings.getAlbumPath();
                if (response.album_path) {
                    this.currentPath = response.album_path;
                    settingsPath.value = response.album_path;
                }
            }

            const langSelect = document.getElementById('language-select');
            if (langSelect && window.I18n) {
                langSelect.value = I18n.getLanguage();
            }
        } catch (error) {
            console.error('加载设置失败:', error);
        }
    }

    /**
     * 检查 FFmpeg
     */
    async checkFFmpeg() {
        try {
            const statusEl = document.getElementById('settings-ffmpeg-status');
            if (!statusEl) return;
            
            statusEl.textContent = '检查中...';
            
            const response = await fetch('/api/settings/ffmpeg-status');
            const data = await response.json();
            
            if (data.status === 'available') {
                statusEl.innerHTML = '<span style="color: #28a745;">✓ 已安装</span>';
            } else {
                statusEl.innerHTML = '<span style="color: #dc3545;">✗ 未安装</span>';
            }
        } catch (error) {
            console.error('检查 FFmpeg 失败:', error);
            const statusEl = document.getElementById('settings-ffmpeg-status');
            if (statusEl) {
                statusEl.innerHTML = '<span style="color: #dc3545;">✗ 检查失败</span>';
            }
        }
    }

    /**
     * 修改相册路径
     */
    async changeAlbumPath() {
        try {
            let newPath = await this.selectFolder();
            
            if (!newPath) {
                return;
            }
            
            const pathInput = document.getElementById('settings-album-path');
            
            if (newPath === this.currentPath) {
                alert('路径未改变');
                return;
            }
            
            if (!confirm('确认修改相册路径为: ' + newPath + '?')) {
                return;
            }
            
            const response = await api.settings.setAlbumPath(newPath);
            
            if (response.error) {
                alert('修改失败: ' + response.error);
                return;
            }
            
            this.currentPath = newPath;
            pathInput.value = newPath;

            if (response.task_id) {
                await this._waitForRebuild(response.task_id);
            }
            
            if (window.app) {
                if (typeof window.app.loadAlbumStats === 'function') {
                    await window.app.loadAlbumStats();
                }
                const photosContainer = document.getElementById('photos-container');
                if (photosContainer) {
                    photosContainer.innerHTML = '<div class="welcome-message"><p>👈 选择左侧的目录查看照片</p></div>';
                }
                const contentTitle = document.getElementById('content-title');
                if (contentTitle) {
                    contentTitle.textContent = '欢迎使用相册管理';
                }
            }
        } catch (error) {
            console.error('修改路径失败:', error);
            alert('修改路径失败: ' + error.message);
        } finally {
            this._hideRebuildLoading();
        }
    }

    /**
     * 等待后台 MD5 索引重建完成，期间显示 loading 弹窗
     */
    async _waitForRebuild(taskId) {
        this._showRebuildLoading('正在扫描相册...');

        return new Promise((resolve, reject) => {
            const poll = async () => {
                try {
                    const res = await fetch(`/api/settings/rebuild-progress/${taskId}`);
                    const data = await res.json();

                    this._updateRebuildLoading(data.message || '处理中...', data.progress || 0);

                    if (data.status === 'done') {
                        this._hideRebuildLoading();
                        resolve();
                    } else if (data.status === 'error') {
                        this._hideRebuildLoading();
                        alert('索引重建失败: ' + data.message);
                        resolve();
                    } else {
                        setTimeout(poll, 500);
                    }
                } catch (e) {
                    this._hideRebuildLoading();
                    reject(e);
                }
            };
            poll();
        });
    }

    /**
     * 显示重建 loading 弹窗
     */
    _showRebuildLoading(message) {
        let overlay = document.getElementById('rebuild-loading-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'rebuild-loading-overlay';
            overlay.style.cssText = `
                position: fixed; inset: 0; z-index: 9999;
                background: rgba(0,0,0,0.55);
                display: flex; align-items: center; justify-content: center;
            `;
            overlay.innerHTML = `
                <div style="
                    background: var(--bg-primary, #fff);
                    border-radius: 12px;
                    padding: 32px 40px;
                    min-width: 320px;
                    text-align: center;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.18);
                ">
                    <div style="font-size: 2rem; margin-bottom: 12px;">⚙️</div>
                    <div style="font-size: 1rem; font-weight: 600; margin-bottom: 8px;">正在建立相册索引</div>
                    <div id="rebuild-loading-msg" style="font-size: 0.85rem; color: var(--text-secondary, #888); margin-bottom: 16px;">${message}</div>
                    <div style="
                        height: 6px; background: var(--border-color, #eee);
                        border-radius: 3px; overflow: hidden;
                    ">
                        <div id="rebuild-loading-bar" style="
                            height: 100%; width: 0%;
                            background: var(--accent-color, #4f8ef7);
                            border-radius: 3px;
                            transition: width 0.3s ease;
                        "></div>
                    </div>
                    <div id="rebuild-loading-pct" style="font-size: 0.8rem; color: var(--text-secondary, #888); margin-top: 6px;">0%</div>
                </div>
            `;
            document.body.appendChild(overlay);
        }
        overlay.style.display = 'flex';
    }

    /**
     * 更新 loading 弹窗内容
     */
    _updateRebuildLoading(message, percent) {
        const msg = document.getElementById('rebuild-loading-msg');
        const bar = document.getElementById('rebuild-loading-bar');
        const pct = document.getElementById('rebuild-loading-pct');
        if (msg) msg.textContent = message;
        if (bar) bar.style.width = percent + '%';
        if (pct) pct.textContent = percent + '%';
    }

    /**
     * 隐藏 loading 弹窗
     */
    _hideRebuildLoading() {
        const overlay = document.getElementById('rebuild-loading-overlay');
        if (overlay) overlay.style.display = 'none';
    }

    /**
     * 使用 PyWebView API 选择文件夹
     */
    async selectFolder() {
        try {
            const changeBtn = document.getElementById('btn-change-album-path');
            const originalText = changeBtn.textContent;
            changeBtn.disabled = true;
            changeBtn.textContent = '⏳ 选择中...';
            
            if (window.pywebview && window.pywebview.api) {
                console.log('使用 PyWebView API 选择文件夹...');
                const path = await window.pywebview.api.select_folder();
                
                if (path && typeof path === 'string' && path.trim()) {
                    console.log('选择的路径:', path);
                    changeBtn.disabled = false;
                    changeBtn.textContent = originalText;
                    return path;
                } else {
                    console.log('用户取消了文件夹选择');
                    changeBtn.disabled = false;
                    changeBtn.textContent = originalText;
                    return null;
                }
            } else {
                console.warn('PyWebView API 不可用，使用手动输入');
                const path = prompt('请输入相册位置的完整路径:\n(例如：D:\\Pictures 或 /home/user/Pictures)');
                changeBtn.disabled = false;
                changeBtn.textContent = originalText;
                if (path && path.trim()) {
                    return path;
                }
                return null;
            }
        } catch (error) {
            console.error('选择文件夹失败:', error);
            const changeBtn = document.getElementById('btn-change-album-path');
            if (changeBtn) {
                changeBtn.disabled = false;
            }
            alert('选择文件夹失败: ' + error.message);
            return null;
        }
    }

    /**
     * 清空缓存
     */
    async clearCache() {
        try {
            if (!confirm('确定要清空缓存吗?')) {
                return;
            }
            
            if (window.app && typeof window.app.clearAppCache === 'function') {
                window.app.clearAppCache();
            }
            
            alert('缓存已清空');
        } catch (error) {
            console.error('清空缓存失败:', error);
            alert('清空缓存失败');
        }
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        const closeBtn = document.getElementById('close-settings-dialog');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.close());
        }
        
        const closeBtn2 = document.getElementById('close-settings');
        if (closeBtn2) {
            closeBtn2.addEventListener('click', () => this.close());
        }
        
        const changePath = document.getElementById('btn-change-album-path');
        if (changePath) {
            changePath.addEventListener('click', () => this.changeAlbumPath());
        }
        
        const clearCacheBtn = document.getElementById('btn-clear-cache');
        if (clearCacheBtn) {
            clearCacheBtn.addEventListener('click', () => this.clearCache());
        }

        const langSelect = document.getElementById('language-select');
        if (langSelect) {
            langSelect.addEventListener('change', async (e) => {
                if (window.I18n) {
                    await I18n.setLanguage(e.target.value);
                }
            });
        }

        if (this.dialog) {
            this.dialog.addEventListener('click', (e) => {
                if (e.target === this.dialog) {
                    this.close();
                }
            });
        }
    }
}
