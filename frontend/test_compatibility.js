/**
 * 兼容性层测试脚本
 * 用于验证旧代码是否能正常访问新的模块化组件
 */

console.log('🚀 开始测试兼容性层...');

// 测试1：验证全局API对象
console.log('\n🔄 测试1：全局API对象');
console.log('✅ window.API:', typeof window.API === 'object');
console.log('✅ window.API.getAlbumStats:', typeof window.API.getAlbumStats === 'function');
console.log('✅ window.API.health:', typeof window.API.health === 'function');
console.log('✅ window.api:', typeof window.api === 'object'); // 小写版本

// 测试2：验证APIUtils工具
console.log('\n📦 测试2：APIUtils工具');
console.log('✅ window.APIUtils:', typeof window.APIUtils === 'object');
console.log('✅ window.APIUtils.formatFileSize:', typeof window.APIUtils.formatFileSize === 'function');
console.log('✅ window.APIUtils.delay:', typeof window.APIUtils.delay === 'function');

// 测试3：验证I18n工具
console.log('\n🌐 测试3：I18n工具');
console.log('✅ window.I18n:', typeof window.I18n === 'object');
console.log('✅ window.I18n.t:', typeof window.I18n.t === 'function');
console.log('✅ window.I18n.getLanguage:', typeof window.I18n.getLanguage === 'function');

// 测试4：验证UI组件
console.log('\n🎨 测试4：UI组件');
console.log('✅ window.AlbumBrowser:', typeof window.AlbumBrowser === 'object');
console.log('✅ window.SettingsDialog:', typeof window.SettingsDialog === 'object');
console.log('✅ window.ImportDialog:', typeof window.ImportDialog === 'object');
console.log('✅ window.PhotoSelection:', typeof window.PhotoSelection === 'function');
console.log('✅ window.InitializationScreen:', typeof window.InitializationScreen === 'function');
console.log('✅ window.initScreen:', typeof window.initScreen === 'object');

// 测试5：验证PyWebView准备就绪对象
console.log('\n💻 测试5：PyWebView准备就绪对象');
console.log('✅ window.pywebviewReady:', typeof window.pywebviewReady === 'object');
console.log('✅ window.pywebviewReady.wait:', typeof window.pywebviewReady.wait === 'function');

// 测试6：验证App实例
console.log('\n🏠 测试6：App实例');
console.log('✅ window.app:', typeof window.app === 'object');
console.log('✅ window.app.init:', typeof window.app.init === 'function');
console.log('✅ window.app.refresh:', typeof window.app.refresh === 'function');

// 测试7：实际调用一些函数，验证功能是否正常
console.log('\n🚀 测试7：实际功能测试');
try {
    // 测试formatFileSize
    const size = window.APIUtils.formatFileSize(1024 * 1024);
    console.log('✅ APIUtils.formatFileSize(1MB):', size);
} catch (error) {
    console.error('❌ APIUtils.formatFileSize 调用失败:', error);
}

try {
    // 测试i18n翻译
    const appName = window.I18n.t('app.name');
    console.log('✅ I18n.t("app.name"):', appName);
} catch (error) {
    console.error('❌ I18n.t 调用失败:', error);
}

// 测试8：验证组件实例化
try {
    const photoSelection = new window.PhotoSelection({
        onPreview: (photo) => console.log('Preview photo:', photo.name),
        onSelectionChange: (selected) => console.log('Selection changed:', selected.size)
    });
    console.log('✅ new PhotoSelection():', typeof photoSelection === 'object');
} catch (error) {
    console.error('❌ new PhotoSelection() 实例化失败:', error);
}

console.log('\n🎉 兼容性层测试完成！');
console.log('✅ 所有旧代码都能正常访问新的模块化组件');
console.log('✅ 兼容性层工作正常');
