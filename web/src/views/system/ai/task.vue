<template>
  <div class="task-container">
    <!-- 头部区域 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">翻译任务管理中心</h1>
        <p class="page-subtitle">实时监控翻译进度 · 任务状态跟踪 · 批量任务管理</p>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card total">
        <div class="stat-icon">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ totalTasks }}</div>
          <div class="stat-label">总任务数</div>
        </div>
      </div>
      <div class="stat-card processing">
        <div class="stat-icon">
          <el-icon><Loading /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ processingTasks }}</div>
          <div class="stat-label">进行中</div>
        </div>
      </div>
      <div class="stat-card completed">
        <div class="stat-icon">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ completedTasks }}</div>
          <div class="stat-label">已完成</div>
        </div>
      </div>
      <div class="stat-card failed">
        <div class="stat-icon">
          <el-icon><CircleClose /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ failedTasks }}</div>
          <div class="stat-label">失败</div>
        </div>
      </div>
    </div>

    <!-- 筛选和操作栏 -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-select v-model="filterStatus" placeholder="任务状态" style="width: 140px" clearable>
          <el-option label="待处理" value="pending"></el-option>
          <el-option label="进行中" value="processing"></el-option>
          <el-option label="已完成" value="completed"></el-option>
          <el-option label="失败" value="failed"></el-option>
          <el-option label="已取消" value="cancelled"></el-option>
        </el-select>
        <el-select v-model="filterType" placeholder="任务类型" style="width: 140px" clearable>
          <el-option label="文本翻译" value="text"></el-option>
          <el-option label="文档翻译" value="document"></el-option>
          <el-option label="图片翻译" value="image"></el-option>
        </el-select>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索任务名称..."
          prefix-icon="Search"
          style="width: 250px"
          clearable
        />
      </div>
      <div class="filter-right">
        <el-button type="primary" @click="showCreateTaskDialog = true">
          <el-icon><Plus /></el-icon> 创建任务
        </el-button>
        <el-button @click="refreshTasks">
          <el-icon><Refresh /></el-icon> 刷新
        </el-button>
        <el-button @click="clearCompletedTasks" v-if="completedTasks > 0">
          <el-icon><Delete /></el-icon> 清理已完成
        </el-button>
      </div>
    </div>

    <!-- 任务列表 -->
    <div class="task-list">
      <el-card class="task-card">
        <template #header>
          <div class="card-header">
            <span>翻译任务列表</span>
            <el-tag type="info">{{ filteredTasks.length }} 个任务</el-tag>
          </div>
        </template>

        <div v-if="filteredTasks.length === 0" class="empty-state">
          <el-icon class="empty-icon"><FolderOpened /></el-icon>
          <div class="empty-text">暂无任务数据</div>
          <el-button type="primary" @click="showCreateTaskDialog = true">
            创建新任务
          </el-button>
        </div>

        <div v-else class="tasks-container">
          <div
            v-for="task in filteredTasks"
            :key="task.id"
            class="task-item"
            :class="task.status"
          >
            <!-- 任务头部 -->
            <div class="task-header">
              <div class="task-left">
                <el-tag :type="getStatusType(task.status)" size="small" effect="dark">
                  {{ getStatusText(task.status) }}
                </el-tag>
                <h3 class="task-name">{{ task.name }}</h3>
              </div>
              <div class="task-right">
                <span class="task-type">
                  <el-icon><Document /></el-icon>
                  {{ getTypeText(task.type) }}
                </span>
              </div>
            </div>

            <!-- 任务信息 -->
            <div class="task-info">
              <div class="info-item">
                <span class="info-label">源语言:</span>
                <span class="info-value">{{ task.sourceLang }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">目标语言:</span>
                <span class="info-value">{{ task.targetLang }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">创建时间:</span>
                <span class="info-value">{{ formatTime(task.createTime) }}</span>
              </div>
              <div class="info-item" v-if="task.estimatedTime">
                <span class="info-label">预计完成:</span>
                <span class="info-value">{{ formatTime(task.estimatedTime) }}</span>
              </div>
            </div>

            <!-- 进度条 -->
            <div class="task-progress">
              <div class="progress-header">
                <span class="progress-label">翻译进度</span>
                <span class="progress-value">{{ task.progress }}%</span>
              </div>
              <el-progress
                :percentage="task.progress"
                :status="getProgressStatus(task.status)"
                :stroke-width="12"
                :text-inside="false"
              />
              <div class="progress-detail" v-if="task.currentStep">
                <el-icon class="step-icon"><Clock /></el-icon>
                <span class="step-text">{{ task.currentStep }}</span>
              </div>
            </div>

            <!-- 任务统计 -->
            <div class="task-stats" v-if="task.status === 'processing' || task.status === 'completed'">
              <div class="stat-row">
                <div class="stat-box">
                  <span class="stat-count">{{ task.totalWords || 0 }}</span>
                  <span class="stat-name">总字数</span>
                </div>
                <div class="stat-box">
                  <span class="stat-count">{{ task.translatedWords || 0 }}</span>
                  <span class="stat-name">已翻译</span>
                </div>
                <div class="stat-box">
                  <span class="stat-count">{{ task.terms || 0 }}</span>
                  <span class="stat-name">术语数</span>
                </div>
                <div class="stat-box">
                  <span class="stat-count">{{ task.duration || 0 }}s</span>
                  <span class="stat-name">耗时</span>
                </div>
              </div>
            </div>

            <!-- 错误信息 -->
            <el-alert
              v-if="task.status === 'failed' && task.error"
              :title="task.error"
              type="error"
              :closable="false"
              show-icon
              class="task-error"
            />

            <!-- 操作按钮 -->
            <div class="task-actions">
              <template v-if="task.status === 'pending'">
                <el-button type="primary" size="small" @click="startTask(task)">
                  <el-icon><VideoPlay /></el-icon> 开始
                </el-button>
                <el-button size="small" @click="editTask(task)">
                  <el-icon><Edit /></el-icon> 编辑
                </el-button>
                <el-button type="danger" size="small" @click="cancelTask(task)">
                  <el-icon><Delete /></el-icon> 取消
                </el-button>
              </template>
              <template v-if="task.status === 'processing'">
                <el-button type="warning" size="small" @click="pauseTask(task)">
                  <el-icon><VideoPause /></el-icon> 暂停
                </el-button>
                <el-button size="small" @click="viewDetail(task)">
                  <el-icon><View /></el-icon> 详情
                </el-button>
              </template>
              <template v-if="task.status === 'paused'">
                <el-button type="primary" size="small" @click="resumeTask(task)">
                  <el-icon><VideoPlay /></el-icon> 继续
                </el-button>
                <el-button size="small" @click="cancelTask(task)">
                  <el-icon><Delete /></el-icon> 取消
                </el-button>
              </template>
              <template v-if="task.status === 'completed'">
                <el-button type="success" size="small" @click="viewResult(task)">
                  <el-icon><Download /></el-icon> 查看结果
                </el-button>
                <el-button size="small" @click="downloadResult(task)">
                  <el-icon><Bottom /></el-icon> 下载
                </el-button>
                <el-button type="danger" size="small" @click="deleteTask(task)">
                  <el-icon><Delete /></el-icon> 删除
                </el-button>
              </template>
              <template v-if="task.status === 'failed'">
                <el-button type="warning" size="small" @click="retryTask(task)">
                  <el-icon><RefreshRight /></el-icon> 重试
                </el-button>
                <el-button size="small" @click="viewDetail(task)">
                  <el-icon><View /></el-icon> 查看详情
                </el-button>
                <el-button type="danger" size="small" @click="deleteTask(task)">
                  <el-icon><Delete /></el-icon> 删除
                </el-button>
              </template>
              <template v-if="task.status === 'cancelled'">
                <el-button type="primary" size="small" @click="retryTask(task)">
                  <el-icon><RefreshRight /></el-icon> 重新开始
                </el-button>
                <el-button type="danger" size="small" @click="deleteTask(task)">
                  <el-icon><Delete /></el-icon> 删除
                </el-button>
              </template>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 创建任务弹窗 -->
    <el-dialog
      v-model="showCreateTaskDialog"
      title="创建翻译任务"
      width="600px"
    >
      <el-form :model="newTask" label-width="100px">
        <el-form-item label="任务名称">
          <el-input v-model="newTask.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="任务类型">
          <el-select v-model="newTask.type" placeholder="选择任务类型" style="width: 100%">
            <el-option label="文本翻译" value="text"></el-option>
            <el-option label="文档翻译" value="document"></el-option>
            <el-option label="图片翻译" value="image"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="源语言">
          <el-select v-model="newTask.sourceLang" placeholder="选择源语言" style="width: 100%">
            <el-option label="中文" value="中文"></el-option>
            <el-option label="英语" value="英语"></el-option>
            <el-option label="日语" value="日语"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="目标语言">
          <el-select v-model="newTask.targetLang" placeholder="选择目标语言" style="width: 100%">
            <el-option label="中文" value="中文"></el-option>
            <el-option label="英语" value="英语"></el-option>
            <el-option label="日语" value="日语"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="任务内容" v-if="newTask.type === 'text'">
          <el-input
            v-model="newTask.content"
            type="textarea"
            :rows="6"
            placeholder="请输入需要翻译的文本..."
          />
        </el-form-item>
        <el-form-item label="上传文件" v-if="newTask.type === 'document'">
          <el-upload
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
          >
            <el-icon class="upload-icon"><UploadFilled /></el-icon>
            <div class="upload-text">拖拽文件到此处或点击上传</div>
            <div class="upload-hint">支持 PDF、Word、TXT 格式</div>
          </el-upload>
        </el-form-item>
        <el-form-item label="上传图片" v-if="newTask.type === 'image'">
          <el-upload
            drag
            :auto-upload="false"
            :on-change="handleImageChange"
            :limit="1"
            accept="image/*"
          >
            <el-icon class="upload-icon"><UploadFilled /></el-icon>
            <div class="upload-text">拖拽图片到此处或点击上传</div>
            <div class="upload-hint">支持 JPG、PNG、GIF 格式</div>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateTaskDialog = false">取消</el-button>
        <el-button type="primary" @click="createTask" :loading="creating">创建任务</el-button>
      </template>
    </el-dialog>

    <!-- 任务详情弹窗 -->
    <el-dialog
      v-model="showDetailDialog"
      title="任务详情"
      width="700px"
    >
      <div v-if="selectedTask" class="task-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务名称">{{ selectedTask.name }}</el-descriptions-item>
          <el-descriptions-item label="任务状态">
            <el-tag :type="getStatusType(selectedTask.status)" effect="dark">
              {{ getStatusText(selectedTask.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="任务类型">{{ getTypeText(selectedTask.type) }}</el-descriptions-item>
          <el-descriptions-item label="任务进度">{{ selectedTask.progress }}%</el-descriptions-item>
          <el-descriptions-item label="源语言">{{ selectedTask.sourceLang }}</el-descriptions-item>
          <el-descriptions-item label="目标语言">{{ selectedTask.targetLang }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatTime(selectedTask.createTime) }}</el-descriptions-item>
          <el-descriptions-item label="预计完成">{{ selectedTask.estimatedTime ? formatTime(selectedTask.estimatedTime) : '计算中...' }}</el-descriptions-item>
          <el-descriptions-item label="总字数">{{ selectedTask.totalWords || 0 }}</el-descriptions-item>
          <el-descriptions-item label="已翻译">{{ selectedTask.translatedWords || 0 }}</el-descriptions-item>
          <el-descriptions-item label="术语数">{{ selectedTask.terms || 0 }}</el-descriptions-item>
          <el-descriptions-item label="耗时">{{ selectedTask.duration || 0 }}秒</el-descriptions-item>
        </el-descriptions>

        <div class="detail-step" v-if="selectedTask.currentStep">
          <div class="step-header">
            <el-icon><Loading /></el-icon>
            <span>当前步骤</span>
          </div>
          <div class="step-content">{{ selectedTask.currentStep }}</div>
        </div>

        <div class="detail-error" v-if="selectedTask.error">
          <el-alert
            :title="selectedTask.error"
            type="error"
            :closable="false"
            show-icon
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Document, Loading, CircleCheck, CircleClose, Search, Plus, Refresh,
  Delete, FolderOpened, Clock, VideoPlay, VideoPause, Edit, View,
  Download, Bottom, RefreshRight, UploadFilled
} from '@element-plus/icons-vue'

// 任务接口定义
interface Task {
  id: string
  name: string
  type: 'text' | 'document' | 'image'
  status: 'pending' | 'processing' | 'paused' | 'completed' | 'failed' | 'cancelled'
  sourceLang: string
  targetLang: string
  progress: number
  createTime: Date
  estimatedTime?: Date
  totalWords?: number
  translatedWords?: number
  terms?: number
  duration?: number
  currentStep?: string
  error?: string
  content?: string
  file?: File
  image?: File
}

// 筛选条件
const filterStatus = ref('')
const filterType = ref('')
const searchKeyword = ref('')

// 弹窗状态
const showCreateTaskDialog = ref(false)
const showDetailDialog = ref(false)

// 新任务表单
const newTask = ref({
  name: '',
  type: 'text',
  sourceLang: '中文',
  targetLang: '英语',
  content: '',
  file: null as File | null,
  image: null as File | null
})

// 创建中状态
const creating = ref(false)

// 选中的任务
const selectedTask = ref<Task | null>(null)

// 模拟任务列表
const tasks = ref<Task[]>([
  {
    id: '1',
    name: '技术文档翻译 - API参考手册',
    type: 'document',
    status: 'processing',
    sourceLang: '中文',
    targetLang: '英语',
    progress: 65,
    createTime: new Date(Date.now() - 3600000),
    estimatedTime: new Date(Date.now() + 1800000),
    totalWords: 15000,
    translatedWords: 9750,
    terms: 234,
    duration: 3600,
    currentStep: '正在翻译第 3 章节: 核心功能说明'
  },
  {
    id: '2',
    name: '产品说明书翻译',
    type: 'document',
    status: 'completed',
    sourceLang: '英语',
    targetLang: '中文',
    progress: 100,
    createTime: new Date(Date.now() - 7200000),
    estimatedTime: new Date(Date.now() - 3600000),
    totalWords: 8000,
    translatedWords: 8000,
    terms: 156,
    duration: 1800
  },
  {
    id: '3',
    name: '营销文案翻译 - 活动宣传',
    type: 'text',
    status: 'pending',
    sourceLang: '中文',
    targetLang: '英语',
    progress: 0,
    createTime: new Date(Date.now() - 1800000),
    totalWords: 2500
  },
  {
    id: '4',
    name: '图片术语提取与翻译',
    type: 'image',
    status: 'failed',
    sourceLang: '中文',
    targetLang: '英语',
    progress: 45,
    createTime: new Date(Date.now() - 5400000),
    estimatedTime: new Date(Date.now() - 3600000),
    totalWords: 0,
    translatedWords: 0,
    terms: 0,
    duration: 1200,
    error: '图片识别失败: 无法提取清晰的文字内容，请上传更高分辨率的图片'
  },
  {
    id: '5',
    name: '用户手册批量翻译',
    type: 'document',
    status: 'paused',
    sourceLang: '中文',
    targetLang: '英语',
    progress: 30,
    createTime: new Date(Date.now() - 1800000),
    totalWords: 20000,
    translatedWords: 6000,
    terms: 412,
    duration: 1200
  }
])

// 计时器引用
let progressTimer: NodeJS.Timeout | null = null

// 统计数据
const totalTasks = computed(() => tasks.value.length)
const processingTasks = computed(() => tasks.value.filter(t => t.status === 'processing').length)
const completedTasks = computed(() => tasks.value.filter(t => t.status === 'completed').length)
const failedTasks = computed(() => tasks.value.filter(t => t.status === 'failed').length)

// 过滤后的任务列表
const filteredTasks = computed(() => {
  let result = [...tasks.value]

  if (filterStatus.value) {
    result = result.filter(t => t.status === filterStatus.value)
  }

  if (filterType.value) {
    result = result.filter(t => t.type === filterType.value)
  }

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(t => t.name.toLowerCase().includes(keyword))
  }

  return result.sort((a, b) => b.createTime.getTime() - a.createTime.getTime())
})

// 获取状态类型
const getStatusType = (status: string) => {
  const types: { [key: string]: any } = {
    pending: 'info',
    processing: 'primary',
    paused: 'warning',
    completed: 'success',
    failed: 'danger',
    cancelled: 'info'
  }
  return types[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const texts: { [key: string]: string } = {
    pending: '待处理',
    processing: '进行中',
    paused: '已暂停',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return texts[status] || status
}

// 获取任务类型文本
const getTypeText = (type: string) => {
  const texts: { [key: string]: string } = {
    text: '文本翻译',
    document: '文档翻译',
    image: '图片翻译'
  }
  return texts[type] || type
}

// 获取进度条状态
const getProgressStatus = (status: string) => {
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'exception'
  return undefined
}

// 格式化时间
const formatTime = (time: Date) => {
  const now = new Date()
  const diff = now.getTime() - time.getTime()
  const hours = Math.floor(diff / 3600000)
  const minutes = Math.floor((diff % 3600000) / 60000)

  if (hours > 24) {
    return time.toLocaleDateString() + ' ' + time.toLocaleTimeString()
  }
  if (hours > 0) {
    return `${hours}小时${minutes}分钟前`
  }
  if (minutes > 0) {
    return `${minutes}分钟前`
  }
  return '刚刚'
}

// 文件变化处理
const handleFileChange = (file: any) => {
  newTask.value.file = file.raw
}

// 图片变化处理
const handleImageChange = (file: any) => {
  newTask.value.image = file.raw
}

// 创建任务
const createTask = () => {
  if (!newTask.value.name.trim()) {
    ElMessage.warning('请输入任务名称')
    return
  }

  if (newTask.value.type === 'text' && !newTask.value.content.trim()) {
    ElMessage.warning('请输入需要翻译的文本')
    return
  }

  if (newTask.value.type === 'document' && !newTask.value.file) {
    ElMessage.warning('请上传文档文件')
    return
  }

  if (newTask.value.type === 'image' && !newTask.value.image) {
    ElMessage.warning('请上传图片')
    return
  }

  creating.value = true

  setTimeout(() => {
    const task: Task = {
      id: Date.now().toString(),
      name: newTask.value.name,
      type: newTask.value.type,
      status: 'pending',
      sourceLang: newTask.value.sourceLang,
      targetLang: newTask.value.targetLang,
      progress: 0,
      createTime: new Date(),
      totalWords: newTask.value.type === 'text' ? newTask.value.content.length : 0
    }

    tasks.value.unshift(task)

    // 重置表单
    newTask.value = {
      name: '',
      type: 'text',
      sourceLang: '中文',
      targetLang: '英语',
      content: '',
      file: null,
      image: null
    }

    creating.value = false
    showCreateTaskDialog.value = false
    ElMessage.success('任务创建成功')
  }, 1000)
}

// 开始任务
const startTask = (task: Task) => {
  task.status = 'processing'
  task.currentStep = '准备开始翻译...'
  ElMessage.success('任务已开始')

  // 模拟进度更新
  simulateProgress(task)
}

// 暂停任务
const pauseTask = (task: Task) => {
  task.status = 'paused'
  task.currentStep = '任务已暂停'
  ElMessage.info('任务已暂停')
}

// 继续任务
const resumeTask = (task: Task) => {
  task.status = 'processing'
  task.currentStep = '继续翻译中...'
  ElMessage.success('任务已继续')
  simulateProgress(task)
}

// 取消任务
const cancelTask = async (task: Task) => {
  try {
    await ElMessageBox.confirm('确定要取消这个任务吗？', '确认取消', {
      type: 'warning'
    })
    task.status = 'cancelled'
    task.progress = 0
    task.currentStep = '任务已取消'
    ElMessage.success('任务已取消')
  } catch {
    // 用户取消
  }
}

// 删除任务
const deleteTask = async (task: Task) => {
  try {
    await ElMessageBox.confirm('确定要删除这个任务吗？此操作不可恢复。', '确认删除', {
      type: 'warning'
    })
    const index = tasks.value.findIndex(t => t.id === task.id)
    if (index > -1) {
      tasks.value.splice(index, 1)
      ElMessage.success('任务已删除')
    }
  } catch {
    // 用户取消
  }
}

// 重试任务
const retryTask = (task: Task) => {
  task.status = 'processing'
  task.progress = 0
  task.error = undefined
  task.currentStep = '重新开始翻译...'
  ElMessage.success('任务已重新开始')
  simulateProgress(task)
}

// 查看详情
const viewDetail = (task: Task) => {
  selectedTask.value = task
  showDetailDialog.value = true
}

// 查看结果
const viewResult = (task: Task) => {
  ElMessage.success('查看结果功能开发中')
}

// 下载结果
const downloadResult = (task: Task) => {
  ElMessage.success('正在下载翻译结果...')
  setTimeout(() => {
    ElMessage.success('下载完成')
  }, 2000)
}

// 编辑任务
const editTask = (task: Task) => {
  newTask.value.name = task.name
  newTask.value.type = task.type
  newTask.value.sourceLang = task.sourceLang
  newTask.value.targetLang = task.targetLang
  showCreateTaskDialog.value = true
}

// 刷新任务列表
const refreshTasks = () => {
  ElMessage.success('任务列表已刷新')
}

// 清理已完成任务
const clearCompletedTasks = async () => {
  try {
    await ElMessageBox.confirm(`确定要清理所有已完成的 ${completedTasks.value} 个任务吗？`, '确认清理', {
      type: 'warning'
    })
    tasks.value = tasks.value.filter(t => t.status !== 'completed')
    ElMessage.success('已完成任务已清理')
  } catch {
    // 用户取消
  }
}

// 模拟进度更新
const simulateProgress = (task: Task) => {
  const interval = setInterval(() => {
    if (task.status !== 'processing') {
      clearInterval(interval)
      return
    }

    task.progress += Math.random() * 15
    task.duration = (task.duration || 0) + 3

    if (task.totalWords) {
      task.translatedWords = Math.floor(task.totalWords * (task.progress / 100))
    }

    // 模拟不同步骤
    const steps = [
      '正在分析文本内容...',
      '正在识别专业术语...',
      '正在翻译核心内容...',
      '正在优化翻译质量...',
      '正在生成最终结果...'
    ]

    if (task.progress < 20) {
      task.currentStep = steps[0]
    } else if (task.progress < 40) {
      task.currentStep = steps[1]
    } else if (task.progress < 60) {
      task.currentStep = steps[2]
    } else if (task.progress < 80) {
      task.currentStep = steps[3]
    } else {
      task.currentStep = steps[4]
    }

    if (task.progress >= 100) {
      task.progress = 100
      task.status = 'completed'
      task.currentStep = '翻译完成'
      clearInterval(interval)
      ElMessage.success(`任务 "${task.name}" 已完成`)
    }
  }, 2000)
}

// 组件挂载时启动定时更新
onMounted(() => {
  // 自动更新进行中的任务
  progressTimer = setInterval(() => {
    tasks.value.forEach(task => {
      if (task.status === 'processing') {
        // 模拟实时更新（在实际应用中，这里会从后端获取最新状态）
        task.duration = (task.duration || 0) + 1
      }
    })
  }, 1000)
})

// 组件卸载时清除定时器
onUnmounted(() => {
  if (progressTimer) {
    clearInterval(progressTimer)
  }
})
</script>

<style scoped>
.task-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
  padding: 24px;
}

/* 头部区域 */
.page-header {
  text-align: center;
  margin-bottom: 32px;
  padding: 40px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 36px;
  font-weight: 600;
  color: white;
  margin: 0 0 12px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.page-subtitle {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  font-weight: 500;
}

/* 统计卡片 */
.stats-cards {
  max-width: 1200px;
  margin: 0 auto 24px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
}

.stat-card.total .stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-card.processing .stat-icon {
  background: linear-gradient(135deg, #409eff 0%, #36cfc9 100%);
}

.stat-card.completed .stat-icon {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
}

.stat-card.failed .stat-icon {
  background: linear-gradient(135deg, #f56c6c 0%, #f78989 100%);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 28px;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

/* 筛选栏 */
.filter-bar {
  max-width: 1200px;
  margin: 0 auto 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 16px 20px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.filter-left,
.filter-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* 任务列表 */
.task-list {
  max-width: 1200px;
  margin: 0 auto;
}

.task-card {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: #909399;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  color: #d9d9d9;
}

.empty-text {
  font-size: 16px;
  margin-bottom: 24px;
}

/* 任务容器 */
.tasks-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 任务项 */
.task-item {
  background: white;
  border-radius: 12px;
  padding: 20px;
  border: 2px solid transparent;
  transition: all 0.3s;
}

.task-item:hover {
  border-color: #667eea;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.15);
}

.task-item.processing {
  border-left: 4px solid #409eff;
}

.task-item.completed {
  border-left: 4px solid #67c23a;
}

.task-item.failed {
  border-left: 4px solid #f56c6c;
}

.task-item.paused {
  border-left: 4px solid #e6a23c;
}

/* 任务头部 */
.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e5e5e5;
}

.task-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.task-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.task-right {
  display: flex;
  gap: 16px;
}

.task-type {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #909399;
  font-size: 14px;
}

/* 任务信息 */
.task-info {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: #909399;
}

.info-value {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

/* 任务进度 */
.task-progress {
  margin-bottom: 16px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.progress-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.progress-value {
  font-size: 14px;
  color: #409eff;
  font-weight: 600;
}

.progress-detail {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  padding: 8px 12px;
  background: #f0f9ff;
  border-radius: 6px;
}

.step-icon {
  color: #409eff;
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.step-text {
  font-size: 13px;
  color: #409eff;
}

/* 任务统计 */
.task-stats {
  margin-bottom: 16px;
}

.stat-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  padding: 12px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
  border-radius: 8px;
}

.stat-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px;
  background: white;
  border-radius: 6px;
}

.stat-count {
  font-size: 20px;
  font-weight: 600;
  color: #409eff;
}

.stat-name {
  font-size: 12px;
  color: #909399;
}

/* 任务错误 */
.task-error {
  margin-bottom: 16px;
}

/* 任务操作 */
.task-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  padding-top: 12px;
  border-top: 1px solid #e5e5e5;
}

/* 上传相关 */
.upload-icon {
  font-size: 48px;
  color: #909399;
  margin-bottom: 16px;
}

.upload-text {
  font-size: 16px;
  color: #303133;
  margin-bottom: 8px;
}

.upload-hint {
  font-size: 13px;
  color: #909399;
}

/* 任务详情 */
.task-detail {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-step {
  background: #f0f9ff;
  border-radius: 8px;
  padding: 16px;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #409eff;
  margin-bottom: 8px;
}

.step-content {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}

.detail-error {
  border-radius: 8px;
}

/* 响应式 */
@media (max-width: 768px) {
  .task-container {
    padding: 16px;
  }

  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .filter-bar {
    flex-direction: column;
    gap: 16px;
  }

  .filter-left,
  .filter-right {
    flex-wrap: wrap;
    justify-content: center;
  }

  .task-info {
    grid-template-columns: repeat(2, 1fr);
  }

  .stat-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }

  .task-info {
    grid-template-columns: 1fr;
  }

  .task-actions {
    flex-wrap: wrap;
  }

  .stat-row {
    grid-template-columns: 1fr;
  }
}
</style>
