<template>
  <div class="agent-collaboration">
    <!-- 头部区域 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">多智能体协作平台</h1>
        <p class="page-subtitle">直升机研究所多部门智能体协同工作台</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" icon="Plus" @click="startNewTask">新建任务</el-button>
        <el-button icon="Document" @click="showHistory">历史记录</el-button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧：智能体部门 -->
      <div class="left-panel">
        <div class="panel-header">
          <h3>智能体部门</h3>
          <el-button text icon="Refresh" @click="refreshAgents">刷新</el-button>
        </div>
        
        <div class="agents-list">
          <div
            v-for="agent in agentDepartments"
            :key="agent.id"
            :class="['agent-item', { active: selectedAgent?.id === agent.id }]"
            @click="selectAgent(agent)"
          >
            <div class="agent-icon" :style="{ backgroundColor: agent.color }">
              <el-icon><component :is="agent.icon" /></el-icon>
            </div>
            <div class="agent-info">
              <div class="agent-name">{{ agent.name }}</div>
              <div class="agent-department">{{ agent.department }}</div>
              <el-tag v-if="agent.status === 'active'" type="success" size="small">在线</el-tag>
              <el-tag v-else type="info" size="small">离线</el-tag>
            </div>
          </div>
        </div>
      </div>

      <!-- 中间：任务和协作过程 -->
      <div class="center-panel">
        <!-- 问题输入区 -->
        <div class="task-input-section">
          <div class="section-header">
            <h3>复杂问题输入</h3>
          </div>
          <el-input
            v-model="currentQuestion"
            type="textarea"
            :rows="6"
            placeholder="请输入需要多智能体协作解决的复杂问题，例如：如何优化直升机在高空高温环境下的发动机性能？"
            class="question-input"
          />
          <div class="input-actions">
            <el-button type="primary" icon="Position" :loading="processing" @click="startCollaboration">
              启动协作
            </el-button>
            <el-button icon="Search" @click="findMaterials">查找素材</el-button>
            <el-button icon="Upload">上传资料</el-button>
          </div>
        </div>

        <!-- 协作过程展示 -->
        <div class="collaboration-process">
          <div class="section-header">
            <h3>协作过程</h3>
            <el-tag type="info">{{ collaborationSteps.length }} 步骤</el-tag>
          </div>
          
          <div class="process-timeline">
            <el-timeline>
              <el-timeline-item
                v-for="(step, index) in collaborationSteps"
                :key="index"
                :timestamp="step.time"
                :type="step.type"
                placement="top"
              >
                <div class="step-content">
                  <div class="step-header">
                    <el-tag :type="getAgentType(step.agentId)" size="small">
                      {{ getAgentName(step.agentId) }}
                    </el-tag>
                    <span class="step-title">{{ step.title }}</span>
                  </div>
                  <div class="step-description">{{ step.description }}</div>
                  <div v-if="step.result" class="step-result">
                    <el-icon><Document /></el-icon>
                    <span>生成结果：{{ step.result }}</span>
                  </div>
                </div>
              </el-timeline-item>
            </el-timeline>
          </div>
        </div>

        <!-- 多答案生成区 -->
        <div class="answers-section">
          <div class="section-header">
            <h3>多智能体答案</h3>
            <el-button text icon="Plus" @click="generateMoreAnswers">生成更多答案</el-button>
          </div>
          
          <div class="answers-grid">
            <div
              v-for="(answer, index) in answers"
              :key="index"
              :class="['answer-card', { selected: selectedAnswerIndex === index }]"
              @click="selectAnswer(index)"
            >
              <div class="answer-header">
                <span class="answer-title">答案 {{ index + 1 }}</span>
                <el-tag size="small" :type="getAnswerConfidenceType(answer.confidence)">
                  置信度: {{ answer.confidence }}%
                </el-tag>
              </div>
              <div class="answer-content">{{ answer.content }}</div>
              <div class="answer-footer">
                <el-tag size="small">{{ answer.agent }}</el-tag>
                <el-tag size="small" type="info">{{ answer.time }}</el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：对比评价验证 -->
      <div class="right-panel">
        <!-- 答案对比 -->
        <div class="comparison-section">
          <div class="section-header">
            <h3>答案对比</h3>
          </div>
          
          <el-table :data="answers" style="width: 100%" size="small">
            <el-table-column type="index" label="#" width="50" />
            <el-table-column prop="agent" label="协作智能体" width="120" />
            <el-table-column prop="confidence" label="置信度" width="90">
              <template #default="{ row }">
                <el-progress :percentage="row.confidence" :stroke-width="10" />
              </template>
            </el-table-column>
            <el-table-column prop="completeness" label="完整度" width="90">
              <template #default="{ row }">
                <el-progress :percentage="row.completeness" :stroke-width="10" color="#67c23a" />
              </template>
            </el-table-column>
            <el-table-column prop="innovation" label="创新性" width="90">
              <template #default="{ row }">
                <el-progress :percentage="row.innovation" :stroke-width="10" color="#e6a23c" />
              </template>
            </el-table-column>
            <el-table-column prop="practicality" label="实用性" width="90">
              <template #default="{ row }">
                <el-progress :percentage="row.practicality" :stroke-width="10" color="#409eff" />
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 评价结果 -->
        <div class="evaluation-section">
          <div class="section-header">
            <h3>评价结果</h3>
          </div>
          
          <div class="evaluation-cards">
            <div class="eval-card">
              <div class="eval-title">最佳答案</div>
              <div class="eval-value">答案 {{ bestAnswerIndex + 1 }}</div>
              <div class="eval-reason">
                综合评分最高，多部门协作度高
              </div>
            </div>
            
            <div class="eval-card">
              <div class="eval-title">协作部门数</div>
              <div class="eval-value">{{ collaborationAgentCount }}</div>
              <div class="eval-reason">
                涉及 {{ collaborationAgentCount }} 个研发部门
              </div>
            </div>
            
            <div class="eval-card">
              <div class="eval-title">综合评分</div>
              <div class="eval-value">{{ overallScore }}</div>
              <div class="eval-reason">
                多维度评估加权得分
              </div>
            </div>
          </div>
        </div>

        <!-- 人工验证 -->
        <div class="validation-section">
          <div class="section-header">
            <h3>人工验证</h3>
          </div>
          
          <el-form :model="validationForm" label-width="80px" size="small">
            <el-form-item label="验证人员">
              <el-input v-model="validationForm.validator" placeholder="请输入验证人员姓名" />
            </el-form-item>
            
            <el-form-item label="验证状态">
              <el-radio-group v-model="validationForm.status">
                <el-radio label="pass">通过</el-radio>
                <el-radio label="reject">驳回</el-radio>
                <el-radio label="review">待评审</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="验证意见">
              <el-input
                v-model="validationForm.comment"
                type="textarea"
                :rows="4"
                placeholder="请输入验证意见和建议"
              />
            </el-form-item>
            
            <el-form-item label="推荐度">
              <el-rate v-model="validationForm.rating" :max="5" show-text />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="submitValidation">提交验证</el-button>
              <el-button @click="resetValidation">重置</el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 保存发布 -->
        <div class="publish-section">
          <div class="section-header">
            <h3>保存发布</h3>
          </div>
          
          <el-form :model="publishForm" label-width="80px" size="small">
            <el-form-item label="保存标题">
              <el-input v-model="publishForm.title" placeholder="请输入保存标题" />
            </el-form-item>
            
            <el-form-item label="保存分类">
              <el-select v-model="publishForm.category" placeholder="请选择分类" style="width: 100%">
                <el-option label="技术研究" value="research" />
                <el-option label="设计方案" value="design" />
                <el-option label="测试报告" value="test" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="发布范围">
              <el-checkbox-group v-model="publishForm.scope">
                <el-checkbox label="internal">内部发布</el-checkbox>
                <el-checkbox label="external">外部发布</el-checkbox>
                <el-checkbox label="share">允许分享</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            
            <el-form-item>
              <el-button type="success" icon="Check" @click="saveAnswer">保存答案</el-button>
              <el-button type="primary" icon="Upload" @click="publishAnswer">发布答案</el-button>
              <el-button icon="Download" @click="exportReport">导出报告</el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Document
} from '@element-plus/icons-vue'

