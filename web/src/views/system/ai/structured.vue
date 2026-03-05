<template>
  <div class="structured-container">
    <!-- 顶部导航栏 -->
    <div class="top-navbar">
      <div class="navbar-left">
        <div class="logo-area">
          <el-icon class="logo-icon"><Document /></el-icon>
          <span class="logo-text">文档管理中心</span>
        </div>
        <el-breadcrumb separator="/" class="breadcrumb">
          <el-breadcrumb-item>文档</el-breadcrumb-item>
          <el-breadcrumb-item>结构化管理</el-breadcrumb-item>
          <el-breadcrumb-item v-if="currentNode">{{ currentNode.title }}</el-breadcrumb-item>
        </el-breadcrumb>
      </div>

      <div class="navbar-center">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索文档..."
          prefix-icon="Search"
          class="search-input"
          clearable
        >
        </el-input>
      </div>

      <div class="navbar-right">
        <div class="stats-info">
          <span class="stat-item">
            <el-icon><Document /></el-icon>
            总文档 {{ totalChapters }}
          </span>
          <span class="stat-item success">
            <el-icon><CircleCheck /></el-icon>
            已完成 {{ completedChapters }}
          </span>
          <span class="stat-item warning">
            <el-icon><Clock /></el-icon>
            进行中 {{ incompleteChapters }}
          </span>
        </div>
        <el-dropdown>
          <el-button class="more-btn" :icon="MoreFilled">更多</el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item :icon="Upload">导入文档</el-dropdown-item>
              <el-dropdown-item :icon="Download">导出文档</el-dropdown-item>
              <el-dropdown-item :icon="Share">分享文档</el-dropdown-item>
              <el-dropdown-item :icon="Star">收藏文档</el-dropdown-item>
              <el-dropdown-item :icon="Setting">设置</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button type="primary" :icon="Plus" @click="handleAddChapter">新建文档</el-button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="content-wrapper">
      <!-- 左侧：文档导航 -->
      <div class="doc-nav-panel">
        <div class="nav-header">
          <div class="nav-title">
            <el-icon><FolderOpened /></el-icon>
            <span>文档目录</span>
          </div>
          <div class="nav-actions">
            <el-tooltip content="添加文件夹" placement="top">
              <el-button text :icon="FolderAdd" @click="handleAddFolder" />
            </el-tooltip>
            <el-tooltip content="刷新" placement="top">
              <el-button text :icon="Refresh" @click="handleRefresh" />
            </el-tooltip>
            <el-tooltip content="设置" placement="top">
              <el-button text :icon="Setting" />
            </el-tooltip>
          </div>
        </div>

        <div class="nav-toolbar">
          <el-button-group>
            <el-button :type="viewMode === 'tree' ? 'primary' : ''" size="small" @click="viewMode = 'tree'">
              <el-icon><List /></el-icon>
            </el-button>
            <el-button :type="viewMode === 'card' ? 'primary' : ''" size="small" @click="viewMode = 'card'">
              <el-icon><Grid /></el-icon>
            </el-button>
          </el-button-group>
          <el-input
            v-model="navSearch"
            placeholder="筛选文档..."
            size="small"
            prefix-icon="Search"
            clearable
            class="nav-search"
          />
        </div>

        <div class="nav-content">
          <!-- 树形视图 -->
          <div v-if="viewMode === 'tree'" class="tree-view">
            <el-tree
              ref="treeRef"
              :data="structureData"
              :props="treeProps"
              :highlight-current="true"
              :expand-on-click-node="false"
              :filter-node-method="filterNode"
              node-key="id"
              default-expand-all
              @node-click="handleNodeClick"
            >
              <template #default="{ node, data }">
                <div class="tree-node-wrapper">
                  <div class="node-main">
                    <el-icon class="node-type-icon" :class="data.type">
                      <Folder v-if="data.type === 'folder'" />
                      <Document v-else />
                    </el-icon>
                    <span class="node-text">{{ node.label }}</span>
                    <el-tag v-if="data.status === 'completed'" type="success" size="small" effect="plain">
                      <el-icon><Check /></el-icon>
                    </el-tag>
                  </div>
                  <div class="node-meta">
                    <el-dropdown trigger="click">
                      <el-button text size="small" :icon="MoreFilled" />
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item v-if="data.type === 'folder'" :icon="Plus">添加子项</el-dropdown-item>
                          <el-dropdown-item :icon="Edit">编辑</el-dropdown-item>
                          <el-dropdown-item :icon="CopyDocument">复制</el-dropdown-item>
                          <el-dropdown-item :icon="Download">下载</el-dropdown-item>
                          <el-dropdown-item :icon="Share">分享</el-dropdown-item>
                          <el-dropdown-item divided :icon="Delete">删除</el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </div>
                </div>
              </template>
            </el-tree>
          </div>

          <!-- 卡片视图 -->
          <div v-else class="card-view">
            <div
              v-for="item in flattenDocs"
              :key="item.id"
              class="doc-card"
              :class="{ active: currentNode?.id === item.id }"
              @click="handleNodeClick(item)"
            >
              <div class="card-icon">
                <el-icon :class="item.type">
                  <Folder v-if="item.type === 'folder'" />
                  <Document v-else />
                </el-icon>
              </div>
              <div class="card-content">
                <div class="card-title">{{ item.title }}</div>
                <div class="card-meta">
                  <span class="meta-item">
                    <el-icon><Clock /></el-icon>
                    {{ item.order }}
                  </span>
                  <span class="meta-item" v-if="item.tags.length > 0">
                    <el-icon><PriceTag /></el-icon>
                    {{ item.tags[0] }}
                  </span>
                </div>
              </div>
              <div class="card-status">
                <el-tag :type="getStatusType(item.status)" size="small">
                  {{ getStatusText(item.status) }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：编辑区 -->
      <div class="editor-panel">
        <div v-if="currentNode" class="editor-wrapper">
          <!-- 文档头部 -->
          <div class="doc-header">
            <div class="doc-title-area">
              <el-input
                v-model="nodeForm.title"
                class="title-input"
                placeholder="文档标题"
                :disabled="!isEditing"
              />
              <div class="doc-meta">
                <span class="meta-tag">
                  <el-icon><Document /></el-icon>
                  {{ nodeForm.type === 'folder' ? '文件夹' : '文档' }}
                </span>
                <span class="meta-tag">
                  <el-icon><PriceTag /></el-icon>
                  {{ nodeForm.tags.join(', ') || '无标签' }}
                </span>
                <span class="meta-tag">
                  <el-icon><Clock /></el-icon>
                  {{ formatTime(new Date()) }}
                </span>
              </div>
            </div>
            <div class="doc-actions">
              <el-button v-if="!isEditing" :icon="Edit" @click="isEditing = true">编辑</el-button>
              <template v-else>
                <el-button @click="handleReset">取消</el-button>
                <el-button type="primary" :icon="Check" @click="handleSave">保存</el-button>
              </template>
              <el-dropdown>
                <el-button :icon="MoreFilled">更多</el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item :icon="Share">分享</el-dropdown-item>
                    <el-dropdown-item :icon="Download">下载</el-dropdown-item>
                    <el-dropdown-item :icon="CopyDocument">复制</el-dropdown-item>
                    <el-dropdown-item :icon="Delete">删除</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>

          <!-- 编辑内容 -->
          <div class="editor-content">
            <el-form :model="nodeForm" label-width="100px" :disabled="!isEditing">
              <el-form-item label="文档类型">
                <el-select v-model="nodeForm.type" placeholder="选择类型">
                  <el-option label="文件夹" value="folder"></el-option>
                  <el-option label="文档" value="document"></el-option>
                </el-select>
              </el-form-item>

              <el-form-item label="排序序号">
                <el-input-number v-model="nodeForm.order" :min="1" :max="999" />
              </el-form-item>

              <el-form-item label="文档状态">
                <el-radio-group v-model="nodeForm.status">
                  <el-radio label="pending">未开始</el-radio>
                  <el-radio label="processing">进行中</el-radio>
                  <el-radio label="completed">已完成</el-radio>
                </el-radio-group>
              </el-form-item>

              <el-form-item label="标签管理">
                <div class="tags-input">
                  <el-select
                    v-model="nodeForm.tags"
                    multiple
                    filterable
                    allow-create
                    placeholder="添加标签"
                  >
                    <el-option
                      v-for="tag in tagOptions"
                      :key="tag"
                      :label="tag"
                      :value="tag"
                    />
                  </el-select>
                </div>
              </el-form-item>

              <el-form-item label="文档描述">
                <el-input
                  v-model="nodeForm.description"
                  type="textarea"
                  :rows="3"
                  placeholder="添加文档说明或备注"
                />
              </el-form-item>

              <el-form-item label="文档内容" v-if="nodeForm.type === 'document'">
                <div class="content-editor">
                  <el-input
                    v-model="nodeForm.content"
                    type="textarea"
                    :rows="15"
                    placeholder="输入文档内容..."
                    class="textarea-editor"
                  />
                </div>
              </el-form-item>

              <el-form-item label="关联资源" v-if="nodeForm.type === 'document'">
                <div class="resource-list">
                  <div
                    v-for="(resource, index) in nodeForm.resources"
                    :key="index"
                    class="resource-item"
                  >
                    <el-icon><Link /></el-icon>
                    <span>{{ resource }}</span>
                    <el-button text size="small" :icon="Close" @click="handleRemoveResource(index)" />
                  </div>
                  <el-button
                    size="small"
                    :icon="Plus"
                    @click="handleAddResource"
                    class="add-resource-btn"
                  >
                    添加资源
                  </el-button>
                </div>
              </el-form-item>
            </el-form>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="empty-state">
          <el-icon class="empty-icon"><DocumentAdd /></el-icon>
          <h3>选择文档开始编辑</h3>
          <p>从左侧选择一个文档，或创建新文档开始使用</p>
          <el-button type="primary" :icon="Plus" @click="handleAddChapter">创建新文档</el-button>
        </div>
      </div>
    </div>

    <!-- 添加/编辑文档对话框 -->
    <el-dialog
      v-model="showNodeDialog"
      :title="dialogTitle"
      width="500px"
    >
      <el-form :model="nodeForm" label-width="100px">
        <el-form-item label="文档名称">
          <el-input v-model="nodeForm.title" placeholder="请输入文档名称" />
        </el-form-item>
        <el-form-item label="文档类型">
          <el-radio-group v-model="nodeForm.type">
            <el-radio label="folder">文件夹</el-radio>
            <el-radio label="document">文档</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="排序序号">
          <el-input-number v-model="nodeForm.order" :min="1" :max="999" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showNodeDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmNode">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Upload,
  FolderOpened,
  Refresh,
  Download,
  Plus,
  Sort,
  Edit,
  Delete,
  Folder,
  Document,
  Check,
  Search,
  MoreFilled,
  FolderAdd,
  List,
  Grid,
  CircleCheck,
  Clock,
  Star,
  Setting,
  Share,
  CopyDocument,
  PriceTag,
  Link,
  Close,
  DocumentAdd
} from '@element-plus/icons-vue'

