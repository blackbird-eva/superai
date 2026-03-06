<template>
  <div class="knowledge-base">
    <!-- 顶部导航栏 -->
    <div class="top-navbar">
      <div class="navbar-left">
        <div class="logo">
          <el-icon :size="24" color="#2932e1"><Document /></el-icon>
          <span class="logo-text">文档中心</span>
        </div>
        <div class="breadcrumb">
          <span class="breadcrumb-item active">我的文档</span>
          <span class="breadcrumb-separator">/</span>
          <span class="breadcrumb-item">知识库</span>
        </div>
      </div>
      <div class="navbar-right">
        <el-input
          v-model="searchQuery"
          placeholder="搜索文档..."
          prefix-icon="Search"
          clearable
          class="search-input"
        />
        <el-button circle icon="Bell" size="large" />
        <div class="user-avatar">
          <el-avatar :size="36">用户</el-avatar>
        </div>
      </div>
    </div>

    <div class="content-layout">
      <!-- 左侧边栏 -->
      <div class="sidebar">
        <div class="sidebar-section">
          <div class="sidebar-title">
            <span>快速访问</span>
          </div>
          <div class="sidebar-items">
            <div
              v-for="item in quickAccessItems"
              :key="item.key"
              :class="['sidebar-item', { active: currentView === item.key }]"
              @click="currentView = item.key"
            >
              <el-icon><component :is="item.icon" /></el-icon>
              <span>{{ item.label }}</span>
              <span v-if="item.count" class="count">{{ item.count }}</span>
            </div>
          </div>
        </div>

        <div class="sidebar-section">
          <div class="sidebar-title">
            <span>文件夹</span>
            <el-button text icon="Plus" size="small" @click="createFolder" />
          </div>
          <div class="sidebar-items">
            <div
              v-for="folder in folders"
              :key="folder.id"
              :class="['sidebar-item', { active: currentFolder === folder.id }]"
              @click="currentFolder = folder.id"
            >
              <el-icon><Folder /></el-icon>
              <span>{{ folder.name }}</span>
              <el-dropdown trigger="click" @command="(cmd) => handleFolderCommand(cmd, folder)">
                <el-button text icon="MoreFilled" size="small" @click.stop />
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="rename">重命名</el-dropdown-item>
                    <el-dropdown-item command="delete">删除</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </div>
      </div>

      <!-- 主内容区 -->
      <div class="main-content">
        <!-- 工具栏 -->
        <div class="toolbar">
          <div class="toolbar-left">
            <el-button-group>
              <el-button
                :type="viewMode === 'list' ? 'primary' : ''"
                icon="List"
                @click="viewMode = 'list'"
              />
              <el-button
                :type="viewMode === 'card' ? 'primary' : ''"
                icon="Grid"
                @click="viewMode = 'card'"
              />
            </el-button-group>
            <el-dropdown trigger="click" @click="handleSort">
              <el-button>
                {{ getSortLabel() }}<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="name">按名称排序</el-dropdown-item>
                  <el-dropdown-item command="date">按时间排序</el-dropdown-item>
                  <el-dropdown-item command="size">按大小排序</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          <div class="toolbar-right">
            <el-button type="success" icon="Upload" @click="showUploadDialog = true">
              上传文档
            </el-button>
            <el-button type="primary" icon="Plus" @click="showAddDialog = true">
              新建文档
            </el-button>
          </div>
        </div>

        <!-- 文档列表 -->
        <div class="doc-list" v-if="viewMode === 'list'">
          <div class="list-header">
            <div class="list-cell name">名称</div>
            <div class="list-cell author">作者</div>
            <div class="list-cell date">更新时间</div>
            <div class="list-cell size">大小</div>
            <div class="list-cell actions">操作</div>
          </div>
          <div
            v-for="item in filteredDocuments"
            :key="item.id"
            :class="['list-row', { selected: selectedDoc === item.id }]"
            @click="selectDoc(item)"
            @contextmenu.prevent="showContextMenu($event, item)"
          >
            <div class="list-cell name">
              <el-icon class="doc-icon"><component :is="getDocIcon(item)" /></el-icon>
              <span class="doc-name">{{ item.title }}</span>
              <el-icon v-if="item.isFavorite" class="favorite-icon" color="#f5a623"><Star /></el-icon>
            </div>
            <div class="list-cell author">{{ item.author }}</div>
            <div class="list-cell date">{{ item.updateTime }}</div>
            <div class="list-cell size">{{ item.size }}</div>
            <div class="list-cell actions">
              <el-button-group>
                <el-button text icon="View" size="small" @click.stop="viewDetail(item)" />
                <el-button text icon="Edit" size="small" @click.stop="editItem(item)" />
                <el-button text icon="Share" size="small" @click.stop="shareDoc(item)" />
                <el-button text icon="Delete" size="small" type="danger" @click.stop="deleteItem(item)" />
              </el-button-group>
            </div>
          </div>
        </div>

        <div class="doc-grid" v-else>
          <div
            v-for="item in filteredDocuments"
            :key="item.id"
            :class="['doc-card', { selected: selectedDoc === item.id }]"
            @click="selectDoc(item)"
            @contextmenu.prevent="showContextMenu($event, item)"
          >
            <div class="card-icon">
              <el-icon :size="48"><component :is="getDocIcon(item)" /></el-icon>
            </div>
            <div class="card-info">
              <h3 class="card-title" :title="item.title">{{ item.title }}</h3>
              <p class="card-summary">{{ item.summary }}</p>
            </div>
            <div class="card-meta">
              <span>{{ item.updateTime }}</span>
              <el-icon v-if="item.isFavorite" class="favorite-icon" color="#f5a623"><Star /></el-icon>
            </div>
            <div class="card-actions">
              <el-button-group>
                <el-button text icon="View" size="small" @click.stop="viewDetail(item)" />
                <el-button text icon="Edit" size="small" @click.stop="editItem(item)" />
                <el-button text icon="Share" size="small" @click.stop="shareDoc(item)" />
                <el-button text icon="Delete" size="small" type="danger" @click.stop="deleteItem(item)" />
              </el-button-group>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="filteredDocuments.length === 0" class="empty-state">
          <el-empty description="暂无文档">
            <el-button type="primary" @click="showAddDialog = true">创建文档</el-button>
          </el-empty>
        </div>
      </div>
    </div>

    <!-- 右键菜单 -->
    <div
      v-if="contextMenu.visible"
      :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
      class="context-menu"
    >
      <div class="menu-item" @click="openDoc(contextMenu.item)">
        <el-icon><FolderOpened /></el-icon>
        <span>打开</span>
      </div>
      <div class="menu-item" @click="editItem(contextMenu.item)">
        <el-icon><Edit /></el-icon>
        <span>编辑</span>
      </div>
      <div class="menu-item" @click="shareDoc(contextMenu.item)">
        <el-icon><Share /></el-icon>
        <span>分享</span>
      </div>
      <div class="menu-item" @click="toggleFavorite(contextMenu.item)">
        <el-icon><Star /></el-icon>
        <span>{{ contextMenu.item?.isFavorite ? '取消收藏' : '收藏' }}</span>
      </div>
      <div class="menu-divider"></div>
      <div class="menu-item danger" @click="deleteItem(contextMenu.item)">
        <el-icon><Delete /></el-icon>
        <span>删除</span>
      </div>
    </div>

    <!-- 上传对话框 -->
    <el-dialog
      title="上传文档"
      v-model="showUploadDialog"
      width="500px"
    >
      <el-upload
        class="upload-area"
        drag
        :auto-upload="false"
        :on-change="handleFileUpload"
        :show-file-list="false"
        accept=".docx,.doc"
        :disabled="uploadLoading"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 .docx、.doc 格式的 Word 文档，最大 10MB
          </div>
        </template>
      </el-upload>
    </el-dialog>

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
      :title="isEditing ? '编辑文档' : '新建文档'"
      v-model="showAddDialog"
      width="700px"
      @close="resetForm"
    >
      <el-form :model="knowledgeForm" :rules="formRules" ref="formRef" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="knowledgeForm.title" placeholder="请输入文档标题" />
        </el-form-item>

        <el-form-item label="文件夹" prop="folderId">
          <el-select v-model="knowledgeForm.folderId" placeholder="选择文件夹" style="width: 100%">
            <el-option label="根目录" value="" />
            <el-option
              v-for="folder in folders"
              :key="folder.id"
              :label="folder.name"
              :value="folder.id"
            />
          </el-select>
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
            placeholder="简要描述文档内容"
          />
        </el-form-item>

        <el-form-item label="内容" prop="content">
          <el-input
            v-model="knowledgeForm.content"
            type="textarea"
            :rows="10"
            placeholder="详细的文档内容..."
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
      title="文档详情"
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
            <span class="views">阅读 {{ selectedItem.views }}</span>
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

    <!-- 分享对话框 -->
    <el-dialog
      title="分享文档"
      v-model="showShareDialog"
      width="500px"
    >
      <div v-if="shareItem" class="share-content">
        <el-alert
          title="分享链接"
          type="info"
          :description="getShareLink(shareItem)"
          :closable="false"
        />
        <div class="share-actions">
          <el-button @click="copyShareLink">复制链接</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Plus, View, Edit, Delete, Upload, Document, Folder, Star,
  ArrowDown, Grid, List, Share, MoreFilled, FolderOpened, UploadFilled,
  Clock, Collection, DeleteFilled, User, Files
} from '@element-plus/icons-vue'
import { request } from '/@/utils/service'

