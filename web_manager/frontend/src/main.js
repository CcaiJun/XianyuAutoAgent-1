/**
 * Vue.js 主应用入口文件
 * 
 * 配置和启动XianyuAutoAgent Web管理界面的前端应用
 * 
 * 技术栈：
 * - Vue 3 + Composition API
 * - Element Plus UI组件库
 * - Pinia状态管理
 * - Vue Router路由管理
 * 
 * Author: AI Assistant
 * Created: 2024-01-XX
 * Version: 1.0.0
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

import App from './App.vue'
import router from './router'

// 创建Vue应用实例
const app = createApp(App)

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 安装插件和配置
app.use(createPinia())  // 状态管理
app.use(router)         // 路由管理
app.use(ElementPlus, {  // UI组件库
  locale: zhCn,         // 中文语言包
})

// 挂载应用
app.mount('#app') 