// 类型定义
interface DocNode {
  id: string
  title: string
  type: 'folder' | 'document'
  order: number
  status: string
  tags: string[]
  description: string
  content: string
  resources: string[]
  children?: DocNode[]
}

// 数据状态
const treeRef = ref<any>(null)
const structureData = ref<DocNode[]>([])
const currentNode = ref<DocNode | null>(null)
const showNodeDialog = ref(false)
const dialogTitle = ref('添加文档')
const dialogMode = ref('add')
const parentNode = ref<DocNode | null>(null)
const viewMode = ref('tree') // tree 或 card
const navSearch = ref('')
const searchKeyword = ref('')
const isEditing = ref(false)

const nodeForm = reactive({
  id: '',
  title: '',
  type: 'document' as 'folder' | 'document',
  order: 1,
  status: 'pending',
  tags: [] as string[],
  description: '',
  content: '',
  resources: [] as string[]
})

const treeProps = {
  children: 'children',
  label: 'title'
}

const tagOptions = ref(['重要', '紧急', '审核中', '待翻译', '已完成', '草稿', '发布'])

// 计算属性
const totalChapters = computed(() => countNodes(structureData.value))
const incompleteChapters = computed(() => countNodesByStatus(structureData.value, ['pending', 'processing']))
const completedChapters = computed(() => countNodesByStatus(structureData.value, ['completed']))

