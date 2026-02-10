<template>
  <div class="helicopter-research">
    <!-- 头部区域 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">直升机智能研发协作平台</h1>
        <p class="page-subtitle">多智能体协同设计 · 智能推理分析 · 设计图纸生成</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" icon="Plus" @click="createNewProject">新建项目</el-button>
        <el-button icon="FolderOpened">打开项目</el-button>
        <el-button icon="Document">设计模板</el-button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧：设计系统模块 -->
      <div class="left-panel">
        <div class="panel-header">
          <h3>研发设计模块</h3>
        </div>
        
        <div class="design-modules">
          <div
            v-for="module in designModules"
            :key="module.id"
            :class="['module-item', { active: selectedModule?.id === module.id }]"
            @click="selectModule(module)"
          >
            <div class="module-icon" :style="{ backgroundColor: module.color }">
              <el-icon><component :is="module.icon" /></el-icon>
            </div>
            <div class="module-info">
              <div class="module-name">{{ module.name }}</div>
              <div class="module-term">{{ module.term }}</div>
              <el-tag size="small" :type="module.status === 'active' ? 'success' : 'info'">
                {{ module.status === 'active' ? '已启用' : '未启用' }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>

      <!-- 中间：协作推理区 -->
      <div class="center-panel">
        <!-- 场景描述输入 -->
        <div class="scenario-section">
          <div class="section-header">
            <h3>设计场景描述</h3>
          </div>
          
          <el-input
            v-model="scenarioDescription"
            type="textarea"
            :rows="4"
            placeholder="请描述直升机设计场景，例如：设计一款适用于高原环境的轻型运输直升机，要求在海拔4000米以上保持良好性能，载重能力2吨，航程500公里..."
            class="scenario-input"
          />
          
          <div class="design-params">
            <div class="param-item">
              <label>飞行高度</label>
              <el-input-number v-model="designParams.altitude" :min="0" :max="10000" />
              <span class="param-unit">米</span>
            </div>
            <div class="param-item">
              <label>最大速度</label>
              <el-input-number v-model="designParams.speed" :min="0" :max="500" />
              <span class="param-unit">km/h</span>
            </div>
            <div class="param-item">
              <label>载重能力</label>
              <el-input-number v-model="designParams.payload" :min="0" :max="20" :step="0.5" />
              <span class="param-unit">吨</span>
            </div>
            <div class="param-item">
              <label>航程距离</label>
              <el-input-number v-model="designParams.range" :min="0" :max="2000" />
              <span class="param-unit">公里</span>
            </div>
          </div>
          
          <div class="input-actions">
            <el-button type="primary" icon="Cpu" :loading="analyzing" @click="startAnalysis">
              启动智能推理
            </el-button>
          </div>
        </div>

        <!-- 智能体协作推理过程 -->
        <div class="reasoning-process">
          <div class="section-header">
            <h3>智能体推理协作</h3>
            <el-tag type="info">{{ reasoningSteps.length }} 步骤</el-tag>
          </div>
          
          <el-steps direction="vertical" :active="currentReasoningStep" finish-status="success">
            <el-step
              v-for="(step, index) in reasoningSteps"
              :key="index"
              :title="step.title"
              :description="step.description"
            >
              <template #icon>
                <div class="step-icon" :style="{ backgroundColor: step.color }">
                  <el-icon><component :is="step.icon" /></el-icon>
                </div>
              </template>
              
              <div class="step-detail">
                <div class="detail-header">
                  <el-tag size="small">{{ step.agent }}</el-tag>
                  <span class="detail-time">{{ step.time }}</span>
                </div>
                <div v-if="step.result" class="detail-result">
                  <div class="result-label">分析结果：</div>
                  <div class="result-content">{{ step.result }}</div>
                </div>
                <div v-if="step.metrics" class="detail-metrics">
                  <div v-for="(value, key) in step.metrics" :key="key" class="metric-item">
                    <span class="metric-label">{{ key }}：</span>
                    <span class="metric-value">{{ value }}</span>
                  </div>
                </div>
              </div>
            </el-step>
          </el-steps>
        </div>

        <!-- 设计方案生成 -->
        <div class="solutions-section">
          <div class="section-header">
            <h3>设计方案</h3>
            <el-button text icon="Plus" @click="generateMoreSolutions">生成更多方案</el-button>
          </div>
          
          <div class="solutions-grid">
            <div
              v-for="(solution, index) in solutions"
              :key="index"
              :class="['solution-card', { selected: selectedSolutionIndex === index }]"
              @click="selectSolution(index)"
            >
              <div class="solution-header">
                <span class="solution-title">方案 {{ index + 1 }}</span>
                <el-tag size="small" :type="getSolutionType(solution.score)">
                  评分: {{ solution.score }}
                </el-tag>
              </div>
              <div class="solution-content">
                <div class="content-row">
                  <span class="content-label">主旋翼：</span>
                  <span class="content-value">{{ solution.rotor }}</span>
                </div>
                <div class="content-row">
                  <span class="content-label">发动机：</span>
                  <span class="content-value">{{ solution.engine }}</span>
                </div>
                <div class="content-row">
                  <span class="content-label">机身长度：</span>
                  <span class="content-value">{{ solution.fuselage }} 米</span>
                </div>
                <div class="content-row">
                  <span class="content-label">载重：</span>
                  <span class="content-value">{{ solution.payload }} 吨</span>
                </div>
                <div class="content-row">
                  <span class="content-label">航程：</span>
                  <span class="content-value">{{ solution.range }} 公里</span>
                </div>
              </div>
              <div class="solution-footer">
                <el-tag size="small">{{ solution.mechanics }}</el-tag>
                <el-tag size="small" type="info">{{ solution.scenario }}</el-tag>
                <el-tag size="small" type="warning">置信度 {{ solution.confidence }}%</el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：设计细节和分析 -->
      <div class="right-panel">
        <!-- 设计图纸生成 -->
        <div class="blueprint-section">
          <div class="section-header">
            <h3>设计图纸生成</h3>
          </div>
          
          <el-tabs v-model="activeBlueprintTab" class="blueprint-tabs">
            <el-tab-pane label="主视图" name="main">
              <div class="blueprint-preview">
                <div v-if="blueprintGenerating" class="generating-overlay">
                  <el-icon class="is-loading" :size="48"><Loading /></el-icon>
                  <p>正在生成设计图纸...</p>
                </div>
                <div v-else class="blueprint-placeholder">
                  <el-icon><Picture /></el-icon>
                  <p>点击下方按钮生成设计图纸</p>
                  <el-button type="primary" size="small" @click="generateBlueprint">
                    生成主视图
                  </el-button>
                  <el-button size="small" @click="uploadBlueprint">上传图纸</el-button>
                </div>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="侧视图" name="side">
              <div class="blueprint-preview">
                <div class="blueprint-placeholder">
                  <el-icon><Picture /></el-icon>
                  <p>侧视图图纸</p>
                </div>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="顶视图" name="top">
              <div class="blueprint-preview">
                <div class="blueprint-placeholder">
                  <el-icon><Picture /></el-icon>
                  <p>顶视图图纸</p>
                </div>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="分解图" name="exploded">
              <div class="blueprint-preview">
                <div class="blueprint-placeholder">
                  <el-icon><Picture /></el-icon>
                  <p>零部件分解图</p>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>

        <!-- 力学分析 -->
        <div class="analysis-section">
          <div class="section-header">
            <h3>力学分析</h3>
          </div>
          
          <div class="analysis-cards">
            <div class="analysis-card">
              <div class="card-title">气动力分析</div>
              <div class="card-metrics">
                <div class="metric-row">
                  <span class="metric-label">升力系数</span>
                  <span class="metric-value">0.85</span>
                </div>
                <div class="metric-row">
                  <span class="metric-label">阻力系数</span>
                  <span class="metric-value">0.045</span>
                </div>
                <div class="metric-row">
                  <span class="metric-label">最大升力</span>
                  <span class="metric-value">18000 N</span>
                </div>
              </div>
              <el-progress :percentage="85" :stroke-width="12" color="#409eff">
                <template #default="{ percentage }">
                  <span class="percentage-value">{{ percentage }}%</span>
                </template>
              </el-progress>
            </div>
            
            <div class="analysis-card">
              <div class="card-title">结构强度分析</div>
              <div class="card-metrics">
                <div class="metric-row">
                  <span class="metric-label">最大载荷</span>
                  <span class="metric-value">2.5 G</span>
                </div>
                <div class="metric-row">
                  <span class="metric-label">疲劳寿命</span>
                  <span class="metric-value">12000 h</span>
                </div>
                <div class="metric-row">
                  <span class="metric-label">安全系数</span>
                  <span class="metric-value">1.8</span>
                </div>
              </div>
              <el-progress :percentage="92" :stroke-width="12" color="#67c23a">
                <template #default="{ percentage }">
                  <span class="percentage-value">{{ percentage }}%</span>
                </template>
              </el-progress>
            </div>
            
            <div class="analysis-card">
              <div class="card-title">振动特性</div>
              <div class="card-metrics">
                <div class="metric-row">
                  <span class="metric-label">主旋翼频率</span>
                  <span class="metric-value">5.2 Hz</span>
                </div>
                <div class="metric-row">
                  <span class="metric-label">尾桨频率</span>
                  <span class="metric-value">42.6 Hz</span>
                </div>
                <div class="metric-row">
                  <span class="metric-label">振动水平</span>
                  <span class="metric-value">0.15 g</span>
                </div>
              </div>
              <el-progress :percentage="88" :stroke-width="12" color="#e6a23c">
                <template #default="{ percentage }">
                  <span class="percentage-value">{{ percentage }}%</span>
                </template>
              </el-progress>
            </div>
          </div>
        </div>

        <!-- 机械原理分析 -->
        <div class="mechanics-section">
          <div class="section-header">
            <h3>机械原理分析</h3>
          </div>
          
          <div class="mechanics-list">
            <div class="mechanics-item">
              <div class="item-header">
                <el-icon><Cpu /></el-icon>
                <span class="item-title">旋翼系统</span>
              </div>
              <div class="item-content">
                <div class="content-row">
                  <span class="content-label">旋翼类型：</span>
                  <span class="content-value">铰接式主旋翼</span>
                </div>
                <div class="content-row">
                  <span class="content-label">桨叶数量：</span>
                  <span class="content-value">4 片</span>
                </div>
                <div class="content-row">
                  <span class="content-label">旋翼直径：</span>
                  <span class="content-value">12.8 米</span>
                </div>
                <div class="content-row">
                  <span class="content-label">桨毂形式：</span>
                  <span class="content-value">半刚性连接</span>
                </div>
              </div>
            </div>
            
            <div class="mechanics-item">
              <div class="item-header">
                <el-icon><Setting /></el-icon>
                <span class="item-title">传动系统</span>
              </div>
              <div class="item-content">
                <div class="content-row">
                  <span class="content-label">传动比：</span>
                  <span class="content-value">1:3.2</span>
                </div>
                <div class="content-row">
                  <span class="content-label">离合器：</span>
                  <span class="content-value">液压多片式</span>
                </div>
                <div class="content-row">
                  <span class="content-label">主减速器：</span>
                  <span class="content-value">行星齿轮组</span>
                </div>
              </div>
            </div>
            
            <div class="mechanics-item">
              <div class="item-header">
                <el-icon><Aim /></el-icon>
                <span class="item-title">尾桨系统</span>
              </div>
              <div class="item-content">
                <div class="content-row">
                  <span class="content-label">尾桨类型：</span>
                  <span class="content-value">推力式尾桨</span>
                </div>
                <div class="content-row">
                  <span class="content-label">桨叶数量：</span>
                  <span class="content-value">4 片</span>
                </div>
                <div class="content-row">
                  <span class="content-label">控制方式：</span>
                  <span class="content-value">伺服液压</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 驾驶场景分析 -->
        <div class="scenario-analysis-section">
          <div class="section-header">
            <h3>驾驶场景分析</h3>
          </div>
          
          <el-tabs v-model="activeScenarioTab" class="scenario-tabs">
            <el-tab-pane label="巡航飞行" name="cruise">
              <div class="scenario-content">
                <div class="scenario-metric">
                  <span class="metric-label">最优巡航高度</span>
                  <span class="metric-value">3500 米</span>
                </div>
                <div class="scenario-metric">
                  <span class="metric-label">巡航速度</span>
                  <span class="metric-value">280 km/h</span>
                </div>
                <div class="scenario-metric">
                  <span class="metric-label">燃油消耗</span>
                  <span class="metric-value">450 L/h</span>
                </div>
                <div class="scenario-metric">
                  <span class="metric-label">航程</span>
                  <span class="metric-value">650 公里</span>
                </div>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="悬停作业" name="hover">
              <div class="scenario-content">
                <div class="scenario-metric">
                  <span class="metric-label">最大悬停高度</span>
                  <span class="metric-value">2800 米</span>
                </div>
                <div class="scenario-metric">
                  <span class="metric-label">悬停油耗</span>
                  <span class="metric-value">520 L/h</span>
                </div>
                <div class="scenario-metric">
                  <span class="metric-label">稳定时间</span>
                  <span class="metric-value">8 秒</span>
                </div>
                <div class="scenario-metric">
                  <span class="metric-label">侧风限制</span>
                  <span class="metric-value">45 km/h</span>
                </div>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="高原飞行" name="highland">
              <div class="scenario-content">
                <div class="scenario-metric">
                  <span class="metric-label">最大升限</span>
                  <span class="metric-value">6200 米</span>
                </div>
                <div class="scenario-metric">
                  <span class="metric-label">4000米高度性能</span>
                  <span class="metric-value">92%</span>
                </div>
                <div class="scenario-metric">
                  <span class="metric-label">氧气补充</span>
                  <span class="metric-value">需配备</span>
                </div>
                <div class="scenario-metric">
                  <span class="metric-label">发动机降额</span>
                  <span class="metric-value">15%</span>
                </div>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="应急情况" name="emergency">
              <div class="scenario-content">
                <div class="scenario-metric">
                  <span class="metric-label">自转下滑率</span>
                  <span class="metric-value">2.1 m/s</span>
                </div>
                <div class="scenario-metric">
                  <span class="metric-label">单发失效升限</span>
                  <span class="metric-value">3200 米</span>
                </div>
                <div class="scenario-metric">
                  <span class="metric-label">水上迫降</span>
                  <span class="metric-value">支持</span>
                </div>
                <div class="scenario-metric">
                  <span class="metric-label">紧急油量</span>
                  <span class="metric-value">30 分钟</span>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>

        <!-- 操作按钮 -->
        <div class="action-section">
          <el-button type="primary" icon="Document" @click="exportDesignReport" style="width: 100%">
            导出设计报告
          </el-button>
          <el-button type="success" icon="Check" @click="saveDesign" style="width: 100%">
            保存设计
          </el-button>
          <el-button icon="Share" @click="shareDesign" style="width: 100%">
            分享设计
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Cpu, Loading, Picture, Setting, Aim
} from '@element-plus/icons-vue'

