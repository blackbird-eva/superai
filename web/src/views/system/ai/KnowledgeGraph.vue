<template>
  <div class="knowledge-graph">
    <!-- 简洁头部 -->
    <div class="header">
      <h2>知识图谱</h2>
      <p>以树状结构展示知识间的关联关系</p>
    </div>

    <!-- 简单控制栏 -->
    <div class="toolbar">
      <div class="search-box">
        <el-input
          v-model="searchKey"
          placeholder="搜索知识点..."
          prefix-icon="Search"
          clearable
          @input="filterTree"
          size="large"
        />
      </div>
      
      <el-button type="primary" icon="Plus" @click="expandAll">
        展开全部
      </el-button>
    </div>

    <!-- 树状知识图谱 -->
    <div class="graph-content">
      <div class="tree-container">
        <el-tree
          :data="filteredTreeData"
          :props="treeProps"
          node-key="id"
          :expand-on-click-node="false"
          :default-expand-all="false"
          @node-click="selectNode"
          highlight-current
          class="knowledge-tree"
        >
          <template #default="{ node, data }">
            <div class="tree-node">
              <span class="node-icon">{{ getNodeIcon(data.type) }}</span>
              <span class="node-label">{{ node.label }}</span>
              <el-tag :type="getTagType(data.type)" size="small" class="node-type">
                {{ getTypeName(data.type) }}
              </el-tag>
            </div>
          </template>
        </el-tree>
      </div>

      <!-- 右侧详情面板 -->
      <div class="detail-panel" :class="{ active: selectedNode }">
        <div v-if="selectedNode" class="node-detail">
          <div class="detail-header">
            <h3>{{ selectedNode.label }}</h3>
            <el-tag :type="getTagType(selectedNode.type)" size="small">
              {{ getTypeName(selectedNode.type) }}
            </el-tag>
          </div>
          
          <div class="detail-body">
            <div class="section">
              <h4>描述</h4>
              <p>{{ selectedNode.description || '暂无描述' }}</p>
            </div>
            
            <div class="section" v-if="getChildren(selectedNode).length > 0">
              <h4>子知识点 ({{ getChildren(selectedNode).length }})</h4>
              <ul class="child-list">
                <li v-for="child in getChildren(selectedNode)" :key="child.id">
                  {{ child.label }}
                </li>
              </ul>
            </div>
            
            <div class="section" v-if="getParent(selectedNode)">
              <h4>上级知识点</h4>
              <p>{{ getParent(selectedNode).label }}</p>
            </div>
          </div>

          <div class="detail-actions">
            <el-button icon="Edit" size="small" @click="editNode">编辑</el-button>
            <el-button icon="Plus" size="small" @click="addChildNode">添加子节点</el-button>
            <el-button icon="Delete" size="small" type="danger" @click="deleteNode">删除</el-button>
          </div>
        </div>

        <!-- 默认提示 -->
        <div v-else class="panel-placeholder">
          <el-icon><InfoFilled /></el-icon>
          <p>点击左侧知识点查看详情</p>
        </div>
      </div>
    </div>

    <!-- 统计信息 -->
    <div class="stats">
      <span class="stat-item">共 {{ totalNodes }} 个知识点</span>
      <span class="stat-item">最大层级 {{ maxLevel }} 层</span>
    </div>

    <!-- 添加节点对话框 -->
    <el-dialog title="添加知识点" v-model="showAddDialog" width="400px">
      <el-form :model="newNodeForm" :rules="formRules" ref="formRef" label-width="80px">
        <el-form-item label="名称" prop="label">
          <el-input v-model="newNodeForm.label" placeholder="请输入知识点名称" />
        </el-form-item>
        <el-form-item label="类型" prop="type">
          <el-select v-model="newNodeForm.type" placeholder="选择类型" style="width: 100%">
            <el-option label="主题" value="topic"></el-option>
            <el-option label="概念" value="concept"></el-option>
            <el-option label="实例" value="instance"></el-option>
            <el-option label="属性" value="property"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="newNodeForm.description"
            type="textarea"
            :rows="3"
            placeholder="知识点描述（可选）"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="addNode" :loading="adding">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Edit, Delete, InfoFilled } from '@element-plus/icons-vue'

// 节点接口
interface KnowledgeNode {
  id: string
  label: string
  type: 'topic' | 'concept' | 'instance' | 'property'
  description?: string
  children?: KnowledgeNode[]
}

// 响应式数据
const searchKey = ref('')
const selectedNode = ref<KnowledgeNode | null>(null)
const showAddDialog = ref(false)
const adding = ref(false)
const formRef = ref()

// 表单数据
const newNodeForm = reactive({
  label: '',
  type: 'concept' as const,
  description: '',
  parentId: ''
})

// 表单验证
const formRules = {
  label: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择类型', trigger: 'change' }]
}

// 树形控件配置
const treeProps = {
  children: 'children',
  label: 'label'
}

