/**
 * 导入 API 模块
 * 提供导入相关的 API 调用
 */

import * as client from './client.js';
import { delay } from '../utils/async.js';

/**
 * 检查导入路径
 * @param {string} sourcePath - 源路径
 * @param {Function} progressCallback - 进度回调函数
 * @param {Function} shouldStopPolling - 是否停止轮询的函数
 * @returns {Promise<object>} 检查结果
 */
export async function checkImportPath(sourcePath, progressCallback, shouldStopPolling) {
    console.log('[API] 检查导入路径:', sourcePath);

    const started = await client.post('/import/check/start', {
        source_path: sourcePath,
    });
    const checkId = started.check_id;

    if (!checkId) {
        throw new Error('检查任务启动失败，未返回 check_id');
    }

    const pollIntervalMs = 300;
    while (true) {
        if (typeof shouldStopPolling === 'function' && shouldStopPolling()) {
            throw new Error('CHECK_CANCELLED');
        }

        const progressData = await client.get(`/import/check/progress/${checkId}`);
        const progressRatio = Math.max(0, Math.min(1, (progressData.progress || 0) / 100));

        if (typeof progressCallback === 'function') {
            progressCallback(progressRatio, progressData);
        }

        if (progressData.status === 'completed') {
            console.log('[API] ✅ 路径检查结果:', progressData.result);
            return progressData.result;
        }

        if (progressData.status === 'failed') {
            throw new Error(progressData.error || '路径检查失败');
        }

        await delay(pollIntervalMs);
    }
}

/**
 * 开始导入
 * @param {string} sourcePath - 源路径
 * @param {string} targetPath - 目标路径
 * @param {string} importMode - 导入模式 ('copy' 或 'move')
 * @param {boolean} skipSourceDuplicates - 是否跳过源重复文件
 * @param {boolean} skipTargetDuplicates - 是否跳过目标重复文件
 * @returns {Promise<object>} 导入结果
 */
export function startImport(sourcePath, targetPath, importMode = 'copy', skipSourceDuplicates = false, skipTargetDuplicates = false) {
    console.log('[API] 开始导入，源:', sourcePath, '目标:', targetPath, '模式:', importMode, '跳过源重复:', skipSourceDuplicates, '跳过目标重复:', skipTargetDuplicates);
    return client.post('/import/start', {
        source_path: sourcePath,
        target_path: targetPath,
        import_mode: importMode,
        skip_source_duplicates: skipSourceDuplicates,
        skip_target_duplicates: skipTargetDuplicates,
    }).then(data => {
        console.log('[API] ✅ 导入已启动:', data);
        return data;
    }).catch(error => {
        console.error('[API] ❌ 导入启动失败:', error);
        throw error;
    });
}

/**
 * 获取导入进度
 * @param {string} importId - 导入ID
 * @returns {Promise<object>} 进度数据
 */
export function getImportProgress(importId) {
    console.log('[API] 获取进度，导入 ID:', importId);
    return client.get(`/import/progress/${importId}`).then(data => {
        console.log('[API] ✅ 进度数据:', data);
        return data;
    }).catch(error => {
        console.error('[API] ❌ 获取进度失败:', error);
        throw error;
    });
}

/**
 * 取消导入
 * @param {string} importId - 导入ID
 * @returns {Promise<object>} 取消结果
 */
export function cancelImport(importId) {
    console.log('[API] 取消导入，导入 ID:', importId);
    return client.post(`/import/cancel/${importId}`, {}).then(data => {
        console.log('[API] ✅ 导入已取消:', data);
        return data;
    }).catch(error => {
        console.error('[API] ❌ 取消导入失败:', error);
        throw error;
    });
}

/**
 * 暂停导入
 * @param {string} importId - 导入ID
 * @returns {Promise<object>} 暂停结果
 */
export function pauseImport(importId) {
    console.log('[API] 暂停导入，导入 ID:', importId);
    return client.post(`/import/pause/${importId}`, {}).then(data => {
        console.log('[API] ✅ 导入已暂停:', data);
        return data;
    }).catch(error => {
        console.error('[API] ❌ 暂停导入失败:', error);
        throw error;
    });
}

/**
 * 继续导入
 * @param {string} importId - 导入ID
 * @returns {Promise<object>} 继续结果
 */
export function resumeImport(importId) {
    console.log('[API] 继续导入，导入 ID:', importId);
    return client.post(`/import/resume/${importId}`, {}).then(data => {
        console.log('[API] ✅ 导入已继续:', data);
        return data;
    }).catch(error => {
        console.error('[API] ❌ 继续导入失败:', error);
        throw error;
    });
}
