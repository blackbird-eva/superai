<template>
  <div class="output-container">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button type="primary" :icon="Upload" @click="handleImport">
          导入翻译任务
        </el-button>
        <el-button :icon="Refresh" @click="handleRefresh">
          刷新
        </el-button>
      </div>
      <div class="toolbar-right">
        <el-tag type="info">总条目: {{ totalItems }}</el-tag>
        <el-tag type="warning">待定稿: {{ pendingItems }}</el-tag>
        <el-tag type="success">已定稿: {{ finalizedItems }}</el-tag>
        <el-button type="success" :icon="Check" @click="handleFinalizeAll" :disabled="pendingItems === 0">
          全部定稿
        </el-button>
        <el-button type="primary" :icon="Download" @click="handleExport">
          导出结果
        </el-button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="content-wrapper">
      <!-- 左侧：翻译任务列表 -->
      <div class="task-panel">
        <div class="panel-header">
          <h3>翻译任务</h3>
          <el-select v-model="currentTaskId" placeholder="选择任务" style="width: 250px" @change="handleTaskChange">
            <el-option
              v-for="task in tasks"
              :key="task.id"
              :label="task.name"
              :value="task.id"
            >
              <div class="task-option">
                <span>{{ task.name }}</span>
                <el-tag size="small" :type="task.status === 'completed' ? 'success' : 'warning'">
                  {{ task.statusText }}
                </el-tag>
              </div>
            </el-option>
          </el-select>
        </div>

        <div class="task-info" v-if="currentTask">
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="源语言">{{ currentTask.sourceLang }}</el-descriptions-item>
            <el-descriptions-item label="目标语言">{{ currentTask.targetLang }}</el-descriptions-item>
            <el-descriptions-item label="翻译类型">{{ currentTask.type }}</el-descriptions-item>
            <el-descriptions-item label="完成时间">{{ currentTask.completedTime }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 内容列表 -->
        <div class="content-list">
          <div
            v-for="(item, index) in items"
            :key="item.id"
            :class="['content-item', { active: selectedItem?.id === item.id, finalized: item.finalized }]"
            @click="selectItem(item)"
          >
            <div class="item-header">
              <span class="line-number">{{ index + 1 }}</span>
              <el-tag v-if="item.finalized" type="success" size="small">已定稿</el-tag>
              <el-tag v-else type="warning" size="small">待定稿</el-tag>
            </div>
            <div class="item-content">
              <div class="original-text">{{ item.original }}</div>
              <div class="translated-text">{{ item.translation }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：编辑区域 -->
      <div class="editor-panel">
        <div class="panel-header">
          <h3>内容定稿</h3>
          <div class="header-actions">
            <el-button size="small" @click="handleReset" :disabled="!selectedItem || selectedItem.finalized">
              重置修改
            </el-button>
            <el-button size="small" type="primary" @click="handleFinalizeItem" :disabled="!selectedItem || selectedItem.finalized">
              <el-icon><Check /></el-icon> 确认定稿
            </el-button>
          </div>
        </div>

        <div v-if="selectedItem" class="editor-content">
          <!-- 原文 -->
          <div class="edit-section">
            <div class="section-header">
              <span class="section-title">原文</span>
              <el-tag type="info" size="small">{{ currentTask?.sourceLang }}</el-tag>
            </div>
            <div class="text-display">{{ selectedItem.original }}</div>
          </div>

          <!-- 译文编辑 -->
          <div class="edit-section">
            <div class="section-header">
              <span class="section-title">译文</span>
              <el-tag type="success" size="small">{{ currentTask?.targetLang }}</el-tag>
            </div>
            <el-input
              v-model="editingTranslation"
              type="textarea"
              :rows="4"
              placeholder="请输入或编辑译文"
              :disabled="selectedItem.finalized"
            />
          </div>

          <!-- 备注 -->
          <div class="edit-section">
            <div class="section-header">
              <span class="section-title">备注</span>
            </div>
            <el-input
              v-model="editingNote"
              type="textarea"
              :rows="2"
              placeholder="添加备注信息（可选）"
              :disabled="selectedItem.finalized"
            />
          </div>

          <!-- 历史记录 -->
          <div class="edit-section" v-if="selectedItem.history && selectedItem.history.length > 0">
            <div class="section-header">
              <span class="section-title">修改历史</span>
            </div>
            <div class="history-list">
              <div v-for="(record, idx) in selectedItem.history" :key="idx" class="history-item">
                <div class="history-time">{{ record.time }}</div>
                <div class="history-content">
                  <span class="history-label">修改前：</span>
                  <span class="history-before">{{ record.before }}</span>
                </div>
                <div class="history-content">
                  <span class="history-label">修改后：</span>
                  <span class="history-after">{{ record.after }}</span>
                </div>
                <div v-if="record.note" class="history-note">备注：{{ record.note }}</div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="empty-state">
          <el-icon class="empty-icon"><Edit /></el-icon>
          <p>请从左侧选择要定稿的内容</p>
        </div>
      </div>
    </div>

    <!-- 导出对话框 -->
    <el-dialog v-model="showExportDialog" title="导出定稿结果" width="500px">
      <el-form :model="exportForm" label-width="100px">
        <el-form-item label="导出格式">
          <el-radio-group v-model="exportForm.format">
            <el-radio label="docx">Word 文档</el-radio>
            <el-radio label="xlsx">Excel 表格</el-radio>
            <el-radio label="txt">纯文本</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="包含内容">
          <el-checkbox-group v-model="exportForm.include">
            <el-checkbox label="original">原文</el-checkbox>
            <el-checkbox label="translation">译文</el-checkbox>
            <el-checkbox label="note">备注</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="导出范围">
          <el-radio-group v-model="exportForm.range">
            <el-radio label="all">全部内容</el-radio>
            <el-radio label="finalized">仅已定稿</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showExportDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmExport">导出</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Refresh, Check, Download, Edit } from '@element-plus/icons-vue'

// 数据状态
const tasks = ref([])
const currentTaskId = ref('')
const items = ref([])
const selectedItem = ref(null)
const editingTranslation = ref('')
const editingNote = ref('')
const showExportDialog = ref(false)
const exportForm = ref({
  format: 'docx',
  include: ['original', 'translation', 'note'],
  range: 'all'
})

// 计算属性
const currentTask = computed(() => tasks.value.find(t => t.id === currentTaskId.value))
const totalItems = computed(() => items.value.length)
const pendingItems = computed(() => items.value.filter(item => !item.finalized).length)
const finalizedItems = computed(() => items.value.filter(item => item.finalized).length)

// 初始化演示数据
const initDemoData = () => {
  tasks.value = [
    {
      id: 'task_1',
      name: '技术手册翻译 - 中文到英文',
      sourceLang: '中文',
      targetLang: 'English',
      type: '文档翻译',
      status: 'completed',
      statusText: '已完成',
      completedTime: '2026-01-27 14:30:00'
    },
    {
      id: 'task_2',
      name: '产品说明书 - 中文到日文',
      sourceLang: '中文',
      targetLang: '日语',
      type: '文档翻译',
      status: 'completed',
      statusText: '已完成',
      completedTime: '2026-01-26 16:45:00'
    },
    {
      id: 'task_3',
      name: '用户协议 - 英文到中文',
      sourceLang: 'English',
      targetLang: '中文',
      type: '文档翻译',
      status: 'processing',
      statusText: '进行中',
      completedTime: null
    }
  ]

  items.value = [
    {
      id: 1,
      original: '本产品采用最新的AI翻译技术，支持多语言互译。',
      translation: 'This product adopts the latest AI translation technology and supports multi-language translation.',
      finalized: false,
      note: '',
      history: []
    },
    {
      id: 2,
      original: '系统会在翻译过程中保持原文格式和排版。',
      translation: 'The system maintains the original format and layout during the translation process.',
      finalized: true,
      note: '已确认无误',
      history: [
        {
          time: '2026-01-27 14:32:15',
          before: 'The system keeps original format during translation.',
          after: 'The system maintains the original format and layout during the translation process.',
          note: '调整用词使表达更准确'
        }
      ]
    },
    {
      id: 3,
      original: '翻译完成后，用户可以导出多种格式的文件。',
      translation: 'After translation is completed, users can export files in various formats.',
      finalized: false,
      note: '',
      history: []
    },
    {
      id: 4,
      original: '我们提供专业的术语库管理功能。',
      translation: 'We provide professional terminology management functions.',
      finalized: false,
      note: '',
      history: []
    },
    {
      id: 5,
      original: '支持批量翻译，提高工作效率。',
      translation: 'Supports batch translation to improve work efficiency.',
      finalized: true,
      note: '',
      history: []
    }
  ]

  // 默认选中第一个任务
  if (tasks.value.length > 0) {
    currentTaskId.value = tasks.value[0].id
  }
}

// 生命周期
onMounted(() => {
  initDemoData()
})

// 方法
const handleImport = () => {
  ElMessage.info('导入翻译任务功能开发中...')
}

const handleRefresh = () => {
  ElMessage.success('数据已刷新')
}

const handleTaskChange = (taskId) => {
  // 实际项目中这里应该加载对应任务的数据
  selectedItem.value = null
  editingTranslation.value = ''
  editingNote.value = ''
}

const selectItem = (item) => {
  selectedItem.value = item
  editingTranslation.value = item.translation
  editingNote.value = item.note || ''
}

const handleReset = () => {
  if (!selectedItem.value) return

  ElMessageBox.confirm(
    '确定要重置当前修改吗？',
    '重置修改',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    editingTranslation.value = selectedItem.value.translation
    ElMessage.success('已重置修改')
  }).catch(() => {})
}

const handleFinalizeItem = () => {
  if (!selectedItem.value) return

  // 检查是否有修改
  if (editingTranslation.value === selectedItem.value.translation) {
    selectedItem.value.finalized = true
    selectedItem.value.note = editingNote.value
    ElMessage.success('内容已定稿')
    return
  }

  // 记录修改历史
  const now = new Date().toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  })

  selectedItem.value.history = selectedItem.value.history || []
  selectedItem.value.history.unshift({
    time: now,
    before: selectedItem.value.translation,
    after: editingTranslation.value,
    note: editingNote.value
  })

  // 更新译文
  selectedItem.value.translation = editingTranslation.value
  selectedItem.value.note = editingNote.value
  selectedItem.value.finalized = true

  ElMessage.success('内容已定稿')
}