const flattenDocs = computed(() => {
  const result: DocNode[] = []
  const flatten = (nodes: DocNode[]) => {
    nodes.forEach(node => {
      result.push(node)
      if (node.children) {
        flatten(node.children)
      }
    })
  }
  flatten(structureData.value)
  return result
})

// 监听搜索
watch(navSearch, (val) => {
  if (treeRef.value) {
    treeRef.value.filter(val)
  }
})

// 方法
const filterNode = (value: string, data: DocNode) => {
  if (!value) return true
  return data.title.toLowerCase().includes(value.toLowerCase())
}

const countNodes = (nodes: DocNode[]) => {
  let count = 0
  nodes.forEach(node => {
    count++
    if (node.children) {
      count += countNodes(node.children)
    }
  })
  return count
}

const countNodesByStatus = (nodes: DocNode[], statuses: string[]) => {
  let count = 0
  nodes.forEach(node => {
    if (statuses.includes(node.status)) {
      count++
    }
    if (node.children) {
      count += countNodesByStatus(node.children, statuses)
    }
  })
  return count
}

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    pending: 'info',
    processing: 'warning',
    completed: 'success'
  }
  return types[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    pending: '未开始',
    processing: '进行中',
    completed: '已完成'
  }
  return texts[status] || '未知'
}

