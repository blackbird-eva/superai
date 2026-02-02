<template>
  <div class="ppt-generate-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><Document /></el-icon>
        PPT智能生成
      </h2>
      <p class="page-desc">上传文档、图片或其他内容，AI将自动为您生成专业的PPT演示文稿</p>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content" v-if="currentTab === 'generate'">
      <!-- 左侧上传区域 -->
      <div class="left-panel">
        <el-card class="upload-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><Upload /></el-icon>
                内容上传
              </span>
            </div>
          </template>

          <!-- 上传区域 -->
          <div class="upload-section">
            <el-upload
              class="upload-area"
              drag
              :auto-upload="false"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              :file-list="fileList"
              accept=".txt,.md,.doc,.docx,.pdf,.jpg,.jpeg,.png,.gif,.ppt,.pptx"
              multiple
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                拖拽文件到此处或 <em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持 txt, md, doc, pdf, 图片等格式，单个文件不超过 10MB
                </div>
              </template>
            </el-upload>
          </div>

          <!-- 文本输入区域 -->
          <div class="text-input-section">
            <div class="section-title">
              <el-icon><EditPen /></el-icon>
              或直接输入文本内容
            </div>
            <el-input
              v-model="inputText"
              type="textarea"
              :rows="6"
              placeholder="请输入您想要生成PPT的文本内容，支持Markdown格式..."
              class="text-input"
            />
          </div>

          <!-- 生成选项 -->
          <div class="options-section">
            <div class="section-title">
              <el-icon><Setting /></el-icon>
              生成选项
            </div>
            
            <el-form :model="generateOptions" label-width="80px" size="default">
              <el-form-item label="主题风格">
                <el-select v-model="generateOptions.theme" placeholder="选择PPT主题风格">
                  <el-option label="商务简约" value="business" />
                  <el-option label="科技现代" value="tech" />
                  <el-option label="教育培训" value="education" />
                  <el-option label="创意活泼" value="creative" />
                  <el-option label="学术正式" value="academic" />
                </el-select>
              </el-form-item>

              <el-form-item label="幻灯片数量">
                <el-slider
                  v-model="generateOptions.slideCount"
                  :min="5"
                  :max="30"
                  :step="1"
                  show-input
                  :show-input-controls="false"
                />
              </el-form-item>

              <el-form-item label="包含图表">
                <el-switch v-model="generateOptions.includeCharts" />
              </el-form-item>

              <el-form-item label="语言">
                <el-radio-group v-model="generateOptions.language">
                  <el-radio label="zh">中文</el-radio>
                  <el-radio label="en">英文</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-form>
          </div>

          <!-- 生成按钮 -->
          <div class="generate-section">
            <el-button
              type="primary"
              size="large"
              :loading="isGenerating"
              :disabled="!canGenerate"
              @click="generatePPT"
              class="generate-btn"
            >
              <el-icon><MagicStick /></el-icon>
              {{ isGenerating ? '正在生成...' : '开始生成PPT' }}
            </el-button>
          </div>
        </el-card>
      </div>

      <!-- 右侧预览区域 -->
      <div class="right-panel">
        <el-card class="preview-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><View /></el-icon>
                生成预览
              </span>
              <div class="header-actions" v-if="generatedPPT">
                <el-button type="success" @click="downloadPPT" :loading="isDownloading">
                  <el-icon><Download /></el-icon>
                  下载PPT
                </el-button>
                <el-button @click="previewPPT">
                  <el-icon><ZoomIn /></el-icon>
                  预览
                </el-button>
              </div>
            </div>
          </template>

          <!-- 初始状态 -->
          <div v-if="!generatedPPT && !isGenerating" class="initial-state">
            <div class="empty-icon">📊</div>
            <h3>等待生成PPT</h3>
            <p>上传内容或输入文本后，点击生成按钮即可创建PPT</p>
          </div>

          <!-- 生成中状态 -->
          <div v-if="isGenerating" class="generating-state">
            <el-progress
              :percentage="generationProgress"
              :stroke-width="8"
              status="success"
              :duration="0.5"
            />
            <div class="generating-text">
              <el-icon class="rotating"><Loading /></el-icon>
              <span>{{ generationStatus }}</span>
            </div>
            <div class="progress-steps">
              <div v-for="(step, index) in progressSteps" :key="index" 
                   class="step-item" :class="{ active: step.active, completed: step.completed }">
                <el-icon><component :is="step.icon" /></el-icon>
                <span>{{ step.text }}</span>
              </div>
            </div>
          </div>

          <!-- 生成完成状态 -->
          <div v-if="generatedPPT" class="generated-state">
            <!-- PPT缩略图列表 -->
            <div class="ppt-preview">
              <div class="ppt-info">
                <h4>{{ generatedPPT.title }}</h4>
                <p>{{ generatedPPT.description }}</p>
                <div class="ppt-meta">
                  <el-tag size="small" type="success">{{ generatedPPT.slideCount }}张幻灯片</el-tag>
                  <el-tag size="small" type="info">{{ generatedPPT.theme }}</el-tag>
                  <el-tag size="small" type="warning">{{ generatedPPT.createTime }}</el-tag>
                </div>
              </div>

              <div class="slides-preview">
                <div v-for="(slide, index) in generatedPPT.slides" :key="index" 
                     class="slide-item" @click="viewSlideDetail(index)">
                  <div class="slide-number">#{{ index + 1 }}</div>
                  <div class="slide-content" :class="slide.layout">
                    <div class="slide-title">{{ slide.title }}</div>
                    <div class="slide-body">
                      <p v-if="slide.content">{{ slide.content }}</p>
                      <div v-if="slide.bullets" class="bullet-points">
                        <div v-for="(bullet, i) in slide.bullets.slice(0, 3)" :key="i" class="bullet">
                          • {{ bullet }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- PPT文件列表 -->
    <div class="ppt-list-section" v-if="currentTab === 'list'">
      <el-card class="list-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><Folder /></el-icon>
              我的PPT文件
            </span>
            <div class="header-actions">
              <el-button type="primary" @click="currentTab = 'generate'">
                <el-icon><Plus /></el-icon>
                新建PPT
              </el-button>
            </div>
          </div>
        </template>

        <!-- 搜索栏 -->
        <div class="search-bar">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索PPT标题..."
            clearable
            @clear="loadPPTList"
            @keyup.enter="loadPPTList"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" @click="loadPPTList">搜索</el-button>
        </div>

        <!-- PPT列表表格 -->
        <el-table
          :data="pptList"
          v-loading="listLoading"
          style="width: 100%"
          @sort-change="handleSortChange"
        >
          <el-table-column prop="title" label="PPT标题" min-width="200" sortable>
            <template #default="{ row }">
              <div class="ppt-title-cell">
                <el-icon><Document /></el-icon>
                <span>{{ row.title }}</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="theme" label="主题" width="120">
            <template #default="{ row }">
              <el-tag size="small">{{ getThemeLabel(row.theme) }}</el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="slide_count" label="幻灯片数" width="100" sortable align="center" />

          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">
                {{ getStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="create_time" label="创建时间" width="180" sortable>
            <template #default="{ row }">
              {{ formatDate(row.create_time) }}
            </template>
          </el-table-column>

          <el-table-column prop="download_count" label="下载次数" width="100" sortable align="center" />

          <el-table-column label="操作" width="240" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="viewPPT(row)">
                <el-icon><View /></el-icon>
                查看
              </el-button>
              <el-button link type="warning" @click="editPPT(row)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button link type="success" @click="downloadPPTFromList(row)">
                <el-icon><Download /></el-icon>
                下载
              </el-button>
              <el-popconfirm
                title="确定要删除这个PPT吗？"
                @confirm="deletePPT(row.id)"
              >
                <template #reference>
                  <el-button link type="danger">
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="loadPPTList"
            @current-change="loadPPTList"
          />
        </div>
      </el-card>
    </div>

    <!-- 切换标签页 -->
    <div class="tab-switcher">
      <el-button-group>
        <el-button
          :type="currentTab === 'generate' ? 'primary' : ''"
          @click="currentTab = 'generate'"
        >
          <el-icon><MagicStick /></el-icon>
          生成PPT
        </el-button>
        <el-button
          :type="currentTab === 'list' ? 'primary' : ''"
          @click="currentTab = 'list'; loadPPTList()"
        >
          <el-icon><Folder /></el-icon>
          我的PPT
          <el-badge :value="total" :max="99" class="badge" />
        </el-button>
      </el-button-group>
    </div>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑PPT"
      width="600px"
      :before-close="closeEditDialog"
    >
      <el-form
        v-if="editingPPT"
        :model="editingPPT"
        :rules="editRules"
        ref="editFormRef"
        label-width="100px"
      >
        <el-form-item label="PPT标题" prop="title">
          <el-input v-model="editingPPT.title" placeholder="请输入PPT标题" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="editingPPT.description"
            type="textarea"
            :rows="4"
            placeholder="请输入描述"
          />
        </el-form-item>
        <el-form-item label="主题" prop="theme">
          <el-select v-model="editingPPT.theme" placeholder="选择主题">
            <el-option label="商务简约" value="business" />
            <el-option label="科技现代" value="tech" />
            <el-option label="教育培训" value="education" />
            <el-option label="创意活泼" value="creative" />
            <el-option label="学术正式" value="academic" />
          </el-select>
        </el-form-item>
        <el-form-item label="幻灯片数">
          <el-input-number v-model="editingPPT.slide_count" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="editingPPT.status" placeholder="选择状态">
            <el-option label="待处理" value="pending" />
            <el-option label="生成中" value="generating" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closeEditDialog">取消</el-button>
          <el-button type="primary" @click="savePPT" :loading="saving">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 幻灯片详情对话框 -->
    <el-dialog
      v-model="slideDetailVisible"
      title="幻灯片详情"
      width="60%"
      :before-close="closeSlideDetail"
    >
      <div v-if="selectedSlide" class="slide-detail">
        <div class="detail-header">
          <h3>{{ selectedSlide.title }}</h3>
          <el-tag>{{ selectedSlide.layout }}</el-tag>
        </div>
        <div class="detail-content">
          <div v-if="selectedSlide.content" class="content-section">
            <h4>正文内容</h4>
            <p>{{ selectedSlide.content }}</p>
          </div>
          <div v-if="selectedSlide.bullets" class="bullets-section">
            <h4>要点列表</h4>
            <ul>
              <li v-for="(bullet, index) in selectedSlide.bullets" :key="index">{{ bullet }}</li>
            </ul>
          </div>
          <div v-if="selectedSlide.note" class="note-section">
            <h4>演讲者备注</h4>
            <p>{{ selectedSlide.note }}</p>
          </div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closeSlideDetail">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Document, Upload, UploadFilled, EditPen, Setting, MagicStick,
  View, Download, ZoomIn, Loading, Edit, Folder, Plus, Search, Delete
} from '@element-plus/icons-vue'
import { GeneratePPT, DownloadPPT, GetPPTList, GetPPTDetail, UpdatePPT, DeletePPT, UploadFileAndGeneratePPT, ReadUploadFile } from './api'

// 响应式数据
const fileList = ref<any[]>([])
const inputText = ref('')
const isGenerating = ref(false)
const isDownloading = ref(false)
const generatedPPT = ref<any | null>(null)
const slideDetailVisible = ref(false)
const selectedSlide = ref<any | null>(null)
const generationProgress = ref(0)
const generationStatus = ref('')
const pptFilePath = ref('')
const pptFileName = ref('')

// CRUD相关数据
const currentTab = ref('generate')
const pptList = ref<any[]>([])
const listLoading = ref(false)
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const editDialogVisible = ref(false)
const editingPPT = ref<any | null>(null)
const saving = ref(false)
const editFormRef = ref<any | null>(null)

// 生成选项
const generateOptions = reactive({
  theme: 'business',
  slideCount: 10,
  includeCharts: true,
  language: 'zh'
})

// 编辑表单验证规则
const editRules = {
  title: [{ required: true, message: '请输入PPT标题', trigger: 'blur' }],
  description: [{ required: false }],
  theme: [{ required: true, message: '请选择主题', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

// 进度步骤
const progressSteps = ref([
  { text: '分析内容', icon: 'Edit', active: false, completed: false },
  { text: '提取要点', icon: 'Share', active: false, completed: false },
  { text: '设计布局', icon: 'Picture', active: false, completed: false },
  { text: '生成幻灯片', icon: 'Star', active: false, completed: false },
  { text: '优化排版', icon: 'Check', active: false, completed: false }
])

// 计算属性
const canGenerate = computed(() => {
  return (fileList.value.length > 0 || inputText.value.trim()) && !isGenerating.value
})

// 文件上传处理
const handleFileChange = async (file: any, files: any[]) => {
  fileList.value = files
  
  // 验证文件大小和类型
  const maxSize = 10 * 1024 * 1024 // 10MB
  if (file.size > maxSize) {
    ElMessage.error(`文件 ${file.name} 超过10MB限制`)
    // 移除超大文件
    fileList.value = fileList.value.filter((f: any) => f.uid !== file.uid)
    return
  }
  
  // 获取文件扩展名
  const fileName = file.name.toLowerCase()
  const fileExtension = fileName.split('.').pop()
  
  // 支持的扩展名列表
  const supportedExtensions = [
    'txt', 'md',
    'pdf',
    'doc', 'docx',
    'jpg', 'jpeg', 'png', 'gif', 'bmp',
    'ppt', 'pptx'
  ]
  
  // 支持的MIME类型
  const supportedMimeTypes = [
    'text/plain', 'text/markdown',
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/msword',
    'image/jpeg', 'image/png', 'image/gif', 'image/bmp',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/vnd.ms-powerpoint'
  ]
  
  // 检查文件是否支持（通过扩展名或MIME类型）
  const isExtensionSupported = fileExtension && supportedExtensions.includes(fileExtension)
  const isMimeTypeSupported = file.type && supportedMimeTypes.includes(file.type)
  
  // 更宽松的验证：扩展名支持就认为是支持的格式
  if (!isExtensionSupported && !isMimeTypeSupported) {
    ElMessage.warning(`文件 ${file.name} 格式可能不受支持，但仍会尝试处理`)
  } else {
    const supportReason = isExtensionSupported ? '扩展名' : 'MIME类型'
    console.log(`文件 ${file.name} 通过${supportReason}验证支持`)
  }
  
  ElMessage.success(`已添加文件: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)}MB)`)
  
  // 如果是文本文件，尝试读取内容并显示在文本框中
  if (file.type.startsWith('text/')) {
    try {
      const content = await ReadUploadFile(file.raw)
      if (content && content.trim()) {
        // 如果文本框为空，自动填入文件内容
        if (!inputText.value.trim()) {
          inputText.value = content.substring(0, 5000) // 限制长度
          ElMessage.info(`已自动填充文件内容到文本框（前5000字符）`)
        }
      }
    } catch (error) {
      console.warn('无法读取文件内容:', error)
    }
  }
}

const handleFileRemove = (file: any, files: any[]) => {
  fileList.value = files
  ElMessage.info(`已移除文件: ${file.name}`)
}

// 生成PPT
const generatePPT = async () => {
  if (!canGenerate.value) return

  isGenerating.value = true
  generationProgress.value = 0

  try {
    // 重置进度步骤
    progressSteps.value.forEach(step => {
      step.active = false
      step.completed = false
    })

    // 模拟生成过程
    await simulateGenerationProcess()

    let response
    
    // 如果有文件上传，使用文件上传API
    if (fileList.value.length > 0) {
      isGenerating.value = true
      generationStatus.value = '正在准备上传...'
      
      try {
        // 创建FormData对象
        const formData = new FormData()
        
        // 添加文件
        fileList.value.forEach(file => {
          formData.append('files', file.raw)
        })
        
        // 添加其他参数
        formData.append('title', inputText.value || '上传文件生成的PPT')
        formData.append('theme', generateOptions.theme)
        formData.append('slide_count', generateOptions.slideCount.toString())
        formData.append('include_charts', generateOptions.includeCharts.toString())
        formData.append('language', generateOptions.language)
        formData.append('source_type', 'file_upload')
        
        // 如果有文本内容，也添加到描述中
        if (inputText.value.trim()) {
          formData.append('content_summary', inputText.value.substring(0, 2000))
        }
        
        // 重置进度步骤
        progressSteps.value.forEach(step => {
          step.active = false
          step.completed = false
        })
        
        // 模拟文件上传进度
        await simulateFileUploadProgress()
        
        // 调用文件上传API
        response = await UploadFileAndGeneratePPT(formData)
        
        ElMessage.success('文件上传并生成PPT成功！')
      } catch (uploadError: any) {
        console.error('文件上传失败:', uploadError)
        ElMessage.error(uploadError.response?.data?.msg || '文件上传失败，请重试')
        isGenerating.value = false
        return
      }
    } else {
      // 如果没有文件，使用原有的文本生成API
      const requestData = {
        text: inputText.value,
        theme: generateOptions.theme,
        slide_count: generateOptions.slideCount,
        include_charts: generateOptions.includeCharts,
        language: generateOptions.language
      }
      
      // 重置进度步骤
      progressSteps.value.forEach(step => {
        step.active = false
        step.completed = false
      })
      
      // 模拟生成过程
      await simulateGenerationProcess()
      
      // 调用API生成PPT
      response = await GeneratePPT(requestData)
    }

    // 保存生成的PPT数据和文件信息
    generatedPPT.value = {
      title: response.data.title,
      description: response.data.description,
      theme: response.data.theme,
      slideCount: response.data.slide_count,
      createTime: response.data.create_time,
      slides: response.data.slides
    }

    // 保存PPT文件路径，用于下载
    if (response.data.ppt_file_path) {
      pptFilePath.value = response.data.ppt_file_path
      pptFileName.value = response.data.ppt_file_name
    }

    ElMessage.success('PPT生成成功！')
  } catch (error: any) {
    console.error('PPT生成失败:', error)
    ElMessage.error(error.response?.data?.msg || 'PPT生成失败，请重试')
  } finally {
    isGenerating.value = false
    generationProgress.value = 100
  }
}

// 模拟生成过程
const simulateGenerationProcess = async () => {
  const steps = [
    { text: '正在分析上传内容...', duration: 1000 },
    { text: '提取关键信息和要点...', duration: 1500 },
    { text: '设计幻灯片布局和样式...', duration: 2000 },
    { text: '生成幻灯片内容...', duration: 1500 },
    { text: '优化排版和视觉效果...', duration: 1000 }
  ]

  for (let i = 0; i < steps.length; i++) {
    const step = steps[i]
    const progressStep = progressSteps.value[i]
    
    progressStep.active = true
    generationStatus.value = step.text
    
    await new Promise(resolve => setTimeout(resolve, step.duration))
    
    progressStep.active = false
    progressStep.completed = true
    generationProgress.value = ((i + 1) / steps.length) * 100
  }
}

// 真实文件上传进度模拟
const simulateFileUploadProgress = async () => {
  const uploadSteps = [
    { text: '正在上传文件...', duration: 2000 },
    { text: '解析文件内容...', duration: 1500 },
    { text: 'AI分析文档结构...', duration: 2500 },
    { text: '提取关键信息...', duration: 2000 },
    { text: '生成PPT内容...', duration: 3000 }
  ]

  for (let i = 0; i < uploadSteps.length; i++) {
    const step = uploadSteps[i]
    const progressStep = progressSteps.value[i]
    
    progressStep.active = true
    generationStatus.value = step.text
    
    await new Promise(resolve => setTimeout(resolve, step.duration))
    
    progressStep.active = false
    progressStep.completed = true
    generationProgress.value = ((i + 1) / uploadSteps.length) * 100
  }
}

// 生成模拟PPT数据
const generateMockPPT = () => {
  const themes = {
    business: '商务简约风格',
    tech: '科技现代风格', 
    education: '教育培训风格',
    creative: '创意活泼风格',
    academic: '学术正式风格'
  }

  const titles = [
    '人工智能发展趋势报告',
    '数字化转型战略规划',
    '产品营销策略分析',
    '团队协作最佳实践',
    '创新技术应用场景'
  ]

  const slideTemplates = [
    {
      layout: 'title-content',
      title: '封面页',
      content: '展示主要观点和核心信息'
    },
    {
      layout: 'title-bullets',
      title: '目录概览',
      bullets: ['背景介绍', '现状分析', '解决方案', '实施计划', '总结展望']
    },
    {
      layout: 'title-content',
      title: '背景介绍',
      content: '阐述项目或话题的背景和发展历程，为后续内容做铺垫。'
    },
    {
      layout: 'title-bullets',
      title: '关键挑战',
      bullets: ['技术复杂度高', '资源投入不足', '团队协作困难', '市场变化快速']
    },
    {
      layout: 'title-content',
      title: '解决方案',
      content: '提出针对性的解决策略和实施方案，确保目标的有效达成。'
    }
  ]

  const slides = []
  const slideCount = Math.min(generateOptions.slideCount, 15)
  
  for (let i = 0; i < slideCount; i++) {
    const template = slideTemplates[i % slideTemplates.length]
    slides.push({
      ...template,
      note: `这是第${i + 1}张幻灯片的演讲者备注，可以在这里添加详细的讲解要点。`
    })
  }

  return {
    title: titles[Math.floor(Math.random() * titles.length)],
    description: `基于您提供的内容生成的${themes[generateOptions.theme]}PPT演示文稿`,
    theme: themes[generateOptions.theme],
    slideCount: slides.length,
    createTime: new Date().toLocaleString('zh-CN'),
    slides: slides
  }
}

// 下载PPT
const downloadPPT = async () => {
  if (!pptFilePath.value) {
    ElMessage.warning('请先生成PPT')
    return
  }

  isDownloading.value = true

  try {
    // 调用下载API
    const response = await DownloadPPT(pptFilePath.value)

    // 创建Blob和下载链接
    const blob = new Blob([response], {
      type: 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    })

    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = pptFileName.value || `AI生成PPT_${new Date().getTime()}.pptx`

    document.body.appendChild(link)
    link.click()

    // 清理
    window.URL.revokeObjectURL(url)
    document.body.removeChild(link)

    ElMessage.success('PPT下载成功！')
  } catch (error: any) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败，请重试')
  } finally {
    isDownloading.value = false
  }
}

// 预览PPT
const previewPPT = () => {
  ElMessage.info('预览功能开发中，敬请期待')
}

// 查看幻灯片详情
const viewSlideDetail = (index: number) => {
  if (generatedPPT.value && generatedPPT.value.slides) {
    selectedSlide.value = generatedPPT.value.slides[index]
    slideDetailVisible.value = true
  }
}

// 关闭幻灯片详情
const closeSlideDetail = () => {
  slideDetailVisible.value = false
  selectedSlide.value = null
}

// CRUD功能实现

// 加载PPT列表
const loadPPTList = async () => {
  listLoading.value = true
  try {
    const response = await GetPPTList({
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchKeyword.value
    })
    pptList.value = response.data.results || response.data || []
    total.value = response.data.count || response.data.length || 0
  } catch (error: any) {
    console.error('加载PPT列表失败:', error)
    ElMessage.error('加载PPT列表失败')
  } finally {
    listLoading.value = false
  }
}

// 查看PPT详情
const viewPPT = async (ppt: any) => {
  try {
    const response = await GetPPTDetail(ppt.id)
    generatedPPT.value = {
      title: response.data.title,
      description: response.data.description,
      theme: getThemeLabel(response.data.theme),
      slideCount: response.data.slide_count,
      createTime: formatDate(response.data.create_time),
      slides: response.data.slides || []
    }
    pptFilePath.value = response.data.ppt_file_path
    pptFileName.value = response.data.ppt_file_name || `${response.data.title}.pptx`
    currentTab.value = 'generate'
    ElMessage.success('加载PPT成功')
  } catch (error: any) {
    console.error('加载PPT详情失败:', error)
    ElMessage.error('加载PPT详情失败')
  }
}

// 编辑PPT
const editPPT = (ppt: any) => {
  editingPPT.value = {
    id: ppt.id,
    title: ppt.title,
    description: ppt.description || '',
    theme: ppt.theme,
    slide_count: ppt.slide_count,
    status: ppt.status
  }
  editDialogVisible.value = true
}

// 保存PPT
const savePPT = async () => {
  if (!editFormRef.value || !editingPPT.value) return

  try {
    await editFormRef.value.validate()
    saving.value = true

    await UpdatePPT({
      id: editingPPT.value.id,
      title: editingPPT.value.title,
      description: editingPPT.value.description,
      theme: editingPPT.value.theme,
      slide_count: editingPPT.value.slide_count,
      status: editingPPT.value.status
    })
    ElMessage.success('保存成功')
    closeEditDialog()
    loadPPTList()
  } catch (error: any) {
    if (error.response?.data) {
      ElMessage.error(error.response.data.msg || '保存失败')
    } else {
      console.error('保存失败:', error)
    }
  } finally {
    saving.value = false
  }
}

// 删除PPT
const deletePPT = async (id: string) => {
  try {
    await DeletePPT(id)
    ElMessage.success('删除成功')
    loadPPTList()
  } catch (error: any) {
    console.error('删除失败:', error)
    ElMessage.error(error.response?.data?.msg || '删除失败')
  }
}

// 从列表下载PPT
const downloadPPTFromList = async (ppt: any) => {
  isDownloading.value = true
  try {
    const response = await DownloadPPT(ppt.ppt_file_path || ppt.file_path)
    const blob = new Blob([response], {
      type: 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = ppt.ppt_file_name || `${ppt.title}.pptx`
    document.body.appendChild(link)
    link.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(link)
    ElMessage.success('下载成功')
  } catch (error: any) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败')
  } finally {
    isDownloading.value = false
  }
}

// 关闭编辑对话框
const closeEditDialog = () => {
  editDialogVisible.value = false
  editingPPT.value = null
}

// 处理排序变化
const handleSortChange = ({ prop, order }: any) => {
  // 可以在这里实现排序逻辑
  console.log('排序:', prop, order)
  loadPPTList()
}

// 工具函数
const getThemeLabel = (theme: string) => {
  const themes: { [key: string]: string } = {
    business: '商务简约',
    tech: '科技现代',
    education: '教育培训',
    creative: '创意活泼',
    academic: '学术正式'
  }
  return themes[theme] || theme
}

const getStatusType = (status: string) => {
  const types: { [key: string]: string } = {
    pending: 'info',
    generating: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return types[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const labels: { [key: string]: string } = {
    pending: '待处理',
    generating: '生成中',
    completed: '已完成',
    failed: '失败'
  }
  return labels[status] || status
}

const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 组件挂载
onMounted(() => {
  // 初始加载PPT列表
  loadPPTList()
})
</script>

<style scoped>
.ppt-generate-container {
  padding: 24px;
  background-color: #f5f5f5;
  min-height: 100vh;
  position: relative;
}

.page-header {
  margin-bottom: 24px;
  text-align: center;
}

.page-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #333;
}

.page-desc {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.main-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  height: calc(100vh - 140px);
}

.left-panel,
.right-panel {
  display: flex;
  flex-direction: column;
}

.upload-card,
.preview-card {
  flex: 1;
  border: none;
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-weight: 500;
  color: #333;
}

.upload-section {
  margin-bottom: 24px;
}

:deep(.upload-area .el-upload-dragger) {
  border-radius: 12px;
  border: 2px dashed #d9d9d9;
  background-color: #fafafa;
  transition: all 0.3s;
}

:deep(.upload-area .el-upload-dragger:hover) {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.text-input-section {
  margin-bottom: 24px;
}

.text-input {
  width: 100%;
}

:deep(.text-input .el-textarea__inner) {
  border-radius: 8px;
  font-family: 'Monaco', 'Consolas', monospace;
}

.options-section {
  margin-bottom: 24px;
}

:deep(.options-section .el-form-item) {
  margin-bottom: 18px;
}

.generate-section {
  text-align: center;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.generate-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  border-radius: 24px;
}

.initial-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  text-align: center;
  color: #999;
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.generating-state {
  padding: 40px;
  text-align: center;
}

.generating-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin: 20px 0;
  color: #666;
}

.rotating {
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  margin-top: 30px;
  position: relative;
}

.progress-steps::before {
  content: '';
  position: absolute;
  top: 15px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: #e5e5e5;
  z-index: 1;
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  position: relative;
  z-index: 2;
  background-color: #f5f5f5;
  padding: 0 8px;
}

.step-item .el-icon {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: #e5e5e5;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: #999;
  transition: all 0.3s;
}

.step-item.active .el-icon {
  background-color: #409eff;
  color: white;
}

.step-item.completed .el-icon {
  background-color: #67c23a;
  color: white;
}

.step-item span {
  font-size: 12px;
  color: #666;
  white-space: nowrap;
}

.generated-state {
  height: 100%;
  overflow-y: auto;
}

.ppt-preview {
  padding: 16px;
}

.ppt-info {
  margin-bottom: 24px;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
}

.ppt-info h4 {
  margin: 0 0 8px 0;
  font-size: 18px;
}

.ppt-info p {
  margin: 0 0 12px 0;
  opacity: 0.9;
}

.ppt-meta {
  display: flex;
  gap: 8px;
}

.slides-preview {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.slide-item {
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  background-color: white;
}

.slide-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.slide-number {
  background-color: #f5f5f5;
  padding: 8px;
  text-align: center;
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.slide-content {
  padding: 16px;
  min-height: 120px;
}

.slide-title {
  font-weight: 600;
  margin-bottom: 12px;
  color: #333;
  font-size: 14px;
}

.slide-body p {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: #666;
  line-height: 1.4;
}

.bullet-points {
  font-size: 12px;
}

.bullet {
  margin-bottom: 4px;
  color: #666;
  line-height: 1.3;
}

.slide-detail {
  max-height: 500px;
  overflow-y: auto;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.detail-header h3 {
  margin: 0;
  color: #333;
}

.detail-content h4 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 14px;
}

.content-section,
.bullets-section,
.note-section {
  margin-bottom: 24px;
}

.content-section p,
.note-section p {
  margin: 0;
  line-height: 1.6;
  color: #666;
}

.bullets-section ul {
  margin: 0;
  padding-left: 20px;
}

.bullets-section li {
  margin-bottom: 8px;
  color: #666;
  line-height: 1.5;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .ppt-generate-container {
    padding: 16px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .slides-preview {
    grid-template-columns: 1fr;
  }
}

/* PPT列表相关样式 */
.ppt-list-section {
  max-width: 1400px;
  margin: 0 auto;
}

.list-card {
  border: none;
  border-radius: 12px;
}

.search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.search-bar .el-input {
  flex: 1;
  max-width: 400px;
}

.ppt-title-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.tab-switcher {
  position: fixed;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
}

.badge {
  margin-left: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>