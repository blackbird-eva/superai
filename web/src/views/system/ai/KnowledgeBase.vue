<template>
  <div class="knowledge-base">
    <!-- 简洁头部 -->
    <div class="header">
      <h2>知识库</h2>
      <p>快速查找和使用知识内容</p>
    </div>

    <!-- 搜索和操作区 -->
    <div class="search-section">
      <div class="search-box">
        <el-input
          v-model="searchQuery"
          placeholder="搜索知识点、标题或内容..."
          prefix-icon="Search"
          clearable
          @input="debouncedSearch"
          size="large"
        />
      </div>
      
      <div class="action-buttons">
        <el-upload
          class="upload-demo"
          :auto-upload="false"
          :on-change="handleFileUpload"
          :show-file-list="false"
          accept=".docx,.doc"
          :disabled="uploadLoading"
        >
          <el-button 
            type="success" 
            icon="Upload" 
            :loading="uploadLoading"
          >
            {{ uploadLoading ? '解析中...' : '上传Word文档' }}
          </el-button>
        </el-upload>
        
        <el-button type="primary" icon="Plus" @click="showAddDialog = true">
          添加知识
        </el-button>
      </div>
    </div>

    <!-- 分类导航 -->
    <div class="categories">
      <div class="category-tabs">
        <button
          v-for="cat in categories"
          :key="cat.key"
          :class="['tab-btn', { active: activeCategory === cat.key }]"
          @click="activeCategory = cat.key"
        >
          {{ cat.label }}
          <span class="count">{{ getCategoryCount(cat.key) }}</span>
        </button>
      </div>
    </div>

    <!-- 知识列表 -->
    <div class="knowledge-list">
      <div
        v-for="item in filteredKnowledge"
        :key="item.id"
        class="knowledge-item"
        @click="viewDetail(item)"
      >
        <div class="item-header">
          <h3 class="title">{{ item.title }}</h3>
          <el-tag :type="getTagType(item.category)" size="small">
            {{ getCategoryLabel(item.category) }}
          </el-tag>
        </div>
        
        <p class="summary">{{ item.summary }}</p>
        
        <div class="item-meta">
          <span class="author">作者：{{ item.author }}</span>
          <span class="date">更新：{{ item.updateTime }}</span>
          <span class="views">阅读 {{ item.views }}</span>
        </div>

        <div class="item-actions">
          <el-button icon="View" size="small" text @click.stop="viewDetail(item)">
            查看
          </el-button>
          <el-button icon="Edit" size="small" text @click.stop="editItem(item)">
            编辑
          </el-button>
          <el-button icon="Delete" size="small" text type="danger" @click.stop="deleteItem(item)">
            删除
          </el-button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="filteredKnowledge.length === 0" class="empty-state">
      <el-empty description="暂无相关知识">
        <el-button type="primary" @click="showAddDialog = true">创建第一篇知识</el-button>
      </el-empty>
    </div>

    <!-- Word解析结果 -->
    <div v-if="parseResult" class="parse-result">
      <el-card class="parse-result-card">
        <template #header>
          <div class="parse-header">
            <span>📄 Word文档解析结果</span>
            <el-button type="text" @click="parseResult = null">×</el-button>
          </div>
        </template>
        
        <div v-if="parseResult.success" class="parse-success">
          <el-alert
            :title="`解析成功: ${parseResult.fileName}`"
            type="success"
            :description="`共提取 ${parseResult.data.length} 个知识点`"
            show-icon
            :closable="false"
          />
          
          <!-- 解析内容预览 -->
          <div class="parse-preview">
            <h4>📋 提取的知识点：</h4>
            <div class="preview-list">
              <div 
                v-for="(item, index) in parseResult.data" 
                :key="index"
                class="preview-item"
              >
                <h5>{{ item.title }}</h5>
                <p>{{ item.summary }}</p>
                <el-tag :type="getTagType(item.category)" size="mini">
                  {{ getCategoryLabel(item.category) }}
                </el-tag>
              </div>
            </div>
          </div>
          
          <div class="parse-actions">
            <el-button type="primary" @click="importToKnowledge" :loading="importLoading">
              导入到知识库
            </el-button>
            <el-button @click="clearParseResult">
              清除结果
            </el-button>
          </div>
        </div>
        
        <div v-else class="parse-error">
          <el-alert
            title="解析失败"
            type="error"
            :description="parseResult.error"
            show-icon
            :closable="false"
          />
        </div>
      </el-card>
    </div>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      :title="isEditing ? '编辑知识' : '添加知识'"
      v-model="showAddDialog"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="knowledgeForm" :rules="formRules" ref="formRef" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="knowledgeForm.title" placeholder="请输入知识标题" />
        </el-form-item>
        
        <el-form-item label="分类" prop="category">
          <el-select v-model="knowledgeForm.category" placeholder="选择分类" style="width: 100%">
            <el-option label="产品知识" value="product"></el-option>
            <el-option label="技术文档" value="tech"></el-option>
            <el-option label="操作指南" value="guide"></el-option>
            <el-option label="常见问题" value="faq"></el-option>
            <el-option label="业务流程" value="process"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="摘要" prop="summary">
          <el-input
            v-model="knowledgeForm.summary"
            type="textarea"
            :rows="3"
            placeholder="简要描述知识内容"
          />
        </el-form-item>
        
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="knowledgeForm.content"
            type="textarea"
            :rows="8"
            placeholder="详细的知识内容..."
          />
        </el-form-item>
        
        <el-form-item label="标签">
          <el-input
            v-model="knowledgeForm.tags"
            placeholder="用逗号分隔多个标签"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveKnowledge" :loading="saving">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog
      title="知识详情"
      v-model="showDetailDialog"
      width="70%"
      center
    >
      <div v-if="selectedItem" class="detail-content">
        <div class="detail-header">
          <h2>{{ selectedItem.title }}</h2>
          <div class="detail-meta">
            <el-tag :type="getTagType(selectedItem.category)">
              {{ getCategoryLabel(selectedItem.category) }}
            </el-tag>
            <span class="author">作者：{{ selectedItem.author }}</span>
            <span class="date">更新：{{ selectedItem.updateTime }}</span>
          </div>
        </div>

        <div class="detail-body">
          <div class="content-text" v-html="formatContent(selectedItem.content)"></div>
        </div>

        <div class="detail-tags" v-if="selectedItem.tags">
          <el-tag v-for="tag in selectedItem.tags.split(',')" :key="tag" size="small" type="info">
            {{ tag.trim() }}
          </el-tag>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, View, Edit, Delete, Upload } from '@element-plus/icons-vue'