const formatTime = (date: Date) => {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN')
}

// 初始化演示数据
const initDemoData = () => {
  structureData.value = [
    {
      id: '1',
      title: '产品文档',
      type: 'folder',
      order: 1,
      status: 'completed',
      tags: ['重要', '发布'],
      description: '产品相关的文档集合',
      content: '',
      resources: [],
      children: [
        {
          id: '1-1',
          title: '产品介绍',
          type: 'document',
          order: 1,
          status: 'completed',
          tags: ['已完成'],
          description: '简要介绍产品定位和目标用户',
          content: '本产品是一款基于AI技术的智能翻译系统，支持多语言实时翻译，具备术语管理、质量校对等核心功能。',
          resources: ['产品图片.png', '功能演示.pdf']
        },
        {
          id: '1-2',
          title: '核心功能',
          type: 'document',
          order: 2,
          status: 'completed',
          tags: ['重要'],
          description: '详细说明产品的核心功能模块',
          content: '系统包含智能翻译、术语管理、质量校对等核心功能。智能翻译支持多种语言对，术语管理提供专业的术语库，质量校对确保翻译质量。',
          resources: ['功能架构图.png']
        },
        {
          id: '1-3',
          title: '技术架构',
          type: 'document',
          order: 3,
          status: 'completed',
          tags: [],
          description: '系统技术架构说明',
          content: '系统采用微服务架构，前端使用Vue3框架，后端使用Python+FastAPI，数据库使用MySQL，支持水平扩展。',
          resources: []
        }
      ]
    },
    {
      id: '2',
      title: '用户指南',
      type: 'folder',
      order: 2,
      status: 'processing',
      tags: ['待翻译'],
      description: '用户使用指南',
      content: '',
      resources: [],
      children: [
        {
          id: '2-1',
          title: '快速开始',
          type: 'document',
          order: 1,
          status: 'completed',
          tags: [],
          description: '新用户快速上手指南',
          content: '本章节将指导您完成系统的初始化配置，包括账户注册、项目创建、团队设置等基础操作。',
          resources: ['快速开始教程.mp4']
        },
        {
          id: '2-2',
          title: '创建任务',
          type: 'document',
          order: 2,
          status: 'processing',
          tags: ['审核中'],
          description: '创建和管理翻译任务的详细步骤',
          content: '创建翻译任务需要设置源语言、目标语言、术语库等参数。系统支持批量上传文档，自动识别文档类型。',
          resources: []
        },
        {
          id: '2-3',
          title: '质量校对',
          type: 'document',
          order: 3,
          status: 'pending',
          tags: ['待翻译'],
          description: '使用校对工具提高翻译质量',
          content: '质量校对工具提供语法检查、术语一致性检查、格式验证等功能，帮助用户提高翻译质量。',
          resources: []
        },
        {
          id: '2-4',
          title: '团队协作',
          type: 'document',
          order: 4,
          status: 'pending',
          tags: [],
          description: '团队协作功能说明',
          content: '支持多人协作翻译，提供任务分配、进度跟踪、评论讨论等功能，提高团队协作效率。',
          resources: []
        }
      ]
    },
    {
      id: '3',
      title: '常见问题',
      type: 'folder',
      order: 3,
      status: 'pending',
      tags: [],
      description: '用户常见问题解答',
      content: '',
      resources: [],
      children: [
        {
          id: '3-1',
          title: '安装问题',
          type: 'document',
          order: 1,
          status: 'pending',
          tags: [],
          description: '安装过程中的常见问题',
          content: 'Q: 系统支持哪些浏览器？\nA: 支持Chrome、Firefox、Safari、Edge等主流浏览器。\n\nQ: 需要安装什么插件？\nA: 无需安装任何插件，直接访问网页即可使用。',
          resources: []
        },
        {
          id: '3-2',
          title: '使用问题',
          type: 'document',
          order: 2,
          status: 'pending',
          tags: [],
          description: '使用过程中的常见问题',
          content: 'Q: 如何提高翻译质量？\nA: 建议使用术语库，定期进行质量校对，保持术语一致性。\n\nQ: 支持批量翻译吗？\nA: 支持，可以批量上传多个文档进行翻译。',
          resources: []
        }
      ]
    },
    {
      id: '4',
      title: 'API文档',
      type: 'document',
      order: 4,
      status: 'completed',
      tags: ['重要', 'API'],
      description: 'API接口文档',
      content: '提供完整的REST API接口，支持文档上传、翻译、下载等操作。API使用OAuth2认证，安全可靠。',
      resources: ['API文档.pdf', 'SDK下载.zip']
    }
  ]
}