// 文档接口
export interface DocItem {
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
  size: string
  isFavorite: boolean
  folderId: string
}

// 文件夹接口
export interface FolderItem {
  id: string
  name: string
  createTime: string
}

// 响应式数据
const searchQuery = ref('')
const currentView = ref('all')
const currentFolder = ref('')
const viewMode = ref<'list' | 'card'>('list')
const sortBy = ref('date')
const showAddDialog = ref(false)
const showDetailDialog = ref(false)
const showUploadDialog = ref(false)
const showShareDialog = ref(false)
const isEditing = ref(false)
const saving = ref(false)
const uploadLoading = ref(false)
const importLoading = ref(false)
const selectedItem = ref<DocItem | null>(null)
const shareItem = ref<DocItem | null>(null)
const selectedDoc = ref<string>('')
const formRef = ref()

// Word解析相关
const parseResult = ref<any>(null)

// 右键菜单
const contextMenu = reactive({
  visible: false,
  x: 0,
  y: 0,
  item: null as DocItem | null
})

// 表单数据
const knowledgeForm = reactive({
  id: '',
  title: '',
  summary: '',
  content: '',
  category: '',
  tags: '',
  author: '管理员',
  folderId: ''
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
  { key: 'product', label: '产品知识', color: 'primary' },
  { key: 'tech', label: '技术文档', color: 'success' },
  { key: 'guide', label: '操作指南', color: 'warning' },
  { key: 'faq', label: '常见问题', color: 'info' },
  { key: 'process', label: '业务流程', color: 'danger' }
]

// 快速访问项
const quickAccessItems = ref([
  { key: 'all', label: '我的文档', icon: Files, count: 0 },
  { key: 'recent', label: '最近访问', icon: Clock, count: 0 },
  { key: 'favorites', label: '收藏夹', icon: Star, count: 0 },
  { key: 'trash', label: '回收站', icon: DeleteFilled, count: 0 }
])

// 文件夹数据
const folders = ref<FolderItem[]>([
  { id: 'folder1', name: '产品文档', createTime: '2024-01-10' },
  { id: 'folder2', name: '技术资料', createTime: '2024-01-12' },
  { id: 'folder3', name: '操作手册', createTime: '2024-01-15' }
])

// 示例知识库数据
const knowledgeData = ref<DocItem[]>([
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
    views: 156,
    size: '25 KB',
    isFavorite: true,
    folderId: 'folder1'
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
    views: 89,
    size: '18 KB',
    isFavorite: false,
    folderId: 'folder2'
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
    views: 203,
    size: '12 KB',
    isFavorite: true,
    folderId: 'folder3'
  },
  {
    id: '4',
    title: '系统常见问题解答',
    summary: '用户在使用系统过程中遇到的常见问题及解决方案',
    content: '常见问题：\n\nQ1：如何重置密码？\nA1：点击登录页面的"忘记密码"链接，按照提示操作。\n\nQ2：上传文件失败怎么办？\nA2：请检查文件大小和格式，确保不超过限制。\n\nQ3：如何联系客服？\nA3：点击页面右下角的客服图标即可在线咨询。',
    category: 'faq',
    tags: 'FAQ,常见问题,帮助',
    author: '客服团队',
    createTime: '2024-01-03',
    updateTime: '2024-01-13',
    views: 342,
    size: '8 KB',
    isFavorite: false,
    folderId: ''
  },
  {
    id: '5',
    title: '业务流程优化方案',
    summary: '企业业务流程的优化思路和实施步骤',
    content: '业务流程优化方案：\n\n一、现状分析\n梳理现有业务流程，识别瓶颈点。\n\n二、目标设定\n明确优化目标和关键指标。\n\n三、方案设计\n设计新的流程方案，考虑系统支持能力。\n\n四、试点实施\n选择试点部门，小范围验证。\n\n五、全面推广\n总结试点经验，逐步推广全公司。',
    category: 'process',
    tags: '业务流程,优化,管理',
    author: '管理咨询',
    createTime: '2024-01-01',
    updateTime: '2024-01-11',
    views: 67,
    size: '15 KB',
    isFavorite: false,
    folderId: ''
  }
])

