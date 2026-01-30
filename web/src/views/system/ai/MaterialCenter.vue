<template>
  <div class="material-center">
    <!-- 简洁头部 -->
    <div class="header">
      <h2>素材中心</h2>
      <p>管理您的图片、视频、文档等素材</p>
    </div>

    <!-- 简单操作栏 -->
    <div class="toolbar">
      <div class="search-box">
        <el-input
          v-model="searchKey"
          placeholder="搜索素材..."
          prefix-icon="Search"
          clearable
          @input="filterMaterials"
        />
      </div>
      
      <div class="filters">
        <el-select v-model="typeFilter" placeholder="类型" clearable @change="filterMaterials">
          <el-option label="全部" value=""></el-option>
          <el-option label="图片" value="image"></el-option>
          <el-option label="视频" value="video"></el-option>
          <el-option label="文档" value="document"></el-option>
        </el-select>
        
        <el-button type="primary" icon="Plus" @click="showUpload = true">
          上传
        </el-button>
      </div>
    </div>

    <!-- 素材统计 -->
    <div class="stats">
      <span class="stat-item">共 {{ filteredList.length }} 项</span>
      <span class="stat-item">图片 {{ imageCount }} 张</span>
      <span class="stat-item">视频 {{ videoCount }} 个</span>
    </div>

    <!-- 清爽的素材网格 -->
    <div class="material-grid">
      <div
        v-for="item in filteredList"
        :key="item.id"
        class="material-card"
        @click="previewItem(item)"
      >
        <!-- 缩略图 -->
        <div class="thumb">
          <img v-if="item.type === 'image'" :src="item.url" :alt="item.name" />
          <div v-else-if="item.type === 'video'" class="video-thumb">
            <el-icon><VideoPlay /></el-icon>
          </div>
          <div v-else class="doc-thumb">
            <el-icon><Document /></el-icon>
          </div>
          
          <!-- 文件类型标签 -->
          <span class="type-badge">{{ getTypeText(item.type) }}</span>
        </div>

        <!-- 素材信息 -->
        <div class="info">
          <h4 class="name" :title="item.name">{{ item.name }}</h4>
          <p class="meta">
            <span class="size">{{ formatSize(item.size) }}</span>
            <span class="time">{{ item.uploadTime }}</span>
          </p>
        </div>

        <!-- 快捷操作 -->
        <div class="actions">
          <el-button icon="Download" size="small" text @click.stop="downloadItem(item)" />
          <el-button icon="Delete" size="small" text type="danger" @click.stop="deleteItem(item)" />
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="filteredList.length === 0" class="empty">
      <el-empty description="暂无素材" />
      <el-button type="primary" @click="showUpload = true">上传第一个素材</el-button>
    </div>

    <!-- 简洁上传对话框 -->
    <el-dialog v-model="showUpload" title="上传素材" width="400px" center>
      <el-upload
        class="simple-upload"
        drag
        :auto-upload="false"
        :on-change="handleUpload"
        accept=".jpg,.png,.mp4,.pdf,.doc"
        :show-file-list="false"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">点击或拖拽文件到此处</div>
        <div class="el-upload__tip">支持 jpg, png, mp4, pdf, doc 格式</div>
      </el-upload>
      
      <div v-if="uploadFile" class="upload-preview">
        <p><strong>文件名：</strong>{{ uploadFile.name }}</p>
        <p><strong>大小：</strong>{{ formatSize(uploadFile.size) }}</p>
      </div>

      <template #footer>
        <el-button @click="cancelUpload">取消</el-button>
        <el-button type="primary" @click="confirmUpload" :disabled="!uploadFile">确认上传</el-button>
      </template>
    </el-dialog>

    <!-- 简单预览 -->
    <el-dialog v-model="showPreview" title="预览" width="60%" center>
      <div v-if="previewData" class="preview-content">
        <img v-if="previewData.type === 'image'" :src="previewData.url" class="preview-img" />
        <video v-else-if="previewData.type === 'video'" :src="previewData.url" controls class="preview-video"></video>
        <div v-else class="preview-doc">
          <el-icon><Document /></el-icon>
          <p>{{ previewData.name }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Plus, VideoPlay, Document, UploadFilled,
  Download, Delete
} from '@element-plus/icons-vue'

// 素材接口
interface MaterialItem {
  id: string
  name: string
  type: 'image' | 'video' | 'document'
  url: string
  size: number
  uploadTime: string
}

// 响应式数据
const searchKey = ref('')
const typeFilter = ref('')
const showUpload = ref(false)
const showPreview = ref(false)
const uploadFile = ref<any>(null)
const previewData = ref<MaterialItem | null>(null)

// 素材数据
const materials = ref<MaterialItem[]>([
  {
    id: '1',
    name: '产品展示图.jpg',
    type: 'image',
    url: 'https://via.placeholder.com/300x200/409eff/ffffff?text=Product',
    size: 1024000,
    uploadTime: '2024-01-15'
  },
  {
    id: '2',
    name: '宣传视频.mp4',
    type: 'video',
    url: '',
    size: 15728640,
    uploadTime: '2024-01-14'
  },
  {
    id: '3',
    name: '使用说明.pdf',
    type: 'document',
    url: '',
    size: 2048576,
    uploadTime: '2024-01-13'
  },
  {
    id: '4',
    name: '团队照片.png',
    type: 'image',
    url: 'https://via.placeholder.com/300x200/67c23a/ffffff?text=Team',
    size: 1536000,
    uploadTime: '2024-01-12'
  },
  {
    id: '5',
    name: '演示视频.mp4',
    type: 'video',
    url: '',
    size: 25165824,
    uploadTime: '2024-01-11'
  },
  {
    id: '6',
    name: '合同模板.doc',
    type: 'document',
    url: '',
    size: 512000,
    uploadTime: '2024-01-10'
  }
])

