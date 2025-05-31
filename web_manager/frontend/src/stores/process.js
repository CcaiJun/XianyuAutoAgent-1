import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

// 配置axios基础URL
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000
})

export const useProcessStore = defineStore('process', () => {
  // 状态
  const isRunning = ref(false)
  const processInfo = ref(null)
  const logs = ref([])
  const systemStats = ref({
    cpu: 0,
    memory: 0,
    uptime: 0
  })

  // 计算属性
  const statusText = computed(() => {
    return isRunning.value ? '运行中' : '已停止'
  })

  const statusType = computed(() => {
    return isRunning.value ? 'success' : 'danger'
  })

  // API交互方法
  
  /**
   * 获取进程状态
   */
  const getStatus = async () => {
    try {
      const response = await api.get('/api/process/status')
      const data = response.data
      
      // 更新状态
      isRunning.value = data.is_running || false
      processInfo.value = data.process_info || null
      systemStats.value = {
        cpu: data.cpu_usage || 0,
        memory: data.memory_usage || 0,
        uptime: data.uptime || 0
      }
      
      return {
        is_running: isRunning.value,
        pid: processInfo.value?.pid || null,
        status: statusText.value
      }
    } catch (error) {
      console.error('获取进程状态失败:', error)
      
      // 返回默认状态
      return {
        is_running: false,
        pid: null,
        status: '获取失败'
      }
    }
  }

  /**
   * 启动进程
   */
  const startProcess = async () => {
    try {
      const response = await api.post('/api/process/start')
      const data = response.data
      
      if (data.success) {
        isRunning.value = true
        processInfo.value = data.process_info || null
        return { success: true, message: data.message }
      } else {
        return { success: false, message: data.message || '启动失败' }
      }
    } catch (error) {
      console.error('启动进程失败:', error)
      return { 
        success: false, 
        message: error.response?.data?.detail || '启动进程时发生错误' 
      }
    }
  }

  /**
   * 停止进程
   */
  const stopProcess = async () => {
    try {
      const response = await api.post('/api/process/stop')
      const data = response.data
      
      if (data.success) {
        isRunning.value = false
        processInfo.value = null
        return { success: true, message: data.message }
      } else {
        return { success: false, message: data.message || '停止失败' }
      }
    } catch (error) {
      console.error('停止进程失败:', error)
      return { 
        success: false, 
        message: error.response?.data?.detail || '停止进程时发生错误' 
      }
    }
  }

  /**
   * 重启进程
   */
  const restartProcess = async () => {
    try {
      const response = await api.post('/api/process/restart')
      const data = response.data
      
      if (data.success) {
        isRunning.value = true
        processInfo.value = data.process_info || null
        return { success: true, message: data.message }
      } else {
        return { success: false, message: data.message || '重启失败' }
      }
    } catch (error) {
      console.error('重启进程失败:', error)
      return { 
        success: false, 
        message: error.response?.data?.detail || '重启进程时发生错误' 
      }
    }
  }

  /**
   * 获取系统统计信息
   */
  const getSystemStats = async () => {
    try {
      const response = await api.get('/api/system/stats')
      const data = response.data
      
      systemStats.value = {
        cpu: data.cpu_usage || 0,
        memory: data.memory_usage || 0,
        uptime: data.uptime || 0
      }
      
      return systemStats.value
    } catch (error) {
      console.error('获取系统统计失败:', error)
      return systemStats.value
    }
  }

  // 本地状态管理方法
  const updateStatus = (status) => {
    isRunning.value = status
  }

  const updateProcessInfo = (info) => {
    processInfo.value = info
  }

  const addLog = (logEntry) => {
    logs.value.push(logEntry)
    // 保持最新的1000条日志
    if (logs.value.length > 1000) {
      logs.value = logs.value.slice(-1000)
    }
  }

  const clearLogs = () => {
    logs.value = []
  }

  const updateSystemStats = (stats) => {
    systemStats.value = stats
  }

  return {
    // 状态
    isRunning,
    processInfo,
    logs,
    systemStats,
    // 计算属性
    statusText,
    statusType,
    // API方法
    getStatus,
    startProcess,
    stopProcess,
    restartProcess,
    getSystemStats,
    // 本地方法
    updateStatus,
    updateProcessInfo,
    addLog,
    clearLogs,
    updateSystemStats
  }
}) 