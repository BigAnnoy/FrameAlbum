/**
 * API 客户端模块
 * 提供统一的 API 调用接口，处理错误和日志
 */

const BASE_URL = 'http://127.0.0.1:5000/api';

/**
 * 发送 HTTP 请求
 * @param {string} endpoint - API 端点
 * @param {object} options - 请求选项
 * @returns {Promise<object>} 响应数据
 */
async function request(endpoint, options = {}) {
    const url = `${BASE_URL}${endpoint}`;
    const method = options.method || 'GET';
    console.log(`[API] 📤 发送请求: ${method} ${endpoint}`, { url });
    
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
        ...options,
    };

    try {
        console.log(`[API] ⏳ 等待响应...`);
        const response = await fetch(url, config);
        console.log(`[API] 📥 收到响应: ${response.status} ${response.statusText}`);
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            const errorMsg = error.error || `HTTP ${response.status}`;
            console.error(`[API] ❌ 请求失败: ${errorMsg}`);
            throw new Error(errorMsg);
        }
        
        const data = await response.json();
        console.log(`[API] ✅ 响应成功`, data);
        return data;
    } catch (error) {
        console.error(`[API] ❌ 请求异常 [${method} ${endpoint}]:`, error.message);
        console.error(`[API] 错误详情:`, error);
        throw error;
    }
}

/**
 * GET 请求
 * @param {string} endpoint - API 端点
 * @param {object} params - 查询参数
 * @param {object} options - HTTP 选项
 * @returns {Promise<object>} 响应数据
 */
export function get(endpoint, params = {}, options = {}) {
    const queryString = Object.entries(params)
        .filter(([_, value]) => value !== null && value !== undefined)
        .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`)
        .join('&');
    
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    
    return request(url, {
        ...options,
        method: 'GET',
    });
}

/**
 * POST 请求
 * @param {string} endpoint - API 端点
 * @param {object} data - 请求数据
 * @param {object} options - HTTP 选项
 * @returns {Promise<object>} 响应数据
 */
export function post(endpoint, data, options = {}) {
    return request(endpoint, {
        ...options,
        method: 'POST',
        body: JSON.stringify(data),
    });
}

/**
 * PUT 请求
 * @param {string} endpoint - API 端点
 * @param {object} data - 请求数据
 * @param {object} options - HTTP 选项
 * @returns {Promise<object>} 响应数据
 */
export function put(endpoint, data, options = {}) {
    return request(endpoint, {
        ...options,
        method: 'PUT',
        body: JSON.stringify(data),
    });
}

/**
 * DELETE 请求
 * @param {string} endpoint - API 端点
 * @param {object} options - HTTP 选项
 * @returns {Promise<object>} 响应数据
 */
export function del(endpoint, options = {}) {
    return request(endpoint, {
        ...options,
        method: 'DELETE',
    });
}
