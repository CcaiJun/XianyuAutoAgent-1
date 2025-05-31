<template>
  <div class="log-viewer">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>实时日志</span>
          <div>
            <el-button @click="clearLogs" type="warning">
              清空日志
            </el-button>
            <el-button @click="toggleAutoScroll" :type="autoScroll ? 'success' : 'info'">
              {{ autoScroll ? '关闭自动滚动' : '开启自动滚动' }}
            </el-button>
          </div>
        </div>
      </template>
      
      <div class="log-container" ref="logContainer">
        <div 
          v-for="(log, index) in processStore.logs" 
          :key="index"
          :class="['log-entry', getLogLevelClass(log.level)]"
        >
          <span class="log-time">{{ formatTime(log.timestamp) }}</span>
          <span class="log-level">{{ log.level }}</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
        
        <div v-if="processStore.logs.length === 0" class="no-logs">
          暂无日志数据
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import { useProcessStore } from '../stores/process'
import { ElMessage } from 'element-plus'

const processStore = useProcessStore()
const logContainer = ref(null)
const autoScroll = ref(true)

const clearLogs = () => {
  processStore.clearLogs()
  ElMessage.success('日志已清空')
}

const toggleAutoScroll = () => {
  autoScroll.value = !autoScroll.value
  ElMessage.info(`自动滚动已${autoScroll.value ? '开启' : '关闭'}`)
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleString()
}

const getLogLevelClass = (level) => {
  switch (level?.toUpperCase()) {
    case 'ERROR':
      return 'log-error'
    case 'WARNING':
    case 'WARN':
      return 'log-warning'
    case 'INFO':
      return 'log-info'
    case 'DEBUG':
      return 'log-debug'
    default:
      return 'log-default'
  }
}

const scrollToBottom = () => {
  if (autoScroll.value && logContainer.value) {
    nextTick(() => {
      logContainer.value.scrollTop = logContainer.value.scrollHeight
    })
  }
}

// 监听日志变化，自动滚动到底部
watch(
  () => processStore.logs.length,
  () => {
    scrollToBottom()
  }
)

// 模拟添加一些日志数据
processStore.addLog({
  timestamp: Date.now(),
  level: 'INFO',
  message: 'Web管理器启动完成'
})
</script>

<style scoped>
.log-viewer {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.log-container {
  height: 600px;
  overflow-y: auto;
  background-color: #1e1e1e;
  color: #ffffff;
  padding: 15px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
}

.log-entry {
  margin-bottom: 5px;
  display: flex;
  align-items: center;
}

.log-time {
  color: #888;
  margin-right: 10px;
  min-width: 150px;
}

.log-level {
  margin-right: 10px;
  min-width: 60px;
  font-weight: bold;
}

.log-message {
  flex: 1;
  word-break: break-all;
}

.log-error .log-level {
  color: #f56565;
}

.log-warning .log-level {
  color: #ed8936;
}

.log-info .log-level {
  color: #4299e1;
}

.log-debug .log-level {
  color: #48bb78;
}

.log-default .log-level {
  color: #a0aec0;
}

.no-logs {
  text-align: center;
  color: #888;
  padding: 50px 0;
}
</style> 