// 初始化
initDemoData()

// 事件处理
const handleRefresh = () => {
  ElMessage.success('数据已刷新')
}

const handleNodeClick = (data: DocNode) => {
  currentNode.value = data
  Object.assign(nodeForm, {
    id: data.id,
    title: data.title,
    type: data.type,
    order: data.order,
    status: data.status,
    tags: [...(data.tags || [])],
    description: data.description || '',
    content: data.content || '',
    resources: [...(data.resources || [])]
  })
  isEditing.value = false
}

const handleAddChapter = () => {
  dialogTitle.value = '新建文档'
  dialogMode.value = 'add'
  parentNode.value = null
  resetForm()
  showNodeDialog.value = true
}

const handleAddFolder = () => {
  dialogTitle.value = '新建文件夹'
  dialogMode.value = 'add'
  parentNode.value = null
  resetForm()
  nodeForm.type = 'folder'
  showNodeDialog.value = true
}

const handleReset = () => {
  if (currentNode.value) {
    handleNodeClick(currentNode.value)
  }
  isEditing.value = false
}

const handleSave = () => {
  if (!currentNode.value) {
    ElMessage.warning('请先选择要保存的文档')
    return
  }

  // 更新节点数据
  Object.assign(currentNode.value, {
    title: nodeForm.title,
    type: nodeForm.type,
    order: nodeForm.order,
    status: nodeForm.status,
    tags: nodeForm.tags,
    description: nodeForm.description,
    content: nodeForm.content,
    resources: nodeForm.resources
  })

  ElMessage.success('保存成功')
  isEditing.value = false
}