const handleFinalizeAll = () => {
  ElMessageBox.confirm(
    `确定要将所有 ${pendingItems.value} 条待定稿内容全部定稿吗？`,
    '全部定稿',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    items.value.forEach(item => {
      if (!item.finalized) {
        item.finalized = true
      }
    })
    ElMessage.success('全部内容已定稿')
  }).catch(() => {})
}

const handleExport = () => {
  showExportDialog.value = true
}

const confirmExport = () => {
  const { format, include, range } = exportForm.value

  // 根据范围筛选数据
  let exportData = items.value
  if (range === 'finalized') {
    exportData = items.value.filter(item => item.finalized)
  }

  if (exportData.length === 0) {
    ElMessage.warning('没有可导出的数据')
    return
  }

  // 这里应该调用实际的导出API
  ElMessage.success(`已导出 ${exportData.length} 条数据为 ${format.toUpperCase()} 格式`)
  showExportDialog.value = false
}
</script>

<style scoped>
.output-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* 主内容区 */
.content-wrapper {
  display: flex;
  flex: 1;
  overflow: hidden;
  padding: 16px;
  gap: 16px;
}

/* 左侧任务面板 */
.task-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

.task-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.task-info {
  padding: 12px 16px;
  background: #f9f9f9;
  border-bottom: 1px solid #e0e0e0;
}

