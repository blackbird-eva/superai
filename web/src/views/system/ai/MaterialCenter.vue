<template>
  <div class="ppt-material-center">
    <!-- 专业头部 -->
  <div class="header">
    <div class="header-content">
      <h2 class="title">
        <el-icon class="title-icon"><Document /></el-icon>
        PPT模板中心
      </h2>
      <p class="subtitle">专业的PPT模板与初始模板库，快速创建精美演示文稿</p>
    </div>
      <div class="header-stats">
        <div class="quick-stat">
          <span class="number">{{ totalMaterials }}</span>
          <span class="label">总素材</span>
        </div>
      </div>
    </div>

    <!-- 专业工具栏 -->
    <div class="toolbar">
      <div class="search-section">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索PPT模板..."
          prefix-icon="Search"
          clearable
          class="search-input"
          @input="handleSearch"
        >
          <template #append>
            <el-button icon="Search" @click="handleSearch" />
          </template>
        </el-input>
      </div>
      
      <div class="filter-section">
        <el-select 
          v-model="categoryFilter" 
          placeholder="模板分类" 
          clearable 
          @change="handleFilter"
          class="category-filter"
        >
          <el-option label="全部分类" value=""></el-option>
          <el-option label="初始模板" value="initial"></el-option>
          <el-option label="商务模板" value="business"></el-option>
          <el-option label="教育模板" value="education"></el-option>
          <el-option label="创意模板" value="creative"></el-option>
          <el-option label="数据图表" value="data"></el-option>
        </el-select>
        
        <el-select 
          v-model="colorFilter" 
          placeholder="主题色彩" 
          clearable 
          @change="handleFilter"
          class="color-filter"
        >
          <el-option label="全部色彩" value=""></el-option>
          <el-option label="蓝色系" value="blue"></el-option>
          <el-option label="红色系" value="red"></el-option>
          <el-option label="绿色系" value="green"></el-option>
          <el-option label="紫色系" value="purple"></el-option>
          <el-option label="黑白灰" value="monochrome"></el-option>
        </el-select>
      </div>
      
      <div class="action-section">
        <el-button type="primary" icon="Plus" @click="showUploadDialog = true">
          上传模板
        </el-button>
        <el-button icon="FolderOpened" @click="showCollections = true">
          我的模板
        </el-button>
      </div>
    </div>

    <!-- 分类导航 -->
    <div class="category-nav">
      <div 
        v-for="category in categories"
        :key="category.key"
        :class="['category-tab', { active: activeCategory === category.key }]"
        @click="switchCategory(category.key)"
      >
        <el-icon><component :is="category.icon" /></el-icon>
        <span>{{ category.name }}</span>
        <span class="count">{{ category.count }}</span>
      </div>
    </div>

    <!-- 素材展示区域 -->
    <div class="material-workspace">
      <!-- 推荐素材 -->
      <div v-if="activeCategory === 'all'" class="featured-section">
        <h3 class="section-title">
          <el-icon><Star /></el-icon>
          精选推荐
        </h3>
        <div class="featured-grid">
          <div 
            v-for="item in featuredMaterials"
            :key="item.id"
            class="featured-card"
            @click="previewMaterial(item)"
          >
            <div class="featured-thumb">
              <img :src="item.thumbnail" :alt="item.name" />
              <div class="featured-overlay">
                <el-button type="primary" size="small" @click.stop="useMaterial(item)">
                  立即使用
                </el-button>
              </div>
            </div>
    <div class="featured-info">
      <h4>{{ item.name }}</h4>
      <p>{{ item.description }}</p>
      <div class="featured-meta">
        <span class="downloads">下载 {{ item.downloads }} 次</span>
        <el-tag size="small" :type="item.isPremium ? 'warning' : 'success'">
          {{ item.isPremium ? '高级' : '免费' }}
        </el-tag>
        <el-tag size="small" type="info">
          {{ item.slideCount }}页
        </el-tag>
      </div>
    </div>
          </div>
        </div>
      </div>

      <!-- 素材网格 -->
      <div class="material-grid-section">
        <div class="section-header">
          <h3 class="section-title">
            <el-icon><Grid /></el-icon>
            {{ getCurrentCategoryName() }}
          </h3>
          <div class="view-controls">
            <el-radio-group v-model="viewMode" size="small">
              <el-radio-button label="grid"><el-icon><Grid /></el-icon></el-radio-button>
              <el-radio-button label="list"><el-icon><List /></el-icon></el-radio-button>
            </el-radio-group>
          </div>
        </div>

        <!-- 网格视图 -->
        <div v-if="viewMode === 'grid'" class="material-grid">
          <div
            v-for="item in filteredMaterials"
            :key="item.id"
            class="material-card"
            :class="{ premium: item.isPremium, favorite: item.isFavorite }"
            @click="previewMaterial(item)"
          >
        <!-- 素材缩略图 -->
        <div class="material-thumb">
          <img v-if="item.type === 'image'" :src="item.thumbnail" :alt="item.name" />
          <div v-else class="template-thumb">
            <div class="template-preview" :style="{ background: item.previewStyle }"></div>
          </div>
              
      <!-- 素材标记 -->
      <div class="material-badges">
        <el-tag v-if="item.isPremium" size="small" type="warning" class="premium-badge">高级</el-tag>
        <el-tag v-if="item.isNew" size="small" type="success" class="new-badge">NEW</el-tag>
        <el-tag size="small" type="info" class="slide-badge">
          {{ item.slideCount }}页
        </el-tag>
        <el-button 
          :icon="item.isFavorite ? StarFilled : Star"
          size="small" 
          text 
          class="favorite-btn"
          @click.stop="toggleFavorite(item)"
        />
      </div>
            </div>

            <!-- 素材信息 -->
            <div class="material-info">
              <h4 class="material-name" :title="item.name">{{ item.name }}</h4>
              <p class="material-desc">{{ item.description }}</p>
              
              <div class="material-meta">
                <div class="meta-left">
                  <span class="category-tag">{{ getCategoryText(item.category) }}</span>
                  <span class="size">{{ item.size }}</span>
                </div>
                <div class="meta-right">
                  <span class="downloads">↓{{ item.downloads }}</span>
                </div>
              </div>
            </div>

            <!-- 快捷操作 -->
            <div class="material-actions">
              <el-button icon="Download" size="small" text @click.stop="downloadMaterial(item)">
                下载
              </el-button>
              <el-button icon="Plus" size="small" text type="primary" @click.stop="insertToSlide(item)">
                插入
              </el-button>
            </div>
          </div>
        </div>

        <!-- 列表视图 -->
        <div v-else class="material-list">
          <div 
            v-for="item in filteredMaterials"
            :key="item.id"
            class="list-item"
            :class="{ premium: item.isPremium, favorite: item.isFavorite }"
            @click="previewMaterial(item)"
          >
            <div class="list-thumb">
              <img v-if="item.type === 'image'" :src="item.thumbnail" :alt="item.name" />
              <div v-else class="list-type-icon">
                <el-icon><component :is="getCategoryIcon(item.category)" /></el-icon>
              </div>
            </div>
            
            <div class="list-info">
              <h4>{{ item.name }}</h4>
              <p>{{ item.description }}</p>
              <div class="list-meta">
                <span>{{ getCategoryText(item.category) }}</span>
                <span>{{ item.size }}</span>
                <span>下载 {{ item.downloads }} 次</span>
              </div>
            </div>
            
            <div class="list-actions">
              <el-button icon="Download" size="small" text @click.stop="downloadMaterial(item)">
                下载
              </el-button>
              <el-button icon="Plus" size="small" text type="primary" @click.stop="insertToSlide(item)">
                插入
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="filteredMaterials.length === 0 && !loading" class="empty-state">
      <el-empty description="未找到相关素材">
        <el-button type="primary" @click="clearFilters">清除筛选条件</el-button>
      </el-empty>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-loading-service :loading="loading" />
      <p>正在加载素材...</p>
    </div>

    <!-- 素材预览对话框 -->
    <el-dialog 
      v-model="showPreview" 
      :title="previewMaterialData?.name"
      width="80%"
      center
      class="preview-dialog"
    >
      <div v-if="previewMaterialData" class="preview-content">
        <div class="preview-main">
          <img v-if="previewMaterialData.type === 'image'" :src="previewMaterialData.url" class="preview-image" />
          <div v-else class="preview-placeholder">
            <el-icon :size="64"><component :is="getCategoryIcon(previewMaterialData.category)" /></el-icon>
            <p>{{ previewMaterialData.name }}</p>
          </div>
        </div>
        <div class="preview-sidebar">
          <h4>素材信息</h4>
    <p><strong>分类：</strong>{{ getCategoryText(previewMaterialData.category) }}</p>
    <p><strong>尺寸：</strong>{{ previewMaterialData.dimensions }}</p>
    <p><strong>大小：</strong>{{ previewMaterialData.size }}</p>
    <p><strong>格式：</strong>{{ previewMaterialData.format }}</p>
    <p><strong>页数：</strong>{{ previewMaterialData.slideCount }}页</p>
    <p><strong>描述：</strong>{{ previewMaterialData.description }}</p>
          
          <div class="preview-actions">
            <el-button type="primary" size="large" @click="downloadMaterial(previewMaterialData)">
              <el-icon><Download /></el-icon>
              下载素材
            </el-button>
            <el-button type="success" size="large" @click="insertToSlide(previewMaterialData)">
              <el-icon><Plus /></el-icon>
              插入幻灯片
            </el-button>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 上传对话框 -->
    <el-dialog v-model="showUploadDialog" title="上传PPT素材" width="500px" center>
      <el-upload
        class="ppt-upload"
        drag
        :auto-upload="false"
        :on-change="handleFileSelect"
        accept=".png,.jpg,.svg,.ppt,.pptx,.eps"
        :show-file-list="true"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">将素材文件拖到此处，或<em>点击上传</em></div>
    <div class="el-upload__tip">
      支持 PPT、PPTX 格式模板文件，单个文件不超过 20MB
    </div>
      </el-upload>
      
      <el-form :model="uploadForm" label-width="80px" style="margin-top: 20px;">
        <el-form-item label="素材名称">
          <el-input v-model="uploadForm.name" placeholder="请输入素材名称" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="uploadForm.category" placeholder="选择分类">
            <el-option label="初始模板" value="initial"></el-option>
            <el-option label="商务模板" value="business"></el-option>
            <el-option label="教育模板" value="education"></el-option>
            <el-option label="创意模板" value="creative"></el-option>
            <el-option label="数据图表" value="data"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input 
            v-model="uploadForm.description" 
            type="textarea" 
            :rows="2"
            placeholder="请输入素材描述"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmUpload" :disabled="!canUpload">确认上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Picture, Search, Plus, FolderOpened, Star, StarFilled,
  Grid, List, Download, UploadFilled, 
  Brush, Briefcase, School, Document, DataAnalysis, 
  CollectionTag
} from '@element-plus/icons-vue'

