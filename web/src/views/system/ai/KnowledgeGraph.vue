<template>
  <div class="knowledge-graph-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <el-icon class="title-icon"><Share /></el-icon>
          知识图谱管理
        </h1>
        <p class="page-subtitle">可视化展示和管理知识体系关联关系</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" icon="Plus" @click="showCreateDialog = true">
          创建图谱
        </el-button>
        <el-button type="success" icon="Upload" @click="importGraph">
          导入图谱
        </el-button>
        <el-button type="warning" icon="Download" @click="exportGraph">
          导出图谱
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ graphStats.totalNodes }}</div>
              <div class="stat-label">节点总数</div>
            </div>
            <div class="stat-icon nodes-icon">
              <el-icon><Location /></el-icon>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ graphStats.totalEdges }}</div>
              <div class="stat-label">关系总数</div>
            </div>
            <div class="stat-icon edges-icon">
              <el-icon><Connection /></el-icon>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ graphStats.totalGraphs }}</div>
              <div class="stat-label">图谱数量</div>
            </div>
            <div class="stat-icon graphs-icon">
              <el-icon><Share /></el-icon>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ graphStats.domains }}</div>
              <div class="stat-label">涉及领域</div>
            </div>
            <div class="stat-icon domains-icon">
              <el-icon><Collection /></el-icon>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <el-row :gutter="20">
        <!-- 图谱列表 -->
        <el-col :span="8">
          <el-card class="graph-list-card">
            <template #header>
              <div class="card-header">
                <span>知识图谱列表</span>
                <el-input
                  v-model="searchKeyword"
                  placeholder="搜索图谱..."
                  prefix-icon="Search"
                  clearable
                  style="width: 200px"
                />
              </div>
            </template>
            
            <div class="graph-list">
              <div
                v-for="graph in filteredGraphs"
                :key="graph.id"
                :class="['graph-item', { active: selectedGraph?.id === graph.id }]"
                @click="selectGraph(graph)"
              >
                <div class="graph-info">
                  <div class="graph-name">{{ graph.name }}</div>
                  <div class="graph-desc">{{ graph.description }}</div>
                  <div class="graph-meta">
                    <el-tag size="small" :type="getDomainColor(graph.domain)">
                      {{ graph.domain }}
                    </el-tag>
                    <span class="node-count">{{ graph.nodeCount }} 节点</span>
                  </div>
                </div>
                <div class="graph-actions">
                  <el-button icon="Edit" size="small" @click.stop="editGraph(graph)" />
                  <el-button icon="Delete" size="small" type="danger" @click.stop="deleteGraph(graph)" />
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 图谱可视化区域 -->
        <el-col :span="16">
          <el-card class="graph-viewer-card">
            <template #header>
              <div class="card-header">
                <div class="viewer-title">
                  <span v-if="selectedGraph">{{ selectedGraph.name }}</span>
                  <span v-else>请选择一个知识图谱</span>
                </div>
                <div class="viewer-controls" v-if="selectedGraph">
                  <el-button-group>
                    <el-button icon="RefreshLeft" @click="refreshGraph" />
                    <el-button icon="Setting" @click="showLayoutSettings = true" />
                  </el-button-group>
                  <el-button type="primary" icon="Plus" @click="addNode">添加节点</el-button>
                </div>
              </div>
            </template>

            <!-- 图谱容器 - 使用普通div而不是动态ref -->
            <div class="graph-container">
              <div v-if="!selectedGraph" class="empty-state">
                <el-empty description="请从左侧选择一个知识图谱进行查看" />
              </div>
              <div v-else-if="loading" class="loading-state">
                <div class="loading-wrapper">
                  <el-icon class="loading-icon" :size="32"><Loading /></el-icon>
                  <p>正在加载图谱数据...</p>
                </div>
              </div>
              <div v-else class="simple-graph-container">
                <!-- 使用简单的CSS和HTML来显示图谱 -->
                <div class="simple-graph">
                  <h3>{{ selectedGraph.name }}</h3>
                  <div class="graph-nodes">
                    <div 
                      v-for="node in currentNodes"
                      :key="node.id"
                      :class="['graph-node', node.category]"
                      :style="getNodeStyle(node)"
                      @mouseover="hoverNode = node"
                      @mouseleave="hoverNode = null"
                    >
                      {{ node.name }}
                    </div>
                  </div>
                  <div class="graph-legend">
                    <h4>图例</h4>
                    <div class="legend-item">
                      <span class="legend-color core"></span>
                      <span>核心概念</span>
                    </div>
                    <div class="legend-item">
                      <span class="legend-color algorithm"></span>
                      <span>算法技术</span>
                    </div>
                    <div class="legend-item">
                      <span class="legend-color application"></span>
                      <span>应用领域</span>
                    </div>
                  </div>
                  <div v-if="hoverNode" class="node-tooltip">
                    <strong>{{ hoverNode.name }}</strong><br>
                    类别: {{ hoverNode.category }}<br>
                    ID: {{ hoverNode.id }}
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 创建/编辑图谱对话框 -->
    <el-dialog
      :title="isEditing ? '编辑知识图谱' : '创建知识图谱'"
      v-model="showCreateDialog"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="graphForm" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="图谱名称" prop="name">
          <el-input v-model="graphForm.name" placeholder="请输入图谱名称" />
        </el-form-item>
        <el-form-item label="所属领域" prop="domain">
          <el-select v-model="graphForm.domain" placeholder="选择领域">
            <el-option label="人工智能" value="人工智能" />
            <el-option label="机器学习" value="机器学习" />
            <el-option label="深度学习" value="深度学习" />
            <el-option label="自然语言处理" value="自然语言处理" />
            <el-option label="计算机视觉" value="计算机视觉" />
            <el-option label="数据挖掘" value="数据挖掘" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述信息" prop="description">
          <el-input
            v-model="graphForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入图谱描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveGraph" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Share, Location, Connection, Collection, Search, 
  Plus, Upload, Download, Edit, Delete, RefreshLeft, 
  Setting, Loading 
} from '@element-plus/icons-vue'