// 设计模块数据
const designModules = ref([
  {
    id: 1,
    name: '旋翼系统',
    term: 'Rotor System',
    icon: 'Position',
    color: '#ff6b6b',
    status: 'active',
    expertise: ['主旋翼设计', '尾桨系统', '铰接机构', '变距控制']
  },
  {
    id: 2,
    name: '动力系统',
    term: 'Power System',
    icon: 'Lightning',
    color: '#f39c12',
    status: 'active',
    expertise: ['发动机选型', '涡轮技术', '燃油系统', '冷却系统']
  },
  {
    id: 3,
    name: '传动系统',
    term: 'Transmission System',
    icon: 'Connection',
    color: '#4ecdc4',
    status: 'active',
    expertise: ['主减速器', '传动轴', '离合器', '润滑系统']
  },
  {
    id: 4,
    name: '机身结构',
    term: 'Fuselage Structure',
    icon: 'Grid',
    color: '#9b59b6',
    status: 'active',
    expertise: ['机身设计', '材料选择', '强度分析', '疲劳评估']
  },
  {
    id: 5,
    name: '驾驶控制',
    term: 'Flight Control',
    icon: 'Monitor',
    color: '#3498db',
    status: 'active',
    expertise: ['人机界面', '操纵系统', '自动驾驶', '仪表显示']
  },
  {
    id: 6,
    name: '武器系统',
    term: 'Weapon System',
    icon: 'Aim',
    color: '#1abc9c',
    status: 'inactive',
    expertise: ['武器挂载', '火控系统', '瞄准系统', '弹道计算']
  },
  {
    id: 7,
    name: '航电系统',
    term: 'Avionics System',
    icon: 'DataLine',
    color: '#e74c3c',
    status: 'active',
    expertise: ['通信导航', '雷达系统', '电子对抗', '数据处理']
  }
])

