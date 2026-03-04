<template>
  <div class="knowledge-graph-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <el-icon class="title-icon"><TrendCharts /></el-icon>
          直升机知识图谱中心
        </h1>
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

    <!-- 主要内容区域 -->
    <div class="main-content">
      <el-row :gutter="16">
        <!-- 图谱列表 -->
        <el-col :span="3">
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
            
            <!-- 统计信息列表 -->
            <div class="vertical-stats-list">
              <div class="stats-list-item">
                <div class="stats-list-item-content">
                  <div class="stats-list-item-number">{{ graphStats.totalNodes }}</div>
                  <div class="stats-list-item-label">专业术语</div>
                </div>
                <div class="stats-list-item-icon nodes-icon">
                  <el-icon><TrendCharts /></el-icon>
                </div>
              </div>
              <div class="stats-list-item">
                <div class="stats-list-item-content">
                  <div class="stats-list-item-number">{{ graphStats.totalEdges }}</div>
                  <div class="stats-list-item-label">关联关系</div>
                </div>
                <div class="stats-list-item-icon edges-icon">
                  <el-icon><WindPower /></el-icon>
                </div>
              </div>
              <div class="stats-list-item">
                <div class="stats-list-item-content">
                  <div class="stats-list-item-number">{{ graphStats.totalGraphs }}</div>
                  <div class="stats-list-item-label">专业图谱</div>
                </div>
                <div class="stats-list-item-icon graphs-icon">
                  <el-icon><VideoPlay /></el-icon>
                </div>
              </div>
              <div class="stats-list-item">
                <div class="stats-list-item-content">
                  <div class="stats-list-item-number">{{ graphStats.domains }}</div>
                  <div class="stats-list-item-label">技术领域</div>
                </div>
                <div class="stats-list-item-icon domains-icon">
                  <el-icon><Tools /></el-icon>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 图谱可视化区域 -->
        <el-col :span="21">
          <el-card class="graph-viewer-card">
            <template #header>
              <div class="viewer-header">
                <div class="viewer-title">
                  {{ selectedGraph ? selectedGraph.name : '知识图谱可视化' }}
                </div>
                <div class="viewer-controls">
                  <!-- 布局选择 -->
                  <el-select v-model="currentLayout" placeholder="选择布局" size="small" style="width: 120px">
                    <el-option label="力导向布局" value="cose" />
                    <el-option label="圆形布局" value="circle" />
                    <el-option label="网格布局" value="grid" />
                    <el-option label="树形布局" value="breadthfirst" />
                    <el-option label="随机布局" value="random" />
                  </el-select>
                  
                  <el-divider direction="vertical" />
                  
                  <!-- 缩放控制 -->
                  <el-button-group>
                    <el-button size="small" @click="zoomIn">
                      <el-icon><ZoomIn /></el-icon>
                    </el-button>
                    <el-button size="small" @click="zoomOut">
                      <el-icon><ZoomOut /></el-icon>
                    </el-button>
                    <el-button size="small" @click="fitGraph">
                      <el-icon><FullScreen /></el-icon>
                    </el-button>
                    <el-button size="small" @click="resetGraph">
                      <el-icon><RefreshRight /></el-icon>
                    </el-button>
                  </el-button-group>
                  
                  <el-divider direction="vertical" />
                  
                  <!-- 其他操作 -->
                  <el-button size="small" @click="toggleLabels">
                    <el-icon><View /></el-icon>
                    {{ showLabels ? '隐藏标签' : '显示标签' }}
                  </el-button>
                  
                  <el-button size="small" @click="exportImage">
                    <el-icon><Download /></el-icon>
                    导出图片
                  </el-button>
                </div>
              </div>
            </template>
            
            <!-- 图谱容器 -->
            <div class="graph-container">
              <div v-if="!selectedGraph" class="empty-state">
                <div class="empty-content">
                  <el-icon :size="80" color="#d3d4d6"><TrendCharts /></el-icon>
                  <p class="empty-text">请从左侧选择一个知识图谱</p>
                  <p class="empty-hint">选择图谱后将展示交互式知识网络</p>
                </div>
              </div>
              <div v-else-if="loading" class="loading-state">
                <div class="loading-wrapper">
                  <el-icon class="loading-icon" :size="48"><Loading /></el-icon>
                  <p>正在加载图谱数据...</p>
                </div>
              </div>
              <div v-else class="cytoscape-container" ref="cytoscapeContainer">
                <!-- Cytoscape 图形将在这里渲染 -->
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
            <el-option label="总体设计" value="总体设计" />
            <el-option label="空气动力学" value="空气动力学" />
            <el-option label="飞行控制" value="飞行控制" />
            <el-option label="结构设计" value="结构设计" />
            <el-option label="动力系统" value="动力系统" />
            <el-option label="材料工艺" value="材料工艺" />
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

    <!-- 节点详情对话框 -->
    <el-dialog
      title="节点详情"
      v-model="showNodeDetail"
      width="500px"
    >
      <div v-if="selectedNode" class="node-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="节点名称">{{ selectedNode.name }}</el-descriptions-item>
          <el-descriptions-item label="类别">{{ getCategoryLabel(selectedNode.category) }}</el-descriptions-item>
          <el-descriptions-item label="专业领域">{{ selectedGraph?.domain }}</el-descriptions-item>
          <el-descriptions-item label="关联节点">
            <el-tag
              v-for="neighbor in getNodeNeighbors(selectedNode.id)"
              :key="neighbor.id"
              size="small"
              style="margin: 2px"
              @click="focusNode(neighbor.id)"
            >
              {{ neighbor.name }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  TrendCharts, VideoPlay, WindPower, Tools, Search, 
  Plus, Upload, Download, Edit, Delete, RefreshLeft, 
  Setting, Loading, ZoomIn, ZoomOut, FullScreen, 
  RefreshRight, View
} from '@element-plus/icons-vue'
import cytoscape, { Core, NodeSingular, EdgeSingular } from 'cytoscape'

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const showNodeDetail = ref(false)
const isEditing = ref(false)
const selectedGraph = ref<any>(null)
const selectedNode = ref<any>(null)
const searchKeyword = ref('')
const currentLayout = ref('cose')
const showLabels = ref(true)
const cytoscapeContainer = ref<HTMLElement | null>(null)