// 响应式数据 - 简化版，不使用复杂的DOM引用
const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const showLayoutSettings = ref(false)
const isEditing = ref(false)
const selectedGraph = ref<any>(null)
const searchKeyword = ref('')
const hoverNode = ref<any>(null)

// 统计数据
const graphStats = reactive({
  totalNodes: 1247,
  totalEdges: 2356,
  totalGraphs: 8,
  domains: 6
})

// 图谱表单
const graphForm = reactive({
  name: '',
  domain: '',
  description: ''
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入图谱名称', trigger: 'blur' },
    { min: 2, max: 50, message: '名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  domain: [
    { required: true, message: '请选择所属领域', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请输入描述信息', trigger: 'blur' }
  ]
}

// 重新生成知识图谱列表 - 使用更真实的数据
const graphList = ref([
  {
    id: 1,
    name: '人工智能知识体系',
    description: '涵盖AI基础概念、算法、应用的完整知识体系',
    domain: '人工智能',
    nodeCount: 9,
    nodes: [
      { id: 'ai', name: '人工智能', category: 'core', symbolSize: 40, x: 50, y: 50 },
      { id: 'ml', name: '机器学习', category: 'algorithm', symbolSize: 30, x: 20, y: 20 },
      { id: 'dl', name: '深度学习', category: 'algorithm', symbolSize: 30, x: 80, y: 20 },
      { id: 'nn', name: '神经网络', category: 'algorithm', symbolSize: 25, x: 35, y: 5 },
      { id: 'cnn', name: 'CNN', category: 'algorithm', symbolSize: 20, x: 10, y: 5 },
      { id: 'rnn', name: 'RNN', category: 'algorithm', symbolSize: 20, x: 60, y: 5 },
      { id: 'nlp', name: 'NLP', category: 'application', symbolSize: 25, x: 20, y: 80 },
      { id: 'cv', name: 'CV', category: 'application', symbolSize: 25, x: 80, y: 80 },
      { id: 'robotics', name: '机器人学', category: 'application', symbolSize: 20, x: 50, y: 95 }
    ],
    edges: [
      { source: 'ai', target: 'ml', relation: '包含' },
      { source: 'ai', target: 'dl', relation: '包含' },
      { source: 'ml', target: 'dl', relation: '发展为' },
      { source: 'dl', target: 'nn', relation: '基于' },
      { source: 'nn', target: 'cnn', relation: '包含' },
      { source: 'nn', target: 'rnn', relation: '包含' },
      { source: 'ai', target: 'nlp', relation: '应用于' },
      { source: 'ai', target: 'cv', relation: '应用于' },
      { source: 'ai', target: 'robotics', relation: '应用于' }
    ]
  },
  {
    id: 2,
    name: '机器学习算法图谱',
    description: '各种机器学习算法的分类和关系图谱',
    domain: '机器学习',
    nodeCount: 6,
    nodes: [
      { id: 'ml', name: '机器学习', category: 'core', symbolSize: 35, x: 50, y: 50 },
      { id: 'supervised', name: '监督学习', category: 'algorithm', symbolSize: 25, x: 20, y: 25 },
      { id: 'unsupervised', name: '无监督学习', category: 'algorithm', symbolSize: 25, x: 80, y: 25 },
      { id: 'regression', name: '回归', category: 'method', symbolSize: 20, x: 5, y: 5 },
      { id: 'classification', name: '分类', category: 'method', symbolSize: 20, x: 35, y: 5 },
      { id: 'clustering', name: '聚类', category: 'method', symbolSize: 20, x: 65, y: 5 }
    ],
    edges: [
      { source: 'ml', target: 'supervised', relation: '包含' },
      { source: 'ml', target: 'unsupervised', relation: '包含' },
      { source: 'supervised', target: 'regression', relation: '包含' },
      { source: 'supervised', target: 'classification', relation: '包含' },
      { source: 'unsupervised', target: 'clustering', relation: '包含' }
    ]
  },
  {
    id: 3,
    name: '深度学习框架生态',
    description: '主流深度学习框架及其生态系统',
    domain: '深度学习',
    nodeCount: 7,
    nodes: [
      { id: 'dl', name: '深度学习', category: 'core', symbolSize: 35, x: 50, y: 50 },
      { id: 'tensorflow', name: 'TensorFlow', category: 'framework', symbolSize: 25, x: 20, y: 25 },
      { id: 'pytorch', name: 'PyTorch', category: 'framework', symbolSize: 25, x: 80, y: 25 },
      { id: 'keras', name: 'Keras', category: 'framework', symbolSize: 20, x: 5, y: 5 },
      { id: 'mxnet', name: 'MXNet', category: 'framework', symbolSize: 20, x: 35, y: 5 },
      { id: 'caffe', name: 'Caffe', category: 'framework', symbolSize: 20, x: 65, y: 5 },
      { id: 'theano', name: 'Theano', category: 'framework', symbolSize: 15, x: 50, y: 5 }
    ],
    edges: [
      { source: 'dl', target: 'tensorflow', relation: '使用' },
      { source: 'dl', target: 'pytorch', relation: '使用' },
      { source: 'tensorflow', target: 'keras', relation: '包含' },
      { source: 'tensorflow', target: 'mxnet', relation: '竞争' },
      { source: 'pytorch', target: 'caffe', relation: '替代' }
    ]
  }
])

// 当前显示的节点
const currentNodes = ref([])

// 计算属性
const filteredGraphs = computed(() => {
  if (!searchKeyword.value) return graphList.value
  return graphList.value.filter(graph => 
    graph.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
    graph.description.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

// 方法
const selectGraph = (graph: any) => {
  console.log('选择图谱:', graph.name)
  selectedGraph.value = graph
  loading.value = true
  
  // 模拟加载延迟
  setTimeout(() => {
    currentNodes.value = graph.nodes || []
    loading.value = false
    console.log('图谱加载完成，节点数:', currentNodes.value.length)
  }, 800)
}

const getNodeStyle = (node: any) => {
  const colors = {
    core: '#ff6b6b',
    algorithm: '#4ecdc4',
    application: '#45b7d1',
    method: '#f7b731',
    framework: '#5f27cd'
  }
  
  return {
    left: `${node.x}%`,
    top: `${node.y}%`,
    backgroundColor: colors[node.category] || '#ccc',
    width: `${node.symbolSize * 0.8}px`,
    height: `${node.symbolSize * 0.8}px`
  }
}

const getDomainColor = (domain: string) => {
  const colors: { [key: string]: string } = {
    '人工智能': 'danger',
    '机器学习': 'success',
    '深度学习': 'warning',
    '自然语言处理': 'info',
    '计算机视觉': 'primary',
    '数据挖掘': ''
  }
  return colors[domain] || ''
}

const refreshGraph = () => {
  if (selectedGraph.value) {
    selectGraph(selectedGraph.value)
    ElMessage.success('图谱已刷新')
  }
}

const editGraph = (graph: any) => {
  isEditing.value = true
  Object.assign(graphForm, {
    name: graph.name,
    domain: graph.domain,
    description: graph.description
  })
  showCreateDialog.value = true
}

const deleteGraph = (graph: any) => {
  ElMessageBox.confirm(
    `确定要删除图谱 "${graph.name}" 吗？此操作不可恢复。`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    const index = graphList.value.findIndex(g => g.id === graph.id)
    if (index > -1) {
      graphList.value.splice(index, 1)
      ElMessage.success('删除成功')
      if (selectedGraph.value?.id === graph.id) {
        selectedGraph.value = null
        currentNodes.value = []
      }
    }
  })
}

const saveGraph = async () => {
  try {
    saving.value = true
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    if (isEditing.value) {
      const graph = graphList.value.find(g => g.name === graphForm.name)
      if (graph) {
        Object.assign(graph, {
          domain: graphForm.domain,
          description: graphForm.description
        })
      }
      ElMessage.success('图谱更新成功')
    } else {
      const newGraph = {
        id: Date.now(),
        name: graphForm.name,
        domain: graphForm.domain,
        description: graphForm.description,
        nodeCount: Math.floor(Math.random() * 10) + 5,
        nodes: [],
        edges: []
      }
      graphList.value.unshift(newGraph)
      ElMessage.success('图谱创建成功')
    }
    
    showCreateDialog.value = false
    resetForm()
    
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  Object.assign(graphForm, {
    name: '',
    domain: '',
    description: ''
  })
  isEditing.value = false
}

const importGraph = () => {
  ElMessage.info('导入功能开发中...')
}

const exportGraph = () => {
  ElMessage.info('导出功能开发中...')
}

const addNode = () => {
  ElMessage.info('添加节点功能开发中...')
}

// 生命周期
onMounted(() => {
  console.log('KnowledgeGraph 页面加载完成')
  // 默认不自动选择，让用户手动选择
})
</script>

<style scoped>
.knowledge-graph-page {
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

.stats-section {
  margin-bottom: 20px;
}

.stat-card {
  position: relative;
  overflow: hidden;
}

.stat-content {
  position: relative;
  z-index: 2;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
}

.stat-label {
  margin-top: 8px;
  color: #909399;
  font-size: 14px;
}

.stat-icon {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 40px;
  opacity: 0.3;
  z-index: 1;
}

.nodes-icon { color: #409eff; }
.edges-icon { color: #67c23a; }
.graphs-icon { color: #e6a23c; }
.domains-icon { color: #f56c6c; }

.main-content {
  height: calc(100vh - 300px);
}

.graph-list-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.graph-list {
  max-height: 600px;
  overflow-y: auto;
}

.graph-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  margin-bottom: 10px;
  background: #f8f9fa;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.graph-item:hover {
  background: #e9ecef;
  transform: translateX(5px);
}

.graph-item.active {
  background: #409eff;
  color: white;
}

.graph-info {
  flex: 1;
}

.graph-name {
  font-weight: bold;
  margin-bottom: 5px;
}

.graph-desc {
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
  line-height: 1.4;
}

.graph-item.active .graph-desc {
  color: rgba(255,255,255,0.8);
}

.graph-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.node-count {
  font-size: 12px;
  color: #999;
}

.graph-item.active .node-count {
  color: rgba(255,255,255,0.7);
}

.graph-viewer-card {
  height: 100%;
}

.viewer-title {
  font-size: 18px;
  font-weight: bold;
}

.viewer-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.graph-container {
  height: 600px;
  position: relative;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
}

.loading-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
}

.loading-icon {
  animation: rotate 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 简单图谱样式 */
.simple-graph-container {
  height: 100%;
  padding: 20px;
  position: relative;
}

.simple-graph {
  height: 100%;
  position: relative;
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
}

.simple-graph h3 {
  text-align: center;
  margin-bottom: 30px;
  color: #303133;
}

.graph-nodes {
  position: relative;
  height: 400px;
  border: 1px dashed #ddd;
  border-radius: 4px;
}

.graph-node {
  position: absolute;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  transform: translate(-50%, -50%);
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.graph-node:hover {
  transform: translate(-50%, -50%) scale(1.2);
  z-index: 10;
}

.graph-node.core {
  background: #ff6b6b;
}

.graph-node.algorithm {
  background: #4ecdc4;
}

.graph-node.application {
  background: #45b7d1;
}

.graph-node.method {
  background: #f7b731;
}

.graph-node.framework {
  background: #5f27cd;
}

.graph-legend {
  position: absolute;
  top: 20px;
  right: 20px;
  background: white;
  padding: 15px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  min-width: 120px;
}

.graph-legend h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #303133;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 5px;
  font-size: 12px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-color.core { background: #ff6b6b; }
.legend-color.algorithm { background: #4ecdc4; }
.legend-color.application { background: #45b7d1; }
.legend-color.method { background: #f7b731; }
.legend-color.framework { background: #5f27cd; }

.node-tooltip {
  position: absolute;
  background: rgba(0,0,0,0.8);
  color: white;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  z-index: 100;
  pointer-events: none;
  max-width: 200px;
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