// 智能体部门数据
const agentDepartments = ref([
  {
    id: 1,
    name: '发动机智能体',
    department: '发动机研发部',
    icon: 'Cpu',
    color: '#ff6b6b',
    status: 'active',
    expertise: ['发动机设计', '热力学', '材料力学', '燃油系统']
  },
  {
    id: 2,
    name: '驾驶智能体',
    department: '驾驶舱研发部',
    icon: 'Monitor',
    color: '#4ecdc4',
    status: 'active',
    expertise: ['人机工程', '控制系统', '显示界面', '操作逻辑']
  },
  {
    id: 3,
    name: '武器智能体',
    department: '武器系统研发部',
    icon: 'Aim',
    color: '#f39c12',
    status: 'active',
    expertise: ['武器挂载', '火控系统', '瞄准系统', '弹道计算']
  },
  {
    id: 4,
    name: '监控仪表智能体',
    department: '仪表研发部',
    icon: 'DataLine',
    color: '#9b59b6',
    status: 'active',
    expertise: ['仪表显示', '传感器', '数据处理', '报警系统']
  },
  {
    id: 5,
    name: '结构智能体',
    department: '结构设计研发部',
    icon: 'Grid',
    color: '#3498db',
    status: 'active',
    expertise: ['机身结构', '材料选择', '气动设计', '强度分析']
  },
  {
    id: 6,
    name: '通信智能体',
    department: '通信系统研发部',
    icon: 'Connection',
    color: '#1abc9c',
    status: 'active',
    expertise: ['无线通信', '数据链', '加密传输', '抗干扰']
  }
])