// 示例知识树数据
const treeData = ref<KnowledgeNode[]>([
  {
    id: '1',
    label: '人工智能',
    type: 'topic',
    description: '研究如何让机器模拟人类智能的科学领域',
    children: [
      {
        id: '2',
        label: '机器学习',
        type: 'concept',
        description: '让计算机通过经验自动改进的算法',
        children: [
          {
            id: '3',
            label: '监督学习',
            type: 'concept',
            description: '从标记的训练数据中学习预测模型'
          },
          {
            id: '4',
            label: '无监督学习',
            type: 'concept',
            description: '从无标记数据中发现隐藏的模式'
          },
          {
            id: '5',
            label: '强化学习',
            type: 'concept',
            description: '通过与环境交互获得奖励信号来学习'
          }
        ]
      },
      {
        id: '6',
        label: '深度学习',
        type: 'concept',
        description: '基于多层神经网络的机器学习方法',
        children: [
          {
            id: '7',
            label: '卷积神经网络',
            type: 'concept',
            description: '专门用于处理网格结构数据的神经网络'
          },
          {
            id: '8',
            label: '循环神经网络',
            type: 'concept',
            description: '能够处理序列数据的神经网络'
          }
        ]
      },
      {
        id: '9',
        label: '应用领域',
        type: 'topic',
        children: [
          {
            id: '10',
            label: '计算机视觉',
            type: 'concept',
            description: '让机器理解和分析图像和视频的技术'
          },
          {
            id: '11',
            label: '自然语言处理',
            type: 'concept',
            description: '让机器理解、解释和生成人类语言的技术'
          }
        ]
      }
    ]
  },
  {
    id: '12',
    label: '数据挖掘',
    type: 'topic',
    description: '从大量数据中发现有用模式和知识的过程',
    children: [
      {
        id: '13',
        label: '关联规则',
        type: 'concept',
        description: '发现数据项之间有趣关系的算法'
      },
      {
        id: '14',
        label: '聚类分析',
        type: 'concept',
        description: '将数据分组为具有相似特征的簇'
      }
    ]
  }
])

// 过滤后的树数据
const filteredTreeData = ref<KnowledgeNode[]>(treeData.value)

// 统计信息
const totalNodes = computed(() => {
  const countNodes = (nodes: KnowledgeNode[]): number => {
    return nodes.reduce((total, node) => {
      return total + 1 + (node.children ? countNodes(node.children) : 0)
    }, 0)
  }
  return countNodes(treeData.value)
})

const maxLevel = computed(() => {
  const getDepth = (nodes: KnowledgeNode[], level: number = 1): number => {
    let maxDepth = level
    nodes.forEach(node => {
      if (node.children && node.children.length > 0) {
        maxDepth = Math.max(maxDepth, getDepth(node.children, level + 1))
      }
    })
    return maxDepth
  }
  return getDepth(treeData.value)
})

// 过滤树数据
const filterTree = () => {
  if (!searchKey.value.trim()) {
    filteredTreeData.value = JSON.parse(JSON.stringify(treeData.value))
    return
  }

  const filterNodes = (nodes: KnowledgeNode[]): KnowledgeNode[] => {
    const key = searchKey.value.toLowerCase()
    
    return nodes.reduce((result: KnowledgeNode[], node) => {
      const matches = node.label.toLowerCase().includes(key) ||
                     (node.description && node.description.toLowerCase().includes(key))
      
      const filteredChildren = node.children ? filterNodes(node.children) : []
      
      if (matches || filteredChildren.length > 0) {
        result.push({
          ...node,
          children: filteredChildren
        })
      }
      
      return result
    }, [])
  }

  filteredTreeData.value = filterNodes(treeData.value)
}

// 展开所有节点
const expandAll = () => {
  // ElementUI tree 的默认展开逻辑已在 default-expand-all 中处理
  ElMessage.success('已展开全部节点')
}

// 选择节点
const selectNode = (data: KnowledgeNode) => {
  selectedNode.value = data
}

// 获取节点图标
const getNodeIcon = (type: string) => {
  const icons: { [key: string]: string } = {
    topic: '📚',
    concept: '💡',
    instance: '🔍',
    property: '📊'
  }
  return icons[type] || '📄'
}

// 获取类型名称
const getTypeName = (type: string) => {
  const names: { [key: string]: string } = {
    topic: '主题',
    concept: '概念',
    instance: '实例',
    property: '属性'
  }
  return names[type] || '未知'
}

// 获取标签类型
const getTagType = (type: string) => {
  const types: { [key: string]: string } = {
    topic: 'primary',
    concept: 'success',
    instance: 'warning',
    property: 'info'
  }
  return types[type] || 'info'
}

// 获取子节点
const getChildren = (node: KnowledgeNode) => {
  return node.children || []
}

// 获取父节点
const getParent = (node: KnowledgeNode): KnowledgeNode | null => {
  const findParent = (nodes: KnowledgeNode[], targetId: string, parent?: KnowledgeNode): KnowledgeNode | null => {
    for (const node of nodes) {
      if (node.id === targetId) {
        return parent || null
      }
      if (node.children) {
        const found = findParent(node.children, targetId, node)
        if (found) return found
      }
    }
    return null
  }
  
  return findParent(treeData.value, node.id)
}

