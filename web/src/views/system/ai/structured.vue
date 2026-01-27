<template>
  <div class="structured-container">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button type="primary" :icon="Upload" @click="handleImport">
          导入文档
        </el-button>
        <el-button :icon="FolderOpened" @click="handleOpenTask">
          打开任务
        </el-button>
        <el-button :icon="Refresh" @click="handleRefresh">
          刷新
        </el-button>
      </div>
      <div class="toolbar-right">
        <el-tag type="info">总章节: {{ totalChapters }}</el-tag>
        <el-tag type="warning">未完成: {{ incompleteChapters }}</el-tag>
        <el-tag type="success">已完成: {{ completedChapters }}</el-tag>
        <el-button type="success" :icon="View" @click="showPreview = true">
          预览文档
        </el-button>
        <el-button type="primary" :icon="Download" @click="handleExport">
          导出结构
        </el-button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="content-wrapper">
      <!-- 左侧：结构树 -->
      <div class="structure-panel">
        <div class="panel-header">
          <h3>文档结构</h3>
          <div class="header-actions">
            <el-button size="small" :icon="Plus" @click="handleAddChapter">
              添加章节
            </el-button>
            <el-button size="small" :icon="Sort" @click="handleSort">
              自动排序
            </el-button>
          </div>
        </div>

        <div class="structure-tree">
          <el-tree
            ref="treeRef"
            :data="structureData"
            :props="treeProps"
            :highlight-current="true"
            :expand-on-click-node="false"
            node-key="id"
            default-expand-all
            @node-click="handleNodeClick"
          >
            <template #default="{ node, data }">
              <div class="tree-node">
                <span class="node-icon">
                  <el-icon>
                    <component :is="data.type === 'folder' ? Folder : Document" />
                  </el-icon>
                </span>
                <span class="node-title">{{ node.label }}</span>
                <div class="node-actions">
                  <el-button
                    size="small"
                    text
                    :icon="Plus"
                    @click.stop="handleAddChild(node, data)"
                    v-if="data.type === 'folder'"
                  >
                  </el-button>
                  <el-button
                    size="small"
                    text
                    :icon="Edit"
                    @click.stop="handleEditNode(node, data)"
                  >
                  </el-button>
                  <el-button
                    size="small"
                    text
                    :icon="Top"
                    @click.stop="handleMoveUp(node, data)"
                    :disabled="node.isFirst"
                  >
                  </el-button>
                  <el-button
                    size="small"
                    text
                    :icon="Bottom"
                    @click.stop="handleMoveDown(node, data)"
                    :disabled="node.isLast"
                  >
                  </el-button>
                  <el-button
                    size="small"
                    text
                    type="danger"
                    :icon="Delete"
                    @click.stop="handleDeleteNode(node, data)"
                  >
                  </el-button>
                </div>
              </div>
            </template>
          </el-tree>
        </div>
      </div>

      <!-- 右侧：编辑区 -->
      <div class="editor-panel">
        <div class="panel-header">
          <h3>章节编辑</h3>
          <div class="header-actions">
            <el-button size="small" @click="handleReset">重置</el-button>
            <el-button size="small" type="primary" @click="handleSave">保存</el-button>
          </div>
        </div>

        <div v-if="currentNode" class="editor-content">
          <el-form :model="nodeForm" label-width="100px">
            <el-form-item label="章节名称">
              <el-input v-model="nodeForm.title" placeholder="请输入章节名称" />
            </el-form-item>

            <el-form-item label="章节类型">
              <el-select v-model="nodeForm.type" placeholder="选择类型">
                <el-option label="文件夹" value="folder"></el-option>
                <el-option label="文档" value="document"></el-option>
              </el-select>
            </el-form-item>

            <el-form-item label="排序序号">
              <el-input-number v-model="nodeForm.order" :min="1" :max="999" />
            </el-form-item>

            <el-form-item label="状态">
              <el-radio-group v-model="nodeForm.status">
                <el-radio label="pending">未开始</el-radio>
                <el-radio label="processing">进行中</el-radio>
                <el-radio label="completed">已完成</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="标签">
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
            </el-form-item>

            <el-form-item label="备注说明">
              <el-input
                v-model="nodeForm.description"
                type="textarea"
                :rows="3"
                placeholder="添加章节说明或备注"
              />
            </el-form-item>

            <el-form-item label="内容预览" v-if="nodeForm.type === 'document'">
              <el-input
                v-model="nodeForm.content"
                type="textarea"
                :rows="8"
                placeholder="章节内容预览（可选）"
              />
            </el-form-item>

            <el-form-item label="关联资源" v-if="nodeForm.type === 'document'">
              <div class="resource-list">
                <el-tag
                  v-for="(resource, index) in nodeForm.resources"
                  :key="index"
                  closable
                  @close="handleRemoveResource(index)"
                >
                  {{ resource }}
                </el-tag>
                <el-button
                  size="small"
                  text
                  :icon="Plus"
                  @click="handleAddResource"
                >
                  添加资源
                </el-button>
              </div>
            </el-form-item>
          </el-form>
        </div>

        <div v-else class="empty-state">
          <el-icon class="empty-icon"><Edit /></el-icon>
          <p>请从左侧结构树选择要编辑的章节</p>
        </div>
      </div>
    </div>

    <!-- 添加/编辑章节对话框 -->
    <el-dialog
      v-model="showNodeDialog"
      :title="dialogTitle"
      width="600px"
    >
      <el-form :model="nodeForm" label-width="100px">
        <el-form-item label="章节名称">
          <el-input v-model="nodeForm.title" placeholder="请输入章节名称" />
        </el-form-item>
        <el-form-item label="章节类型">
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

    <!-- 预览对话框 -->
    <el-dialog v-model="showPreview" title="文档预览" width="900px" fullscreen>
      <div class="preview-content">
        <el-tree
          :data="structureData"
          :props="treeProps"
          default-expand-all
        >
          <template #default="{ node, data }">
            <div class="preview-node">
              <el-icon>
                <component :is="data.type === 'folder' ? Folder : Document" />
              </el-icon>
              <span>{{ node.label }}</span>
              <el-tag v-if="data.status" :type="getStatusType(data.status)" size="small">
                {{ getStatusText(data.status) }}
              </el-tag>
            </div>
          </template>
        </el-tree>
      </div>
    </el-dialog>

    <!-- 导出对话框 -->
    <el-dialog v-model="showExportDialog" title="导出结构" width="500px">
      <el-form :model="exportForm" label-width="100px">
        <el-form-item label="导出格式">
          <el-radio-group v-model="exportForm.format">
            <el-radio label="json">JSON</el-radio>
            <el-radio label="xml">XML</el-radio>
            <el-radio label="csv">CSV</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="导出内容">
          <el-checkbox-group v-model="exportForm.include">
            <el-checkbox label="structure">结构树</el-checkbox>
            <el-checkbox label="content">内容预览</el-checkbox>
            <el-checkbox label="resources">关联资源</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="包含状态">
          <el-select v-model="exportForm.status" placeholder="选择状态">
            <el-option label="全部" value="all"></el-option>
            <el-option label="仅未开始" value="pending"></el-option>
            <el-option label="仅进行中" value="processing"></el-option>
            <el-option label="仅已完成" value="completed"></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showExportDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmExport">导出</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Upload,
  FolderOpened,
  Refresh,
  View,
  Download,
  Plus,
  Sort,
  Edit,
  Top,
  Bottom,
  Delete,
  Folder,
  Document,
  Check
} from '@element-plus/icons-vue'