// 当前选中的智能体
const selectedAgent = ref<any>(null)

// 当前输入的问题
const currentQuestion = ref('')

// 处理状态
const processing = ref(false)

// 协作步骤
const collaborationSteps = ref<any[]>([])

// 答案列表
const answers = ref<any[]>([])

// 选中的答案索引
const selectedAnswerIndex = ref(-1)

// 最佳答案索引
const bestAnswerIndex = ref(0)

// 协作的智能体数量
const collaborationAgentCount = ref(0)

// 验证表单
const validationForm = ref({
  validator: '',
  status: 'review',
  comment: '',
  rating: 0
})

// 发布表单
const publishForm = ref({
  title: '',
  category: 'research',
  scope: ['internal']
})

// 综合评分
const overallScore = computed(() => {
  if (answers.value.length === 0) return 0
  const total = answers.value.reduce((sum, answer) => {
    return sum + (
      answer.confidence * 0.4 +
      answer.completeness * 0.25 +
      answer.innovation * 0.2 +
      answer.practicality * 0.15
    )
  }, 0)
  return (total / answers.value.length).toFixed(1)
})

// 选择智能体
const selectAgent = (agent: any) => {
  selectedAgent.value = agent
  ElMessage.info(`已选择: ${agent.name} - ${agent.department}`)
}

// 刷新智能体
const refreshAgents = () => {
  ElMessage.success('智能体状态已刷新')
}

// 启动新任务
const startNewTask = () => {
  ElMessageBox.confirm('确定要新建任务吗？当前任务将被清空。', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    currentQuestion.value = ''
    collaborationSteps.value = []
    answers.value = []
    selectedAnswerIndex.value = -1
    ElMessage.success('新任务已创建')
  })
}

// 显示历史记录
const showHistory = () => {
  ElMessage.info('历史记录功能开发中...')
}

// 启动协作
const startCollaboration = async () => {
  if (!currentQuestion.value.trim()) {
    ElMessage.warning('请输入复杂问题')
    return
  }

  processing.value = true
  collaborationSteps.value = []
  answers.value = []

  try {
    // 模拟多智能体协作过程
    await simulateCollaboration()
    ElMessage.success('协作完成，已生成多个答案')
  } catch (error) {
    ElMessage.error('协作失败，请重试')
  } finally {
    processing.value = false
  }
}

