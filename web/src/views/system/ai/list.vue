<template>
  <div class="agent-list-container">
    <!-- 头部区域 -->
    <div class="page-header">
      <h1 class="page-title">智能体中心</h1>
      <p class="page-subtitle">探索AI智能体，让工作更高效</p>
    </div>

    <!-- 搜索栏 -->
    <div class="search-section">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索智能体名称或功能描述..."
        prefix-icon="Search"
        size="large"
        clearable
        class="search-input"
        @input="handleSearch"
      >
        <template #append>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
        </template>
      </el-input>
    </div>

    <!-- 分类标签 -->
    <div class="category-section">
      <el-tabs v-model="activeCategory" @tab-change="handleCategoryChange" class="category-tabs">
        <el-tab-pane label="全部" name="all"></el-tab-pane>
        <el-tab-pane label="研发助手" name="writing"></el-tab-pane>
        <el-tab-pane label="文档助手" name="coding"></el-tab-pane>
        <el-tab-pane label="研发卖家" name="learning"></el-tab-pane>
        <el-tab-pane label="行业知识" name="life"></el-tab-pane>
        <el-tab-pane label="图书馆" name="business"></el-tab-pane>
        <el-tab-pane label="创意设计" name="creative"></el-tab-pane>
      </el-tabs>
    </div>

    <!-- 统计信息 -->
    <div class="stats-section">
      <el-alert :title="`共找到 ${filteredAgents.length} 个智能体`" type="info" :closable="false" />
    </div>

    <!-- 智能体列表 -->
    <div class="agent-list" v-loading="loading">
      <el-row :gutter="20" class="agent-grid">
        <el-col
          v-for="agent in filteredAgents"
          :key="agent.id"
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
          :xl="6"
          class="agent-col"
        >
          <el-card class="agent-card" shadow="hover" @click="openAgentDetail(agent)">
            <div class="agent-header">
              <div class="agent-icon" :style="{ background: agent.iconBg }">
                {{ agent.icon }}
              </div>
              <div class="agent-badge" v-if="agent.isHot">
                <el-tag size="small" type="danger">热门</el-tag>
              </div>
            </div>
            <div class="agent-body">
              <h3 class="agent-name">{{ agent.name }}</h3>
              <p class="agent-description">{{ agent.description }}</p>
              <div class="agent-tags">
                <el-tag
                  v-for="tag in agent.tags"
                  :key="tag"
                  size="small"
                  type="info"
                  class="agent-tag"
                >
                  {{ tag }}
                </el-tag>
              </div>
              <div class="agent-stats">
                <span class="stat-item">
                  <el-icon><User /></el-icon>
                  {{ formatNumber(agent.usageCount) }}
                </span>
                <span class="stat-item">
                  <el-icon><Star /></el-icon>
                  {{ agent.rating }}
                </span>
              </div>
            </div>
            <div class="agent-footer">
              <el-button type="primary" size="small" @click.stop="useAgent(agent)">
                立即使用
              </el-button>
              <el-button size="small" @click.stop="toggleFavorite(agent)">
                <el-icon v-if="agent.isFavorite"><StarFilled /></el-icon>
                <el-icon v-else><Star /></el-icon>
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 空状态 -->
      <el-empty
        v-if="filteredAgents.length === 0 && !loading"
        description="没有找到匹配的智能体"
        class="empty-state"
      >
        <el-button type="primary" @click="resetSearch">重置筛选</el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, User, Star, StarFilled } from '@element-plus/icons-vue'

// 智能体类型
interface Agent {
  id: string
  name: string
  description: string
  icon: string
  iconBg: string
  category: string
  tags: string[]
  usageCount: number
  rating: number
  isHot: boolean
  isFavorite: boolean
}

// 搜索关键词
const searchKeyword = ref('')

// 当前分类
const activeCategory = ref('all')

// 加载状态
const loading = ref(false)

// 智能体数据
const agents = ref<Agent[]>([])

// 分类映射
const categoryMap: { [key: string]: string } = {
  all: '全部',
  writing: '写作助手',
  coding: '编程开发',
  learning: '学习辅导',
  life: '生活服务',
  business: '商业分析',
  creative: '创意设计'
}

