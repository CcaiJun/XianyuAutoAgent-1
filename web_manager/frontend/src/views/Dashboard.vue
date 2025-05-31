<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统概览</span>
            </div>
          </template>
          <div class="system-overview">
            <h2>🎯 XianyuAutoAgent Web管理器</h2>
            <p>欢迎使用XianyuAutoAgent智能客服机器人Web管理界面</p>
            
            <el-row :gutter="20" style="margin-top: 20px;">
              <el-col :span="8">
                <el-card class="status-card">
                  <div class="status-item">
                    <el-tag :type="processStore.statusType" size="large">
                      {{ processStore.statusText }}
                    </el-tag>
                    <p>主进程状态</p>
                  </div>
                </el-card>
              </el-col>
              
              <el-col :span="8">
                <el-card class="status-card">
                  <div class="status-item">
                    <span class="metric">{{ processStore.systemStats.cpu }}%</span>
                    <p>CPU使用率</p>
                  </div>
                </el-card>
              </el-col>
              
              <el-col :span="8">
                <el-card class="status-card">
                  <div class="status-item">
                    <span class="metric">{{ processStore.systemStats.memory }}MB</span>
                    <p>内存使用</p>
                  </div>
                </el-card>
              </el-col>
            </el-row>
            
            <div class="quick-actions" style="margin-top: 30px;">
              <h3>快速操作</h3>
              <el-space wrap>
                <el-button type="primary" @click="$router.push('/process')">
                  进程管理
                </el-button>
                <el-button type="success" @click="$router.push('/logs')">
                  实时日志
                </el-button>
                <el-button type="warning" @click="$router.push('/config')">
                  配置管理
                </el-button>
                <el-button type="info" @click="$router.push('/prompts')">
                  提示词管理
                </el-button>
              </el-space>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { useProcessStore } from '../stores/process'

const processStore = useProcessStore()
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.system-overview {
  text-align: center;
}

.status-card {
  text-align: center;
}

.status-item {
  padding: 20px 0;
}

.metric {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.quick-actions {
  text-align: left;
}
</style> 