// 选中的模块
const selectedModule = ref<any>(null)

// 场景描述
const scenarioDescription = ref('')

// 设计参数
const designParams = ref({
  altitude: 3500,
  speed: 280,
  payload: 2,
  range: 500
})

// 分析状态
const analyzing = ref(false)

// 推理步骤
const reasoningSteps = ref<any[]>([])

// 当前推理步骤
const currentReasoningStep = ref(0)

// 设计方案
const solutions = ref<any[]>([])

// 选中的方案索引
const selectedSolutionIndex = ref(-1)

// 设计图纸生成状态
const blueprintGenerating = ref(false)

// 当前图纸标签页
const activeBlueprintTab = ref('main')

// 当前场景标签页
const activeScenarioTab = ref('cruise')

// 选择模块
const selectModule = (module: any) => {
  selectedModule.value = module
  ElMessage.info(`已选择: ${module.name} - ${module.term}`)
}

// 新建项目
const createNewProject = () => {
  ElMessage.success('新建设计项目')
}

// 启动分析
const startAnalysis = async () => {
  if (!scenarioDescription.value.trim()) {
    ElMessage.warning('请描述设计场景')
    return
  }

  analyzing.value = true
  reasoningSteps.value = []
  solutions.value = []

  try {
    await simulateReasoning()
    ElMessage.success('智能推理完成，已生成设计方案')
  } catch (error) {
    ElMessage.error('分析失败，请重试')
  } finally {
    analyzing.value = false
  }
}

