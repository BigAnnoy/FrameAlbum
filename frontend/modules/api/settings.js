/**
 * 设置 API 模块
 * 提供设置相关的 API 调用
 */

import * as client from './client.js';

/**
 * 获取当前相册路径
 * @returns {Promise<object>} 相册路径数据
 */
export function getAlbumPath() {
    console.log('[API] 获取相册路径...');
    return client.get('/settings/album-path').then(data => {
        console.log('[API] ✅ 相册路径:', data);
        return data;
    }).catch(error => {
        console.error('[API] ❌ 获取相册路径失败:', error);
        throw error;
    });
}

/**
 * 修改相册路径
 * @param {string} path - 新的相册路径
 * @returns {Promise<object>} 响应数据
 */
export function setAlbumPath(path) {
    console.log('[API] 设置相册路径:', path);
    return client.put('/settings/album-path', {
        album_path: path,
    }).then(data => {
        console.log('[API] ✅ 相册路径设置成功:', data);
        return data;
    }).catch(error => {
        console.error('[API] ❌ 设置相册路径失败:', error);
        throw error;
    });
}
