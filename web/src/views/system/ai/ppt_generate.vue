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
    <div class="main-content">
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
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Document, Upload, UploadFilled, EditPen, Setting, MagicStick,
  View, Download, ZoomIn, Loading, Picture, Edit, Share,
  Check, Clock, Star
} from '@element-plus/icons-vue'

// 响应式数据
const fileList = ref([])
const inputText = ref('')
const isGenerating = ref(false)
const isDownloading = ref(false)
const generatedPPT = ref(null)
const slideDetailVisible = ref(false)
const selectedSlide = ref(null)
const generationProgress = ref(0)
const generationStatus = ref('')

// 生成选项
const generateOptions = reactive({
  theme: 'business',
  slideCount: 10,
  includeCharts: true,
  language: 'zh'
})

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
const handleFileChange = (file: any, files: any[]) => {
  fileList.value = files
  ElMessage.success(`已添加文件: ${file.name}`)
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

    // 生成PPT数据
    generatedPPT.value = generateMockPPT()
    
    ElMessage.success('PPT生成成功！')
  } catch (error) {
    ElMessage.error('PPT生成失败，请重试')
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
  isDownloading.value = true
  
  try {
    // 模拟下载过程
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 这里应该调用实际的下载API
    ElMessage.success('PPT下载已开始，请查看浏览器下载列表')
  } catch (error) {
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
  selectedSlide.value = generatedPPT.value.slides[index]
  slideDetailVisible.value = true
}

// 关闭幻灯片详情
const closeSlideDetail = () => {
  slideDetailVisible.value = false
  selectedSlide.value = null
}

// 组件挂载
onMounted(() => {
  // 可以在这里加载用户的历史记录等
})
</script>

<style scoped>
.ppt-generate-container {
  padding: 24px;
  background-color: #f5f5f5;
  min-height: 100vh;
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
</style>