// 模拟推理过程
const simulateReasoning = async () => {
  const now = new Date()

  // 步骤1：场景分析
  await delay(600)
  reasoningSteps.value.push({
    title: '场景分析',
    description: '分析高原运输直升机设计要求和约束条件',
    agent: '场景智能体',
    icon: 'DataAnalysis',
    color: '#409eff',
    time: formatTime(new Date(now.getTime() + 600)),
    result: '识别关键需求：海拔4000米、载重2吨、航程500公里',
    metrics: {
      '设计复杂度': '中等',
      '技术风险': '较低',
      '开发周期': '18个月'
    }
  })

  // 步骤2：旋翼系统推理
  await delay(600)
  reasoningSteps.value.push({
    title: '旋翼系统设计推理',
    description: '基于场景需求推理旋翼直径、桨叶数量、桨毂形式',
    agent: '旋翼智能体',
    icon: 'Position',
    color: '#ff6b6b',
    time: formatTime(new Date(now.getTime() + 1200)),
    result: '推荐4叶铰接式主旋翼，直径12.8米，适合高原环境',
    metrics: {
      '升力效率': '82%',
      '振动控制': '良好',
      '噪声水平': '中等'
    }
  })

  // 步骤3：动力系统推理
  await delay(600)
  reasoningSteps.value.push({
    title: '动力系统选型推理',
    description: '根据高原性能需求推理发动机型号和功率配置',
    agent: '动力智能体',
    icon: 'Lightning',
    color: '#f39c12',
    time: formatTime(new Date(now.getTime() + 1800)),
    result: '选型涡轴-8C发动机，额定功率1800kW，配备高原增压器',
    metrics: {
      '高原功率保持': '85%',
      '燃油效率': '良好',
      '可靠性': '高'
    }
  })

  // 步骤4：结构系统推理
  await delay(600)
  reasoningSteps.value.push({
    title: '机身结构推理',
    description: '推理机身材料选择和结构优化方案',
    agent: '结构智能体',
    icon: 'Grid',
    color: '#9b59b6',
    time: formatTime(new Date(now.getTime() + 2400)),
    result: '采用碳纤维复合材料机身，铝合金主梁，优化整体重量分布',
    metrics: {
      '结构重量': '3200kg',
      '强度系数': '1.8',
      '疲劳寿命': '12000小时'
    }
  })

  // 步骤5：多智能体协作
  await delay(800)
  reasoningSteps.value.push({
    title: '多系统协同优化',
    description: '旋翼、动力、结构、控制四系统联合评审方案',
    agent: '协作中心',
    icon: 'Connection',
    color: '#4ecdc4',
    time: formatTime(new Date(now.getTime() + 3200)),
    result: '综合优化：旋翼-发动机匹配度95%，结构-动力协调性92%',
    metrics: {
      '系统匹配度': '优秀',
      '设计冲突': '无',
      '协调成本': '中等'
    }
  })

  currentReasoningStep.value = reasoningSteps.value.length

  // 生成方案
  await delay(600)
  solutions.value = [
    {
      score: 92,
      rotor: '4叶铰接式，直径12.8米',
      engine: '涡轴-8C，1800kW',
      fuselage: '12.5',
      payload: '2.1',
      range: '520',
      mechanics: '刚性传动',
      scenario: '高原运输',
      confidence: 92
    },
    {
      score: 88,
      rotor: '3叶半刚性，直径13.2米',
      engine: '涡轴-8C，1650kW',
      fuselage: '13.2',
      payload: '2.3',
      range: '560',
      mechanics: '半刚性传动',
      scenario: '高原运输',
      confidence: 88
    },
    {
      score: 85,
      rotor: '4叶铰接式，直径12.5米',
      engine: '涡轴-8C，1900kW',
      fuselage: '12.0',
      payload: '1.8',
      range: '480',
      mechanics: '柔性传动',
      scenario: '高原运输',
      confidence: 85
    }
  ]

  selectedSolutionIndex.value = 0
}

