<template>
  <div class="process-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>进程管理</span>
          <el-button 
            :type="processStore.isRunning ? 'danger' : 'primary'"
            @click="toggleProcess"
            :loading="loading"
          >
            {{ processStore.isRunning ? '停止进程' : '启动进程' }}
          </el-button>
        </div>
      </template>
      
      <div class="process-info">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="运行状态">
            <el-tag :type="processStore.statusType">
              {{ processStore.statusText }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="进程ID">
            {{ processStore.processInfo?.pid || 'N/A' }}
          </el-descriptions-item>
          <el-descriptions-item label="CPU使用率">
            {{ processStore.systemStats.cpu }}%
          </el-descriptions-item>
          <el-descriptions-item label="内存使用">
            {{ processStore.systemStats.memory }}MB
          </el-descriptions-item>
          <el-descriptions-item label="运行时长">
            {{ formatUptime(processStore.systemStats.uptime) }}
          </el-descriptions-item>
          <el-descriptions-item label="启动时间">
            {{ processStore.processInfo?.start_time || 'N/A' }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="action-buttons" style="margin-top: 20px;">
          <el-space>
            <el-button 
              type="info" 
              @click="refreshStatus"
              :loading="refreshing"
            >
              刷新状态
            </el-button>
            <el-button 
              type="warning" 
              @click="restartProcess"
              :loading="restarting"
              :disabled="!processStore.isRunning"
            >
              重启进程
            </el-button>
          </el-space>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useProcessStore } from '../stores/process'
import { ElMessage } from 'element-plus'

const processStore = useProcessStore()
const loading = ref(false)
const refreshing = ref(false)
const restarting = ref(false)

const toggleProcess = async () => {
  loading.value = true
  try {
    let result
    
    if (processStore.isRunning) {
      result = await processStore.stopProcess()
    } else {
      result = await processStore.startProcess()
    }
    
    if (result.success) {
      ElMessage.success(result.message)
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error('操作失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const refreshStatus = async () => {
  refreshing.value = true
  try {
    await processStore.getStatus()
    ElMessage.success('状态刷新成功')
  } catch (error) {
    ElMessage.error('刷新状态失败: ' + error.message)
  } finally {
    refreshing.value = false
  }
}

const restartProcess = async () => {
  restarting.value = true
  try {
    const result = await processStore.restartProcess()
    
    if (result.success) {
      ElMessage.success(result.message)
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error('重启失败: ' + error.message)
  } finally {
    restarting.value = false
  }
}

const formatUptime = (seconds) => {
  if (!seconds) return '0秒'
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  
  return `${hours}时${minutes}分${secs}秒`
}

// 页面加载时获取状态
onMounted(() => {
  refreshStatus()
})
</script>

<style scoped>
.process-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.process-info {
  margin-top: 20px;
}

.action-buttons {
  text-align: center;
}
</style> 