// 素材接口定义
interface MaterialItem {
  id: string
  name: string
  description: string
  category: 'initial' | 'business' | 'education' | 'creative' | 'data'
  type: 'ppt' | 'template'
  thumbnail: string
  url: string
  size: string
  dimensions: string
  format: string
  downloads: number
  isPremium: boolean
  isNew: boolean
  isFavorite: boolean
  previewStyle?: string
  slideCount?: number
}

// 响应式数据
const searchKeyword = ref('')
const categoryFilter = ref('')
const colorFilter = ref('')
const activeCategory = ref('all')
const viewMode = ref('grid')
const loading = ref(false)
const showUploadDialog = ref(false)
const showPreview = ref(false)
const showCollections = ref(false)
const previewMaterialData = ref<MaterialItem | null>(null)

// 上传表单
const uploadForm = reactive({
  name: '',
  category: '',
  description: '',
  file: null as any
})

// 分类数据
const categories = ref([
  { key: 'all', name: '全部模板', icon: 'Grid', count: 156 },
  { key: 'initial', name: '初始模板', icon: 'Document', count: 48 },
  { key: 'business', name: '商务模板', icon: 'Briefcase', count: 36 },
  { key: 'education', name: '教育模板', icon: 'School', count: 28 },
  { key: 'creative', name: '创意模板', icon: 'Brush', count: 24 },
  { key: 'data', name: '数据图表', icon: 'DataAnalysis', count: 20 }
])