// 生成更多方案
const generateMoreSolutions = () => {
  ElMessage.info('正在生成更多设计方案...')
}

// 选择方案
const selectSolution = (index: number) => {
  selectedSolutionIndex.value = index
  currentReasoningStep.value = reasoningSteps.value.length
}

// 获取方案类型
const getSolutionType = (score: number) => {
  if (score >= 90) return 'success'
  if (score >= 85) return 'warning'
  return 'info'
}

// 生成设计图纸
const generateBlueprint = () => {
  blueprintGenerating.value = true
  setTimeout(() => {
    blueprintGenerating.value = false
    ElMessage.success('设计图纸生成成功！')
  }, 3000)
}

// 上传图纸
const uploadBlueprint = () => {
  ElMessage.info('上传设计图纸')
}

// 导出设计报告
const exportDesignReport = () => {
  ElMessage.info('正在生成设计报告...')
  setTimeout(() => {
    ElMessage.success('设计报告已导出')
  }, 2000)
}

// 保存设计
const saveDesign = () => {
  ElMessage.success('设计方案已保存')
}

// 分享设计
const shareDesign = () => {
  ElMessage.info('分享设计方案')
}

// 延迟函数
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

// 格式化时间
const formatTime = (date: Date) => {
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
.helicopter-research {
  width: 100%;
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
}

/* 头部区域 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.header-content h1 {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* 主内容区 */
.main-content {
  display: grid;
  grid-template-columns: 280px 1fr 380px;
  gap: 20px;
}

/* 左右面板 */
.left-panel, .right-panel {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  height: fit-content;
}

/* 中间面板 */
.center-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 面板头部 */
.panel-header, .section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #e5e7eb;
}