// 过滤后的素材列表
const filteredList = ref<MaterialItem[]>(materials.value)

// 统计信息
const imageCount = computed(() => materials.value.filter(item => item.type === 'image').length)
const videoCount = computed(() => materials.value.filter(item => item.type === 'video').length)

// 过滤素材
const filterMaterials = () => {
  let list = materials.value
  
  // 按类型过滤
  if (typeFilter.value) {
    list = list.filter(item => item.type === typeFilter.value)
  }
  
  // 按关键词搜索
  if (searchKey.value) {
    const key = searchKey.value.toLowerCase()
    list = list.filter(item => 
      item.name.toLowerCase().includes(key)
    )
  }
  
  filteredList.value = list
}

// 获取类型文本
const getTypeText = (type: string) => {
  const types: { [key: string]: string } = {
    image: '图',
    video: '视',
    document: '文'
  }
  return types[type] || '文'
}

// 格式化文件大小
const formatSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

// 上传处理
const handleUpload = (file: any) => {
  uploadFile.value = file.raw
}

const confirmUpload = () => {
  if (!uploadFile.value) return
  
  // 创建新素材
  const newItem: MaterialItem = {
    id: Date.now().toString(),
    name: uploadFile.value.name,
    type: getFileType(uploadFile.value.name),
    url: URL.createObjectURL(uploadFile.value),
    size: uploadFile.value.size,
    uploadTime: new Date().toISOString().split('T')[0]
  }
  
  materials.value.unshift(newItem)
  filterMaterials()
  
  ElMessage.success('上传成功')
  cancelUpload()
}

const cancelUpload = () => {
  showUpload.value = false
  uploadFile.value = null
}

const getFileType = (filename: string): MaterialItem['type'] => {
  const ext = filename.split('.').pop()?.toLowerCase()
  if (['jpg', 'jpeg', 'png', 'gif'].includes(ext || '')) return 'image'
  if (['mp4', 'avi', 'mov'].includes(ext || '')) return 'video'
  return 'document'
}

// 预览处理
const previewItem = (item: MaterialItem) => {
  previewData.value = item
  showPreview.value = true
}

// 下载处理
const downloadItem = (item: MaterialItem) => {
  if (item.url) {
    const link = document.createElement('a')
    link.href = item.url
    link.download = item.name
    link.click()
    ElMessage.success('开始下载')
  }
}

// 删除处理
const deleteItem = async (item: MaterialItem) => {
  try {
    await ElMessageBox.confirm(`确定删除 "${item.name}"？`, '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const index = materials.value.findIndex(m => m.id === item.id)
    if (index > -1) {
      materials.value.splice(index, 1)
      filterMaterials()
      ElMessage.success('删除成功')
    }
  } catch {
    // 用户取消
  }
}

// 初始化
onMounted(() => {
  filterMaterials()
})
</script>

<style scoped>
.material-center {
  padding: 20px;
  background: #f8f9fa;
  min-height: 100vh;
}

/* 简洁头部 */
.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 500;
}

.header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

/* 简单工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 16px 20px;
  border-radius: 8px;
  margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.search-box {
  flex: 1;
  max-width: 300px;
}

.filters {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* 统计信息 */
.stats {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  padding: 0 4px;
}

.stat-item {
  color: #606266;
  font-size: 14px;
}

/* 清爽网格布局 */
.material-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.material-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.material-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

/* 缩略图 */
.thumb {
  position: relative;
  height: 160px;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-thumb,
.doc-thumb {
  color: #909399;
  font-size: 48px;
}

.type-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(0,0,0,0.7);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

/* 素材信息 */
.info {
  padding: 12px 16px;
}

.name {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
  margin: 0;
}

/* 快捷操作 */
.actions {
  padding: 8px 16px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: flex-end;
  gap: 4px;
}

/* 空状态 */
.empty {
  text-align: center;
  padding: 60px 20px;
}

/* 简洁上传 */
.simple-upload {
  text-align: center;
}

.upload-preview {
  margin-top: 16px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 14px;
}

/* 简单预览 */
.preview-content {
  text-align: center;
}

.preview-img {
  max-width: 100%;
  max-height: 400px;
  border-radius: 4px;
}

.preview-video {
  max-width: 100%;
  max-height: 400px;
}

.preview-doc {
  padding: 60px 20px;
  color: #909399;
}

.preview-doc .el-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

/* 响应式 */
@media (max-width: 768px) {
  .material-center {
    padding: 16px;
  }
  
  .toolbar {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .search-box {
    max-width: none;
  }
  
  .filters {
    justify-content: space-between;
  }
  
  .stats {
    flex-direction: column;
    gap: 8px;
  }
  
  .material-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 12px;
  }
}
</style>