// PPT模板数据
const materials = ref<MaterialItem[]>([
  {
    id: '1',
    name: '简约初始模板',
    description: '极简风格初始模板，适合快速开始制作',
    category: 'initial',
    type: 'ppt',
    thumbnail: 'https://via.placeholder.com/300x200/ffffff/333333?text=Initial',
    url: '',
    size: '1.2MB',
    dimensions: '1920×1080',
    format: 'PPTX',
    downloads: 2456,
    isPremium: false,
    isNew: false,
    isFavorite: true,
    previewStyle: 'background: linear-gradient(135deg, #f5f7fa, #ffffff)',
    slideCount: 12
  },
  {
    id: '2',
    name: '商务汇报模板',
    description: '专业商务风格，适合企业汇报和工作总结',
    category: 'business',
    type: 'ppt',
    thumbnail: 'https://via.placeholder.com/300x200/409eff/ffffff?text=Business',
    url: '',
    size: '2.8MB',
    dimensions: '1920×1080',
    format: 'PPTX',
    downloads: 1876,
    isPremium: true,
    isNew: false,
    isFavorite: false,
    previewStyle: 'background: linear-gradient(135deg, #409eff, #66b1ff)',
    slideCount: 24
  },
  {
    id: '3',
    name: '教育培训模板',
    description: '清新教育风格，适合课程教学和培训演示',
    category: 'education',
    type: 'ppt',
    thumbnail: 'https://via.placeholder.com/300x200/67c23a/ffffff?text=Education',
    url: '',
    size: '3.5MB',
    dimensions: '1920×1080',
    format: 'PPTX',
    downloads: 1324,
    isPremium: false,
    isNew: true,
    isFavorite: true,
    previewStyle: 'background: linear-gradient(135deg, #67c23a, #95d475)',
    slideCount: 18
  },
  {
    id: '4',
    name: '创意设计模板',
    description: '创意视觉风格，适合产品发布和创意展示',
    category: 'creative',
    type: 'ppt',
    thumbnail: 'https://via.placeholder.com/300x200/e6a23c/ffffff?text=Creative',
    url: '',
    size: '4.2MB',
    dimensions: '1920×1080',
    format: 'PPTX',
    downloads: 967,
    isPremium: true,
    isNew: true,
    isFavorite: false,
    previewStyle: 'background: linear-gradient(135deg, #e6a23c, #f0c78a)',
    slideCount: 32
  },
  {
    id: '5',
    name: '数据分析模板',
    description: '专业数据可视化模板，适合报表和分析',
    category: 'data',
    type: 'ppt',
    thumbnail: 'https://via.placeholder.com/300x200/5f27cd/ffffff?text=Data',
    url: '',
    size: '3.8MB',
    dimensions: '1920×1080',
    format: 'PPTX',
    downloads: 743,
    isPremium: true,
    isNew: false,
    isFavorite: false,
    previewStyle: 'background: linear-gradient(135deg, #5f27cd, #a29bfe)',
    slideCount: 20
  },
  {
    id: '6',
    name: '创业路演模板',
    description: '现代创业风格，适合融资路演和商业计划',
    category: 'business',
    type: 'ppt',
    thumbnail: 'https://via.placeholder.com/300x200/ff6b6b/ffffff?text=Pitch',
    url: '',
    size: '4.1MB',
    dimensions: '1920×1080',
    format: 'PPTX',
    downloads: 1156,
    isPremium: true,
    isNew: false,
    isFavorite: true,
    previewStyle: 'background: linear-gradient(135deg, #ff6b6b, #ffa8a8)',
    slideCount: 28
  }
])

  // 精选推荐素材
  const featuredMaterials = computed(() => 
    materials.value.filter(item => item.downloads > 500 && item.type === 'ppt').slice(0, 4)
  )

