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
                    <el-button icon="ZoomIn" @click="zoomIn" />
                    <el-button icon="ZoomOut" @click="zoomOut" />
                    <el-button icon="RefreshLeft" @click="resetView" />
                  </el-button-group>
                  <el-button icon="Setting" @click="showLayoutSettings = true" />
                  <el-button type="primary" icon="Plus" @click="addNode">添加节点</el-button>
                </div>
              </div>
            </template>

            <!-- 图谱容器 -->
            <div class="graph-container" ref="graphContainer">
              <div v-if="!selectedGraph" class="empty-state">
                <el-empty description="请从左侧选择一个知识图谱进行查看" />
              </div>
              <div v-else-if="loading" class="loading-state">
                <el-loading-service :loading="loading" />
                <p>正在加载图谱数据...</p>
              </div>
              <div v-else ref="chartContainer" class="echarts-container"></div>
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
        <el-form-item label="标签">
          <el-tag
            v-for="tag in graphForm.tags"
            :key="tag"
            closable
            @close="removeTag(tag)"
            style="margin: 2px 5px"
          >
            {{ tag }}
          </el-tag>
          <el-input
            v-if="tagInputVisible"
            v-model="tagInputValue"
            @keyup.enter="addTag"
            @blur="addTag"
            style="width: 100px"
            size="small"
          />
          <el-button v-else icon="Plus" size="small" @click="showTagInput" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveGraph" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 布局设置抽屉 -->
    <el-drawer
      title="布局设置"
      v-model="showLayoutSettings"
      direction="rtl"
      size="400px"
    >
      <div class="layout-settings">
        <el-form label-width="120px">
          <el-form-item label="布局算法">
            <el-select v-model="layoutConfig.type">
              <el-option label="力导向布局" value="force" />
              <el-option label="圆形布局" value="circular" />
              <el-option label="树形布局" value="tree" />
              <el-option label="网格布局" value="grid" />
            </el-select>
          </el-form-item>
          <el-form-item label="节点大小">
            <el-slider v-model="layoutConfig.nodeSize" :min="10" :max="50" />
          </el-form-item>
          <el-form-item label="连线粗细">
            <el-slider v-model="layoutConfig.lineWidth" :min="1" :max="10" />
          </el-form-item>
          <el-form-item label="动画效果">
            <el-switch v-model="layoutConfig.animation" />
          </el-form-item>
        </el-form>
        <el-button type="primary" @click="applyLayout" style="width: 100%">应用设置</el-button>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Share, Location, Connection, Collection, Search, 
  Plus, Upload, Download, Edit, Delete, ZoomIn, 
  ZoomOut, RefreshLeft, Setting 
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// 响应式数据
const graphContainer = ref()
const chartContainer = ref()
const formRef = ref()
const chartInstance = ref<echarts.ECharts>()

const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const showLayoutSettings = ref(false)
const isEditing = ref(false)
const selectedGraph = ref<any>(null)
const searchKeyword = ref('')
const tagInputVisible = ref(false)
const tagInputValue = ref('')

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
  description: '',
  tags: ['AI', '知识图谱']
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
    { required: true, message: '请输入描述信息', trigger: 'blur' },
    { min: 10, max: 200, message: '描述长度在 10 到 200 个字符', trigger: 'blur' }
  ]
}

// 布局配置
const layoutConfig = reactive({
  type: 'force',
  nodeSize: 20,
  lineWidth: 2,
  animation: true
})