// 初始化智能体数据
const initAgents = () => {
  agents.value = [
    // 写作助手
    
    
    {
      id: '1',
      name: '直升所默认',
      description: '专业的单位文档和直升机理论知识',
      icon: '✍️',
      iconBg: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      category: 'writing',
      tags: ['营销', '文案', '广告'],
      usageCount: 12580,
      rating: 4.8,
      isHot: true,
      isFavorite: false
    },
    {
      id: '2',
      name: '直升机文档编写',
      description: '专业的单位文档和直升机理论知识,编写各类直升机文档',
      icon: '📝',
      iconBg: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      category: 'writing',
      tags: ['润色', '编辑', '校对'],
      usageCount: 8920,
      rating: 4.6,
      isHot: false,
      isFavorite: false
    },
    {
      id: '3',
      name: '直升机研发大全',
      description: '顶级直升机理论专家',
      icon: '📧',
      iconBg: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      category: 'writing',
      tags: ['邮件', '商务', '沟通'],
      usageCount: 6750,
      rating: 4.7,
      isHot: false,
      isFavorite: false
    },

    // 编程开发
    {
      id: '4',
      name: '发动机专业',
      description: '直升机发动机各类理论知识',
      icon: '💻',
      iconBg: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
      category: 'coding',
      tags: ['代码', '开发', '多语言'],
      usageCount: 18920,
      rating: 4.9,
      isHot: true,
      isFavorite: false
    },
    {
      id: '5',
      name: 'PPT生成',
      description: '直升所与直升机PPT生成',
      icon: '🔍',
      iconBg: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
      category: 'coding',
      tags: ['调试', '修复', '优化'],
      usageCount: 11200,
      rating: 4.7,
      isHot: false,
      isFavorite: false
    },
    {
      id: '6',
      name: '直升所翻译',
      description: '直升所专业翻译',
      icon: '📋',
      iconBg: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
      category: 'coding',
      tags: ['审查', '质量', '规范'],
      usageCount: 7340,
      rating: 4.5,
      isHot: false,
      isFavorite: false
    },

    // 学习辅导
    {
      id: '7',
      name: '飞行动力学卖家',
      description: '飞行动力学理论知识库',
      icon: '🗣️',
      iconBg: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
      category: 'learning',
      tags: ['英语', '口语', '发音'],
      usageCount: 15600,
      rating: 4.8,
      isHot: true,
      isFavorite: false
    },
    {
      id: '8',
      name: '图书馆',
      description: '直升所专业图书馆',
      icon: '🔢',
      iconBg: 'linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%)',
      category: 'learning',
      tags: ['数学', '解题', '步骤'],
      usageCount: 9870,
      rating: 4.6,
      isHot: false,
      isFavorite: false
    },
    {
      id: '9',
      name: '历史知识库',
      description: '探索历史事件、人物传记、历史文化等知识',
      icon: '📚',
      iconBg: 'linear-gradient(135deg, #d299c2 0%, #fef9d7 100%)',
      category: 'learning',
      tags: ['历史', '知识', '文化'],
      usageCount: 5430,
      rating: 4.4,
      isHot: false,
      isFavorite: false
    },

    // 生活服务
    {
      id: '10',
      name: '健康咨询',
      description: '提供健康建议、营养搭配、运动指导等服务',
      icon: '🏥',
      iconBg: 'linear-gradient(135deg, #96fbc4 0%, #f9f586 100%)',
      category: 'life',
      tags: ['健康', '营养', '运动'],
      usageCount: 13450,
      rating: 4.7,
      isHot: false,
      isFavorite: false
    },
    {
      id: '11',
      name: '旅行规划师',
      description: '智能规划旅行路线、推荐景点、制定行程安排',
      icon: '✈️',
      iconBg: 'linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)',
      category: 'life',
      tags: ['旅行', '规划', '景点'],
      usageCount: 11200,
      rating: 4.8,
      isHot: false,
      isFavorite: false
    },
    {
      id: '12',
      name: '美食推荐',
      description: '根据口味推荐美食、提供烹饪方法和食谱',
      icon: '🍽️',
      iconBg: 'linear-gradient(135deg, #f6d365 0%, #fda085 100%)',
      category: 'life',
      tags: ['美食', '食谱', '烹饪'],
      usageCount: 8760,
      rating: 4.5,
      isHot: false,
      isFavorite: false
    },

    // 商业分析
    {
      id: '13',
      name: '数据分析助手',
      description: '分析业务数据、生成报表、提供数据洞察',
      icon: '📊',
      iconBg: 'linear-gradient(135deg, #5ee7df 0%, #b490ca 100%)',
      category: 'business',
      tags: ['数据', '分析', '报表'],
      usageCount: 14500,
      rating: 4.8,
      isHot: true,
      isFavorite: false
    },
    {
      id: '14',
      name: '市场调研',
      description: '进行市场分析、竞品研究、趋势预测',
      icon: '📈',
      iconBg: 'linear-gradient(135deg, #c471ed 0%, #f64f59 100%)',
      category: 'business',
      tags: ['市场', '调研', '竞品'],
      usageCount: 9230,
      rating: 4.6,
      isHot: false,
      isFavorite: false
    },
    {
      id: '15',
      name: '财务顾问',
      description: '提供财务规划、投资建议、风险评估',
      icon: '💰',
      iconBg: 'linear-gradient(135deg, #2af598 0%, #009efd 100%)',
      category: 'business',
      tags: ['财务', '投资', '规划'],
      usageCount: 7890,
      rating: 4.5,
      isHot: false,
      isFavorite: false
    },

    // 创意设计
    {
      id: '16',
      name: '创意构思',
      description: '激发创意灵感、头脑风暴、提供设计思路',
      icon: '💡',
      iconBg: 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)',
      category: 'creative',
      tags: ['创意', '灵感', '设计'],
      usageCount: 10200,
      rating: 4.7,
      isHot: false,
      isFavorite: false
    },
    {
      id: '17',
      name: '配色方案',
      description: '提供配色建议、色彩搭配、设计风格指导',
      icon: '🎨',
      iconBg: 'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)',
      category: 'creative',
      tags: ['配色', '色彩', '设计'],
      usageCount: 6540,
      rating: 4.4,
      isHot: false,
      isFavorite: false
    },
    {
      id: '18',
      name: 'Logo设计',
      description: 'Logo设计创意、品牌标识建议、视觉方案',
      icon: '🔮',
      iconBg: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
      category: 'creative',
      tags: ['Logo', '品牌', '视觉'],
      usageCount: 8120,
      rating: 4.6,
      isHot: false,
      isFavorite: false
    }
  ]
}