const handleAddResource = () => {
  ElMessageBox.prompt('请输入资源名称', '添加资源', {
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(({ value }) => {
    if (value && value.trim()) {
      nodeForm.resources.push(value.trim())
    }
  }).catch(() => {})
}

const handleRemoveResource = (index: number) => {
  nodeForm.resources.splice(index, 1)
}

const confirmNode = () => {
  if (!nodeForm.title) {
    ElMessage.warning('请输入文档名称')
    return
  }

  const newNode: DocNode = {
    id: dialogMode.value === 'add' ? Date.now().toString() : nodeForm.id,
    title: nodeForm.title,
    type: nodeForm.type,
    order: nodeForm.order,
    status: nodeForm.status || 'pending',
    tags: [...nodeForm.tags],
    description: nodeForm.description,
    content: nodeForm.content,
    resources: [...nodeForm.resources]
  }

  if (dialogMode.value === 'add') {
    if (parentNode.value) {
      if (!parentNode.value.children) {
        parentNode.value.children = []
      }
      parentNode.value.children.push(newNode)
    } else {
      structureData.value.push(newNode)
    }
    ElMessage.success('创建成功')
  } else {
    // 编辑模式更新
    if (currentNode.value) {
      Object.assign(currentNode.value, newNode)
    }
    ElMessage.success('修改成功')
  }

  showNodeDialog.value = false
}

const resetForm = () => {
  Object.assign(nodeForm, {
    id: '',
    title: '',
    type: 'document',
    order: 1,
    status: 'pending',
    tags: [],
    description: '',
    content: '',
    resources: []
  })
}
</script>

<style scoped>
.structured-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f6f7;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
}

/* 顶部导航栏 */
.top-navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 56px;
  background: white;
  border-bottom: 1px solid #e8eaed;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  flex-shrink: 0;
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 24px;
  flex: 1;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.logo-icon {
  font-size: 24px;
  color: #2932e1;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #2932e1;
}

.breadcrumb {
  font-size: 14px;
}

.breadcrumb :deep(.el-breadcrumb__item) {
  cursor: pointer;
}

.breadcrumb :deep(.el-breadcrumb__item:hover) {
  color: #2932e1;
}

.navbar-center {
  flex: 1;
  max-width: 600px;
  padding: 0 24px;
}

.search-input {
  width: 100%;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 8px;
  background: #f5f6f7;
  border: none;
  box-shadow: none;
}

.search-input :deep(.el-input__wrapper:hover),
.search-input :deep(.el-input__wrapper.is-focus) {
  background: #e8eaed;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stats-info {
  display: flex;
  align-items: center;
  gap: 20px;
  padding-right: 16px;
  border-right: 1px solid #e8eaed;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: color 0.3s ease;
}

.stat-item:hover {
  color: #2932e1;
}

.stat-item.success {
  color: #52c41a;
}

.stat-item.warning {
  color: #faad14;
}

.stat-item .el-icon {
  font-size: 16px;
}

.more-btn {
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 500;
}

/* 主内容区 */
.content-wrapper {
  display: flex;
  flex: 1;
  overflow: hidden;
  padding: 16px;
  gap: 16px;
}

/* 左侧文档导航面板 */
.doc-nav-panel {
  flex: 0 0 300px;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.nav-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e8eaed;
}

.nav-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.nav-title .el-icon {
  color: #2932e1;
  font-size: 20px;
}

.nav-actions {
  display: flex;
  gap: 4px;
}

.nav-actions .el-button {
  padding: 6px;
  border-radius: 6px;
  color: #666;
  transition: all 0.3s ease;
}

.nav-actions .el-button:hover {
  background: #f5f6f7;
  color: #2932e1;
}

.nav-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f6f7;
  border-bottom: 1px solid #e8eaed;
}

.nav-search {
  width: 140px;
}

.nav-search :deep(.el-input__wrapper) {
  background: white;
  border-radius: 6px;
}

.nav-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

/* 滚动条美化 */
.nav-content::-webkit-scrollbar {
  width: 6px;
}

.nav-content::-webkit-scrollbar-track {
  background: transparent;
}

.nav-content::-webkit-scrollbar-thumb {
  background: #d9d9d9;
  border-radius: 3px;
}

.nav-content::-webkit-scrollbar-thumb:hover {
  background: #bfbfbf;
}

/* 树形视图 */
.tree-view {
  padding: 0 8px;
}

.tree-node-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.2s ease;
  cursor: pointer;
}

.tree-node-wrapper:hover {
  background: #f5f6f7;
}

.tree-node-wrapper.is-current > .node-main {
  background: #e6f7ff;
  border-color: #2932e1;
}

.node-main {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  padding: 6px 10px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.node-type-icon {
  font-size: 18px;
  color: #666;
  transition: color 0.2s ease;
}

.node-type-icon.folder {
  color: #faad14;
}

.node-type-icon.document {
  color: #2932e1;
}

.node-text {
  font-size: 14px;
  color: #333;
  flex: 1;
}

.node-meta {
  display: flex;
  align-items: center;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.tree-node-wrapper:hover .node-meta {
  opacity: 1;
}

/* 卡片视图 */
.card-view {
  padding: 8px;
  display: grid;
  gap: 8px;
}

.doc-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: white;
  border: 1px solid #e8eaed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.doc-card:hover {
  border-color: #2932e1;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.doc-card.active {
  background: #e6f7ff;
  border-color: #2932e1;
}

.card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: #f5f6f7;
  border-radius: 8px;
}