import { request } from '/@/utils/service'

// 知识条目接口
export interface KnowledgeItem {
  id: string
  title: string
  summary: string
  content: string
  category: string
  tags: string
  author: string
  createTime: string
  updateTime: string
  views: number
}

// 响应式数据
const searchQuery = ref('')
const activeCategory = ref('all')
const showAddDialog = ref(false)
const showDetailDialog = ref(false)
const isEditing = ref(false)
const saving = ref(false)
const uploadLoading = ref(false)
const importLoading = ref(false)
const selectedItem = ref<KnowledgeItem | null>(null)
const formRef = ref()

// Word解析相关
const parseResult = ref<any>(null)

// 表单数据
const knowledgeForm = reactive({
  id: '',
  title: '',
  summary: '',
  content: '',
  category: '',
  tags: '',
  author: '管理员'
})

// 表单验证规则
const formRules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  summary: [{ required: true, message: '请输入摘要', trigger: 'blur' }],
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }]
}

// 分类配置
const categories = [
  { key: 'all', label: '全部' },
  { key: 'product', label: '产品知识' },
  { key: 'tech', label: '技术文档' },
  { key: 'guide', label: '操作指南' },
  { key: 'faq', label: '常见问题' },
  { key: 'process', label: '业务流程' }
]

// 示例知识库数据
const knowledgeData = ref<KnowledgeItem[]>([
  {
    id: '1',
    title: '产品功能介绍与使用指南',
    summary: '详细介绍产品的核心功能特性以及具体的使用方法',
    content: '本产品具有以下几大核心功能：\n\n1. 智能分析：基于AI技术提供深度数据分析\n2. 可视化展示：丰富的图表和仪表板展示\n3. 协作功能：支持团队协作和权限管理\n4. 数据安全：企业级安全保障措施\n\n使用步骤：\n1. 注册并登录系统\n2. 创建项目和工作空间\n3. 导入数据源\n4. 配置分析模型\n5. 生成报告和可视化图表',
    category: 'product',
    tags: '产品,使用指南,功能介绍',
    author: '产品经理',
    createTime: '2024-01-10',
    updateTime: '2024-01-15',
    views: 156
  },
  {
    id: '2',
    title: 'API接口调用说明',
    summary: '开发者如何调用我们的API接口进行二次开发',
    content: 'API调用说明：\n\n接口地址：https://api.example.com/v1\n\n认证方式：Bearer Token\n\n请求示例：\n```\nGET /data/analysis\nAuthorization: Bearer your-token\nContent-Type: application/json\n```\n\n返回格式：JSON\n\n错误码说明：\n- 200: 成功\n- 401: 未授权\n- 404: 资源不存在\n- 500: 服务器错误',
    category: 'tech',
    tags: 'API,开发,技术文档',
    author: '技术团队',
    createTime: '2024-01-08',
    updateTime: '2024-01-12',
    views: 89
  },
  {
    id: '3',
    title: '如何导出分析报告',
    summary: 'step by step指导用户如何导出和分享分析报告',
    content: '导出报告的操作步骤：\n\n1. 进入报告页面\n2. 点击右上角的"导出"按钮\n3. 选择导出格式（PDF、Excel、PowerPoint）\n4. 选择导出范围（当前页、全部数据）\n5. 点击"确认导出"\n\n注意事项：\n- PDF格式保持最佳视觉效果\n- Excel格式便于进一步数据处理\n- PPT格式适合演示汇报',
    category: 'guide',
    tags: '导出,报告,操作指南',
    author: '培训专员',
    createTime: '2024-01-05',
    updateTime: '2024-01-14',
    views: 203
  }
])

