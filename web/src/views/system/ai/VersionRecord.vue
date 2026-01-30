<template>
  <div class="version-record-container">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button type="primary" :icon="Plus" @click="handleCreateVersion">
          创建新版本
        </el-button>
        <el-button :icon="Refresh" @click="handleRefresh">
          刷新
        </el-button>
      </div>
      <div class="toolbar-right">
        <el-tag type="info">总版本数: {{ versions.length }}</el-tag>
        <el-button type="primary" :icon="Download" @click="handleExport">
          导出
        </el-button>
      </div>
    </div>

    <!-- 版本列表 -->
    <div class="version-list">
      <div
        v-for="version in versions"
        :key="version.id"
        :class="['version-item', { current: version.isCurrent }]"
        @click="handleViewVersion(version)"
      >
        <div class="version-header">
          <div class="version-info">
            <el-icon v-if="version.isCurrent" class="star-icon"><Star /></el-icon>
            <span class="version-number">v{{ version.version }}</span>
          </div>
          <el-tag :type="version.status === 'formal' ? 'success' : 'warning'" size="small">
            {{ version.status === 'formal' ? '正式' : '草稿' }}
          </el-tag>
        </div>
        <div class="version-title">{{ version.title }}</div>
        <div class="version-meta">
          <span>{{ version.author }}</span>
          <span>{{ version.createTime }}</span>
        </div>
        <div class="version-desc" v-if="version.description">
          {{ version.description }}
        </div>
        <div class="version-actions">
          <el-button size="small" text @click.stop="handleRollback(version)" :disabled="version.isCurrent">
            回滚
          </el-button>
          <el-button size="small" text @click.stop="handleDownload(version)">
            下载
          </el-button>
        </div>
      </div>
    </div>

    <!-- 创建版本对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建新版本" width="500px">
      <el-form :model="versionForm" label-width="80px">
        <el-form-item label="版本号">
          <el-input v-model="versionForm.version" placeholder="例如：2.1.0" />
        </el-form-item>
        <el-form-item label="版本标题">
          <el-input v-model="versionForm.title" placeholder="请输入版本标题" />
        </el-form-item>
        <el-form-item label="版本描述">
          <el-input
            v-model="versionForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入版本描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmCreateVersion">创建</el-button>
      </template>
    </el-dialog>

    <!-- 版本详情对话框 -->
    <el-dialog v-model="showDetailDialog" :title="`版本 v${currentVersion?.version}`" width="600px">
      <div v-if="currentVersion" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="版本号">v{{ currentVersion.version }}</el-descriptions-item>
          <el-descriptions-item label="版本状态">
            <el-tag :type="currentVersion.status === 'formal' ? 'success' : 'warning'" size="small">
              {{ currentVersion.status === 'formal' ? '正式' : '草稿' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建者">{{ currentVersion.author }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentVersion.createTime }}</el-descriptions-item>
          <el-descriptions-item label="文件大小">{{ currentVersion.size }}</el-descriptions-item>
          <el-descriptions-item label="是否当前版本">
            <el-tag v-if="currentVersion.isCurrent" type="success" size="small">是</el-tag>
            <el-tag v-else type="info" size="small">否</el-tag>
          </el-descriptions-item>
        </el-descriptions>
        <div class="description-section">
          <h4>版本描述</h4>
          <div class="description-text">
            {{ currentVersion.description || '暂无描述' }}
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Download, Star } from '@element-plus/icons-vue'

// 数据状态
const versions = ref([])
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const currentVersion = ref(null)

const versionForm = reactive({
  version: '',
  title: '',
  description: ''
})

// 初始化演示数据
const initDemoData = () => {
  versions.value = [
    {
      id: 1,
      version: '2.1.0',
      title: '产品功能更新版本',
      status: 'formal',
      author: '张三',
      createTime: '2026-01-27 16:30:00',
      size: '350 KB',
      isCurrent: true,
      description: '更新产品功能介绍，新增用户指南章节，优化翻译质量'
    },
    {
      id: 2,
      version: '2.0.5',
      title: 'Bug修复版本',
      status: 'formal',
      author: '李四',
      createTime: '2026-01-25 14:20:00',
      size: '345 KB',
      isCurrent: false,
      description: '修复翻译错误，优化格式显示'
    },
    {
      id: 3,
      version: '2.0.4',
      title: '性能优化版本',
      status: 'formal',
      author: '王五',
      createTime: '2026-01-23 11:15:00',
      size: '340 KB',
      isCurrent: false,
      description: '优化系统性能，提升翻译速度'
    },
    {
      id: 4,
      version: '2.0.3',
      title: '功能增强版本',
      status: 'formal',
      author: '张三',
      createTime: '2026-01-20 16:45:00',
      size: '335 KB',
      isCurrent: false,
      description: '增强翻译功能，新增术语库管理'
    },
    {
      id: 5,
      version: '2.0.2',
      title: '修复格式问题',
      status: 'formal',
      author: '李四',
      createTime: '2026-01-18 09:30:00',
      size: '330 KB',
      isCurrent: false,
      description: '修复文档格式问题，调整排版'
    }
  ]
}

// 初始化
initDemoData()

// 方法
const handleCreateVersion = () => {
  const nextVersion = getNextVersion()
  versionForm.version = nextVersion
  versionForm.title = ''
  versionForm.description = ''
  showCreateDialog.value = true
}

const getNextVersion = () => {
  const current = versions.value.find(v => v.isCurrent)
  if (current) {
    const ver = current.version.replace('v', '')
    const [major, minor, patch] = ver.split('.').map(Number)
    return `v${major}.${minor}.${patch + 1}`
  }
  return 'v1.0.0'
}

const confirmCreateVersion = () => {
  if (!versionForm.version || !versionForm.title) {
    ElMessage.warning('请填写版本号和标题')
    return
  }

  const now = new Date().toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  })

  const newVersion = {
    id: versions.value.length + 1,
    version: versionForm.version,
    title: versionForm.title,
    status: 'draft',
    author: '当前用户',
    createTime: now,
    size: '350 KB',
    isCurrent: false,
    description: versionForm.description
  }

  versions.value.unshift(newVersion)
  ElMessage.success('版本创建成功')
  showCreateDialog.value = false
}

