/**
 * 咸鱼AI客服系统 - Web前端主要JavaScript文件
 * 
 * 功能:
 * - WebSocket连接管理
 * - 实时日志显示
 * - 用户交互控制
 * - 日志过滤和展示
 */

class XianyuLogViewer {
    /**
     * 构造函数 - 初始化日志查看器
     */
    constructor() {
        // WebSocket相关
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectInterval = 3000; // 3秒
        
        // 应用状态
        this.isPaused = false;
        this.autoScroll = true;
        this.logCount = 0;
        this.maxLogEntries = 1000; // 最大日志条目数
        
        // 过滤器状态
        this.filters = {
            info: true,
            warning: true,
            error: true,
            debug: false
        };
        
        // DOM元素引用
        this.elements = {
            logContent: document.getElementById('logContent'),
            statusIndicator: document.getElementById('statusIndicator'),
            statusText: document.getElementById('statusText'),
            clientCount: document.getElementById('clientCount'),
            logCount: document.getElementById('logCount'),
            logFileInfo: document.getElementById('logFileInfo'),
            lastUpdateTime: document.getElementById('lastUpdateTime'),
            serverStatus: document.getElementById('serverStatus'),
            pauseBtn: document.getElementById('pauseBtn'),
            pauseIcon: document.getElementById('pauseIcon'),
            pauseText: document.getElementById('pauseText'),
            autoScrollCheckbox: document.getElementById('autoScroll'),
            toast: document.getElementById('toast'),
            toastIcon: document.getElementById('toastIcon'),
            toastMessage: document.getElementById('toastMessage')
        };
        
        // 初始化
        this.init();
    }
    
    /**
     * 初始化应用
     */
    init() {
        console.log('初始化咸鱼AI客服日志查看器...');
        
        // 连接WebSocket
        this.connectWebSocket();
        
        // 绑定事件监听器
        this.bindEventListeners();
        
        // 初始化过滤器状态
        this.updateFilterState();
        
        // 定期检查服务器状态
        this.startStatusCheck();
        
        console.log('日志查看器初始化完成');
    }
    
    /**
     * 连接WebSocket
     */
    connectWebSocket() {
        try {
            console.log('正在连接WebSocket服务器...');
            this.updateConnectionStatus('connecting', '连接中...');
            
            // 创建Socket.IO连接
            this.socket = io('/logs', {
                transports: ['websocket', 'polling'],
                upgrade: true,
                rememberUpgrade: true,
                timeout: 10000
            });
            
            // 注册Socket.IO事件处理器
            this.registerSocketEvents();
            
        } catch (error) {
            console.error('WebSocket连接失败:', error);
            this.updateConnectionStatus('disconnected', '连接失败');
            this.scheduleReconnect();
        }
    }
    
    /**
     * 注册Socket.IO事件处理器
     */
    registerSocketEvents() {
        // 连接成功
        this.socket.on('connect', () => {
            console.log('WebSocket连接成功');
            this.updateConnectionStatus('connected', '已连接');
            this.reconnectAttempts = 0;
            this.showToast('success', '✅ 已连接到日志监控服务');
            
            // 请求加载历史日志
            this.requestLogHistory(50);
        });
        
        // 连接断开
        this.socket.on('disconnect', (reason) => {
            console.log('WebSocket连接断开:', reason);
            this.updateConnectionStatus('disconnected', '连接断开');
            this.showToast('warning', '⚠️ 连接已断开，尝试重连中...');
            this.scheduleReconnect();
        });
        
        // 接收新日志
        this.socket.on('new_log', (logData) => {
            if (!this.isPaused) {
                this.addLogEntry(logData);
            }
        });
        
        // 连接状态更新
        this.socket.on('connection_status', (data) => {
            console.log('连接状态更新:', data);
            if (data.status === 'connected') {
                this.updateLastUpdateTime();
            }
        });
        
        // 服务器状态更新
        this.socket.on('status_update', (data) => {
            this.updateServerStatus(data);
        });
        
        // 清空日志命令
        this.socket.on('clear_logs', () => {
            this.clearLogDisplay();
            this.showToast('info', 'ℹ️ 日志已被管理员清空');
        });
        
        // 历史日志加载完成
        this.socket.on('log_history_loaded', (data) => {
            if (data.status === 'success') {
                console.log(`历史日志加载完成: ${data.lines_count} 条`);
                this.showToast('info', `📋 已加载 ${data.lines_count} 条历史日志`);
            } else {
                console.error('历史日志加载失败:', data.error);
                this.showToast('error', '❌ 历史日志加载失败');
            }
        });
        
        // 心跳响应
        this.socket.on('pong', (data) => {
            console.log('收到服务器心跳响应:', data.timestamp);
        });
        
        // 连接错误
        this.socket.on('connect_error', (error) => {
            console.error('WebSocket连接错误:', error);
            this.updateConnectionStatus('disconnected', '连接错误');
            this.scheduleReconnect();
        });
    }
    