// 数据状态
const treeRef = ref(null)
const structureData = ref([])
const currentNode = ref(null)
const showNodeDialog = ref(false)
const showPreview = ref(false)
const showExportDialog = ref(false)
const dialogTitle = ref('添加章节')
const dialogMode = ref('add') // add 或 edit
const parentNode = ref(null)

const nodeForm = reactive({
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

const treeProps = {
  children: 'children',
  label: 'title'
}

const exportForm = reactive({
  format: 'json',
  include: ['structure'],
  status: 'all'
})

const tagOptions = ref(['重要', '紧急', '审核中', '待翻译', '已完成'])

// 计算属性
const totalChapters = computed(() => countNodes(structureData.value))
const incompleteChapters = computed(() => countNodesByStatus(structureData.value, ['pending', 'processing']))
const completedChapters = computed(() => countNodesByStatus(structureData.value, ['completed']))

// 方法
const countNodes = (nodes) => {
  let count = 0
  nodes.forEach(node => {
    count++
    if (node.children) {
      count += countNodes(node.children)
    }
  })
  return count
}

const countNodesByStatus = (nodes, statuses) => {
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

const getStatusType = (status) => {
  const types = {
    pending: 'info',
    processing: 'warning',
    completed: 'success'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    pending: '未开始',
    processing: '进行中',
    completed: '已完成'
  }
  return texts[status] || '未知'
}

// 初始化演示数据
const initDemoData = () => {
  structureData.value = [
    {
      id: '1',
      title: '第一章 产品介绍',
      type: 'folder',
      order: 1,
      status: 'completed',
      tags: ['重要'],
      description: '产品概述和核心功能介绍',
      content: '',
      resources: [],
      children: [
        {
          id: '1-1',
          title: '1.1 产品概述',
          type: 'document',
          order: 1,
          status: 'completed',
          tags: ['已完成'],
          description: '简要介绍产品定位和目标用户',
          content: '本产品是一款基于AI技术的智能翻译系统...',
          resources: ['产品图片.png', '功能演示.pdf']
        },
        {
          id: '1-2',
          title: '1.2 核心功能',
          type: 'document',
          order: 2,
          status: 'completed',
          tags: ['重要'],
          description: '详细说明产品的核心功能模块',
          content: '系统包含智能翻译、术语管理、质量校对等核心功能...',
          resources: ['功能架构图.png']
        }
      ]
    },
    {
      id: '2',
      title: '第二章 使用指南',
      type: 'folder',
      order: 2,
      status: 'processing',
      tags: ['待翻译'],
      description: '详细的使用说明和操作步骤',
      content: '',
      resources: [],
      children: [
        {
          id: '2-1',
          title: '2.1 快速开始',
          type: 'document',
          order: 1,
          status: 'completed',
          tags: [],
          description: '新用户快速上手指南',
          content: '本章节将指导您完成系统的初始化配置...',
          resources: ['快速开始教程.mp4']
        },
        {
          id: '2-2',
          title: '2.2 创建翻译任务',
          type: 'document',
          order: 2,
          status: 'processing',
          tags: ['审核中'],
          description: '创建和管理翻译任务的详细步骤',
          content: '创建翻译任务需要设置源语言、目标语言等参数...',
          resources: []
        },
        {
          id: '2-3',
          title: '2.3 质量校对',
          type: 'document',
          order: 3,
          status: 'pending',
          tags: ['待翻译'],
          description: '使用校对工具提高翻译质量',
          content: '',
          resources: []
        }
      ]
    },
    {
      id: '3',
      title: '第三章 常见问题',
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
          title: '3.1 安装问题',
          type: 'document',
          order: 1,
          status: 'pending',
          tags: [],
          description: '安装过程中的常见问题',
          content: '',
          resources: []
        },
        {
          id: '3-2',
          title: '3.2 使用问题',
          type: 'document',
          order: 2,
          status: 'pending',
          tags: [],
          description: '使用过程中的常见问题',
          content: '',
          resources: []
        }
      ]
    }
  ]
}

// 初始化
initDemoData()

// 事件处理
const handleImport = () => {
  ElMessage.info('导入文档功能开发中...')
}

const handleOpenTask = () => {
  ElMessage.info('打开任务功能开发中...')
}

const handleRefresh = () => {
  ElMessage.success('数据已刷新')
}

const handleNodeClick = (data) => {
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
}

const handleAddChapter = () => {
  dialogTitle.value = '添加章节'
  dialogMode.value = 'add'
  parentNode.value = null
  resetForm()
  showNodeDialog.value = true
}

const handleAddChild = (node, data) => {
  dialogTitle.value = '添加子章节'
  dialogMode.value = 'add'
  parentNode.value = data
  resetForm()
  nodeForm.order = (data.children?.length || 0) + 1
  showNodeDialog.value = true
}

const handleEditNode = (node, data) => {
  dialogTitle.value = '编辑章节'
  dialogMode.value = 'edit'
  parentNode.value = null
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
  showNodeDialog.value = true
}

const handleMoveUp = (node, data) => {
  ElMessage.info('上移功能开发中...')
}

const handleMoveDown = (node, data) => {
  ElMessage.info('下移功能开发中...')
}

const handleDeleteNode = (node, data) => {
  ElMessageBox.confirm(
    `确定要删除"${data.title}"吗？` + (data.children?.length ? '此操作将同时删除其所有子章节。' : ''),
    '删除章节',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    ElMessage.success('删除成功')
  }).catch(() => {})
}