// 过滤后的文档列表
const filteredDocuments = computed(() => {
  let data = [...knowledgeData.value]

  // 按当前视图过滤
  if (currentView.value === 'recent') {
    data = data.filter(item => item.views > 100).slice(0, 5)
  } else if (currentView.value === 'favorites') {
    data = data.filter(item => item.isFavorite)
  } else if (currentView.value === 'trash') {
    // 回收站逻辑可以扩展
    data = []
  }

  // 按文件夹过滤
  if (currentFolder.value) {
    data = data.filter(item => item.folderId === currentFolder.value)
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

  // 排序
  if (sortBy.value === 'name') {
    data.sort((a, b) => a.title.localeCompare(b.title))
  } else if (sortBy.value === 'date') {
    data.sort((a, b) => new Date(b.updateTime).getTime() - new Date(a.updateTime).getTime())
  } else if (sortBy.value === 'size') {
    data.sort((a, b) => {
      const sizeA = parseInt(a.size)
      const sizeB = parseInt(b.size)
      return sizeB - sizeA
    })
  }

  // 更新计数
  quickAccessItems.value[0].count = knowledgeData.value.length
  quickAccessItems.value[1].count = knowledgeData.value.filter(i => i.views > 100).length
  quickAccessItems.value[2].count = knowledgeData.value.filter(i => i.isFavorite).length

  return data
})

// 获取排序标签
const getSortLabel = () => {
  const labels = {
    name: '按名称排序',
    date: '按时间排序',
    size: '按大小排序'
  }
  return labels[sortBy.value as keyof typeof labels]
}

// 获取分类标签
const getCategoryLabel = (category: string) => {
  const cat = categories.find(c => c.key === category)
  return cat ? cat.label : '未分类'
}

// 获取标签类型
const getTagType = (category: string) => {
  const cat = categories.find(c => c.key === category)
  return cat ? cat.color : 'info'
}

// 获取文档图标
const getDocIcon = (item: DocItem) => {
  if (item.category === 'product') return Document
  if (item.category === 'tech') return Document
  return Document
}

// 格式化内容
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

// 选择文档
const selectDoc = (item: DocItem) => {
  selectedDoc.value = item.id
}

// 打开文档
const openDoc = (item: DocItem) => {
  viewDetail(item)
  hideContextMenu()
}

// 查看详情
const viewDetail = (item: DocItem) => {
  selectedItem.value = item
  item.views += 1
  showDetailDialog.value = true
  hideContextMenu()
}

// 编辑项目
const editItem = (item: DocItem) => {
  isEditing.value = true
  Object.assign(knowledgeForm, item)
  showAddDialog.value = true
  hideContextMenu()
}

// 删除项目
const deleteItem = (item: DocItem) => {
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
      ElMessage.success('删除成功')
    }
  }).catch(() => {
    // 用户取消
  })
  hideContextMenu()
}

