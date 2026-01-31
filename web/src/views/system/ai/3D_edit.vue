<template>
  <div class="three-d-edit-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <el-icon class="title-icon"><Box /></el-icon>
          3D 文件编辑器
        </h1>
        <p class="page-subtitle">支持多种 3D 格式文件的在线编辑、预览与转换</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" icon="Plus" @click="importModel">
          导入模型
        </el-button>
        <el-button type="success" icon="Download" @click="exportModel">
          导出文件
        </el-button>
        <el-button type="warning" icon="Setting" @click="openSettings">
          设置
        </el-button>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <el-row :gutter="20">
        <!-- 左侧工具栏 -->
        <el-col :span="3">
          <el-card class="toolbar-card">
            <template #header>
              <div class="card-header">
                <span>工具栏</span>
              </div>
            </template>
            
            <div class="toolbar-section">
              <h4>视图控制</h4>
              <div class="tool-buttons">
                <el-button-group vertical>
                  <el-button icon="ZoomIn" @click="zoomIn" title="放大" />
                  <el-button icon="ZoomOut" @click="zoomOut" title="缩小" />
                  <el-button icon="RefreshLeft" @click="rotateLeft" title="左旋转" />
                  <el-button icon="RefreshRight" @click="rotateRight" title="右旋转" />
                  <el-button icon="Refresh" @click="resetView" title="重置视图" />
                </el-button-group>
              </div>
            </div>

            <div class="toolbar-section">
              <h4>编辑工具</h4>
              <div class="tool-buttons">
                <el-button-group vertical>
                  <el-button icon="Crop" @click="toggleSelect" :type="tools.select ? 'primary' : ''" title="选择" />
                  <el-button icon="Edit" @click="toggleMove" :type="tools.move ? 'primary' : ''" title="移动" />
                  <el-button icon="ScaleToOriginal" @click="toggleScale" :type="tools.scale ? 'primary' : ''" title="缩放" />
                  <el-button icon="RotateRight" @click="toggleRotate" :type="tools.rotate ? 'primary' : ''" title="旋转" />
                </el-button-group>
              </div>
            </div>

            <div class="toolbar-section">
              <h4>显示模式</h4>
              <el-radio-group v-model="displayMode" @change="changeDisplayMode">
                <el-radio-button label="wireframe">线框</el-radio-button>
                <el-radio-button label="solid">实体</el-radio-button>
                <el-radio-button label="texture">纹理</el-radio-button>
              </el-radio-group>
            </div>
          </el-card>
        </el-col>

        <!-- 中央 3D 视图区 -->
        <el-col :span="13">
          <el-card class="viewer-card">
            <template #header>
              <div class="card-header">
                <div class="viewer-title">
                  <span v-if="currentModel">当前模型: {{ currentModel.name }}</span>
                  <span v-else>3D 视图区</span>
                </div>
                <div class="viewer-controls">
                  <el-button-group>
                    <el-button icon="VideoPlay" @click="playAnimation" :disabled="!currentModel" />
                    <el-button icon="VideoPause" @click="pauseAnimation" :disabled="!currentModel" />
                    <el-button icon="Refresh" @click="refreshView" />
                  </el-button-group>
                </div>
              </div>
            </template>
            
            <!-- 3D 画布容器 -->
            <div class="viewer-container" ref="viewerContainer">
              <canvas ref="canvas3d" class="three-canvas"></canvas>
              
              <!-- 空状态 -->
              <div v-if="!currentModel" class="empty-state">
                <el-empty description="暂无 3D 模型，请先导入文件">
                  <el-button type="primary" icon="Plus" @click="importModel">
                    导入模型
                  </el-button>
                </el-empty>
              </div>

              <!-- 加载状态 -->
              <div v-if="loading" class="loading-overlay">
                <el-progress type="circle" :percentage="loadProgress" :width="80" />
                <p>加载中... {{ loadProgress }}%</p>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 右侧属性面板 -->
        <el-col :span="8">
          <el-card class="properties-card">
            <template #header>
              <div class="card-header">
                <span>属性面板</span>
                <el-button icon="Refresh" size="small" @click="refreshProperties" />
              </div>
            </template>
            
            <!-- 模型信息 -->
            <div v-if="currentModel" class="property-section">
              <h4>模型信息</h4>
              <el-descriptions :column="1" size="small">
                <el-descriptions-item label="文件名">{{ currentModel.name }}</el-descriptions-item>
                <el-descriptions-item label="格式">{{ currentModel.format }}</el-descriptions-item>
                <el-descriptions-item label="大小">{{ formatFileSize(currentModel.size) }}</el-descriptions-item>
                <el-descriptions-item label="顶点数">{{ currentModel.vertices }}</el-descriptions-item>
                <el-descriptions-item label="面数">{{ currentModel.faces }}</el-descriptions-item>
                <el-descriptions-item label="创建时间">{{ formatDate(currentModel.createTime) }}</el-descriptions-item>
              </el-descriptions>
            </div>

            <!-- 变换属性 -->
            <div v-if="currentModel" class="property-section">
              <h4>变换</h4>
              <el-form label-width="60px">
                <el-form-item label="位置">
                  <el-row :gutter="5">
                    <el-col :span="7">
                      <el-input-number v-model="transform.position.x" size="small" :precision="2" />
                    </el-col>
                    <el-col :span="7">
                      <el-input-number v-model="transform.position.y" size="small" :precision="2" />
                    </el-col>
                    <el-col :span="7">
                      <el-input-number v-model="transform.position.z" size="small" :precision="2" />
                    </el-col>
                  </el-row>
                </el-form-item>
                
                <el-form-item label="旋转">
                  <el-row :gutter="5">
                    <el-col :span="7">
                      <el-input-number v-model="transform.rotation.x" size="small" :precision="1" />
                    </el-col>
                    <el-col :span="7">
                      <el-input-number v-model="transform.rotation.y" size="small" :precision="1" />
                    </el-col>
                    <el-col :span="7">
                      <el-input-number v-model="transform.rotation.z" size="small" :precision="1" />
                    </el-col>
                  </el-row>
                </el-form-item>
                
                <el-form-item label="缩放">
                  <el-row :gutter="5">
                    <el-col :span="7">
                      <el-input-number v-model="transform.scale.x" size="small" :precision="2" />
                    </el-col>
                    <el-col :span="7">
                      <el-input-number v-model="transform.scale.y" size="small" :precision="2" />
                    </el-col>
                    <el-col :span="7">
                      <el-input-number v-model="transform.scale.z" size="small" :precision="2" />
                    </el-col>
                  </el-row>
                </el-form-item>
              </el-form>
            </div>

            <!-- 材质属性 -->
            <div v-if="currentModel" class="property-section">
              <h4>材质</h4>
              <el-form label-width="60px">
                <el-form-item label="颜色">
                  <el-color-picker v-model="material.color" show-alpha />
                </el-form-item>
                <el-form-item label="金属度">
                  <el-slider v-model="material.metalness" :min="0" :max="1" :step="0.1" />
                </el-form-item>
                <el-form-item label="粗糙度">
                  <el-slider v-model="material.roughness" :min="0" :max="1" :step="0.1" />
                </el-form-item>
              </el-form>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 导入文件对话框 -->
    <el-dialog
      title="导入 3D 模型"
      v-model="importDialogVisible"
      width="600px"
      @close="resetImportForm"
    >
      <el-form :model="importForm" :rules="importRules" ref="importFormRef" label-width="100px">
        <el-form-item label="选择文件" prop="file">
          <el-upload
            class="upload-demo"
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            :file-list="importForm.fileList"
            accept=".obj,.fbx,.gltf,.glb,.stl,.ply"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
            <template #tip>
              <div class="el-upload__tip">
                支持 OBJ、FBX、GLTF、GLB、STL、PLY 格式，单个文件不超过 50MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
        
        <el-form-item label="模型名称" prop="name">
          <el-input v-model="importForm.name" placeholder="请输入模型名称" />
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input
            v-model="importForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入模型描述（可选）"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmImport" :loading="importing">
          导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Box, Plus, Download, Setting, ZoomIn, ZoomOut, 
  RefreshLeft, RefreshRight, Refresh, Crop, Edit, 
  ScaleToOriginal, RotateRight, VideoPlay, VideoPause, 
  UploadFilled 
} from '@element-plus/icons-vue'

