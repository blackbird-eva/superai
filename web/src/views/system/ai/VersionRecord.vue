<template>
  <div class="version-record-container">
    <!-- 统计面板 -->
    <div class="stats-panel">
      <div class="stat-item">
        <div class="stat-icon"><el-icon><Document /></el-icon></div>
        <div class="stat-content">
          <div class="stat-value">{{ versions.length }}</div>
          <div class="stat-label">总版本数</div>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon formal"><el-icon><CircleCheck /></el-icon></div>
        <div class="stat-content">
          <div class="stat-value">{{ formalVersions }}</div>
          <div class="stat-label">正式版本</div>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon draft"><el-icon><Edit /></el-icon></div>
        <div class="stat-content">
          <div class="stat-value">{{ draftVersions }}</div>
          <div class="stat-label">草稿版本</div>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon current"><el-icon><Star /></el-icon></div>
        <div class="stat-content">
          <div class="stat-value">v{{ currentVersionInfo?.version || '-' }}</div>
          <div class="stat-label">当前版本</div>
        </div>
      </div>
    </div>

    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button type="primary" :icon="Plus" @click="handleCreateVersion">
          创建新版本
        </el-button>
        <el-button :icon="Refresh" @click="handleRefresh">
          刷新
        </el-button>
        <el-button :icon="Operation" @click="handleBatchOperation">
          批量操作
        </el-button>
        <el-button :icon="View" @click="toggleViewMode">
          {{ viewMode === 'grid' ? '时间线视图' : '网格视图' }}
        </el-button>
      </div>
      <div class="toolbar-right">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索版本号、标题或作者..."
          style="width: 250px"
          :prefix-icon="Search"
          clearable
        />
        <el-select v-model="filterStatus" placeholder="状态筛选" style="width: 120px" clearable>
          <el-option label="全部" value="" />
          <el-option label="正式" value="formal" />
          <el-option label="草稿" value="draft" />
        </el-select>
        <el-select v-model="filterTag" placeholder="标签筛选" style="width: 120px" clearable>
          <el-option label="全部" value="" />
          <el-option label="重要" value="important" />
          <el-option label="稳定" value="stable" />
          <el-option label="测试" value="test" />
        </el-select>
        <el-tag type="info">显示: {{ filteredVersions.length }} / {{ versions.length }}</el-tag>
        <el-button type="primary" :icon="Download" @click="handleExport">
          导出
        </el-button>
      </div>
    </div>

    <!-- 网格视图 -->
    <div v-if="viewMode === 'grid'" class="version-list">
      <div
        v-for="version in filteredVersions"
        :key="version.id"
        :class="['version-item', { current: version.isCurrent }]"
      >
        <div class="version-header">
          <div class="version-info">
            <el-checkbox
              v-if="batchMode"
              v-model="version.selected"
              @change="handleSelectChange"
            />
            <el-icon v-if="version.isCurrent" class="star-icon"><Star /></el-icon>
            <span class="version-number">v{{ version.version }}</span>
            <el-tag
              v-for="tag in version.tags"
              :key="tag"
              size="small"
              :type="getTagType(tag)"
              class="version-tag"
            >
              {{ tag }}
            </el-tag>
          </div>
          <div class="version-status">
            <el-tag :type="version.status === 'formal' ? 'success' : 'warning'" size="small">
              {{ version.status === 'formal' ? '正式' : '草稿' }}
            </el-tag>
          </div>
        </div>
        <div class="version-title">{{ version.title }}</div>
        <div class="version-meta">
          <span><el-icon><User /></el-icon> {{ version.author }}</span>
          <span><el-icon><Clock /></el-icon> {{ version.createTime }}</span>
        </div>
        <div class="version-desc" v-if="version.description">
          {{ version.description }}
        </div>
        <div class="version-stats">
          <el-tag size="small" type="info">
            <el-icon><Download /></el-icon> {{ version.downloadCount || 0 }} 下载
          </el-tag>
          <el-tag size="small" type="info">
            <el-icon><View /></el-icon> {{ version.viewCount || 0 }} 浏览
          </el-tag>
        </div>
        <div class="version-actions">
          <el-button size="small" text @click="handleViewVersion(version)">
            <el-icon><View /></el-icon> 查看
          </el-button>
          <el-button size="small" text @click="handleCompare(version)" :disabled="!canCompare(version)">
            <el-icon><DocumentCopy /></el-icon> 对比
          </el-button>
          <el-button size="small" text @click="handleRollback(version)" :disabled="version.isCurrent">
            <el-icon><RefreshLeft /></el-icon> 回滚
          </el-button>
          <el-button size="small" text @click="handleDownload(version)">
            <el-icon><Download /></el-icon> 下载
          </el-button>
          <el-dropdown @command="(cmd) => handleMoreAction(version, cmd)">
            <el-button size="small" text>
              <el-icon><MoreFilled /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="edit">编辑</el-dropdown-item>
                <el-dropdown-item command="publish">发布</el-dropdown-item>
                <el-dropdown-item command="preview">预览</el-dropdown-item>
                <el-dropdown-item command="tag">管理标签</el-dropdown-item>
                <el-dropdown-item command="history">查看历史</el-dropdown-item>
                <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>

    <!-- 时间线视图 -->
    <div v-else class="timeline-view">
      <el-timeline>
        <el-timeline-item
          v-for="version in filteredVersions"
          :key="version.id"
          :timestamp="version.createTime"
          :type="version.isCurrent ? 'primary' : (version.status === 'formal' ? 'success' : 'warning')"
          :hollow="!version.isCurrent"
          placement="top"
        >
          <div class="timeline-item" @click="handleViewVersion(version)">
            <div class="timeline-header">
              <span class="timeline-version">v{{ version.version }}</span>
              <el-tag :type="version.status === 'formal' ? 'success' : 'warning'" size="small">
                {{ version.status === 'formal' ? '正式' : '草稿' }}
              </el-tag>
              <el-tag v-if="version.isCurrent" type="primary" size="small">当前</el-tag>
            </div>
            <div class="timeline-title">{{ version.title }}</div>
            <div class="timeline-desc">{{ version.description }}</div>
            <div class="timeline-meta">
              <span>{{ version.author }}</span>
              <span>{{ version.size }}</span>
            </div>
          </div>
        </el-timeline-item>
      </el-timeline>
    </div>

    <!-- 批量操作对话框 -->
    <el-dialog v-model="showBatchDialog" title="批量操作" width="500px">
      <div class="batch-actions">
        <el-button type="danger" @click="handleBatchDelete" :disabled="selectedVersions.length === 0">
          批量删除 ({{ selectedVersions.length }})
        </el-button>
        <el-button type="primary" @click="handleBatchDownload" :disabled="selectedVersions.length === 0">
          批量下载 ({{ selectedVersions.length }})
        </el-button>
        <el-button type="success" @click="handleBatchPublish" :disabled="selectedVersions.length === 0">
          批量发布 ({{ selectedVersions.length }})
        </el-button>
      </div>
      <div class="selected-list">
        <h4>已选择 {{ selectedVersions.length }} 个版本:</h4>
        <div class="selected-items">
          <el-tag
            v-for="version in selectedVersions"
            :key="version.id"
            closable
            @close="handleDeselect(version)"
          >
            v{{ version.version }}
          </el-tag>
        </div>
      </div>
    </el-dialog>

    <!-- 创建版本对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建新版本" width="600px">
      <el-form :model="versionForm" label-width="100px">
        <el-form-item label="版本号">
          <el-input v-model="versionForm.version" placeholder="例如：2.1.0" />
        </el-form-item>
        <el-form-item label="版本标题">
          <el-input v-model="versionForm.title" placeholder="请输入版本标题" />
        </el-form-item>
        <el-form-item label="版本类型">
          <el-select v-model="versionForm.type" placeholder="请选择版本类型" style="width: 100%">
            <el-option label="功能更新" value="feature" />
            <el-option label="Bug修复" value="bugfix" />
            <el-option label="性能优化" value="performance" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="版本标签">
          <el-select v-model="versionForm.tags" multiple placeholder="请选择标签" style="width: 100%">
            <el-option label="重要" value="important" />
            <el-option label="稳定" value="stable" />
            <el-option label="测试" value="test" />
          </el-select>
        </el-form-item>
        <el-form-item label="版本描述">
          <el-input
            v-model="versionForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入版本描述"
          />
        </el-form-item>
        <el-form-item label="更新内容">
          <el-input
            v-model="versionForm.changes"
            type="textarea"
            :rows="3"
            placeholder="请输入主要更新内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmCreateVersion">创建</el-button>
      </template>
    </el-dialog>

    <!-- 版本详情对话框 -->
    <el-dialog v-model="showDetailDialog" :title="`版本 v${currentVersion?.version}`" width="700px">
      <div v-if="currentVersion" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="版本号">v{{ currentVersion.version }}</el-descriptions-item>
          <el-descriptions-item label="版本类型">{{ getVersionTypeLabel(currentVersion.type) }}</el-descriptions-item>
          <el-descriptions-item label="版本状态">
            <el-tag :type="currentVersion.status === 'formal' ? 'success' : 'warning'" size="small">
              {{ currentVersion.status === 'formal' ? '正式' : '草稿' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="是否当前版本">
            <el-tag v-if="currentVersion.isCurrent" type="success" size="small">是</el-tag>
            <el-tag v-else type="info" size="small">否</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建者">{{ currentVersion.author }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentVersion.createTime }}</el-descriptions-item>
          <el-descriptions-item label="文件大小">{{ currentVersion.size }}</el-descriptions-item>
          <el-descriptions-item label="下载次数">{{ currentVersion.downloadCount || 0 }}</el-descriptions-item>
          <el-descriptions-item label="浏览次数">{{ currentVersion.viewCount || 0 }}</el-descriptions-item>
          <el-descriptions-item label="标签" :span="2">
            <el-tag
              v-for="tag in currentVersion.tags"
              :key="tag"
              size="small"
              :type="getTagType(tag)"
              style="margin-right: 8px"
            >
              {{ tag }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
        <div class="description-section">
          <h4>版本描述</h4>
          <div class="description-text">
            {{ currentVersion.description || '暂无描述' }}
          </div>
        </div>
        <div v-if="currentVersion.changes" class="changes-section">
          <h4>主要更新内容</h4>
          <div class="changes-text">
            {{ currentVersion.changes }}
          </div>
        </div>
        <div class="detail-actions">
          <el-button type="primary" @click="handleDownload(currentVersion)">
            <el-icon><Download /></el-icon> 下载版本
          </el-button>
          <el-button @click="handlePreview(currentVersion)">
            <el-icon><View /></el-icon> 预览内容
          </el-button>
          <el-button v-if="!currentVersion.isCurrent" @click="handleRollback(currentVersion)">
            <el-icon><RefreshLeft /></el-icon> 回滚到此版本
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 版本对比对话框 -->
    <el-dialog v-model="showCompareDialog" title="版本对比" width="900px">
      <div v-if="compareVersions.source && compareVersions.target" class="compare-content">
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="compare-panel">
              <h4>源版本: v{{ compareVersions.source.version }}</h4>
              <el-descriptions :column="1" border size="small">
                <el-descriptions-item label="标题">{{ compareVersions.source.title }}</el-descriptions-item>
                <el-descriptions-item label="状态">{{ compareVersions.source.status === 'formal' ? '正式' : '草稿' }}</el-descriptions-item>
                <el-descriptions-item label="大小">{{ compareVersions.source.size }}</el-descriptions-item>
                <el-descriptions-item label="时间">{{ compareVersions.source.createTime }}</el-descriptions-item>
              </el-descriptions>
              <div class="compare-desc">
                <h5>描述:</h5>
                <p>{{ compareVersions.source.description }}</p>
              </div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="compare-panel">
              <h4>目标版本: v{{ compareVersions.target.version }}</h4>
              <el-descriptions :column="1" border size="small">
                <el-descriptions-item label="标题">{{ compareVersions.target.title }}</el-descriptions-item>
                <el-descriptions-item label="状态">{{ compareVersions.target.status === 'formal' ? '正式' : '草稿' }}</el-descriptions-item>
                <el-descriptions-item label="大小">{{ compareVersions.target.size }}</el-descriptions-item>
                <el-descriptions-item label="时间">{{ compareVersions.target.createTime }}</el-descriptions-item>
              </el-descriptions>
              <div class="compare-desc">
                <h5>描述:</h5>
                <p>{{ compareVersions.target.description }}</p>
              </div>
            </div>
          </el-col>
        </el-row>
        <div class="compare-diff">
          <h4>差异对比</h4>
          <div class="diff-content">
            <el-alert type="info" :closable="false">
              <template #title>
                <div class="diff-item">
                  <span class="diff-label">版本号变化:</span>
                  <span class="diff-value">
                    <span class="diff-removed">v{{ compareVersions.source.version }}</span>
                    <el-icon><ArrowRight /></el-icon>
                    <span class="diff-added">v{{ compareVersions.target.version }}</span>
                  </span>
                </div>
              </template>
            </el-alert>
            <el-alert type="success" :closable="false" style="margin-top: 12px">
              <template #title>
                <div class="diff-item">
                  <span class="diff-label">大小变化:</span>
                  <span class="diff-value">
                    <span class="diff-removed">{{ compareVersions.source.size }}</span>
                    <el-icon><ArrowRight /></el-icon>
                    <span class="diff-added">{{ compareVersions.target.size }}</span>
                  </span>
                </div>
              </template>
            </el-alert>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 空状态 -->
    <div v-if="filteredVersions.length === 0" class="empty-state">
      <el-icon class="empty-icon"><FolderOpened /></el-icon>
      <p>暂无版本记录</p>
      <el-button type="primary" @click="handleCreateVersion">
        创建第一个版本
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Refresh,
  Download,
  Star,
  Search,
  View,
  Operation,
  Document,
  CircleCheck,
  Edit,
  Clock,
  User,
  DocumentCopy,
  RefreshLeft,
  MoreFilled,
  FolderOpened,
  ArrowRight
} from '@element-plus/icons-vue'

// 数据状态
const versions = ref([])
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const showBatchDialog = ref(false)
const showCompareDialog = ref(false)
const currentVersion = ref(null)
const viewMode = ref('grid') // grid 或 timeline
const batchMode = ref(false)
const searchKeyword = ref('')
const filterStatus = ref('')
const filterTag = ref('')

const versionForm = reactive({
  version: '',
  title: '',
  type: 'feature',
  tags: [],
  description: '',
  changes: ''
})

const compareVersions = reactive({
  source: null,
  target: null
})

// 初始化演示数据
const initDemoData = () => {
  versions.value = [
    {
      id: 1,
      version: '2.1.0',
      title: '产品功能更新版本',
      status: 'formal',
      type: 'feature',
      author: '张三',
      createTime: '2026-01-27 16:30:00',
      size: '350 KB',
      isCurrent: true,
      selected: false,
      downloadCount: 156,
      viewCount: 324,
      tags: ['stable', 'important'],
      description: '更新产品功能介绍，新增用户指南章节，优化翻译质量',
      changes: '1. 新增用户指南章节\n2. 优化翻译质量\n3. 修复已知问题'
    },
    {
      id: 2,
      version: '2.0.5',
      title: 'Bug修复版本',
      status: 'formal',
      type: 'bugfix',
      author: '李四',
      createTime: '2026-01-25 14:20:00',
      size: '345 KB',
      isCurrent: false,
      selected: false,
      downloadCount: 89,
      viewCount: 201,
      tags: ['stable'],
      description: '修复翻译错误，优化格式显示',
      changes: '1. 修复翻译错误\n2. 优化格式显示'
    },
    {
      id: 3,
      version: '2.0.4',
      title: '性能优化版本',
      status: 'formal',
      type: 'performance',
      author: '王五',
      createTime: '2026-01-23 11:15:00',
      size: '340 KB',
      isCurrent: false,
      selected: false,
      downloadCount: 67,
      viewCount: 156,
      tags: ['stable'],
      description: '优化系统性能，提升翻译速度',
      changes: '1. 优化系统性能\n2. 提升翻译速度'
    },
    {
      id: 4,
      version: '2.0.3',
      title: '功能增强版本',
      status: 'formal',
      type: 'feature',
      author: '张三',
      createTime: '2026-01-20 16:45:00',
      size: '335 KB',
      isCurrent: false,
      selected: false,
      downloadCount: 112,
      viewCount: 267,
      tags: ['important'],
      description: '增强翻译功能，新增术语库管理',
      changes: '1. 增强翻译功能\n2. 新增术语库管理'
    },
    {
      id: 5,
      version: '2.0.2',
      title: '修复格式问题',
      status: 'formal',
      type: 'bugfix',
      author: '李四',
      createTime: '2026-01-18 09:30:00',
      size: '330 KB',
      isCurrent: false,
      selected: false,
      downloadCount: 45,
      viewCount: 123,
      tags: [],
      description: '修复文档格式问题，调整排版',
      changes: '1. 修复文档格式问题\n2. 调整排版'
    },
    {
      id: 6,
      version: '2.0.1-beta',
      title: '测试版本',
      status: 'draft',
      type: 'feature',
      author: '王五',
      createTime: '2026-01-15 14:20:00',
      size: '325 KB',
      isCurrent: false,
      selected: false,
      downloadCount: 23,
      viewCount: 56,
      tags: ['test'],
      description: '测试新功能，包含实验性特性',
      changes: '1. 测试新功能\n2. 实验性特性'
    }
  ]
}

// 初始化
initDemoData()

// 计算属性
const formalVersions = computed(() => {
  return versions.value.filter(v => v.status === 'formal').length
})

const draftVersions = computed(() => {
  return versions.value.filter(v => v.status === 'draft').length
})

const currentVersionInfo = computed(() => {
  return versions.value.find(v => v.isCurrent)
})

const selectedVersions = computed(() => {
  return versions.value.filter(v => v.selected)
})

const filteredVersions = computed(() => {
  let result = versions.value

  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(v =>
      v.version.toLowerCase().includes(keyword) ||
      v.title.toLowerCase().includes(keyword) ||
      v.author.toLowerCase().includes(keyword)
    )
  }

  // 状态过滤
  if (filterStatus.value) {
    result = result.filter(v => v.status === filterStatus.value)
  }

  // 标签过滤
  if (filterTag.value) {
    result = result.filter(v => v.tags && v.tags.includes(filterTag.value))
  }

  return result
})

// 辅助方法
const getTagType = (tag) => {
  const types = {
    important: 'danger',
    stable: 'success',
    test: 'warning'
  }
  return types[tag] || 'info'
}

const getVersionTypeLabel = (type) => {
  const labels = {
    feature: '功能更新',
    bugfix: 'Bug修复',
    performance: '性能优化',
    other: '其他'
  }
  return labels[type] || type
}

const canCompare = (version) => {
  return !version.isCurrent && currentVersionInfo.value
}

// 主要方法
const handleCreateVersion = () => {
  const nextVersion = getNextVersion()
  versionForm.version = nextVersion
  versionForm.title = ''
  versionForm.type = 'feature'
  versionForm.tags = []
  versionForm.description = ''
  versionForm.changes = ''
  showCreateDialog.value = true
}

const getNextVersion = () => {
  const current = versions.value.find(v => v.isCurrent)
  if (current) {
    const ver = current.version.replace('v', '').replace('-beta', '')
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
    type: versionForm.type,
    author: '当前用户',
    createTime: now,
    size: '350 KB',
    isCurrent: false,
    selected: false,
    downloadCount: 0,
    viewCount: 0,
    tags: versionForm.tags || [],
    description: versionForm.description,
    changes: versionForm.changes
  }

  versions.value.unshift(newVersion)
  ElMessage.success('版本创建成功')
  showCreateDialog.value = false
}

const handleRefresh = () => {
  ElMessage.success('数据已刷新')
}

const handleViewVersion = (version) => {
  if (!version.viewCount) version.viewCount = 0
  version.viewCount++
  currentVersion.value = version
  showDetailDialog.value = true
}

const handleRollback = (version) => {
  if (version.isCurrent) return

  ElMessageBox.confirm(
    `确定要回滚到版本 ${version.version} 吗？这将把当前版本切换为选中的版本。`,
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
  if (!version.downloadCount) version.downloadCount = 0
  version.downloadCount++
  ElMessage.success(`正在下载版本 ${version.version}...`)
}

const handleExport = () => {
  const data = filteredVersions.value.map(version => ({
    ID: version.id,
    版本号: version.version,
    标题: version.title,
    类型: getVersionTypeLabel(version.type),
    状态: version.status === 'formal' ? '正式' : '草稿',
    作者: version.author,
    创建时间: version.createTime,
    文件大小: version.size,
    是否当前: version.isCurrent ? '是' : '否',
    下载次数: version.downloadCount || 0,
    浏览次数: version.viewCount || 0,
    标签: version.tags?.join(', ') || '',
    描述: version.description
  }))

  // 创建CSV内容
  const headers = Object.keys(data[0]).join(',')
  const rows = data.map(row => Object.values(row).map(v => `"${v}"`).join(','))
  const csv = [headers, ...rows].join('\n')

  // 创建下载链接
  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `版本列表_${new Date().toLocaleDateString('zh-CN')}.csv`
  link.click()
  URL.revokeObjectURL(url)

  ElMessage.success('导出成功')
}

const toggleViewMode = () => {
  viewMode.value = viewMode.value === 'grid' ? 'timeline' : 'grid'
}

const handleBatchOperation = () => {
  batchMode.value = true
  showBatchDialog.value = true
}

const handleSelectChange = () => {
  // 触发重新计算
}

const handleDeselect = (version) => {
  version.selected = false
}

const handleBatchDelete = () => {
  if (selectedVersions.value.length === 0) {
    ElMessage.warning('请先选择要删除的版本')
    return
  }

  ElMessageBox.confirm(
    `确定要删除选中的 ${selectedVersions.value.length} 个版本吗？`,
    '批量删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    const selectedIds = selectedVersions.value.map(v => v.id)
    versions.value = versions.value.filter(v => !selectedIds.includes(v.id))
    showBatchDialog.value = false
    batchMode.value = false
    ElMessage.success('批量删除成功')
  }).catch(() => {})
}

const handleBatchDownload = () => {
  if (selectedVersions.value.length === 0) {
    ElMessage.warning('请先选择要下载的版本')
    return
  }

  ElMessage.success(`开始批量下载 ${selectedVersions.value.length} 个版本...`)
  showBatchDialog.value = false
  batchMode.value = false
}

const handleBatchPublish = () => {
  if (selectedVersions.value.length === 0) {
    ElMessage.warning('请先选择要发布的版本')
    return
  }

  selectedVersions.value.forEach(v => {
    v.status = 'formal'
  })

  ElMessage.success(`已发布 ${selectedVersions.value.length} 个版本`)
  showBatchDialog.value = false
  batchMode.value = false
}

const handleCompare = (version) => {
  compareVersions.source = currentVersionInfo.value
  compareVersions.target = version
  showCompareDialog.value = true
}

const handleMoreAction = (version, command) => {
  switch (command) {
    case 'edit':
      ElMessage.info('编辑功能开发中...')
      break
    case 'publish':
      version.status = 'formal'
      ElMessage.success(`版本 ${version.version} 已发布`)
      break
    case 'preview':
      handlePreview(version)
      break
    case 'tag':
      ElMessage.info('标签管理功能开发中...')
      break
    case 'history':
      ElMessage.info('查看历史功能开发中...')
      break
    case 'delete':
      handleDeleteVersion(version)
      break
  }
}

const handlePreview = (version) => {
  ElMessage.success(`正在预览版本 ${version.version}...`)
}

const handleDeleteVersion = (version) => {
  if (version.isCurrent) {
    ElMessage.warning('不能删除当前版本')
    return
  }

  ElMessageBox.confirm(
    `确定要删除版本 ${version.version} 吗？`,
    '删除版本',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    const index = versions.value.findIndex(v => v.id === version.id)
    if (index !== -1) {
      versions.value.splice(index, 1)
      ElMessage.success('版本删除成功')
    }
  }).catch(() => {})
}
</script>