// 模拟协作过程
const simulateCollaboration = async () => {
  const now = new Date()

  // 阶段1：问题分析
  await delay(600)
  collaborationSteps.value.push({
    time: formatTime(new Date(now.getTime() + 600)),
    agentId: 1,
    type: 'primary',
    title: '🔍 问题分析',
    description: '多智能体联合分析问题：如何优化直升机在高空高温环境下的发动机性能？',
    result: '识别关键问题：热效率下降、材料老化加速、冷却系统不足'
  })

  // 阶段2：生成素材
  await delay(600)
  collaborationSteps.value.push({
    time: formatTime(new Date(now.getTime() + 1200)),
    agentId: 1,
    type: 'success',
    title: '📚 生成素材',
    description: '发动机智能体检索技术文档、设计规范、历史数据',
    result: '生成素材12条：涡轮叶片材料报告、冷却系统设计图、热力学模型等'
  })

  // 阶段3：素材评价
  await delay(600)
  collaborationSteps.value.push({
    time: formatTime(new Date(now.getTime() + 1800)),
    agentId: 4,
    type: 'warning',
    title: '⭐ 素材评价',
    description: '监控智能体评估素材质量和相关性',
    result: '素材评分：技术文档90分、设计规范85分、实验数据88分'
  })

  // 阶段4：推理分析
  await delay(800)
  collaborationSteps.value.push({
    time: formatTime(new Date(now.getTime() + 2600)),
    agentId: 1,
    type: 'info',
    title: '💡 推理分析',
    description: '发动机智能体基于素材进行深度推理分析',
    result: '分析结论：需优化涡轮叶片材料和冷却系统设计'
  })

  // 结构智能体介入
  await delay(600)
  collaborationSteps.value.push({
    time: formatTime(new Date(now.getTime() + 3200)),
    agentId: 5,
    type: 'primary',
    title: '💡 推理分析',
    description: '结构智能体分析机身结构和热传导问题',
    result: '结构优化：采用新型耐高温复合材料，优化散热设计'
  })

  // 驾驶智能体介入
  await delay(600)
  collaborationSteps.value.push({
    time: formatTime(new Date(now.getTime() + 3800)),
    agentId: 2,
    type: 'success',
    title: '💡 推理分析',
    description: '驾驶智能体评估人机工程和环境控制',
    result: '驾驶舱优化：增强空调系统，改进隔热设计'
  })

  // 阶段5：结果验证
  await delay(600)
  collaborationSteps.value.push({
    time: formatTime(new Date(now.getTime() + 4400)),
    agentId: 0,
    type: 'warning',
    title: '✅ 结果验证',
    description: '多智能体交叉验证分析结果',
    result: '验证通过：发动机效率提升15%，结构强度符合标准，驾驶环境改善'
  })

  // 阶段6：最终生成
  await delay(800)
  collaborationSteps.value.push({
    time: formatTime(new Date(now.getTime() + 5200)),
    agentId: 0,
    type: 'primary',
    title: '🎯 最终生成',
    description: '综合所有智能体分析结果，生成最终解决方案',
    result: '形成多方案：1）材料优化方案；2）系统改进方案；3）综合集成方案'
  })

  collaborationAgentCount.value = 3

  // 生成多个答案
  await delay(600)
  answers.value = [
    {
      agent: '发动机智能体',
      confidence: 85,
      completeness: 90,
      innovation: 75,
      practicality: 88,
      content: '建议采用陶瓷基复合材料制造涡轮叶片，配合主动冷却系统，可提升高温环境下的发动机效率约15%。同时优化进气道设计，改善高温条件下的气流组织。',
      time: '10:30'
    },
    {
      agent: '多智能体协作',
      confidence: 92,
      completeness: 95,
      innovation: 85,
      practicality: 90,
      content: '综合发动机、结构、驾驶、仪表四部门方案：1）采用新型耐高温材料；2）优化机身隔热设计；3）增强驾驶舱环境控制；4）升级监控报警系统。预计整体性能提升20%。',
      time: '10:35'
    },
    {
      agent: '结构智能体',
      confidence: 78,
      completeness: 82,
      innovation: 90,
      practicality: 75,
      content: '建议在关键结构部位采用热障涂层技术，减少高温传递。同时优化机身通风设计，增强自然散热效果。此方案可大幅降低制造成本。',
      time: '10:40'
    }
  ]

  bestAnswerIndex.value = 1
  selectedAnswerIndex.value = 1
}

// 查找素材
const findMaterials = () => {
  if (!currentQuestion.value.trim()) {
    ElMessage.warning('请先输入问题')
    return
  }
  ElMessage.info('正在查找相关技术文档和研发数据...')
  setTimeout(() => {
    ElMessage.success(`找到 15 条相关素材，包括：发动机性能报告、材料测试数据、设计规范等`)
  }, 1500)
}

