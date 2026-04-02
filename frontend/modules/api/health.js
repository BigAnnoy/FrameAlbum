/**
 * 健康检查 API 模块
 * 提供健康检查相关的 API 调用
 */

import * as client from './client.js';

/**
 * 健康检查
 * @returns {Promise<object>} 健康检查数据
 */
export function health() {
    console.log('[API] 执行健康检查...');
    return client.get('/health').then(data => {
        console.log('[API] ✅ 后端服务正常:', data);
        return data;
    }).catch(error => {
        console.error('[API] ❌ 健康检查失败（可能后端未启动）:', error);
        throw error;
    });
}

/**
 * 测试 API
 * @returns {Promise<object>} 测试数据
 */
export function test() {
    console.log('[API] 执行测试 API...');
    return client.get('/test').then(data => {
        console.log('[API] ✅ 测试 API 响应:', data);
        return data;
    }).catch(error => {
        console.error('[API] ❌ 测试 API 失败:', error);
        throw error;
    });
}
