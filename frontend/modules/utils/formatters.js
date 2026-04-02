/**
 * 格式化工具模块
 * 提供各种数据格式化函数
 */

/**
 * 格式化文件大小
 * @param {number} bytes - 文件大小（字节）
 * @returns {string} 格式化后的文件大小
 */
export function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

/**
 * 格式化日期时间
 * @param {string|Date} dateString - 日期字符串或Date对象
 * @returns {string} 格式化后的日期时间
 */
export function formatDateTime(dateString) {
    if (!dateString) return '-';
    try {
        const date = new Date(dateString);
        return date.toLocaleString('zh-CN');
    } catch (e) {
        return dateString;
    }
}

/**
 * 格式化日期
 * @param {string|Date} dateString - 日期字符串或Date对象
 * @returns {string} 格式化后的日期
 */
export function formatDate(dateString) {
    if (!dateString) return '-';
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('zh-CN');
    } catch (e) {
        return dateString;
    }
}