// 计算属性
const filteredMaterials = computed(() => {
  let list = materials.value
  
  // 按分类过滤
  if (activeCategory.value !== 'all') {
    list = list.filter(item => item.category === activeCategory.value)
  }
  
  // 按搜索关键词过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    list = list.filter(item => 
      item.name.toLowerCase().includes(keyword) ||
      item.description.toLowerCase().includes(keyword)
    )
  }
  
  // 按分类筛选
  if (categoryFilter.value) {
    list = list.filter(item => item.category === categoryFilter.value)
  }
  
  return list
})

const totalMaterials = computed(() => materials.value.length)

const canUpload = computed(() => {
  return uploadForm.name && uploadForm.category && uploadForm.file
})

// 方法
const handleSearch = () => {
  // 搜索逻辑已在计算属性中处理
}

const handleFilter = () => {
  // 筛选逻辑已在计算属性中处理
}

const switchCategory = (category: string) => {
  activeCategory.value = category
}

const getCurrentCategoryName = () => {
  const category = categories.value.find(c => c.key === activeCategory.value)
  return category ? category.name : '全部素材'
}

  const getCategoryText = (category: string) => {
    const categoryMap: { [key: string]: string } = {
      initial: '初始模板',
      business: '商务模板',
      education: '教育模板',
      creative: '创意模板',
      data: '数据图表'
    }
    return categoryMap[category] || '未知'
  }

  const getCategoryIcon = (category: string) => {
    const iconMap: { [key: string]: string } = {
      initial: 'Document',
      business: 'Briefcase',
      education: 'School',
      creative: 'Brush',
      data: 'DataAnalysis'
    }
    return iconMap[category] || 'Document'
  }

