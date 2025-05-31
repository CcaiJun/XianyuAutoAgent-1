<template>
  <div class="prompt-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>提示词管理</span>
        </div>
      </template>
      
      <div class="prompt-list">
        <el-tabs v-model="activeTab" @tab-click="handleTabClick">
          <el-tab-pane
            v-for="file in promptFiles"
            :key="file.name"
            :label="file.name"
            :name="file.name"
          >
            <div class="prompt-editor">
              <el-input
                v-model="file.content"
                type="textarea"
                :rows="20"
                placeholder="请输入提示词内容..."
              />
              <div class="editor-actions">
                <el-button type="primary" @click="savePrompt(file)">
                  保存
                </el-button>
                <el-button @click="resetPrompt(file)">
                  重置
                </el-button>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('')
const promptFiles = ref([])

const loadPromptFiles = async () => {
  try {
    // 这里调用API加载提示词文件
    // const response = await api.prompts.list()
    // promptFiles.value = response.data
    
    // 模拟数据
    promptFiles.value = [
      {
        name: 'default_prompt.txt',
        content: '这是默认提示词内容...',
        originalContent: '这是默认提示词内容...'
      },
      {
        name: 'price_prompt.txt',
        content: '这是价格相关提示词内容...',
        originalContent: '这是价格相关提示词内容...'
      },
      {
        name: 'tech_prompt.txt',
        content: '这是技术支持提示词内容...',
        originalContent: '这是技术支持提示词内容...'
      },
      {
        name: 'classify_prompt.txt',
        content: '这是分类提示词内容...',
        originalContent: '这是分类提示词内容...'
      }
    ]
    
    if (promptFiles.value.length > 0) {
      activeTab.value = promptFiles.value[0].name
    }
  } catch (error) {
    ElMessage.error('加载提示词文件失败: ' + error.message)
  }
}

const savePrompt = async (file) => {
  try {
    // 这里调用API保存提示词
    // await api.prompts.update(file.name, file.content)
    
    file.originalContent = file.content
    ElMessage.success(`${file.name} 保存成功`)
  } catch (error) {
    ElMessage.error('保存失败: ' + error.message)
  }
}

const resetPrompt = (file) => {
  file.content = file.originalContent
  ElMessage.info(`${file.name} 已重置`)
}

const handleTabClick = (tab) => {
  // 切换tab时的处理
}

onMounted(() => {
  loadPromptFiles()
})
</script>

<style scoped>
.prompt-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.prompt-editor {
  margin-top: 20px;
}

.editor-actions {
  margin-top: 15px;
  text-align: right;
}
</style> 