const handleRefresh = () => {
  ElMessage.success('数据已刷新')
}

const handleViewVersion = (version) => {
  currentVersion.value = version
  showDetailDialog.value = true
}

const handleRollback = (version) => {
  if (version.isCurrent) return

  ElMessageBox.confirm(
    `确定要回滚到版本 ${version.version} 吗？`,
    '版本回滚',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    versions.value.forEach(v => v.isCurrent = false)
    version.isCurrent = true
    ElMessage.success(`已回滚到版本 ${version.version}`)
  }).catch(() => {})
}

const handleDownload = (version) => {
  ElMessage.success(`正在下载版本 ${version.version}...`)
}

const handleExport = () => {
  ElMessage.success('导出功能开发中...')
}
</script>

<style scoped>
.version-record-container {
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

/* 版本列表 */
.version-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px 24px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.version-item {
  background: white;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
}

.version-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.version-item.current {
  border-color: #67c23a;
  background: #f0f9ff;
}

.version-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.version-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.star-icon {
  color: #f6d365;
}

.version-number {
  font-weight: 600;
  font-size: 16px;
  color: #333;
}

.version-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
  color: #333;
}

.version-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
}

.version-desc {
  font-size: 13px;
  color: #666;
  line-height: 1.5;
  margin-bottom: 12px;
}

.version-actions {
  display: flex;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid #e0e0e0;
}

/* 详情内容 */
.detail-content {
  padding: 16px;
}

.description-section {
  margin-top: 16px;
}

.description-section h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.description-text {
  padding: 12px;
  background: #f5f5f5;
  border-radius: 4px;
  font-size: 14px;
  line-height: 1.6;
  color: #666;
}
</style>
