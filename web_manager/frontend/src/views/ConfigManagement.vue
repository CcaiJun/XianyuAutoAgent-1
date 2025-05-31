<template>
  <div class="config-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>配置管理</span>
          <el-button type="primary" @click="saveConfig" :loading="saving">
            保存配置
          </el-button>
        </div>
      </template>
      
      <div class="config-form">
        <el-form :model="configForm" label-width="150px">
          <el-form-item 
            v-for="(value, key) in configForm" 
            :key="key" 
            :label="key"
          >
            <el-input 
              v-model="configForm[key]" 
              :type="isPasswordField(key) ? 'password' : 'text'"
              :placeholder="`请输入${key}`"
            />
          </el-form-item>
        </el-form>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const configForm = ref({})
const saving = ref(false)

const loadConfig = async () => {
  try {
    // 这里调用API加载配置
    // const response = await api.config.get()
    // configForm.value = response.data
    
    // 模拟数据
    configForm.value = {
      'API_KEY': '',
      'DATABASE_URL': '',
      'WEBHOOK_URL': '',
      'LOG_LEVEL': 'INFO',
      'MAX_RETRIES': '3'
    }
  } catch (error) {
    ElMessage.error('加载配置失败: ' + error.message)
  }
}

const saveConfig = async () => {
  saving.value = true
  try {
    // 这里调用API保存配置
    // await api.config.update(configForm.value)
    
    ElMessage.success('配置保存成功')
  } catch (error) {
    ElMessage.error('保存配置失败: ' + error.message)
  } finally {
    saving.value = false
  }
}

const isPasswordField = (key) => {
  return key.toLowerCase().includes('password') || 
         key.toLowerCase().includes('secret') ||
         key.toLowerCase().includes('key')
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.config-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style> 