// 过滤后的知识列表
const filteredKnowledge = ref<KnowledgeItem[]>(knowledgeData.value)

// 防抖函数
const debounce = (func: Function, wait: number) => {
  let timeout: NodeJS.Timeout
  return function executedFunction(...args: any[]) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

// 计算分类数量
const getCategoryCount = (category: string) => {
  if (category === 'all') return knowledgeData.value.length
  return knowledgeData.value.filter(item => item.category === category).length
}

// 获取分类标签
const getCategoryLabel = (category: string) => {
  const cat = categories.find(c => c.key === category)
  return cat ? cat.label : '未分类'
}

// 获取标签类型
const getTagType = (category: string) => {
  const types: { [key: string]: string } = {
    product: 'primary',
    tech: 'success',
    guide: 'warning',
    faq: 'info',
    process: 'danger'
  }
  return types[category] || 'info'
}

// 格式化内容（将换行转换为HTML）
const formatContent = (content: string) => {
  return content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>')
    .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
}

// 搜索功能
const searchKnowledge = () => {
  let data = knowledgeData.value
  
  // 按分类过滤
  if (activeCategory.value !== 'all') {
    data = data.filter(item => item.category === activeCategory.value)
  }
  
  // 按关键词搜索
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    data = data.filter(item =>
      item.title.toLowerCase().includes(query) ||
      item.summary.toLowerCase().includes(query) ||
      item.content.toLowerCase().includes(query) ||
      item.tags.toLowerCase().includes(query)
    )
  }
  
  filteredKnowledge.value = data
}

// 防抖搜索
const debouncedSearch = debounce(searchKnowledge, 300)

// 查看详情
const viewDetail = (item: KnowledgeItem) => {
  selectedItem.value = item
  // 增加阅读量
  item.views += 1
  showDetailDialog.value = true
}

// 编辑项目
const editItem = (item: KnowledgeItem) => {
  isEditing.value = true
  Object.assign(knowledgeForm, item)
  showAddDialog.value = true
}

// 删除项目
const deleteItem = (item: KnowledgeItem) => {
  ElMessageBox.confirm(
    `确定删除 "${item.title}"？`,
    '确认删除',
    {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    const index = knowledgeData.value.findIndex(k => k.id === item.id)
    if (index > -1) {
      knowledgeData.value.splice(index, 1)
      searchKnowledge()
      ElMessage.success('删除成功')
    }
  }).catch(() => {
    // 用户取消
  })
}

// 保存知识
const saveKnowledge = () => {
  if (!formRef.value) return
  
  formRef.value.validate((valid: boolean) => {
    if (valid) {
      saving.value = true
      
      setTimeout(() => {
        if (isEditing.value) {
          // 编辑模式
          const index = knowledgeData.value.findIndex(k => k.id === knowledgeForm.id)
          if (index > -1) {
            Object.assign(knowledgeData.value[index], {
              ...knowledgeForm,
              updateTime: new Date().toISOString().split('T')[0]
            })
          }
          ElMessage.success('更新成功')
        } else {
          // 新增模式
          const newItem: KnowledgeItem = {
            ...knowledgeForm,
            id: Date.now().toString(),
            createTime: new Date().toISOString().split('T')[0],
            updateTime: new Date().toISOString().split('T')[0],
            views: 0
          }
          knowledgeData.value.unshift(newItem)
          ElMessage.success('添加成功')
        }
        
        showAddDialog.value = false
        searchKnowledge()
        resetForm()
        saving.value = false
      }, 500)
    }
  })
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  Object.assign(knowledgeForm, {
    id: '',
    title: '',
    summary: '',
    content: '',
    category: '',
    tags: '',
    author: '管理员'
  })
  isEditing.value = false
}