.content-list {
  flex: 1;
  overflow-y: auto;
}

.content-item {
  padding: 12px 16px;
  border-bottom: 1px solid #e0e0e0;
  cursor: pointer;
  transition: background 0.2s;
}

.content-item:hover {
  background: #f5f5f5;
}

.content-item.active {
  background: #e6f4ff;
  border-left: 3px solid #1890ff;
}

.content-item.finalized {
  border-left: 3px solid #52c41a;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.line-number {
  font-size: 12px;
  color: #999;
  font-weight: 500;
}

.item-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.original-text {
  font-size: 13px;
  color: #666;
}

.translated-text {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

/* 右侧编辑面板 */
.editor-panel {
  flex: 1.2;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.editor-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.edit-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.section-title {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.text-display {
  padding: 12px;
  background: #f9f9f9;
  border-radius: 4px;
  font-size: 14px;
  line-height: 1.6;
  color: #333;
}

.history-list {
  max-height: 300px;
  overflow-y: auto;
}

.history-item {
  padding: 12px;
  background: #f9f9f9;
  border-radius: 4px;
  margin-bottom: 8px;
}

.history-time {
  font-size: 12px;
  color: #999;
  margin-bottom: 6px;
}

.history-content {
  font-size: 13px;
  margin-bottom: 6px;
}

.history-label {
  color: #666;
  margin-right: 8px;
}

.history-before {
  color: #f56c6c;
  text-decoration: line-through;
}

.history-after {
  color: #67c23a;
}

.history-note {
  font-size: 12px;
  color: #999;
  margin-top: 6px;
}

/* 空状态 */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #999;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state p {
  font-size: 14px;
  margin: 0;
}
</style>