// 模拟图谱数据
const graphList = ref([
  {
    id: 1,
    name: '人工智能知识体系',
    description: '涵盖AI基础概念、算法、应用的完整知识体系',
    domain: '人工智能',
    nodeCount: 156,
    nodes: [
      { id: 'ai', name: '人工智能', category: 'core', symbolSize: 40 },
      { id: 'ml', name: '机器学习', category: 'algorithm', symbolSize: 30 },
      { id: 'dl', name: '深度学习', category: 'algorithm', symbolSize: 30 },
      { id: 'nn', name: '神经网络', category: 'algorithm', symbolSize: 25 },
      { id: 'cnn', name: '卷积神经网络', category: 'algorithm', symbolSize: 20 },
      { id: 'rnn', name: '循环神经网络', category: 'algorithm', symbolSize: 20 },
      { id: 'nlp', name: '自然语言处理', category: 'application', symbolSize: 25 },
      { id: 'cv', name: '计算机视觉', category: 'application', symbolSize: 25 },
      { id: 'robotics', name: '机器人学', category: 'application', symbolSize: 20 }
    ],
    edges: [
      { source: 'ai', target: 'ml', relation: '包含' },
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
    nodeCount: 89,
    nodes: [],
    edges: []
  },
  {
    id: 3,
    name: '深度学习框架生态',
    description: '主流深度学习框架及其生态系统',
    domain: '深度学习',
    nodeCount: 67,
    nodes: [],
    edges: []
  }
])

// 计算属性
const filteredGraphs = computed(() => {
  if (!searchKeyword.value) return graphList.value
  return graphList.value.filter(graph => 
    graph.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
    graph.description.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

// 方法
const selectGraph = async (graph: any) => {
  selectedGraph.value = graph
  await nextTick()
  await loadGraphData(graph)
}

const loadGraphData = async (graph: any) => {
  loading.value = true
  try {
    // 模拟API调用延迟
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 初始化ECharts实例
    if (!chartInstance.value && chartContainer.value) {
      chartInstance.value = echarts.init(chartContainer.value)
    }
    
    // 设置图表选项
    const option = {
      backgroundColor: '#fafafa',
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => {
          if (params.dataType === 'node') {
            return `<strong>${params.data.name}</strong><br/>
                    类别: ${params.data.category}<br/>
                    节点ID: ${params.data.id}`
          } else {
            return `${params.data.source} --${params.data.relation}--> ${params.data.target}`
          }
        }
      },
      legend: {
        data: ['core', 'algorithm', 'application'],
        orient: 'vertical',
        left: 10,
        top: 20,
        textStyle: {
          color: '#333'
        }
      },
      series: [{
        type: 'graph',
        layout: 'force',
        data: graph.nodes,
        links: graph.edges,
        categories: [
          { name: 'core', itemStyle: { color: '#ff6b6b' } },
          { name: 'algorithm', itemStyle: { color: '#4ecdc4' } },
          { name: 'application', itemStyle: { color: '#45b7d1' } }
        ],
        roam: true,
        focusNodeAdjacency: true,
        draggable: true,
        symbolSize: (val: any) => val.symbolSize || 20,
        edgeSymbol: ['circle', 'arrow'],
        edgeSymbolSize: [4, 10],
        edgeLabel: {
          fontSize: 12,
          formatter: '{c}'
        },
        force: {
          repulsion: 1000,
          gravity: 0.1,
          edgeLength: 150,
          layoutAnimation: true
        },
        lineStyle: {
          color: 'source',
          curveness: 0.1,
          width: layoutConfig.lineWidth
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: 4
          }
        }
      }]
    }
    
    chartInstance.value?.setOption(option, true)
    
  } catch (error) {
    ElMessage.error('加载图谱数据失败')
  } finally {
    loading.value = false
  }
}

const zoomIn = () => {
  chartInstance.value?.dispatchAction({ type: 'dataZoom', start: 0, end: 50 })
}

const zoomOut = () => {
  chartInstance.value?.dispatchAction({ type: 'dataZoom', start: 0, end: 100 })
}

const resetView = () => {
  chartInstance.value?.dispatchAction({ type: 'restore' })
}

const applyLayout = () => {
  if (selectedGraph.value && chartInstance.value) {
    loadGraphData(selectedGraph.value)
    showLayoutSettings.value = false
    ElMessage.success('布局设置已应用')
  }
}

const editGraph = (graph: any) => {
  isEditing.value = true
  Object.assign(graphForm, {
    name: graph.name,
    domain: graph.domain,
    description: graph.description,
    tags: [...graph.tags]
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
      }
    }
  })
}

const saveGraph = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    saving.value = true
    
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    if (isEditing.value) {
      // 更新现有图谱
      const graph = graphList.value.find(g => g.name === graphForm.name)
      if (graph) {
        Object.assign(graph, {
          domain: graphForm.domain,
          description: graphForm.description,
          tags: [...graphForm.tags]
        })
      }
      ElMessage.success('图谱更新成功')
    } else {
      // 创建新图谱
      const newGraph = {
        id: Date.now(),
        name: graphForm.name,
        domain: graphForm.domain,
        description: graphForm.description,
        tags: [...graphForm.tags],
        nodeCount: Math.floor(Math.random() * 200) + 50,
        nodes: [],
        edges: []
      }
      graphList.value.unshift(newGraph)
      ElMessage.success('图谱创建成功')
    }
    
    showCreateDialog.value = false
    resetForm()
    
  } catch (error) {
    ElMessage.error('请检查表单填写')
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  Object.assign(graphForm, {
    name: '',
    domain: '',
    description: '',
    tags: ['AI', '知识图谱']
  })
  isEditing.value = false
  formRef.value?.resetFields()
}

const addTag = () => {
  if (tagInputValue.value && !graphForm.tags.includes(tagInputValue.value)) {
    graphForm.tags.push(tagInputValue.value)
  }
  tagInputValue.value = ''
  tagInputVisible.value = false
}

const removeTag = (tag: string) => {
  const index = graphForm.tags.indexOf(tag)
  if (index > -1) {
    graphForm.tags.splice(index, 1)
  }
}

const showTagInput = () => {
  tagInputVisible.value = true
  nextTick(() => {
    // 这里可以添加自动聚焦逻辑
  })
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

// 生命周期
onMounted(async () => {
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    chartInstance.value?.resize()
  })
  
  // 默认选择第一个图谱
  if (graphList.value.length > 0) {
    await selectGraph(graphList.value[0])
  }
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

.echarts-container {
  width: 100%;
  height: 100%;
}

.layout-settings {
  padding: 20px;
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