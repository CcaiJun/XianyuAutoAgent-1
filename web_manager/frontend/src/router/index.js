import { createRouter, createWebHistory } from 'vue-router'

// 路由配置
const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue')
  },
  {
    path: '/process',
    name: 'ProcessManagement',
    component: () => import('../views/ProcessManagement.vue')
  },
  {
    path: '/config',
    name: 'ConfigManagement', 
    component: () => import('../views/ConfigManagement.vue')
  },
  {
    path: '/prompts',
    name: 'PromptManagement',
    component: () => import('../views/PromptManagement.vue')
  },
  {
    path: '/logs',
    name: 'LogViewer',
    component: () => import('../views/LogViewer.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 