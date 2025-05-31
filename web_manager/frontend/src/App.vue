<template>
  <div id="app">
    <!-- 顶部导航栏 -->
    <el-header class="app-header">
      <div class="header-content">
        <!-- Logo和标题 -->
        <div class="logo-section">
          <el-icon size="32" color="#409EFF">
            <Monitor />
          </el-icon>
          <h1 class="app-title">XianyuAutoAgent 管理中心</h1>
        </div>

        <!-- 状态指示器 -->
        <div class="status-section">
          <el-tag 
            :type="processStatus.is_running ? 'success' : 'danger'" 
            size="large"
            class="status-tag"
          >
            <el-icon class="status-icon">
              <CircleCheck v-if="processStatus.is_running" />
              <CircleClose v-else />
            </el-icon>
            {{ processStatus.is_running ? '运行中' : '已停止' }}
          </el-tag>
        </div>

        <!-- 操作按钮 -->
        <div class="action-section">
          <el-button 
            type="primary" 
            :icon="Refresh" 
            @click="refreshStatus"
            :loading="refreshing"
          >
            刷新状态
          </el-button>
        </div>
      </div>
    </el-header>

    <!-- 主要内容区域 -->
    <el-container class="main-container">
      <!-- 侧边栏导航 -->
      <el-aside width="220px" class="sidebar">
        <el-menu
          :default-active="$route.path"
          router
          class="sidebar-menu"
          background-color="#f5f7fa"
          text-color="#303133"
          active-text-color="#409EFF"
        >
          <!-- 仪表盘 -->
          <el-menu-item index="/dashboard">
            <el-icon><Odometer /></el-icon>
            <span>仪表盘</span>
          </el-menu-item>

          <!-- 进程控制 -->
          <el-menu-item index="/process">
            <el-icon><Setting /></el-icon>
            <span>进程控制</span>
          </el-menu-item>

          <!-- 实时日志 -->
          <el-menu-item index="/logs">
            <el-icon><Document /></el-icon>
            <span>实时日志</span>
          </el-menu-item>

          <!-- 配置管理 -->
          <el-menu-item index="/config">
            <el-icon><Tools /></el-icon>
            <span>配置管理</span>
          </el-menu-item>

          <!-- 提示词管理 -->
          <el-menu-item index="/prompts">
            <el-icon><Edit /></el-icon>
            <span>提示词管理</span>
          </el-menu-item>

          <!-- 系统信息 -->
          <el-menu-item index="/system">
            <el-icon><Monitor /></el-icon>
            <span>系统信息</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区域 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>

    <!-- 底部状态栏 -->
    <el-footer height="50px" class="app-footer">
      <div class="footer-content">
        <span class="footer-text">
          XianyuAutoAgent Web管理器 v1.0.0 | 
          {{ currentTime }} |
          PID: {{ processStatus.pid || 'N/A' }}
        </span>
      </div>
    </el-footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Monitor,
  Odometer,
  Setting,
  Document,
  Tools,
  Edit,
  CircleCheck,
  CircleClose,
  Refresh
} from '@element-plus/icons-vue'
import { useProcessStore } from './stores/process'
import { formatDateTime } from './utils/format'

// 使用状态管理
const processStore = useProcessStore()
const router = useRouter()

// 响应式数据
const currentTime = ref('')
const refreshing = ref(false)
const processStatus = ref({
  is_running: false,
  pid: null,
  status: '未知'
})

// 定时器
let timeTimer = null
let statusTimer = null

/**
 * 刷新进程状态
 */
const refreshStatus = async () => {
  refreshing.value = true
  
  try {
    const status = await processStore.getStatus()
    processStatus.value = status
  } catch (error) {
    ElMessage.error(`获取进程状态失败: ${error.message}`)
  } finally {
    refreshing.value = false
  }
}

/**
 * 更新当前时间
 */
const updateTime = () => {
  currentTime.value = formatDateTime(new Date())
}

/**
 * 初始化应用
 */
const initApp = async () => {
  // 更新时间
  updateTime()
  timeTimer = setInterval(updateTime, 1000)

  // 初始化进程状态
  await refreshStatus()
  
  // 定期更新状态
  statusTimer = setInterval(refreshStatus, 5000)

  // 如果当前路径是根路径，重定向到仪表盘
  if (router.currentRoute.value.path === '/') {
    router.push('/dashboard')
  }
}

/**
 * 清理资源
 */
const cleanup = () => {
  if (timeTimer) {
    clearInterval(timeTimer)
    timeTimer = null
  }
  
  if (statusTimer) {
    clearInterval(statusTimer)
    statusTimer = null
  }
}

// 生命周期钩子
onMounted(initApp)
onUnmounted(cleanup)
</script>

<style scoped>
/* 全局样式 */
#app {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f0f2f5;
}

/* 顶部导航栏样式 */
.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.header-content {
  height: 100%;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.app-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: white;
}

.status-section {
  flex: 1;
  display: flex;
  justify-content: center;
}

.status-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
}

.status-icon {
  font-size: 16px;
}

.action-section {
  display: flex;
  gap: 10px;
}

/* 主容器样式 */
.main-container {
  flex: 1;
  height: calc(100vh - 110px);
}

/* 侧边栏样式 */
.sidebar {
  background-color: #f5f7fa;
  border-right: 1px solid #e4e7ed;
  box-shadow: 2px 0 6px rgba(0, 0, 0, 0.04);
}

.sidebar-menu {
  border: none;
  padding: 10px 0;
}

.sidebar-menu .el-menu-item {
  height: 50px;
  line-height: 50px;
  margin: 2px 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.sidebar-menu .el-menu-item:hover {
  background-color: #ecf5ff;
  color: #409EFF;
}

.sidebar-menu .el-menu-item.is-active {
  background-color: #409EFF;
  color: white;
}

.sidebar-menu .el-menu-item.is-active .el-icon {
  color: white;
}

/* 主内容区域样式 */
.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

/* 底部状态栏样式 */
.app-footer {
  background-color: #ffffff;
  border-top: 1px solid #e4e7ed;
  box-shadow: 0 -2px 6px rgba(0, 0, 0, 0.04);
}

.footer-content {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 20px;
}

.footer-text {
  color: #606266;
  font-size: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    padding: 0 10px;
  }
  
  .app-title {
    font-size: 16px;
  }
  
  .sidebar {
    width: 180px !important;
  }
  
  .main-content {
    padding: 10px;
  }
}
</style> 