const previewMaterial = (item: MaterialItem) => {
  previewMaterialData.value = item
  showPreview.value = true
}

const downloadMaterial = (item: MaterialItem) => {
  ElMessage.success(`开始下载：${item.name}`)
  item.downloads++
}

const insertToSlide = (item: MaterialItem) => {
  ElMessage.success(`已将「${item.name}」插入到幻灯片`)
}

const toggleFavorite = (item: MaterialItem) => {
  item.isFavorite = !item.isFavorite
  ElMessage.success(item.isFavorite ? '已添加到收藏' : '已从收藏中移除')
}

const useMaterial = (item: MaterialItem) => {
  ElMessage.success(`正在使用：${item.name}`)
}

const handleFileSelect = (file: any) => {
  uploadForm.file = file.raw
  if (!uploadForm.name) {
    uploadForm.name = file.name.split('.').slice(0, -1).join('.')
  }
}

const confirmUpload = () => {
  if (!canUpload.value) return
  
  // 模拟上传
  loading.value = true
  setTimeout(() => {
    const newMaterial: MaterialItem = {
      id: Date.now().toString(),
      name: uploadForm.name,
      description: uploadForm.description,
      category: uploadForm.category as any,
      type: 'ppt',
      thumbnail: URL.createObjectURL(uploadForm.file),
      url: URL.createObjectURL(uploadForm.file),
      size: `${(uploadForm.file.size / 1024 / 1024).toFixed(1)}MB`,
      dimensions: '1920×1080',
      format: uploadForm.file.name.split('.').pop()?.toUpperCase() || 'PPTX',
      downloads: 0,
      isPremium: false,
      isNew: true,
      isFavorite: false,
      slideCount: 10
    }
    
    materials.value.unshift(newMaterial)
    ElMessage.success('上传成功')
    showUploadDialog.value = false
    loading.value = false
    
    // 重置表单
    Object.assign(uploadForm, { name: '', category: '', description: '', file: null })
  }, 1500)
}

const clearFilters = () => {
  searchKeyword.value = ''
  categoryFilter.value = ''
  colorFilter.value = ''
  activeCategory.value = 'all'
}

// 生命周期
onMounted(() => {
  console.log('PPT素材中心加载完成')
})
</script>

<style scoped>
.ppt-material-center {
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
}

/* 专业头部 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 24px 32px;
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

.header-content {
  flex: 1;
}

.title {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 28px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-icon {
  font-size: 32px;
  color: #409eff;
}

.subtitle {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.header-stats {
  display: flex;
  gap: 24px;
}

.quick-stat {
  text-align: center;
}

.quick-stat .number {
  display: block;
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.quick-stat .label {
  font-size: 12px;
  color: #909399;
}

/* 专业工具栏 */
.toolbar {
  display: flex;
  gap: 20px;
  background: white;
  padding: 16px 24px;
  border-radius: 8px;
  margin-bottom: 20px;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.search-section {
  flex: 1;
  max-width: 300px;
}

.search-input {
  width: 100%;
}

.filter-section {
  display: flex;
  gap: 12px;
}

.category-filter,
.color-filter {
  width: 140px;
}

.action-section {
  display: flex;
  gap: 12px;
}

/* 分类导航 */
.category-nav {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  overflow-x: auto;
  padding: 8px 0;
}

.category-tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: white;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
  box-shadow: 0 2px 4px rgba(0,0,0,0.04);
}

.category-tab:hover {
  background: #f0f9ff;
  color: #409eff;
}