const handleSort = () => {
  ElMessage.success('已自动排序')
}

const handleReset = () => {
  if (currentNode.value) {
    handleNodeClick(currentNode.value)
  }
}

const handleSave = () => {
  if (!currentNode.value) {
    ElMessage.warning('请先选择要保存的章节')
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

const handleRemoveResource = (index) => {
  nodeForm.resources.splice(index, 1)
}

const confirmNode = () => {
  if (!nodeForm.title) {
    ElMessage.warning('请输入章节名称')
    return
  }

  const newNode = {
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
    ElMessage.success('添加成功')
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

const handleExport = () => {
  showExportDialog.value = true
}

const confirmExport = () => {
  ElMessage.success(`已导出为 ${exportForm.format.toUpperCase()} 格式`)
  showExportDialog.value = false
}
</script>

<style scoped>
.structured-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* 主内容区 */
.content-wrapper {
  display: flex;
  flex: 1;
  overflow: hidden;
  padding: 16px;
  gap: 16px;
}

/* 左侧结构面板 */
.structure-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.structure-tree {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.tree-node {
  display: flex;
  align-items: center;
  flex: 1;
  padding: 4px 8px;
  border-radius: 4px;
}

.tree-node:hover {
  background: #f5f5f5;
}

.node-icon {
  margin-right: 8px;
  color: #409eff;
}

.node-title {
  flex: 1;
  font-size: 14px;
}

.node-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.tree-node:hover .node-actions {
  opacity: 1;
}

/* 右侧编辑面板 */
.editor-panel {
  flex: 1.2;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.editor-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.resource-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

/* 空状态 */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #999;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state p {
  font-size: 14px;
  margin: 0;
}

/* 预览 */
.preview-content {
  padding: 20px;
}

.preview-node {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
}

.preview-node .el-icon {
  color: #409eff;
}
</style>