// 生成更多答案
const generateMoreAnswers = () => {
  ElMessage.info('正在调用更多智能体生成答案...')
  setTimeout(() => {
    const newAnswer = {
      agent: '通信智能体',
      confidence: 80,
      completeness: 85,
      innovation: 88,
      practicality: 82,
      content: '建议在高温环境下优化通信系统的散热设计，采用耐高温电子元件。同时增强数据链的抗干扰能力，确保极端条件下的通信可靠性。',
      time: formatTime(new Date())
    }
    answers.value.push(newAnswer)
    ElMessage.success('已生成新的答案')
  }, 1000)
}

// 选择答案
const selectAnswer = (index: number) => {
  selectedAnswerIndex.value = index
}

// 获取智能体名称
const getAgentName = (agentId: number) => {
  const agent = agentDepartments.value.find(a => a.id === agentId)
  return agent ? agent.name : '协作中心'
}

// 获取智能体类型标签颜色
const getAgentType = (agentId: number) => {
  const colors: Record<number, string> = {
    1: 'danger',
    2: 'success',
    3: 'warning',
    4: 'info',
    5: 'primary',
    6: ''
  }
  return colors[agentId] || ''
}

// 获取答案置信度类型
const getAnswerConfidenceType = (confidence: number) => {
  if (confidence >= 90) return 'success'
  if (confidence >= 80) return 'warning'
  return 'info'
}

// 提交验证
const submitValidation = () => {
  if (!validationForm.value.validator) {
    ElMessage.warning('请输入验证人员姓名')
    return
  }
  ElMessage.success('验证意见已提交')
}

// 重置验证
const resetValidation = () => {
  validationForm.value = {
    validator: '',
    status: 'review',
    comment: '',
    rating: 0
  }
}

// 保存答案
const saveAnswer = () => {
  if (!publishForm.value.title) {
    ElMessage.warning('请输入保存标题')
    return
  }
  ElMessage.success(`答案已保存：${publishForm.value.title}`)
}

// 发布答案
const publishAnswer = () => {
  if (!publishForm.value.title) {
    ElMessage.warning('请输入保存标题')
    return
  }
  if (publishForm.value.scope.length === 0) {
    ElMessage.warning('请选择发布范围')
    return
  }
  ElMessageBox.confirm('确定要发布此答案吗？发布后将无法撤回。', '确认发布', {
    confirmButtonText: '发布',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('答案已发布成功')
  })
}

// 导出报告
const exportReport = () => {
  ElMessage.info('正在生成报告...')
  setTimeout(() => {
    ElMessage.success('报告已导出到本地')
  }, 2000)
}

// 延迟函数
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

// 格式化时间
const formatTime = (date: Date) => {
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
.agent-collaboration {
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
  grid-template-columns: 280px 1fr 320px;
  gap: 20px;
}

/* 左侧面板 */
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

/* 智能体列表 */
.agents-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.agent-item {
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

.agent-item:hover {
  background: #e5e7eb;
  transform: translateX(4px);
}

.agent-item.active {
  border-color: #409eff;
  background: #ecf5ff;
}

.agent-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.agent-info {
  flex: 1;
}

.agent-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.agent-department {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

/* 任务输入区 */
.task-input-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.question-input {
  margin-bottom: 16px;
}

.input-actions {
  display: flex;
  gap: 12px;
}

/* 协作过程 */
.collaboration-process {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.process-timeline {
  max-height: 400px;
  overflow-y: auto;
}

.step-content {
  padding: 8px;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.step-title {
  font-weight: 600;
  color: #303133;
}

.step-description {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
  line-height: 1.6;
}

.step-result {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px;
  background: #f0f9ff;
  border-radius: 4px;
  font-size: 12px;
  color: #409eff;
}

/* 答案区 */
.answers-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.answers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 12px;
}

.answer-card {
  padding: 12px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.answer-card:hover {
  border-color: #409eff;
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.answer-card.selected {
  border-color: #409eff;
  background: #ecf5ff;
}

.answer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.answer-title {
  font-weight: 600;
  color: #303133;
}

.answer-content {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 8px;
  max-height: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.answer-footer {
  display: flex;
  gap: 6px;
}

/* 对比、评价、验证、发布区 */
.comparison-section,
.evaluation-section,
.validation-section,
.publish-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
}

/* 评价卡片 */
.evaluation-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.eval-card {
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  text-align: center;
}

.eval-title {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.eval-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.eval-reason {
  font-size: 11px;
  color: #606266;
}
</style>