    /**
     * 绑定事件监听器
     */
    bindEventListeners() {
        // 自动滚动复选框
        if (this.elements.autoScrollCheckbox) {
            this.elements.autoScrollCheckbox.addEventListener('change', (e) => {
                this.autoScroll = e.target.checked;
                console.log('自动滚动:', this.autoScroll ? '启用' : '禁用');
            });
        }
        
        // 窗口失焦/聚焦事件
        window.addEventListener('blur', () => {
            console.log('窗口失去焦点');
        });
        
        window.addEventListener('focus', () => {
            console.log('窗口获得焦点');
            this.updateLastUpdateTime();
        });
        
        // 窗口关闭前清理
        window.addEventListener('beforeunload', () => {
            if (this.socket) {
                this.socket.disconnect();
            }
        });
    }
    
    /**
     * 添加日志条目到显示区域
     * 
     * @param {Object} logData - 日志数据对象
     */
    addLogEntry(logData) {
        try {
            // 检查是否应该显示此日志级别
            if (!this.shouldShowLogLevel(logData.level)) {
                return;
            }
            
            // 创建日志条目元素
            const logEntry = this.createLogEntryElement(logData);
            
            // 添加到日志容器
            this.elements.logContent.appendChild(logEntry);
            
            // 更新日志计数
            this.logCount++;
            this.updateLogCount();
            
            // 限制日志条目数量
            this.limitLogEntries();
            
            // 自动滚动到底部
            if (this.autoScroll) {
                this.scrollToBottom();
            }
            
            // 更新最后更新时间
            this.updateLastUpdateTime();
            
            // 移除占位符（如果存在）
            this.removePlaceholder();
            
        } catch (error) {
            console.error('添加日志条目失败:', error);
        }
    }
    
    /**
     * 创建日志条目DOM元素
     * 
     * @param {Object} logData - 日志数据
     * @returns {HTMLElement} 日志条目元素
     */
    createLogEntryElement(logData) {
        const entry = document.createElement('div');
        entry.className = `log-entry log-level-${logData.level.toLowerCase()}`;
        entry.setAttribute('data-level', logData.level.toLowerCase());
        entry.setAttribute('data-category', logData.category);
        
        // 时间戳
        const timestamp = document.createElement('span');
        timestamp.className = 'log-timestamp';
        timestamp.textContent = logData.timestamp;
        
        // 日志级别
        const level = document.createElement('span');
        level.className = `log-level ${logData.level.toLowerCase()}`;
        level.textContent = logData.level;
        
        // 日志分类
        const category = document.createElement('span');
        category.className = `log-category ${logData.category}`;
        category.textContent = this.getCategoryDisplayName(logData.category);
        
        // 日志消息
        const message = document.createElement('span');
        message.className = 'log-message';
        message.textContent = logData.message;
        
        // 组装元素
        entry.appendChild(timestamp);
        entry.appendChild(level);
        entry.appendChild(category);
        entry.appendChild(message);
        
        return entry;
    }
    
    /**
     * 获取分类显示名称
     * 
     * @param {string} category - 分类名称
     * @returns {string} 显示名称
     */
    getCategoryDisplayName(category) {
        const categoryNames = {
            'heartbeat': '心跳',
            'user_message': '用户消息',
            'bot_reply': 'AI回复',
            'manual_mode': '人工接管',
            'system': '系统',
            'error': '错误'
        };
        return categoryNames[category] || category;
    }
    
    /**
     * 检查是否应该显示指定级别的日志
     * 
     * @param {string} level - 日志级别
     * @returns {boolean} 是否显示
     */
    shouldShowLogLevel(level) {
        const levelLower = level.toLowerCase();
        return this.filters[levelLower] !== false;
    }
    
    /**
     * 限制日志条目数量
     */
    limitLogEntries() {
        const entries = this.elements.logContent.querySelectorAll('.log-entry');
        if (entries.length > this.maxLogEntries) {
            const removeCount = entries.length - this.maxLogEntries;
            for (let i = 0; i < removeCount; i++) {
                entries[i].remove();
            }
            this.logCount = this.maxLogEntries;
        }
    }
    