.card-icon .el-icon {
  font-size: 24px;
  color: #666;
}

.card-icon .folder .el-icon {
  color: #faad14;
}

.card-icon .document .el-icon {
  color: #2932e1;
}

.card-content {
  flex: 1;
  min-width: 0;
}

.card-title {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #999;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.card-status {
  flex-shrink: 0;
}

/* 右侧编辑面板 */
.editor-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.editor-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* 文档头部 */
.doc-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px 24px;
  border-bottom: 1px solid #e8eaed;
  background: #fafbfc;
}

.doc-title-area {
  flex: 1;
  min-width: 0;
}

.title-input {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
}

.title-input :deep(.el-input__wrapper) {
  border: none;
  box-shadow: none;
  background: transparent;
  padding: 0;
}

.title-input :deep(.el-input__inner) {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.doc-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.meta-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #666;
  padding: 4px 10px;
  background: #f5f6f7;
  border-radius: 4px;
}

.meta-tag .el-icon {
  font-size: 14px;
  color: #999;
}

.doc-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

/* 编辑内容区 */
.editor-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.editor-content :deep(.el-form-item) {
  margin-bottom: 20px;
}

.editor-content :deep(.el-form-item__label) {
  font-weight: 500;
  color: #333;
}

.editor-content :deep(.el-input__wrapper) {
  border-radius: 6px;
  transition: all 0.2s ease;
}

.editor-content :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #d9d9d9 inset;
}

.editor-content :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #2932e1 inset;
}

.editor-content :deep(.el-textarea__inner) {
  border-radius: 6px;
  border-color: #d9d9d9;
  transition: all 0.2s ease;
}

.editor-content :deep(.el-textarea__inner:hover) {
  border-color: #2932e1;
}

.editor-content :deep(.el-textarea__inner:focus) {
  border-color: #2932e1;
  box-shadow: 0 0 0 2px rgba(41, 50, 225, 0.1);
}

.tags-input {
  width: 100%;
}

.tags-input :deep(.el-select) {
  width: 100%;
}

.content-editor {
  width: 100%;
}

.textarea-editor {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  font-size: 14px;
  line-height: 1.8;
}

/* 资源列表 */
.resource-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background: #f5f6f7;
  border-radius: 8px;
  border: 1px dashed #d9d9d9;
}

.resource-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e8eaed;
  transition: all 0.2s ease;
}

.resource-item:hover {
  border-color: #2932e1;
}

.resource-item .el-icon {
  color: #2932e1;
  font-size: 16px;
}

.resource-item span {
  flex: 1;
  font-size: 13px;
  color: #333;
}

.add-resource-btn {
  align-self: flex-start;
  border-radius: 6px;
}

/* 空状态 */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 40px;
  color: #999;
}

.empty-icon {
  font-size: 80px;
  color: #d9d9d9;
}

.empty-state h3 {
  font-size: 18px;
  font-weight: 500;
  color: #333;
  margin: 0;
}

.empty-state p {
  font-size: 14px;
  margin: 0;
}

.empty-state .el-button {
  padding: 10px 24px;
  border-radius: 8px;
  font-weight: 500;
}

/* 对话框 */
:deep(.el-dialog) {
  border-radius: 12px;
}

:deep(.el-dialog__header) {
  padding: 20px 24px;
  border-bottom: 1px solid #e8eaed;
}

:deep(.el-dialog__title) {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

:deep(.el-dialog__body) {
  padding: 24px;
}

:deep(.el-dialog__footer) {
  padding: 16px 24px;
  border-top: 1px solid #e8eaed;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .content-wrapper {
    flex-direction: column;
    overflow-y: auto;
  }

  .doc-nav-panel {
    flex: none;
    max-height: 400px;
  }

  .editor-panel {
    min-height: 500px;
  }

  .stats-info {
    display: none;
  }
}
</style>