<style scoped>
.version-record-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
  overflow: hidden;
}

/* 统计面板 */
.stats-panel {
  display: flex;
  gap: 16px;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  flex-shrink: 0;
}

.stat-item {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

.stat-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.stat-item:nth-child(2) {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-item:nth-child(3) {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stat-item:nth-child(4) {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon {
  font-size: 36px;
  opacity: 0.9;
}

.stat-icon.formal {
  color: #67c23a;
}

.stat-icon.draft {
  color: #e6a23c;
}

.stat-icon.current {
  color: #f6d365;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  line-height: 1;
  margin-bottom: 6px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  flex-shrink: 0;
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

/* 版本列表 */
.version-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px 24px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.version-item {
  background: white;
  border-radius: 12px;
  padding: 20px;
  border: 2px solid transparent;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.version-item:hover {
  border-color: #409eff;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.2);
  transform: translateY(-2px);
}

.version-item.current {
  border-color: #67c23a;
  background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
}

.version-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.version-info {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.star-icon {
  color: #f6d365;
  font-size: 20px;
}

.version-number {
  font-weight: 600;
  font-size: 18px;
  color: #333;
}

.version-tag {
  margin-left: 4px;
}

.version-title {
  font-size: 15px;
  font-weight: 500;
  margin-bottom: 12px;
  color: #333;
  line-height: 1.5;
}

.version-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #999;
  margin-bottom: 12px;
}

.version-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.version-desc {
  font-size: 13px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 12px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #409eff;
}

.version-stats {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.version-stats .el-tag {
  display: flex;
  align-items: center;
  gap: 4px;
}

.version-actions {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
  flex-wrap: wrap;
}

.version-actions .el-button {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 时间线视图 */
.timeline-view {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: white;
}

.timeline-item {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.timeline-item:hover {
  background: #e6f7ff;
  transform: translateX(4px);
}

.timeline-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.timeline-version {
  font-weight: 600;
  font-size: 16px;
  color: #333;
}

.timeline-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
  color: #333;
}

.timeline-desc {
  font-size: 13px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 8px;
}

.timeline-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #999;
}

/* 批量操作对话框 */
.batch-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.selected-list {
  margin-top: 20px;
}

.selected-list h4 {
  margin-bottom: 12px;
  font-size: 14px;
  color: #333;
}

.selected-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.selected-items .el-tag {
  margin: 0;
}

/* 详情内容 */
.detail-content {
  padding: 16px;
}

.description-section,
.changes-section {
  margin-top: 16px;
}

.description-section h4,
.changes-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.description-text,
.changes-text {
  padding: 16px;
  background: #f5f5f5;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.8;
  color: #666;
  white-space: pre-wrap;
}

.detail-actions {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  gap: 12px;
}

.detail-actions .el-button {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 版本对比 */
.compare-content {
  padding: 16px;
}

.compare-panel {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.compare-panel h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #333;
  font-weight: 600;
}

.compare-desc {
  margin-top: 12px;
}

.compare-desc h5 {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: #666;
}

.compare-desc p {
  margin: 0;
  font-size: 13px;
  color: #999;
  line-height: 1.6;
}

.compare-diff {
  margin-top: 20px;
}

.compare-diff h4 {
  margin: 0 0 16px 0;
  font-size: 15px;
  color: #333;
  font-weight: 600;
}

.diff-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.diff-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.diff-label {
  font-weight: 500;
  color: #333;
}

.diff-value {
  display: flex;
  align-items: center;
  gap: 8px;
}

.diff-removed {
  color: #f56c6c;
  text-decoration: line-through;
}

.diff-added {
  color: #67c23a;
  font-weight: 600;
}

/* 空状态 */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #999;
  background: white;
  margin: 16px 24px;
  border-radius: 12px;
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 20px;
  color: #d9d9d9;
}

.empty-state p {
  font-size: 16px;
  margin-bottom: 20px;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-panel {
    flex-direction: column;
    padding: 12px 16px;
  }

  .stat-item {
    padding: 12px 16px;
  }

  .stat-value {
    font-size: 24px;
  }

  .stat-label {
    font-size: 12px;
  }

  .toolbar {
    padding: 12px 16px;
  }

  .toolbar-left,
  .toolbar-right {
    width: 100%;
    justify-content: center;
  }

  .version-list {
    grid-template-columns: 1fr;
    padding: 12px 16px;
  }

  .version-item {
    padding: 16px;
  }

  .timeline-view {
    padding: 16px;
  }
}

/* 滚动条样式 */
.version-list::-webkit-scrollbar,
.timeline-view::-webkit-scrollbar {
  width: 8px;
}

.version-list::-webkit-scrollbar-track,
.timeline-view::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.version-list::-webkit-scrollbar-thumb,
.timeline-view::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.version-list::-webkit-scrollbar-thumb:hover,
.timeline-view::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