// 过滤后的智能体列表
const filteredAgents = computed(() => {
  let result = agents.value

  // 按分类过滤
  if (activeCategory.value !== 'all') {
    result = result.filter(agent => agent.category === activeCategory.value)
  }

  // 按关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(agent =>
      agent.name.toLowerCase().includes(keyword) ||
      agent.description.toLowerCase().includes(keyword) ||
      agent.tags.some(tag => tag.toLowerCase().includes(keyword))
    )
  }

  return result
})

// 格式化数字
const formatNumber = (num: number): string => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + 'w'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num.toString()
}

// 处理搜索
const handleSearch = () => {
  // 触发计算属性重新计算
}

// 处理分类切换
const handleCategoryChange = (category: string) => {
  activeCategory.value = category
}

// 打开智能体详情
const openAgentDetail = (agent: Agent) => {
  ElMessage.info(`查看智能体: ${agent.name}`)
}

// 使用智能体
const useAgent = (agent: Agent) => {
  ElMessage.success(`正在启动 ${agent.name}...`)
}

// 切换收藏
const toggleFavorite = (agent: Agent) => {
  agent.isFavorite = !agent.isFavorite
  if (agent.isFavorite) {
    ElMessage.success(`已收藏 ${agent.name}`)
  } else {
    ElMessage.info(`已取消收藏 ${agent.name}`)
  }
}

// 重置搜索
const resetSearch = () => {
  searchKeyword.value = ''
  activeCategory.value = 'all'
}

// 页面加载
onMounted(() => {
  loading.value = true
  // 模拟加载延迟
  setTimeout(() => {
    initAgents()
    loading.value = false
  }, 500)
})
</script>

<style scoped>
.agent-list-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 24px;
}

/* 头部区域 */
.page-header {
  text-align: center;
  margin-bottom: 32px;
}

.page-title {
  font-size: 36px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px 0;
}

.page-subtitle {
  font-size: 16px;
  color: #909399;
  margin: 0;
}

/* 搜索区域 */
.search-section {
  max-width: 800px;
  margin: 0 auto 32px;
}

.search-input {
  border-radius: 24px;
}

:deep(.search-input .el-input__wrapper) {
  border-radius: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

:deep(.search-input .el-input-group__append) {
  border-radius: 0 24px 24px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: transparent;
  color: white;
}

/* 分类标签 */
.category-section {
  max-width: 1200px;
  margin: 0 auto 24px;
  background: white;
  border-radius: 12px;
  padding: 0 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

:deep(.category-tabs .el-tabs__header) {
  margin: 0;
}

:deep(.category-tabs .el-tabs__nav-wrap::after) {
  display: none;
}

/* 统计信息 */
.stats-section {
  max-width: 1200px;
  margin: 0 auto 24px;
}

/* 智能体列表 */
.agent-list {
  max-width: 1200px;
  margin: 0 auto;
}

.agent-grid {
  margin: 0 !important;
}

.agent-col {
  margin-bottom: 20px;
}

.agent-card {
  height: 100%;
  border-radius: 16px;
  transition: all 0.3s ease;
  cursor: pointer;
  border: none;
}

.agent-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

/* 卡片头部 */
.agent-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.agent-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.agent-badge {
  margin-left: auto;
}

/* 卡片主体 */
.agent-body {
  margin-bottom: 16px;
}

.agent-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.agent-description {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin: 0 0 12px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  height: 44px;
}

.agent-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.agent-tag {
  border-radius: 12px;
  padding: 2px 8px;
}

.agent-stats {
  display: flex;
  gap: 16px;
  color: #909399;
  font-size: 13px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 卡片底部 */
.agent-footer {
  display: flex;
  gap: 8px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.agent-footer .el-button {
  flex: 1;
}

/* 空状态 */
.empty-state {
  padding: 80px 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .agent-list-container {
    padding: 16px;
  }

  .page-title {
    font-size: 28px;
  }

  .search-section {
    margin-bottom: 24px;
  }

  .category-section {
    overflow-x: auto;
    padding: 0 16px;
  }
}
</style>