// 添加节点
const addNode = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    adding.value = true
    
    await new Promise(resolve => setTimeout(resolve, 300))
    
    const newNode: KnowledgeNode = {
      id: Date.now().toString(),
      label: newNodeForm.label,
      type: newNodeForm.type,
      description: newNodeForm.description
    }
    
    if (newNodeForm.parentId) {
      // 添加到指定父节点下
      const addToParent = (nodes: KnowledgeNode[]): boolean => {
        for (const node of nodes) {
          if (node.id === newNodeForm.parentId) {
            if (!node.children) node.children = []
            node.children.push(newNode)
            return true
          }
          if (node.children && addToParent(node.children)) {
            return true
          }
        }
        return false
      }
      addToParent(treeData.value)
    } else {
      // 添加到根级别
      treeData.value.push(newNode)
    }
    
    filterTree()
    ElMessage.success('添加成功')
    showAddDialog.value = false
    resetForm()
  } catch (error) {
    console.error('表单验证失败:', error)
  } finally {
    adding.value = false
  }
}

// 添加子节点
const addChildNode = () => {
  if (!selectedNode.value) return
  
  newNodeForm.parentId = selectedNode.value.id
  newNodeForm.label = ''
  newNodeForm.type = 'concept'
  newNodeForm.description = ''
  showAddDialog.value = true
}

// 编辑节点
const editNode = () => {
  if (!selectedNode.value) return
  
  newNodeForm.label = selectedNode.value.label
  newNodeForm.type = selectedNode.value.type
  newNodeForm.description = selectedNode.value.description || ''
  newNodeForm.parentId = ''
  showAddDialog.value = true
}

// 删除节点
const deleteNode = async () => {
  if (!selectedNode.value) return
  
  try {
    await ElMessageBox.confirm(
      `确定删除 "${selectedNode.value.label}"？`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const deleteFromTree = (nodes: KnowledgeNode[]): boolean => {
      const index = nodes.findIndex(node => node.id === selectedNode.value!.id)
      if (index > -1) {
        nodes.splice(index, 1)
        return true
      }
      
      for (const node of nodes) {
        if (node.children && deleteFromTree(node.children)) {
          return true
        }
      }
      return false
    }
    
    deleteFromTree(treeData.value)
    selectedNode.value = null
    filterTree()
    ElMessage.success('删除成功')
  } catch {
    // 用户取消
  }
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  Object.assign(newNodeForm, {
    label: '',
    type: 'concept',
    description: '',
    parentId: ''
  })
}

// 初始化
onMounted(() => {
  filterTree()
})
</script>

<style scoped>
.knowledge-graph {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f8fafc;
}

/* 头部 */
.header {
  text-align: center;
  padding: 20px;
  background: white;
  border-bottom: 1px solid #e2e8f0;
}

.header h2 {
  margin: 0 0 8px 0;
  color: #1e293b;
  font-size: 24px;
  font-weight: 500;
}

.header p {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

/* 工具栏 */
.toolbar {
  display: flex;
  gap: 16px;
  padding: 16px 20px;
  background: white;
  border-bottom: 1px solid #e2e8f0;
  align-items: center;
}

.search-box {
  flex: 1;
  max-width: 400px;
}

/* 主要内容区 */
.graph-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.tree-container {
  flex: 1;
  padding: 20px;
  overflow: auto;
}

.knowledge-tree {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* 树节点样式 */
.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.node-icon {
  font-size: 16px;
}

.node-label {
  flex: 1;
  font-size: 14px;
}

.node-type {
  flex-shrink: 0;
}

/* 详情面板 */
.detail-panel {
  width: 350px;
  background: white;
  border-left: 1px solid #e2e8f0;
  transform: translateX(100%);
  transition: transform 0.3s;
  overflow-y: auto;
}

.detail-panel.active {
  transform: translateX(0);
}

.node-detail {
  padding: 20px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.detail-header h3 {
  margin: 0;
  color: #1e293b;
  font-size: 18px;
}

.detail-body {
  margin-bottom: 20px;
}

.section {
  margin-bottom: 20px;
}

.section h4 {
  margin: 0 0 8px 0;
  color: #374151;
  font-size: 14px;
  font-weight: 500;
}

.section p {
  margin: 0;
  color: #64748b;
  line-height: 1.5;
}

.child-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.child-list li {
  padding: 4px 0;
  color: #64748b;
  font-size: 13px;
  border-bottom: 1px solid #f1f5f9;
}

.child-list li:last-child {
  border-bottom: none;
}

.detail-actions {
  display: flex;
  gap: 8px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

.panel-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #9ca3af;
  padding: 20px;
}

.panel-placeholder .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

/* 统计信息 */
.stats {
  display: flex;
  gap: 24px;
  padding: 12px 20px;
  background: white;
  border-top: 1px solid #e2e8f0;
}

.stat-item {
  font-size: 13px;
  color: #64748b;
}

/* 响应式 */
@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    max-width: none;
  }
  
  .graph-content {
    flex-direction: column;
  }
  
  .detail-panel {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    width: 100%;
    z-index: 1000;
  }
  
  .stats {
    flex-direction: column;
    gap: 8px;
  }
}
</style>