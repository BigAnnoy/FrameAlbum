/**
 * 相册 API 模块
 * 提供相册相关的 API 调用
 */

import * as client from './client.js';

/**
 * 获取相册统计信息
 * @returns {Promise<object>} 相册统计数据
 */
export function getAlbumStats() {
    console.log('[API] 获取相册统计...');
    return client.get('/album/stats').then(data => {
        console.log('[API] ✅ 统计数据:', data);
        return data;
    }).catch(error => {
        console.error('[API] ❌ 获取统计失败:', error);
        throw error;
    });
}

/**
 * 获取完整目录树
 * @returns {Promise<object>} 目录树数据
 */
export function getAlbumTree() {
    console.log('[API] 获取目录树...');
    return client.get('/album/tree').then(data => {
        console.log('[API] ✅ 目录树数据:', data);
        return data;
    }).catch(error => {
        console.error('[API] ❌ 获取目录树失败:', error);
        throw error;
    });
}

/**
 * 获取指定路径下的照片列表
 * @param {string} path - 路径
 * @returns {Promise<object>} 照片列表数据
 */
export function getPhotos(path) {
    console.log('[API] 获取照片列表，路径:', path);
    return client.get('/album/photos', { path }).then(data => {
        console.log('[API] ✅ 照片数据:', data);
        return data;
    }).catch(error => {
        console.error('[API] ❌ 获取照片失败:', error);
        throw error;
    });
}