// 保存知识
const saveKnowledge = () => {
  if (!formRef.value) return

  formRef.value.validate((valid: boolean) => {
    if (valid) {
      saving.value = true

      setTimeout(() => {
        if (isEditing.value) {
          const index = knowledgeData.value.findIndex(k => k.id === knowledgeForm.id)
          if (index > -1) {
            Object.assign(knowledgeData.value[index], {
              ...knowledgeForm,
              updateTime: new Date().toISOString().split('T')[0]
            })
          }
          ElMessage.success('更新成功')
        } else {
          const newItem: DocItem = {
            ...knowledgeForm,
            id: Date.now().toString(),
            createTime: new Date().toISOString().split('T')[0],
            updateTime: new Date().toISOString().split('T')[0],
            views: 0,
            size: '10 KB',
            isFavorite: false
          }
          knowledgeData.value.unshift(newItem)
          ElMessage.success('添加成功')
        }

        showAddDialog.value = false
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
    author: '管理员',
    folderId: ''
  })
  isEditing.value = false
}

// Word文档上传与解析
const handleFileUpload = async (file) => {
  if (!file.raw.name.match(/\.(docx|doc)$/)) {
    ElMessage.error('只支持Word文档(.docx, .doc)')
    return
  }

  if (file.raw.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过10MB')
    return
  }

  uploadLoading.value = true
  ElMessage.info('正在上传并解析Word文档，请稍候...')

  try {
    const formData = new FormData()
    formData.append('file', file.raw)

    const response = await request({
      url: '/api/upload/word',
      method: 'POST',
      data: formData,
      baseURL: '',
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    uploadLoading.value = false
    showUploadDialog.value = false

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

    parseResult.value.data.forEach((item: any) => {
      knowledgeData.value.unshift({
        ...item,
        size: '15 KB',
        isFavorite: false,
        folderId: currentFolder.value
      })
    })

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

// 创建文件夹
const createFolder = () => {
  ElMessageBox.prompt('请输入文件夹名称', '新建文件夹', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputPattern: /^.{1,20}$/,
    inputErrorMessage: '文件夹名称长度为1-20个字符'
  }).then(({ value }) => {
    folders.value.push({
      id: 'folder' + Date.now(),
      name: value,
      createTime: new Date().toISOString().split('T')[0]
    })
    ElMessage.success('文件夹创建成功')
  }).catch(() => {
    // 用户取消
  })
}

// 处理文件夹命令
const handleFolderCommand = (cmd: string, folder: FolderItem) => {
  if (cmd === 'rename') {
    ElMessageBox.prompt('请输入新的文件夹名称', '重命名文件夹', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputValue: folder.name
    }).then(({ value }) => {
      const f = folders.value.find(f => f.id === folder.id)
      if (f) {
        f.name = value
        ElMessage.success('重命名成功')
      }
    }).catch(() => {
      // 用户取消
    })
  } else if (cmd === 'delete') {
    ElMessageBox.confirm(
      `确定删除文件夹 "${folder.name}"？文件夹内的文档将不会被删除。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(() => {
      const index = folders.value.findIndex(f => f.id === folder.id)
      if (index > -1) {
        folders.value.splice(index, 1)
        if (currentFolder.value === folder.id) {
          currentFolder.value = ''
        }
        ElMessage.success('删除成功')
      }
    }).catch(() => {
      // 用户取消
    })
  }
}

// 切换收藏
const toggleFavorite = (item: DocItem) => {
  item.isFavorite = !item.isFavorite
  ElMessage.success(item.isFavorite ? '已收藏' : '已取消收藏')
  hideContextMenu()
}

// 分享文档
const shareDoc = (item: DocItem) => {
  shareItem.value = item
  showShareDialog.value = true
  hideContextMenu()
}

// 获取分享链接
const getShareLink = (item: DocItem) => {
  return `https://docs.example.com/share/${item.id}`
}

// 复制分享链接
const copyShareLink = () => {
  if (shareItem.value) {
    navigator.clipboard.writeText(getShareLink(shareItem.value))
    ElMessage.success('链接已复制到剪贴板')
  }
}

// 显示右键菜单
const showContextMenu = (event: MouseEvent, item: DocItem) => {
  contextMenu.visible = true
  contextMenu.x = event.clientX
  contextMenu.y = event.clientY
  contextMenu.item = item
}

// 隐藏右键菜单
const hideContextMenu = () => {
  contextMenu.visible = false
}

// 点击其他地方关闭右键菜单
const handleClickOutside = () => {
  if (contextMenu.visible) {
    hideContextMenu()
  }
}

// 初始化
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.knowledge-base {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f6f7;
  overflow: hidden;
}

/* 顶部导航栏 */
.top-navbar {
  height: 56px;
  background: white;
  border-bottom: 1px solid #e8eaed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 24px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.logo-text {
  font-size: 18px;
  font-weight: 500;
  color: #2932e1;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
  font-size: 14px;
}

.breadcrumb-item {
  cursor: pointer;
  transition: color 0.2s;
}

.breadcrumb-item:hover {
  color: #2932e1;
}

.breadcrumb-item.active {
  color: #303133;
  font-weight: 500;
}

.breadcrumb-separator {
  color: #909399;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.search-input {
  width: 300px;
}

.user-avatar {
  cursor: pointer;
}

/* 内容布局 */
.content-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 左侧边栏 */
.sidebar {
  width: 240px;
  background: white;
  border-right: 1px solid #e8eaed;
  overflow-y: auto;
  flex-shrink: 0;
}

.sidebar-section {
  padding: 16px;
}

.sidebar-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
  margin-bottom: 8px;
  font-size: 12px;
  font-weight: 500;
  color: #909399;
}

.sidebar-items {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  color: #606266;
}

.sidebar-item:hover {
  background: #f5f6f7;
  color: #2932e1;
}

.sidebar-item.active {
  background: #ecf2ff;
  color: #2932e1;
  font-weight: 500;
}

.sidebar-item .count {
  margin-left: auto;
  background: rgba(41, 50, 225, 0.1);
  color: #2932e1;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 12px;
}

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 工具栏 */
.toolbar {
  height: 56px;
  background: white;
  border-bottom: 1px solid #e8eaed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 文档列表视图 */
.doc-list {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.list-header {
  display: flex;
  padding: 12px 16px;
  background: #f5f6f7;
  border-radius: 8px;
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #909399;
}

.list-cell {
  display: flex;
  align-items: center;
}

.list-cell.name {
  flex: 1;
  padding-left: 48px;
}

.list-cell.author {
  width: 120px;
}

.list-cell.date {
  width: 150px;
}

.list-cell.size {
  width: 100px;
}

.list-cell.actions {
  width: 200px;
  justify-content: flex-end;
}

.list-row {
  display: flex;
  padding: 16px;
  background: white;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
  align-items: center;
}

.list-row:hover {
  background: #f8f9fa;
}

.list-row.selected {
  background: #ecf2ff;
  border: 1px solid #2932e1;
}

.doc-icon {
  color: #2932e1;
  margin-right: 8px;
}

.doc-name {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.favorite-icon {
  margin-left: 8px;
}

/* 文档卡片视图 */
.doc-grid {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.doc-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e8eaed;
  display: flex;
  flex-direction: column;
}

.doc-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.doc-card.selected {
  border-color: #2932e1;
  background: #ecf2ff;
}

.card-icon {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 80px;
  margin-bottom: 16px;
  color: #2932e1;
}

.card-info {
  flex: 1;
  margin-bottom: 12px;
}

.card-title {
  margin: 0 0 8px 0;
  font-size: 15px;
  font-weight: 500;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-summary {
  margin: 0;
  font-size: 13px;
  color: #909399;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
  font-size: 12px;
  color: #909399;
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 4px;
  margin-top: 12px;
  opacity: 0;
  transition: opacity 0.2s;
}

.doc-card:hover .card-actions {
  opacity: 1;
}

/* 空状态 */
.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 右键菜单 */
.context-menu {
  position: fixed;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.15);
  padding: 8px 0;
  min-width: 160px;
  z-index: 9999;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 14px;
  color: #606266;
}

.menu-item:hover {
  background: #f5f6f7;
  color: #2932e1;
}

.menu-item.danger:hover {
  background: #fef0f0;
  color: #f56c6c;
}

.menu-divider {
  height: 1px;
  background: #e8eaed;
  margin: 8px 0;
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
  font-size: 24px;
  font-weight: 500;
}

.detail-meta {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  font-size: 14px;
  color: #909399;
}

.detail-body {
  margin-bottom: 24px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
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
  justify-content: center;
}

/* 解析结果样式 */
.parse-result {
  margin: 20px 0;
}

.parse-result-card {
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
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
  border: 1px solid #e8eaed;
  border-radius: 8px;
  background: #f8f9fa;
}

.preview-item h5 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 15px;
  font-weight: 500;
}

.preview-item p {
  margin: 0 0 12px 0;
  color: #606266;
  font-size: 13px;
  line-height: 1.5;
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

/* 上传区域 */
.upload-area {
  padding: 20px 0;
}

.upload-area :deep(.el-upload-dragger) {
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  padding: 40px;
}

/* 分享内容 */
.share-content {
  padding: 20px 0;
}

.share-actions {
  margin-top: 16px;
  text-align: center;
}

/* 自定义滚动条 */
:deep(.sidebar::-webkit-scrollbar),
:deep(.doc-list::-webkit-scrollbar),
:deep(.doc-grid::-webkit-scrollbar),
:deep(.detail-content::-webkit-scrollbar) {
  width: 6px;
}

:deep(.sidebar::-webkit-scrollbar-track),
:deep(.doc-list::-webkit-scrollbar-track),
:deep(.doc-grid::-webkit-scrollbar-track),
:deep(.detail-content::-webkit-scrollbar-track) {
  background: transparent;
}

:deep(.sidebar::-webkit-scrollbar-thumb),
:deep(.doc-list::-webkit-scrollbar-thumb),
:deep(.doc-grid::-webkit-scrollbar-thumb),
:deep(.detail-content::-webkit-scrollbar-thumb) {
  background: #dcdfe6;
  border-radius: 3px;
}

:deep(.sidebar::-webkit-scrollbar-thumb:hover),
:deep(.doc-list::-webkit-scrollbar-thumb:hover),
:deep(.doc-grid::-webkit-scrollbar-thumb:hover),
:deep(.detail-content::-webkit-scrollbar-thumb:hover) {
  background: #b0b4be;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .sidebar {
    width: 200px;
  }

  .list-cell.author {
    width: 100px;
  }

  .list-cell.date {
    width: 120px;
  }

  .list-cell.size {
    display: none;
  }
}

@media (max-width: 768px) {
  .top-navbar {
    padding: 0 16px;
  }

  .search-input {
    width: 200px;
  }

  .sidebar {
    width: 0;
    border: none;
    padding: 0;
  }

  .doc-grid {
    grid-template-columns: 1fr;
    padding: 16px;
  }

  .doc-list {
    padding: 16px;
  }

  .list-cell {
    font-size: 12px;
  }

  .list-cell.actions {
    width: 120px;
  }

  .detail-header h2 {
    font-size: 20px;
  }
}
</style>