.panel-header h3, .section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

/* 设计模块列表 */
.design-modules {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.module-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.3s;
  background: #f9fafb;
}

.module-item:hover {
  background: #e5e7eb;
  transform: translateX(4px);
}

.module-item.active {
  border-color: #409eff;
  background: #ecf5ff;
}

.module-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.module-info {
  flex: 1;
}

.module-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.module-term {
  font-size: 12px;
  color: #909399;
  font-style: italic;
  margin-bottom: 8px;
}

/* 场景描述区 */
.scenario-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.scenario-input {
  margin-bottom: 16px;
}

.design-params {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.param-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.param-item label {
  font-size: 12px;
  color: #606266;
  min-width: 70px;
}

.param-unit {
  font-size: 12px;
  color: #909399;
}

.input-actions {
  display: flex;
  gap: 12px;
}

/* 推理过程 */
.reasoning-process {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.step-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

.step-detail {
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
  margin-top: 8px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.detail-time {
  font-size: 12px;
  color: #909399;
}

.detail-result {
  margin-bottom: 12px;
}

.result-label {
  font-weight: 600;
  color: #409eff;
  margin-bottom: 6px;
}

.result-content {
  font-size: 13px;
  color: #303133;
  line-height: 1.6;
}

.detail-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 8px;
}

.metric-item {
  display: flex;
  gap: 6px;
  font-size: 12px;
}

.metric-label {
  color: #909399;
}

.metric-value {
  color: #303133;
  font-weight: 600;
}

/* 设计方案区 */
.solutions-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.solutions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}

.solution-card {
  padding: 12px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.solution-card:hover {
  border-color: #409eff;
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.solution-card.selected {
  border-color: #409eff;
  background: #ecf5ff;
}

.solution-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.solution-title {
  font-weight: 600;
  color: #303133;
}

.solution-content {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 8px;
}

.content-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.content-label {
  color: #909399;
}

.content-value {
  color: #303133;
  font-weight: 600;
}

.solution-footer {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

/* 右侧面板 */
.blueprint-section,
.analysis-section,
.mechanics-section,
.scenario-analysis-section,
.action-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
}

/* 设计图纸 */
.blueprint-preview {
  min-height: 300px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 2px dashed #e5e7eb;
  border-radius: 8px;
  padding: 20px;
}

.generating-overlay {
  text-align: center;
  color: #409eff;
}

.blueprint-placeholder {
  text-align: center;
  color: #909399;
}

.blueprint-placeholder p {
  margin: 12px 0;
}

/* 分析卡片 */
.analysis-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.analysis-card {
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
}

.card-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.card-metrics {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.percentage-value {
  font-size: 12px;
  color: white;
}

/* 机械原理 */
.mechanics-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mechanics-item {
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
}

.item-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.item-title {
  font-weight: 600;
  color: #303133;
}

.item-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* 驾驶场景 */
.scenario-content {
  padding: 16px;
}

.scenario-metric {
  display: flex;
  justify-content: space-between;
  padding: 8px;
  background: #f9fafb;
  border-radius: 6px;
  margin-bottom: 8px;
}

.scenario-metric .metric-label {
  font-size: 12px;
}

.scenario-metric .metric-value {
  font-size: 12px;
  font-weight: 600;
}

/* 操作按钮 */
.action-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