// Word文档上传与解析
const handleFileUpload = async (file) => {
  // 检查文件类型
  if (!file.raw.name.match(/\.(docx|doc)$/)) {
    ElMessage.error('只支持Word文档(.docx, .doc)')
    return
  }
  
  // 检查文件大小 (限制10MB)
  if (file.raw.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过10MB')
    return
  }
  
  uploadLoading.value = true
  ElMessage.info('正在上传并解析Word文档，请稍候...')
  
  try {
    const formData = new FormData()
    formData.append('file', file.raw)
    
    // 调用后端Word解析API（通过Vite代理）
    const response = await request({
      url: '/api/upload/word',
      method: 'POST',
      data: formData,
      baseURL: '', // 覆盖默认baseURL，使用相对路径通过代理转发
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    uploadLoading.value = false
    
    if (response.success) {
      parseResult.value = response
      ElMessage.success(`成功解析 ${file.raw.name}，提取 ${response.data.length} 个知识点`)
    } else {
      ElMessage.error(`解析失败: ${response.error}`)
    }
    
  } catch (error) {
    console.error('文件处理失败:', error)
    uploadLoading.value = false
    ElMessage.error('文件处理失败，请检查后端服务是否运行')
  }
}



// 导入到知识库
const importToKnowledge = async () => {
  if (!parseResult.value || !parseResult.value.data) {
    ElMessage.warning('没有可导出的数据')
    return
  }
  
  try {
    importLoading.value = true
    const count = parseResult.value.data.length
    
    // 添加到现有知识库
    parseResult.value.data.forEach(item => {
      knowledgeData.value.unshift(item)
    })
    
    // 重新搜索更新列表
    searchKnowledge()
    
    // 清空解析结果
    parseResult.value = null
    
    ElMessage.success(`成功导入 ${count} 个知识点到知识库`)
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error('导入失败，请重试')
  } finally {
    importLoading.value = false
  }
}

// 清除解析结果
const clearParseResult = () => {
  parseResult.value = null
}

// 监听搜索词变化
// 初始化
onMounted(() => {
  searchKnowledge()
})
</script>

<style scoped>
.knowledge-base {
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

/* 搜索区域 */
.search-section {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  align-items: center;
}

.search-box {
  flex: 1;
  max-width: 500px;
}

/* 分类导航 */
.categories {
  margin-bottom: 24px;
}

.category-tabs {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 4px 0;
}

.tab-btn {
  padding: 8px 16px;
  border: 1px solid #dcdfe6;
  background: white;
  border-radius: 20px;
  cursor: pointer;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
  font-size: 14px;
}

.tab-btn:hover {
  border-color: #409eff;
  color: #409eff;
}

.tab-btn.active {
  background: #409eff;
  border-color: #409eff;
  color: white;
}

.count {
  background: rgba(255,255,255,0.2);
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 12px;
}

.tab-btn.active .count {
  background: rgba(255,255,255,0.3);
}

/* 知识列表 */
.knowledge-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.knowledge-item {
  background: white;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.knowledge-item:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  gap: 12px;
}

.title {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: #303133;
  flex: 1;
}

.summary {
  margin: 0 0 16px 0;
  color: #606266;
  line-height: 1.5;
  font-size: 14px;
}

.item-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  font-size: 12px;
  color: #909399;
}

.item-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
}

/* 详情对话框 */
.detail-content {
  max-height: 600px;
  overflow-y: auto;
}

.detail-header {
  margin-bottom: 24px;
  text-align: center;
}

.detail-header h2 {
  margin: 0 0 16px 0;
  color: #303133;
}

.detail-meta {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.detail-body {
  margin-bottom: 24px;
}

.content-text {
  line-height: 1.8;
  color: #303133;
  font-size: 14px;
}

.detail-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* 解析结果样式 */
.parse-result {
  margin: 20px 0;
}

.parse-result-card {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.parse-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
}

.parse-preview {
  margin-top: 20px;
}

.parse-preview h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.preview-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.preview-item {
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
}

.preview-item h5 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 16px;
}

.preview-item p {
  margin: 0 0 12px 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.4;
}

.parse-actions {
  margin-top: 20px;
  display: flex;
  gap: 12px;
}

.parse-success {
  margin-top: 16px;
}

.parse-error {
  margin-top: 16px;
}

.action-buttons {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .knowledge-base {
    padding: 16px;
  }
  
  .search-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    max-width: none;
  }
  
  .category-tabs {
    gap: 6px;
  }
  
  .tab-btn {
    padding: 6px 12px;
    font-size: 13px;
  }
  
  .knowledge-item {
    padding: 16px;
  }
  
  .item-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .item-meta {
    flex-direction: column;
    gap: 4px;
  }
  
  .detail-meta {
    flex-direction: column;
    gap: 8px;
  }
  
  .parse-actions {
    flex-direction: column;
  }
  
  .parse-header {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
  
  .preview-list {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>