// 响应式数据
const viewerContainer = ref<HTMLElement>()
const canvas3d = ref<HTMLCanvasElement>()
const importFormRef = ref()

const currentModel = ref<any>(null)
const loading = ref(false)
const loadProgress = ref(0)
const importing = ref(false)
const importDialogVisible = ref(false)

// 工具栏状态
const tools = reactive({
  select: true,
  move: false,
  scale: false,
  rotate: false
})

// 显示模式
const displayMode = ref('solid')

// 变换属性
const transform = reactive({
  position: { x: 0, y: 0, z: 0 },
  rotation: { x: 0, y: 0, z: 0 },
  scale: { x: 1, y: 1, z: 1 }
})

// 材质属性
const material = reactive({
  color: '#ffffff',
  metalness: 0.1,
  roughness: 0.8
})

// 导入表单
const importForm = reactive({
  file: null,
  fileList: [],
  name: '',
  description: ''
})

// 导入表单验证规则
const importRules = {
  file: [
    { required: true, message: '请选择文件', trigger: 'change' }
  ],
  name: [
    { required: true, message: '请输入模型名称', trigger: 'blur' }
  ]
}

// 模拟模型数据
const mockModels = [
  {
    id: 1,
    name: '机械零件.obj',
    format: 'OBJ',
    size: 2048576,
    vertices: 12580,
    faces: 8760,
    createTime: new Date('2024-01-15'),
    path: '/models/mechanical_part.obj'
  },
  {
    id: 2,
    name: '建筑模型.fbx',
    format: 'FBX',
    size: 5242880,
    vertices: 45600,
    faces: 38900,
    createTime: new Date('2024-01-20'),
    path: '/models/building_model.fbx'
  }
]