    /**
     * 滚动到底部
     */
    scrollToBottom() {
        if (this.elements.logContent) {
            this.elements.logContent.scrollTop = this.elements.logContent.scrollHeight;
        }
    }
    
    /**
     * 移除占位符
     */
    removePlaceholder() {
        const placeholder = this.elements.logContent.querySelector('.log-placeholder');
        if (placeholder) {
            placeholder.remove();
        }
    }
    
    /**
     * 更新连接状态
     * 
     * @param {string} status - 状态: 'connected', 'connecting', 'disconnected'
     * @param {string} text - 状态文本
     */
    updateConnectionStatus(status, text) {
        if (this.elements.statusIndicator) {
            this.elements.statusIndicator.className = `status-indicator ${status}`;
        }
        
        if (this.elements.statusText) {
            this.elements.statusText.textContent = text;
        }
    }
    
    /**
     * 更新日志计数显示
     */
    updateLogCount() {
        if (this.elements.logCount) {
            this.elements.logCount.textContent = this.logCount;
        }
    }
    
    /**
     * 更新最后更新时间
     */
    updateLastUpdateTime() {
        if (this.elements.lastUpdateTime) {
            const now = new Date();
            const timeString = now.toLocaleTimeString('zh-CN', {
                hour12: false,
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
            this.elements.lastUpdateTime.textContent = `最后更新: ${timeString}`;
        }
    }
    
    /**
     * 更新服务器状态
     * 
     * @param {Object} statusData - 状态数据
     */
    updateServerStatus(statusData) {
        if (this.elements.clientCount) {
            this.elements.clientCount.textContent = statusData.connected_clients || 0;
        }
        
        if (this.elements.serverStatus) {
            const status = statusData.log_monitoring ? '正常运行' : '监控停止';
            this.elements.serverStatus.textContent = `服务器状态: ${status}`;
        }
        
        this.updateLastUpdateTime();
    }
    
    /**
     * 显示提示消息
     * 
     * @param {string} type - 消息类型: 'success', 'warning', 'error', 'info'
     * @param {string} message - 消息内容
     */
    showToast(type, message) {
        if (!this.elements.toast) return;
        
        // 设置图标
        const icons = {
            'success': '✅',
            'warning': '⚠️',
            'error': '❌',
            'info': 'ℹ️'
        };
        
        if (this.elements.toastIcon) {
            this.elements.toastIcon.textContent = icons[type] || 'ℹ️';
        }
        
        if (this.elements.toastMessage) {
            this.elements.toastMessage.textContent = message;
        }
        
        // 设置样式类
        this.elements.toast.className = `toast ${type} show`;
        
        // 自动隐藏
        setTimeout(() => {
            this.elements.toast.classList.remove('show');
        }, 3000);
    }
    
    /**
     * 计划重连
     */
    scheduleReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.log('达到最大重连次数，停止重连');
            this.showToast('error', '❌ 连接失败，请刷新页面重试');
            return;
        }
        
        this.reconnectAttempts++;
        console.log(`第 ${this.reconnectAttempts} 次重连尝试...`);
        
        setTimeout(() => {
            this.connectWebSocket();
        }, this.reconnectInterval);
    }
    
    /**
     * 请求历史日志
     * 
     * @param {number} linesCount - 请求的日志行数
     */
    requestLogHistory(linesCount = 100) {
        if (this.socket && this.socket.connected) {
            console.log(`请求历史日志: ${linesCount} 行`);
            this.socket.emit('request_log_history', { lines_count: linesCount });
        }
    }
    
    /**
     * 开始定期状态检查
     */
    startStatusCheck() {
        setInterval(() => {
            if (this.socket && this.socket.connected) {
                // 发送心跳
                this.socket.emit('ping');
                
                // 获取服务器状态
                fetch('/api/status')
                    .then(response => response.json())
                    .then(data => {
                        this.updateServerStatus(data);
                        if (this.elements.logFileInfo) {
                            this.elements.logFileInfo.textContent = `监控文件: ${data.log_file_path || '未知'}`;
                        }
                    })
                    .catch(error => {
                        console.error('获取服务器状态失败:', error);
                    });
            }
        }, 30000); // 每30秒检查一次
    }
    
