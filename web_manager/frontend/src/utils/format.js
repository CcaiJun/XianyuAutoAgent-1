/**
 * 格式化工具函数
 * 
 * 提供各种数据格式化功能，如时间、数字、文件大小等
 * 
 * Author: AI Assistant
 * Created: 2024-01-XX
 */

/**
 * 格式化日期时间
 * @param {Date|string|number} date - 日期对象、时间戳或日期字符串
 * @param {string} format - 格式模板，默认 'YYYY-MM-DD HH:mm:ss'
 * @returns {string} 格式化后的日期时间字符串
 */
export function formatDateTime(date, format = 'YYYY-MM-DD HH:mm:ss') {
  const d = new Date(date)
  
  if (isNaN(d.getTime())) {
    return '无效日期'
  }
  
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')
  
  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 * @param {number} decimals - 小数位数，默认2位
 * @returns {string} 格式化后的文件大小
 */
export function formatFileSize(bytes, decimals = 2) {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB']
  
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}

/**
 * 格式化运行时长
 * @param {number} seconds - 秒数
 * @returns {string} 格式化后的运行时长
 */
export function formatUptime(seconds) {
  if (!seconds || seconds < 0) return '0秒'
  
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  const parts = []
  
  if (days > 0) parts.push(`${days}天`)
  if (hours > 0) parts.push(`${hours}时`)
  if (minutes > 0) parts.push(`${minutes}分`)
  if (secs > 0 || parts.length === 0) parts.push(`${secs}秒`)
  
  return parts.join('')
}

/**
 * 格式化百分比
 * @param {number} value - 数值
 * @param {number} total - 总数
 * @param {number} decimals - 小数位数，默认1位
 * @returns {string} 百分比字符串
 */
export function formatPercentage(value, total, decimals = 1) {
  if (!total || total === 0) return '0%'
  
  const percentage = (value / total) * 100
  return `${percentage.toFixed(decimals)}%`
}

/**
 * 格式化数字，添加千分位分隔符
 * @param {number} number - 数字
 * @returns {string} 格式化后的数字字符串
 */
export function formatNumber(number) {
  if (isNaN(number)) return '0'
  
  return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

/**
 * 格式化内存大小（专用于内存显示）
 * @param {number} bytes - 字节数
 * @returns {string} 格式化后的内存大小
 */
export function formatMemory(bytes) {
  if (!bytes || bytes === 0) return '0 MB'
  
  const mb = bytes / (1024 * 1024)
  
  if (mb < 1024) {
    return `${mb.toFixed(1)} MB`
  } else {
    const gb = mb / 1024
    return `${gb.toFixed(2)} GB`
  }
}

/**
 * 格式化CPU使用率
 * @param {number} percentage - CPU使用率百分比
 * @returns {string} 格式化后的CPU使用率
 */
export function formatCpuUsage(percentage) {
  if (isNaN(percentage) || percentage < 0) return '0.0%'
  
  return `${percentage.toFixed(1)}%`
}

/**
 * 格式化相对时间（如：2分钟前）
 * @param {Date|string|number} date - 日期
 * @returns {string} 相对时间字符串
 */
export function formatRelativeTime(date) {
  const now = new Date()
  const target = new Date(date)
  const diffMs = now.getTime() - target.getTime()
  const diffSeconds = Math.floor(diffMs / 1000)
  
  if (diffSeconds < 60) {
    return `${diffSeconds}秒前`
  } else if (diffSeconds < 3600) {
    const minutes = Math.floor(diffSeconds / 60)
    return `${minutes}分钟前`
  } else if (diffSeconds < 86400) {
    const hours = Math.floor(diffSeconds / 3600)
    return `${hours}小时前`
  } else {
    const days = Math.floor(diffSeconds / 86400)
    return `${days}天前`
  }
} 