// Cytoscape 实例
let cy: Core | null = null

// 统计数据
const graphStats = reactive({
  totalNodes: 33,
  totalEdges: 45,
  totalGraphs: 3,
  domains: 3
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

// 直升机专业知识图谱数据
const graphList = ref([
  {
    id: 1,
    name: '直升机总体设计',
    description: '涵盖直升机总体构型、系统设计、性能分析等核心技术知识',
    domain: '总体设计',
    nodeCount: 12,
    nodes: [
      { id: 'helicopter', name: '直升机', category: 'core', symbolSize: 45 },
      { id: 'configuration', name: '总体构型', category: 'design', symbolSize: 35 },
      { id: 'rotorsystem', name: '旋翼系统', category: 'system', symbolSize: 35 },
      { id: 'transmissionsys', name: '传动系统', category: 'system', symbolSize: 30 },
      { id: 'fuselage', name: '机体结构', category: 'structure', symbolSize: 30 },
      { id: 'tailrotor', name: '尾桨系统', category: 'system', symbolSize: 25 },
      { id: 'landinggear', name: '起落架', category: 'system', symbolSize: 25 },
      { id: 'powerplant', name: '动力装置', category: 'system', symbolSize: 30 },
      { id: 'flightcontrol', name: '飞控系统', category: 'system', symbolSize: 30 },
      { id: 'weightbalance', name: '重量重心', category: 'performance', symbolSize: 25 },
      { id: 'stability', name: '稳定性', category: 'performance', symbolSize: 25 },
      { id: 'maneuverability', name: '操纵性', category: 'performance', symbolSize: 25 }
    ],
    edges: [
      { source: 'helicopter', target: 'configuration', relation: '采用' },
      { source: 'helicopter', target: 'rotorsystem', relation: '配备' },
      { source: 'helicopter', target: 'transmissionsys', relation: '包含' },
      { source: 'helicopter', target: 'fuselage', relation: '具有' },
      { source: 'helicopter', target: 'tailrotor', relation: '配置' },
      { source: 'helicopter', target: 'landinggear', relation: '安装' },
      { source: 'helicopter', target: 'powerplant', relation: '搭载' },
      { source: 'helicopter', target: 'flightcontrol', relation: '集成' },
      { source: 'configuration', target: 'rotorsystem', relation: '决定' },
      { source: 'rotorsystem', target: 'tailrotor', relation: '协同' },
      { source: 'transmissionsys', target: 'powerplant', relation: '传递' },
      { source: 'weightbalance', target: 'stability', relation: '影响' },
      { source: 'stability', target: 'maneuverability', relation: '关联' }
    ]
  },
  {
    id: 2,
    name: '旋翼空气动力学',
    description: '直升机旋翼空气动力学理论与分析方法知识体系',
    domain: '空气动力学',
    nodeCount: 10,
    nodes: [
      { id: 'rotoraero', name: '旋翼空气动力学', category: 'core', symbolSize: 40 },
      { id: 'bladetheory', name: '叶素理论', category: 'theory', symbolSize: 30 },
      { id: 'vortextheory', name: '涡流理论', category: 'theory', symbolSize: 30 },
      { id: 'inducedvelocity', name: '诱导速度', category: 'analysis', symbolSize: 30 },
      { id: 'liftgeneration', name: '升力产生', category: 'mechanism', symbolSize: 25 },
      { id: 'draganalysis', name: '阻力分析', category: 'analysis', symbolSize: 25 },
      { id: 'torqueanalysis', name: '扭矩分析', category: 'analysis', symbolSize: 25 },
      { id: 'loadanalysis', name: '载荷分析', category: 'analysis', symbolSize: 25 },
      { id: 'compressibility', name: '压缩性效应', category: 'phenomenon', symbolSize: 20 },
      { id: 'groundeffect', name: '地面效应', category: 'phenomenon', symbolSize: 20 }
    ],
    edges: [
      { source: 'rotoraero', target: 'bladetheory', relation: '基于' },
      { source: 'rotoraero', target: 'vortextheory', relation: '基于' },
      { source: 'rotoraero', target: 'inducedvelocity', relation: '研究' },
      { source: 'bladetheory', target: 'liftgeneration', relation: '解释' },
      { source: 'bladetheory', target: 'draganalysis', relation: '分析' },
      { source: 'vortextheory', target: 'torqueanalysis', relation: '预测' },
      { source: 'vortextheory', target: 'loadanalysis', relation: '计算' },
      { source: 'inducedvelocity', target: 'liftgeneration', relation: '影响' },
      { source: 'compressibility', target: 'rotoraero', relation: '修正' },
      { source: 'groundeffect', target: 'rotoraero', relation: '影响' }
    ]
  },
  {
    id: 3,
    name: '飞行力学与控制',
    description: '直升机飞行力学特性与飞行控制系统专业知识体系',
    domain: '飞行控制',
    nodeCount: 11,
    nodes: [
      { id: 'flightmechanics', name: '飞行力学', category: 'core', symbolSize: 40 },
      { id: 'motioneq', name: '运动方程', category: 'theory', symbolSize: 30 },
      { id: 'stabilityderiv', name: '稳定性导数', category: 'analysis', symbolSize: 30 },
      { id: 'controlsys', name: '控制系统', category: 'system', symbolSize: 35 },
      { id: 'flightenvelope', name: '飞行包线', category: 'performance', symbolSize: 30 },
      { id: 'handlingquals', name: '操纵品质', category: 'performance', symbolSize: 25 },
      { id: 'autostab', name: '自动稳定', category: 'control', symbolSize: 25 },
      { id: 'attitudecontrol', name: '姿态控制', category: 'control', symbolSize: 25 },
      { id: 'trajectorycontrol', name: '轨迹控制', category: 'control', symbolSize: 25 },
      { id: 'vibrationcontrol', name: '振动控制', category: 'control', symbolSize: 20 },
      { id: 'flighttest', name: '飞行试验', category: 'validation', symbolSize: 20 }
    ],
    edges: [
      { source: 'flightmechanics', target: 'motioneq', relation: '建立' },
      { source: 'flightmechanics', target: 'stabilityderiv', relation: '分析' },
      { source: 'flightmechanics', target: 'controlsys', relation: '设计' },
      { source: 'motioneq', target: 'flightenvelope', relation: '描述' },
      { source: 'stabilityderiv', target: 'handlingquals', relation: '评价' },
      { source: 'controlsys', target: 'autostab', relation: '实现' },
      { source: 'controlsys', target: 'attitudecontrol', relation: '执行' },
      { source: 'controlsys', target: 'trajectorycontrol', relation: '执行' },
      { source: 'autostab', target: 'vibrationcontrol', relation: '抑制' },
      { source: 'flightenvelope', target: 'flighttest', relation: '验证' },
      { source: 'handlingquals', target: 'flighttest', relation: '评估' }
    ]
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

// 获取节点颜色
const getNodeColor = (category: string): string => {
  const colors: { [key: string]: string } = {
    core: '#e74c3c',
    design: '#3498db',
    system: '#2ecc71',
    structure: '#f39c12',
    performance: '#9b59b6',
    theory: '#1abc9c',
    analysis: '#e67e22',
    mechanism: '#34495e',
    phenomenon: '#e91e63',
    control: '#27ae60',
    validation: '#8e44ad'
  }
  return colors[category] || '#95a5a6'
}

// 初始化 Cytoscape
const initCytoscape = () => {
  if (!cytoscapeContainer.value || !selectedGraph.value) return

  // 销毁旧实例
  if (cy) {
    cy.destroy()
  }

  // 准备节点数据
  const nodes = selectedGraph.value.nodes.map((node: any) => ({
    data: {
      id: node.id,
      name: node.name,
      category: node.category,
      size: node.symbolSize,
      color: getNodeColor(node.category)
    }
  }))

  // 准备边数据
  const edges = selectedGraph.value.edges.map((edge: any) => ({
    data: {
      id: `${edge.source}-${edge.target}`,
      source: edge.source,
      target: edge.target,
      relation: edge.relation
    }
  }))

  // 创建 Cytoscape 实例
  cy = cytoscape({
    container: cytoscapeContainer.value,
    elements: [...nodes, ...edges],
    
    // 节点样式
    style: [
      {
        selector: 'node',
        style: {
          'background-color': 'data(color)',
          'label': showLabels.value ? 'data(name)' : '',
          'width': 'data(size)',
          'height': 'data(size)',
          'font-size': '12px',
          'font-weight': 'bold',
          'color': '#2c3e50',
          'text-valign': 'center',
          'text-halign': 'center',
          'text-outline-color': '#fff',
          'text-outline-width': 2,
          'border-width': 2,
          'border-color': '#fff',
          'overlay-opacity': 0
        }
      },
      {
        selector: 'node:selected',
        style: {
          'border-width': 4,
          'border-color': '#3498db',
          'overlay-color': '#3498db',
          'overlay-opacity': 0.2
        }
      },
      {
        selector: 'node.highlighted',
        style: {
          'border-width': 3,
          'border-color': '#f39c12',
          'overlay-color': '#f39c12',
          'overlay-opacity': 0.3
        }
      },
      {
        selector: 'node.faded',
        style: {
          'opacity': 0.3
        }
      },
      {
        selector: 'edge',
        style: {
          'width': 2,
          'line-color': '#bdc3c7',
          'target-arrow-color': '#bdc3c7',
          'target-arrow-shape': 'triangle',
          'curve-style': 'bezier',
          'arrow-scale': 0.8,
          'overlay-opacity': 0
        }
      },
      {
        selector: 'edge:selected',
        style: {
          'line-color': '#3498db',
          'target-arrow-color': '#3498db',
          'width': 3
        }
      },
      {
        selector: 'edge.highlighted',
        style: {
          'line-color': '#e74c3c',
          'target-arrow-color': '#e74c3c',
          'width': 3,
          'z-index': 999
        }
      },
      {
        selector: 'edge.faded',
        style: {
          'opacity': 0.2
        }
      }
    ],
    
    // 交互设置
    minZoom: 0.2,
    maxZoom: 3,
    wheelSensitivity: 0.3,
    
    // 初始化布局
    layout: getLayoutOptions()
  })

  // 绑定事件
  bindCytoscapeEvents()
}

// 获取布局选项
const getLayoutOptions = () => {
  const layouts: { [key: string]: any } = {
    cose: {
      name: 'cose',
      idealEdgeLength: 100,
      nodeOverlap: 20,
      refresh: 20,
      fit: true,
      padding: 30,
      randomize: false,
      componentSpacing: 100,
      nodeRepulsion: 400000,
      edgeElasticity: 100,
      nestingFactor: 5,
      gravity: 80,
      numIter: 1000,
      initialTemp: 200,
      coolingFactor: 0.95,
      minTemp: 1.0
    },
    circle: {
      name: 'circle',
      fit: true,
      padding: 30,
      boundingBox: undefined,
      avoidOverlap: true,
      nodeDimensionsIncludeLabels: false,
      spacingFactor: undefined,
      radius: undefined,
      startAngle: 3/2 * Math.PI,
      sweep: undefined,
      clockwise: true,
      sort: undefined,
      animate: true,
      animationDuration: 1000
    },
    grid: {
      name: 'grid',
      fit: true,
      padding: 30,
      boundingBox: undefined,
      avoidOverlap: true,
      nodeDimensionsIncludeLabels: false,
      spacingFactor: undefined,
      condense: false,
      rows: undefined,
      cols: undefined,
      position: undefined,
      sort: undefined,
      animate: true,
      animationDuration: 1000
    },
    breadthfirst: {
      name: 'breadthfirst',
      fit: true,
      directed: false,
      padding: 30,
      circle: false,
      grid: false,
      spacingFactor: 1.5,
      boundingBox: undefined,
      avoidOverlap: true,
      nodeDimensionsIncludeLabels: false,
      roots: undefined,
      maximal: false,
      animate: true,
      animationDuration: 1000
    },
    random: {
      name: 'random',
      fit: true,
      padding: 30,
      boundingBox: undefined,
      animate: true,
      animationDuration: 1000
    }
  }
  
  return layouts[currentLayout.value] || layouts.cose
}

// 绑定 Cytoscape 事件
const bindCytoscapeEvents = () => {
  if (!cy) return

  // 节点点击
  cy.on('tap', 'node', (evt) => {
    const node = evt.target
    selectedNode.value = node.data()
    showNodeDetail.value = true
    
    // 高亮相关节点和边
    highlightNeighborhood(node)
  })

  // 边点击
  cy.on('tap', 'edge', (evt) => {
    const edge = evt.target
    ElMessage.info(`关系: ${edge.data('relation')}`)
  })

  // 点击空白处
  cy.on('tap', (evt) => {
    if (evt.target === cy) {
      clearHighlight()
      selectedNode.value = null
      showNodeDetail.value = false
    }
  })

  // 节点悬停
  cy.on('mouseover', 'node', (evt) => {
    const node = evt.target
    document.body.style.cursor = 'pointer'
    highlightNeighborhood(node)
  })

  cy.on('mouseout', 'node', (evt) => {
    document.body.style.cursor = 'default'
    if (!showNodeDetail.value) {
      clearHighlight()
    }
  })
}

// 高亮相邻节点
const highlightNeighborhood = (node: NodeSingular) => {
  if (!cy) return

  // 获取相邻节点
  const neighborhood = node.neighborhood().add(node)
  
  // 淡化所有元素
  cy.elements().addClass('faded')
  
  // 高亮相邻元素
  neighborhood.removeClass('faded')
  neighborhood.addClass('highlighted')
}

// 清除高亮
const clearHighlight = () => {
  if (!cy) return
  cy.elements().removeClass('faded highlighted')
}

// 选择图谱
const selectGraph = (graph: any) => {
  console.log('选择图谱:', graph.name)
  selectedGraph.value = graph
  loading.value = true
  
  setTimeout(() => {
    loading.value = false
    initCytoscape()
  }, 500)
}

// 缩放控制
const zoomIn = () => {
  if (!cy) return
  cy.zoom(cy.zoom() * 1.2)
}

const zoomOut = () => {
  if (!cy) return
  cy.zoom(cy.zoom() * 0.8)
}

const fitGraph = () => {
  if (!cy) return
  cy.fit(undefined, 30)
}

const resetGraph = () => {
  if (!cy) return
  cy.reset()
  applyLayout()
}

// 切换标签显示
const toggleLabels = () => {
  showLabels.value = !showLabels.value
  if (cy) {
    cy.nodes().style('label', showLabels.value ? 'data(name)' : '')
  }
}

// 应用布局
const applyLayout = () => {
  if (!cy) return
  
  const layout = cy.layout({
    ...getLayoutOptions(),
    animate: true,
    animationDuration: 1000
  })
  
  layout.run()
}

// 导出图片
const exportImage = () => {
  if (!cy) return
  
  const png = cy.png({
    output: 'blob',
    bg: '#ffffff',
    full: true,
    scale: 2
  })
  
  const link = document.createElement('a')
  link.href = URL.createObjectURL(png as Blob)
  link.download = `${selectedGraph.value?.name || 'knowledge-graph'}.png`
  link.click()
  
  ElMessage.success('图谱已导出为PNG图片')
}

// 聚焦到指定节点
const focusNode = (nodeId: string) => {
  if (!cy) return
  
  const node = cy.getElementById(nodeId)
  if (node) {
    cy.animate({
      zoom: 1.5,
      center: { eles: node }
    }, {
      duration: 500
    })
    node.select()
    selectedNode.value = node.data()
    highlightNeighborhood(node)
  }
}

// 获取节点的邻居节点
const getNodeNeighbors = (nodeId: string) => {
  if (!cy || !nodeId) return []
  
  const node = cy.getElementById(nodeId)
  if (!node) return []
  
  return node.neighborhood('node').map(n => n.data())
}

// 获取类别标签
const getCategoryLabel = (category: string) => {
  const labels: { [key: string]: string } = {
    core: '核心概念',
    design: '总体设计',
    system: '系统组成',
    structure: '结构部件',
    performance: '性能指标',
    theory: '理论基础',
    analysis: '分析方法',
    mechanism: '作用机理',
    phenomenon: '物理现象',
    control: '控制技术',
    validation: '试验验证'
  }
  return labels[category] || category
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
        if (cy) {
          cy.destroy()
          cy = null
        }
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

// 监听布局变化
watch(currentLayout, () => {
  applyLayout()
})

// 生命周期
onMounted(() => {
  console.log('KnowledgeGraph 页面加载完成')
})

onBeforeUnmount(() => {
  if (cy) {
    cy.destroy()
    cy = null
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

.header-actions {
  display: flex;
  gap: 10px;
}

.main-content {
  height: calc(100vh - 180px);
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
  max-height: 400px;
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

.vertical-stats-list {
  display: flex;
  flex-direction: column;
  border-top: 1px solid #e4e7ed;
  margin-top: 16px;
  padding-top: 16px;
}

.stats-list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.stats-list-item:last-child {
  border-bottom: none;
}

.stats-list-item-content {
  flex: 1;
}

.stats-list-item-number {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 2px;
}

.stats-list-item-label {
  margin-top: 0;
  color: #909399;
  font-size: 11px;
  line-height: 1.2;
}

.stats-list-item-icon {
  font-size: 18px;
  opacity: 0.4;
  margin-left: 12px;
}

.nodes-icon { color: #e74c3c; }
.edges-icon { color: #27ae60; }
.graphs-icon { color: #3498db; }
.domains-icon { color: #f39c12; }

.graph-viewer-card {
  height: 100%;
}

.viewer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.viewer-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.viewer-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.graph-container {
  height: 780px;
  position: relative;
  background: white;
  border-radius: 8px;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.empty-content {
  text-align: center;
}

.empty-text {
  margin-top: 20px;
  font-size: 16px;
  color: #909399;
}

.empty-hint {
  margin-top: 10px;
  font-size: 14px;
  color: #c0c4cc;
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

.cytoscape-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.node-detail {
  padding: 10px 0;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 20px;
  }
  
  .main-content .el-col {
    margin-bottom: 20px;
  }
  
  .viewer-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}
</style>