    /**
     * 更新过滤器状态
     */
    updateFilterState() {
        const filterCheckboxes = {
            'filterInfo': 'info',
            'filterWarning': 'warning',
            'filterError': 'error',
            'filterDebug': 'debug'
        };
        
        Object.entries(filterCheckboxes).forEach(([checkboxId, level]) => {
            const checkbox = document.getElementById(checkboxId);
            if (checkbox) {
                this.filters[level] = checkbox.checked;
            }
        });
        
        // 应用过滤器到现有日志
        this.applyLogFilter();
    }
    
    /**
     * 应用日志过滤器
     */
    applyLogFilter() {
        const logEntries = this.elements.logContent.querySelectorAll('.log-entry');
        
        logEntries.forEach(entry => {
            const level = entry.getAttribute('data-level');
            if (this.shouldShowLogLevel(level)) {
                entry.style.display = 'flex';
            } else {
                entry.style.display = 'none';
            }
        });
    }
    
    /**
     * 清空日志显示
     */
    clearLogDisplay() {
        if (this.elements.logContent) {
            // 移除所有日志条目
            const logEntries = this.elements.logContent.querySelectorAll('.log-entry');
            logEntries.forEach(entry => entry.remove());
            
            // 重置计数
            this.logCount = 0;
            this.updateLogCount();
            
            // 显示占位符
            this.showPlaceholder('日志已清空', '等待新的日志消息...');
        }
    }
    
    /**
     * 显示占位符
     * 
     * @param {string} title - 标题
     * @param {string} subtitle - 副标题
     */
    showPlaceholder(title, subtitle) {
        const placeholder = document.createElement('div');
        placeholder.className = 'log-placeholder';
        placeholder.innerHTML = `
            <div class="placeholder-icon">📋</div>
            <div class="placeholder-text">${title}</div>
            <div class="placeholder-subtitle">${subtitle}</div>
        `;
        this.elements.logContent.appendChild(placeholder);
    }
}

// 全局函数定义（供HTML调用）

/**
 * 切换暂停状态
 */
function togglePause() {
    if (window.logViewer) {
        window.logViewer.isPaused = !window.logViewer.isPaused;
        
        const pauseBtn = document.getElementById('pauseBtn');
        const pauseIcon = document.getElementById('pauseIcon');
        const pauseText = document.getElementById('pauseText');
        
        if (window.logViewer.isPaused) {
            pauseIcon.textContent = '▶️';
            pauseText.textContent = '继续';
            pauseBtn.classList.add('paused');
            window.logViewer.showToast('warning', '⏸️ 日志显示已暂停');
        } else {
            pauseIcon.textContent = '⏸️';
            pauseText.textContent = '暂停';
            pauseBtn.classList.remove('paused');
            window.logViewer.showToast('info', '▶️ 日志显示已恢复');
        }
        
        console.log('日志显示状态:', window.logViewer.isPaused ? '暂停' : '运行');
    }
}

/**
 * 清空日志
 */
function clearLogs() {
    if (window.logViewer) {
        window.logViewer.clearLogDisplay();
        window.logViewer.showToast('info', '🗑️ 本地日志已清空');
    }
}

/**
 * 请求历史日志
 */
function requestHistory() {
    if (window.logViewer) {
        window.logViewer.clearLogDisplay();
        window.logViewer.requestLogHistory(200);
        window.logViewer.showToast('info', '📋 正在加载历史日志...');
    }
}

/**
 * 切换自动滚动
 */
function toggleAutoScroll() {
    const checkbox = document.getElementById('autoScroll');
    if (window.logViewer && checkbox) {
        window.logViewer.autoScroll = checkbox.checked;
        console.log('自动滚动:', window.logViewer.autoScroll ? '启用' : '禁用');
    }
}

/**
 * 更新过滤器
 */
function updateFilter() {
    if (window.logViewer) {
        window.logViewer.updateFilterState();
        console.log('过滤器已更新:', window.logViewer.filters);
    }
}

/**
 * 加载演示日志数据
 */
function loadDemoLogs() {
    if (window.logViewer) {
        fetch('/api/logs/demo')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.logViewer.showToast('success', '🎭 演示数据加载成功');
                } else {
                    window.logViewer.showToast('error', '❌ 演示数据加载失败');
                }
            })
            .catch(error => {
                console.error('加载演示数据失败:', error);
                window.logViewer.showToast('error', '❌ 演示数据加载失败');
            });
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM加载完成，初始化日志查看器...');
    
    // 创建全局日志查看器实例
    window.logViewer = new XianyuLogViewer();
    
    console.log('咸鱼AI客服日志查看器启动完成');
}); 