// 方法
const importModel = () => {
  importDialogVisible.value = true
}

const exportModel = () => {
  if (!currentModel.value) {
    ElMessage.warning('请先选择要导出的模型')
    return
  }
  ElMessage.info(`导出 ${currentModel.value.name} 功能开发中...`)
}

const openSettings = () => {
  ElMessage.info('设置功能开发中...')
}

const zoomIn = () => {
  ElMessage.info('放大视图')
}

const zoomOut = () => {
  ElMessage.info('缩小视图')
}

const rotateLeft = () => {
  ElMessage.info('左旋转')
}

const rotateRight = () => {
  ElMessage.info('右旋转')
}

const resetView = () => {
  ElMessage.info('重置视图')
}

const toggleSelect = () => {
  tools.select = !tools.select
  tools.move = false
  tools.scale = false
  tools.rotate = false
}

const toggleMove = () => {
  tools.move = !tools.move
  tools.select = false
  tools.scale = false
  tools.rotate = false
}

const toggleScale = () => {
  tools.scale = !tools.scale
  tools.select = false
  tools.move = false
  tools.rotate = false
}

const toggleRotate = () => {
  tools.rotate = !tools.rotate
  tools.select = false
  tools.move = false
  tools.scale = false
}

const changeDisplayMode = () => {
  ElMessage.info(`切换到${displayMode.value}模式`)
}

const playAnimation = () => {
  ElMessage.info('播放动画')
}

const pauseAnimation = () => {
  ElMessage.info('暂停动画')
}

const refreshView = () => {
  ElMessage.info('刷新视图')
}

const refreshProperties = () => {
  ElMessage.info('刷新属性')
}

const handleFileChange = (file: any) => {
  importForm.file = file.raw
  importForm.name = file.name.split('.').slice(0, -1).join('.')
}

const confirmImport = async () => {
  if (!importFormRef.value) return
  
  try {
    await importFormRef.value.validate()
    importing.value = true
    
    // 模拟导入过程
    loading.value = true
    loadProgress.value = 0
    
    const interval = setInterval(() => {
      loadProgress.value += Math.random() * 15
      if (loadProgress.value >= 100) {
        loadProgress.value = 100
        clearInterval(interval)
        loading.value = false
        
        // 创建新模型
        const newModel = {
          id: Date.now(),
          name: importForm.name,
          format: importForm.file.name.split('.').pop().toUpperCase(),
          size: importForm.file.size,
          vertices: Math.floor(Math.random() * 20000) + 1000,
          faces: Math.floor(Math.random() * 15000) + 800,
          createTime: new Date(),
          path: URL.createObjectURL(importForm.file)
        }
        
        currentModel.value = newModel
        importing.value = false
        importDialogVisible.value = false
        
        ElMessage.success('模型导入成功')
      }
    }, 200)
    
  } catch (error) {
    ElMessage.error('请检查表单填写')
  }
}

const resetImportForm = () => {
  importForm.file = null
  importForm.fileList = []
  importForm.name = ''
  importForm.description = ''
  importFormRef.value?.resetFields()
}

// 工具方法
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (date: Date) => {
  return date.toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  // 这里可以初始化 Three.js 场景
  console.log('3D 编辑器已加载')
})
</script>

<style scoped>
.three-d-edit-page {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header-content {
  flex: 1;
}

.page-title {
  margin: 0;
  font-size: 28px;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-icon {
  font-size: 32px;
  color: #409eff;
}

.page-subtitle {
  margin: 5px 0 0 0;
  color: #909399;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.main-content {
  height: calc(100vh - 200px);
}

.toolbar-card {
  height: fit-content;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar-section {
  margin-bottom: 20px;
}

.toolbar-section h4 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 14px;
  font-weight: bold;
}

.tool-buttons {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.viewer-card {
  height: 100%;
}

.viewer-title {
  font-weight: bold;
  color: #303133;
}

.viewer-controls {
  display: flex;
  gap: 10px;
}

.viewer-container {
  position: relative;
  height: 600px;
  background: #000;
  border-radius: 4px;
  overflow: hidden;
}

.three-canvas {
  width: 100%;
  height: 100%;
  display: block;
}

.empty-state {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
}

.loading-overlay p {
  margin-top: 20px;
  font-size: 16px;
}

.properties-card {
  height: fit-content;
}

.property-section {
  margin-bottom: 20px;
}

.property-section h4 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 14px;
  font-weight: bold;
  padding-bottom: 5px;
  border-bottom: 1px solid #ebeef5;
}

.upload-demo {
  width: 100%;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 20px;
  }
  
  .main-content .el-col {
    margin-bottom: 20px;
  }
}
</style>