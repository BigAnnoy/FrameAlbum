/**
 * API get() 方法测试
 * 验证查询参数正确构建
 */

// 测试用例
const testCases = [
    {
        name: '简单参数',
        endpoint: '/album/photos',
        params: { path: '/home/user/album' },
        expected: '/album/photos?path=%2Fhome%2Fuser%2Falbum'
    },
    {
        name: '多个参数',
        endpoint: '/search',
        params: { q: 'test', limit: 10, offset: 20 },
        expected: '/search?q=test&limit=10&offset=20'
    },
    {
        name: '空参数',
        endpoint: '/list',
        params: {},
        expected: '/list'
    },
    {
        name: '包含空值参数（应被过滤）',
        endpoint: '/list',
        params: { a: 'value', b: null, c: undefined, d: '' },
        expected: '/list?a=value&d='
    },
];

// 测试函数
function buildQueryString(endpoint, params = {}) {
    const queryString = Object.entries(params)
        .filter(([_, value]) => value !== null && value !== undefined)
        .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`)
        .join('&');
    
    return queryString ? `${endpoint}?${queryString}` : endpoint;
}

// 运行测试
console.log('🧪 API get() 查询参数构建测试\n');
testCases.forEach(testCase => {
    const result = buildQueryString(testCase.endpoint, testCase.params);
    const passed = result === testCase.expected;
    const icon = passed ? '✅' : '❌';
    
    console.log(`${icon} ${testCase.name}`);
    console.log(`   输入: ${JSON.stringify(testCase.params)}`);
    console.log(`   预期: ${testCase.expected}`);
    console.log(`   实际: ${result}`);
    if (!passed) {
        console.log(`   ❌ 不匹配！`);
    }
    console.log('');
});