.category-tab.active {
  background: #409eff;
  color: white;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.category-tab .count {
  background: rgba(255,255,255,0.2);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.category-tab.active .count {
  background: rgba(255,255,255,0.3);
}

/* 素材工作区 */
.material-workspace {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

/* 精选推荐 */
.featured-section {
  padding: 24px;
  border-bottom: 1px solid #f0f0f0;
}

.featured-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.featured-card {
  background: #fafbfc;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
}

.featured-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.featured-thumb {
  position: relative;
  height: 160px;
  overflow: hidden;
}

.featured-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.featured-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.featured-card:hover .featured-overlay {
  opacity: 1;
}

.featured-info {
  padding: 16px;
}

.featured-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #303133;
}

.featured-info p {
  margin: 0 0 12px 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.4;
}

.featured-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.downloads {
  font-size: 12px;
  color: #909399;
}

/* 网格视图 */
.material-grid-section {
  padding: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.view-controls {
  display: flex;
  gap: 8px;
}

.material-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.material-card {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.material-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.material-card.premium {
  border-color: #e6a23c;
}

.material-card.favorite::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 0;
  height: 0;
  border-left: 20px solid transparent;
  border-top: 20px solid #f56c6c;
  z-index: 2;
}

.material-thumb {
  position: relative;
  height: 140px;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.material-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.template-thumb {
  width: 100%;
  height: 100%;
}

.template-preview {
  width: 100%;
  height: 100%;
}

.icon-thumb {
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-preview {
  font-size: 48px;
}

.material-badges {
  position: absolute;
  top: 8px;
  left: 8px;
  right: 8px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.premium-badge {
  font-size: 10px;
}

.new-badge {
  font-size: 10px;
}

.favorite-btn {
  color: #ffd700;
}

.material-info {
  padding: 12px;
}

.material-name {
  margin: 0 0 6px 0;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.material-desc {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: #909399;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.material-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.meta-left {
  display: flex;
  gap: 8px;
  align-items: center;
}

.category-tag {
  font-size: 10px;
  color: #409eff;
  background: #f0f9ff;
  padding: 2px 6px;
  border-radius: 4px;
}

.size {
  font-size: 10px;
  color: #909399;
}

.meta-right {
  font-size: 10px;
  color: #909399;
}

.material-actions {
  padding: 8px 12px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: flex-end;
  gap: 4px;
  background: #fafbfc;
}

/* 列表视图 */
.material-list {
  display: flex;
  flex-direction: column;
  gap: 1px;
  background: #f0f0f0;
}

.list-item {
  display: flex;
  align-items: center;
  background: white;
  padding: 12px 16px;
  gap: 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.list-item:hover {
  background: #f8f9fa;
}

.list-item.premium {
  border-left: 4px solid #e6a23c;
}

.list-thumb {
  width: 60px;
  height: 60px;
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
}

.list-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.list-type-icon {
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
}

.list-info {
  flex: 1;
  min-width: 0;
}

.list-info h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: #303133;
}

.list-info p {
  margin: 0 0 6px 0;
  font-size: 12px;
  color: #909399;
}

.list-meta {
  display: flex;
  gap: 12px;
  font-size: 10px;
  color: #c0c4cc;
}

.list-actions {
  display: flex;
  gap: 8px;
}

/* 预览对话框 */
.preview-dialog .el-dialog__body {
  padding: 0;
}

.preview-content {
  display: flex;
  height: 600px;
}

.preview-main {
  flex: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  overflow: auto;
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.preview-placeholder {
  text-align: center;
  color: #909399;
}

.preview-sidebar {
  flex: 1;
  padding: 24px;
  background: white;
  border-left: 1px solid #e4e7ed;
}

.preview-sidebar h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.preview-sidebar p {
  margin: 8px 0;
  color: #606266;
  font-size: 14px;
}

.preview-actions {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 上传区域 */
.ppt-upload {
  text-align: center;
}

/* 空状态和加载状态 */
.empty-state,
.loading-state {
  padding: 60px 20px;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ppt-material-center {
    padding: 16px;
  }
  
  .header {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
  
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-section {
    max-width: none;
  }
  
  .filter-section {
    flex-direction: column;
  }
  
  .category-nav {
    margin: 0 -16px 20px -16px;
    padding: 8px 16px;
  }
  
  .featured-grid {
    grid-template-columns: 1fr;
  }
  
  .material-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
  
  .preview-content {
    flex-direction: column;
    height: auto;
  }
  
  .preview-main {
    height: 300px;
  }
}
</style>
