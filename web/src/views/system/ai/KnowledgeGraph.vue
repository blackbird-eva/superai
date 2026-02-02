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


            <!-- 图谱容器 - 使用普通div而不是动态ref -->
            <div class="graph-container">
              <div v-if="!selectedGraph" class="simple-graph-container">
                <!-- 空的可视化区域 -->
                <div class="simple-graph">
                  <div class="graph-visualization" style="display: flex; align-items: center; justify-content: center;">
                    <div style="color: #909399; font-size: 14px;">请从左侧选择一个知识图谱</div>
                  </div>
                </div>
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
                  <div class="graph-visualization">
                    <!-- 连线表示关系 -->
                    <svg class="relation-lines" width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet" overflow="visible">
                      <defs>
                        <marker id="arrowhead" markerWidth="5" markerHeight="3" 
                                refX="4.5" refY="1.5" orient="auto">
                          <polygon points="0 0, 5 1.5, 0 3" fill="#6366f1" />
                        </marker>
                      </defs>
                      <line 
                        v-for="edge in selectedGraph.edges"
                        :key="edge.source + '-' + edge.target"
                        :x1="getAdjustedEdgePositions(edge).x1"
                        :y1="getAdjustedEdgePositions(edge).y1"
                        :x2="getAdjustedEdgePositions(edge).x2"
                        :y2="getAdjustedEdgePositions(edge).y2"
                        stroke="#6366f1" 
                        stroke-width="1.0"
                        stroke-opacity="0.9"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        marker-end="url(#arrowhead)"
                      />
                    </svg>
                    
                    <!-- 节点 -->
                    <div class="graph-nodes">
                      <div 
                        v-for="node in currentNodes"
                        :key="node.id"
                        :class="['graph-node', node.category]"
                        :style="getNodeStyle(node)"
                        @mouseover="hoverNode = node"
                        @mouseleave="hoverNode = null"
                      >
                        <div class="node-content">
                          <div class="node-name">{{ node.name }}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 关系说明 -->
                  <div class="relations-panel">
                    <h4>主要关联关系</h4>
                    <div class="relation-list">
                      <div 
                        v-for="edge in selectedGraph.edges.slice(0, 6)"
                        :key="edge.source + '-' + edge.target"
                        class="relation-item"
                      >
                        <span class="source-node">{{ getNodeById(edge.source)?.name }}</span>
                        <span class="relation-arrow">→ {{ edge.relation }} →</span>
                        <span class="target-node">{{ getNodeById(edge.target)?.name }}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div class="graph-legend">
                    <h4>专业类别</h4>
                    <div class="legend-item">
                      <span class="legend-color core"></span>
                      <span>核心概念</span>
                    </div>
                    <div class="legend-item">
                      <span class="legend-color design"></span>
                      <span>总体设计</span>
                    </div>
                    <div class="legend-item">
                      <span class="legend-color system"></span>
                      <span>系统组成</span>
                    </div>
                    <div class="legend-item">
                      <span class="legend-color structure"></span>
                      <span>结构部件</span>
                    </div>
                    <div class="legend-item">
                      <span class="legend-color performance"></span>
                      <span>性能指标</span>
                    </div>
                    <div class="legend-item">
                      <span class="legend-color theory"></span>
                      <span>理论基础</span>
                    </div>
                    <div class="legend-item">
                      <span class="legend-color analysis"></span>
                      <span>分析方法</span>
                    </div>
                    <div class="legend-item">
                      <span class="legend-color control"></span>
                      <span>控制技术</span>
                    </div>
                  </div>
                  
                  <div v-if="hoverNode" class="node-tooltip">
                    <strong>{{ hoverNode.name }}</strong><br>
                    类别: {{ getCategoryLabel(hoverNode.category) }}<br>
                    专业领域: {{ selectedGraph.domain }}
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  TrendCharts, VideoPlay, WindPower, Tools, Search, 
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
      name: '直升机总体设计知识图谱',
      description: '涵盖直升机总体构型、系统设计、性能分析等核心技术知识',
      domain: '总体设计',
      nodeCount: 12,
      nodes: [
        { id: 'helicopter', name: '直升机', category: 'core', symbolSize: 45, x: 50, y: 50 },
        { id: 'configuration', name: '总体构型', category: 'design', symbolSize: 35, x: 25, y: 25 },
        { id: 'rotorsystem', name: '旋翼系统', category: 'system', symbolSize: 35, x: 75, y: 25 },
        { id: 'transmissionsys', name: '传动系统', category: 'system', symbolSize: 30, x: 15, y: 45 },
        { id: 'fuselage', name: '机体结构', category: 'structure', symbolSize: 30, x: 85, y: 45 },
        { id: 'tailrotor', name: '尾桨系统', category: 'system', symbolSize: 25, x: 90, y: 15 },
        { id: 'landinggear', name: '起落架', category: 'system', symbolSize: 25, x: 10, y: 65 },
        { id: 'powerplant', name: '动力装置', category: 'system', symbolSize: 30, x: 40, y: 75 },
        { id: 'flightcontrol', name: '飞控系统', category: 'system', symbolSize: 30, x: 60, y: 75 },
        { id: 'weightbalance', name: '重量重心', category: 'performance', symbolSize: 25, x: 25, y: 85 },
        { id: 'stability', name: '稳定性', category: 'performance', symbolSize: 25, x: 50, y: 85 },
        { id: 'maneuverability', name: '操纵性', category: 'performance', symbolSize: 25, x: 75, y: 85 }
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
      name: '旋翼空气动力学知识图谱',
      description: '直升机旋翼空气动力学理论与分析方法知识体系',
      domain: '空气动力学',
      nodeCount: 10,
      nodes: [
        { id: 'rotoraero', name: '旋翼空气动力学', category: 'core', symbolSize: 40, x: 50, y: 50 },
        { id: 'bladetheory', name: '叶素理论', category: 'theory', symbolSize: 30, x: 20, y: 20 },
        { id: 'vortextheory', name: '涡流理论', category: 'theory', symbolSize: 30, x: 80, y: 20 },
        { id: 'inducedvelocity', name: '诱导速度', category: 'analysis', symbolSize: 30, x: 50, y: 20 },
        { id: 'liftgeneration', name: '升力产生', category: 'mechanism', symbolSize: 25, x: 10, y: 40 },
        { id: 'draganalysis', name: '阻力分析', category: 'analysis', symbolSize: 25, x: 35, y: 40 },
        { id: 'torqueanalysis', name: '扭矩分析', category: 'analysis', symbolSize: 25, x: 65, y: 40 },
        { id: 'loadanalysis', name: '载荷分析', category: 'analysis', symbolSize: 25, x: 90, y: 40 },
        { id: 'compressibility', name: '压缩性效应', category: 'phenomenon', symbolSize: 20, x: 30, y: 70 },
        { id: 'groundeffect', name: '地面效应', category: 'phenomenon', symbolSize: 20, x: 70, y: 70 }
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
      name: '飞行力学与控制知识图谱',
      description: '直升机飞行力学特性与飞行控制系统专业知识体系',
      domain: '飞行控制',
      nodeCount: 11,
      nodes: [
        { id: 'flightmechanics', name: '飞行力学', category: 'core', symbolSize: 40, x: 50, y: 50 },
        { id: 'motioneq', name: '运动方程', category: 'theory', symbolSize: 30, x: 25, y: 25 },
        { id: 'stabilityderiv', name: '稳定性导数', category: 'analysis', symbolSize: 30, x: 75, y: 25 },
        { id: 'controlsys', name: '控制系统', category: 'system', symbolSize: 35, x: 50, y: 25 },
        { id: 'flightenvelope', name: '飞行包线', category: 'performance', symbolSize: 30, x: 15, y: 50 },
        { id: 'handlingquals', name: '操纵品质', category: 'performance', symbolSize: 25, x: 85, y: 50 },
        { id: 'autostab', name: '自动稳定', category: 'control', symbolSize: 25, x: 30, y: 75 },
        { id: 'attitudecontrol', name: '姿态控制', category: 'control', symbolSize: 25, x: 50, y: 75 },
        { id: 'trajectorycontrol', name: '轨迹控制', category: 'control', symbolSize: 25, x: 70, y: 75 },
        { id: 'vibrationcontrol', name: '振动控制', category: 'control', symbolSize: 20, x: 40, y: 90 },
        { id: 'flighttest', name: '飞行试验', category: 'validation', symbolSize: 20, x: 60, y: 90 }
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

  // 当前显示的节点和相关数据
const currentNodes = ref([])
const graphWidth = 800
const graphHeight = 400

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
  
  return {
    left: `${node.x}%`,
    top: `${node.y}%`,
    backgroundColor: colors[node.category] || '#ccc',
    width: `${node.symbolSize * 2.0}px`,
    height: `${node.symbolSize * 2.0}px`
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

// 获取节点位置（百分比坐标）
const getNodePosition = (nodeId) => {
  const node = currentNodes.value.find(n => n.id === nodeId)
  if (!node) return { x: 0, y: 0 }
  
  // 直接返回百分比坐标（0-100）
  return {
    x: node.x,
    y: node.y
  }
}

// 获取调整后的边缘线条起点和终点（考虑节点半径）
const getAdjustedEdgePositions = (edge) => {
  const sourceNode = currentNodes.value.find(n => n.id === edge.source)
  const targetNode = currentNodes.value.find(n => n.id === edge.target)
  
  if (!sourceNode || !targetNode) {
    return {
      x1: sourceNode?.x || 0,
      y1: sourceNode?.y || 0,
      x2: targetNode?.x || 0,
      y2: targetNode?.y || 0
    }
  }
  
  // 计算方向向量
  const dx = targetNode.x - sourceNode.x
  const dy = targetNode.y - sourceNode.y
  const distance = Math.sqrt(dx * dx + dy * dy)
  
  if (distance === 0) {
    return {
      x1: sourceNode.x,
      y1: sourceNode.y,
      x2: targetNode.x,
      y2: targetNode.y
    }
  }
  
  // 单位向量
  const ux = dx / distance
  const uy = dy / distance
  
  // 计算节点的实际像素尺寸
  const container = document.querySelector('.graph-visualization')
  if (!container) {
    return {
      x1: sourceNode.x,
      y1: sourceNode.y,
      x2: targetNode.x,
      y2: targetNode.y
    }
  }
  
  const containerRect = container.getBoundingClientRect()
  const containerWidth = containerRect.width
  const containerHeight = containerRect.height
  
  // 节点实际像素尺寸
  const sourceWidthPx = sourceNode.symbolSize * 2.0
  const sourceHeightPx = sourceNode.symbolSize * 2.0
  const targetWidthPx = targetNode.symbolSize * 2.0
  const targetHeightPx = targetNode.symbolSize * 2.0
  
  // 转换为百分比
  const sourceRadiusPercentX = (sourceWidthPx / 2) / containerWidth * 100
  const sourceRadiusPercentY = (sourceHeightPx / 2) / containerHeight * 100
  const targetRadiusPercentX = (targetWidthPx / 2) / containerWidth * 100
  const targetRadiusPercentY = (targetHeightPx / 2) / containerHeight * 100
  
  // 根据方向向量选择对应的半径百分比
  const sourceRadiusPercent = Math.sqrt(
    Math.pow(ux * sourceRadiusPercentX, 2) + 
    Math.pow(uy * sourceRadiusPercentY, 2)
  )
  const targetRadiusPercent = Math.sqrt(
    Math.pow(ux * targetRadiusPercentX, 2) + 
    Math.pow(uy * targetRadiusPercentY, 2)
  )
  
  // 调整源节点坐标：沿向量方向移动半径
  const adjustedSourceX = sourceNode.x + ux * sourceRadiusPercent
  const adjustedSourceY = sourceNode.y + uy * sourceRadiusPercent
  
  // 调整目标节点坐标：沿向量反方向移动半径（让箭头指向边缘）
  const adjustedTargetX = targetNode.x - ux * targetRadiusPercent
  const adjustedTargetY = targetNode.y - uy * targetRadiusPercent
  
  return {
    x1: adjustedSourceX,
    y1: adjustedSourceY,
    x2: adjustedTargetX,
    y2: adjustedTargetY
  }
}

// 根据ID获取节点
const getNodeById = (nodeId) => {
  return currentNodes.value.find(n => n.id === nodeId)
}

// 获取类别标签
const getCategoryLabel = (category) => {
  const labels = {
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



.header-actions {
  display: flex;
  gap: 10px;
}

.stats-section {
  margin-bottom: 20px;
}

.combined-stats-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.vertical-stats-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-top: 16px;
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

.combined-stats-grid {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
}

.stats-item {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 12px;
  position: relative;
  min-height: 50px;
}

.stats-item:not(:last-child) {
  border-right: 1px solid #e4e7ed;
}

.stats-item-content {
  flex: 1;
}

.stats-item-number {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 2px;
}

.stats-item-label {
  margin-top: 0;
  color: #909399;
  font-size: 11px;
  line-height: 1.2;
}

.stats-item-icon {
  font-size: 20px;
  opacity: 0.4;
  margin-left: 12px;
}

.stat-card {
  position: relative;
  overflow: hidden;
}

.stat-content {
  position: relative;
  z-index: 2;
  padding: 8px 12px;
}

.stat-number {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 2px;
}

.stat-label {
  margin-top: 0;
  color: #909399;
  font-size: 11px;
  line-height: 1.2;
}

.stat-icon {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 24px;
  opacity: 0.4;
  z-index: 1;
}

.stat-card.compact {
  min-height: 70px;
}

.stat-card.compact .el-card__body {
  padding: 12px 16px !important;
}

.nodes-icon { color: #e74c3c; }
.edges-icon { color: #27ae60; }
.graphs-icon { color: #3498db; }
.domains-icon { color: #f39c12; }

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
  height: 800px;
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
  padding: 10px;
  position: relative;
}

.simple-graph {
  height: 100%;
  position: relative;
  background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
  border-radius: 8px;
  padding: 10px;
  border: 1px solid #e3e8ff;
  display: flex;
  flex-direction: column;
}

.simple-graph h3 {
  text-align: center;
  margin-bottom: 15px;
  color: #1e40af;
  font-size: 20px;
  font-weight: bold;
}



.graph-visualization {
  position: relative;
  flex: 1;
  margin-bottom: 5px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  min-height: 400px;
}

.relation-lines {
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1;
  pointer-events: none;
}

.graph-nodes {
  position: relative;
  width: 100%;
  height: 100%;
  z-index: 2;
}

.graph-node {
  position: absolute;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  transform: translate(-50%, -50%);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  border: 2px solid rgba(255,255,255,0.3);
  backdrop-filter: blur(4px);
}

.graph-node:hover {
  transform: translate(-50%, -50%) scale(1.15);
  z-index: 10;
  box-shadow: 0 8px 25px rgba(0,0,0,0.25);
}

.node-content {
  text-align: center;
  padding: 8px 12px;
}

.node-name {
  color: #1e40af; /* 深蓝色，对比度高 */
  font-size: 12px;
  font-weight: bold;
  text-shadow: 0 1px 2px rgba(255,255,255,0.8);
  line-height: 1.3;
  text-align: center;
  word-break: break-word;
  padding: 2px;
}

.relations-panel {
  background: white;
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 10px;
  border-left: 3px solid #3b82f6;
}

.relations-panel h4 {
  margin: 0 0 8px 0;
  color: #1e40af;
  font-size: 13px;
  font-weight: bold;
}

.relation-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.relation-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  padding: 2px 0;
}

.source-node {
  color: #dc2626;
  font-weight: bold;
  background: #fef2f2;
  padding: 1px 4px;
  border-radius: 3px;
}

.relation-arrow {
  color: #475569; /* 更深的灰色，对比度更高 */
  font-size: 10px;
  font-weight: 500;
}

.target-node {
  color: #059669;
  font-weight: bold;
  background: #f0fdf4;
  padding: 1px 4px;
  border-radius: 3px;
}





.graph-legend {
  position: absolute;
  top: 15px;
  right: 15px;
  background: white;
  padding: 10px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  min-width: 120px;
}

.graph-legend h4 {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: #303133;
  font-weight: bold;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
  font-size: 11px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-color.core { background: #e74c3c; }
.legend-color.design { background: #3498db; }
.legend-color.system { background: #2ecc71; }
.legend-color.structure { background: #f39c12; }
.legend-color.performance { background: #9b59b6; }
.legend-color.theory { background: #1abc9c; }
.legend-color.analysis { background: #e67e22; }
.legend-color.control { background: #27ae60; }
.legend-color.validation { background: #8e44ad; }

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
