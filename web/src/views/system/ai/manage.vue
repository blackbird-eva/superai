<template>
  <div class="agent-manage-container">
    <!-- 头部区域 -->
    <div class="page-header">
      <h1 class="page-title">智能体管理</h1>
      <p class="page-subtitle">管理和配置AI智能体资源</p>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="action-left">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索智能体名称..."
          prefix-icon="Search"
          clearable
          class="search-input"
          style="width: 300px"
          @input="handleSearch"
        />
        <el-select
          v-model="filterCategory"
          placeholder="选择分类"
          clearable
          class="filter-select"
          @change="handleFilter"
        >
          <el-option label="全部" value=""></el-option>
          <el-option label="写作助手" value="writing"></el-option>
          <el-option label="编程开发" value="coding"></el-option>
          <el-option label="学习辅导" value="learning"></el-option>
          <el-option label="生活服务" value="life"></el-option>
          <el-option label="商业分析" value="business"></el-option>
          <el-option label="创意设计" value="creative"></el-option>
        </el-select>
        <el-select
          v-model="filterStatus"
          placeholder="状态筛选"
          clearable
          class="filter-select"
          @change="handleFilter"
        >
          <el-option label="全部" value=""></el-option>
          <el-option label="启用" value="enabled"></el-option>
          <el-option label="禁用" value="disabled"></el-option>
        </el-select>
      </div>
      <div class="action-right">
        <el-button type="primary" icon="Plus" @click="openAddDialog">添加智能体</el-button>
        <el-button icon="Refresh" @click="refreshData">刷新</el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">总数</div>
        </div>
        <el-icon class="stat-icon" color="#409eff"><Grid /></el-icon>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-value">{{ stats.enabled }}</div>
          <div class="stat-label">启用</div>
        </div>
        <el-icon class="stat-icon" color="#67c23a"><CircleCheck /></el-icon>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-value">{{ stats.disabled }}</div>
          <div class="stat-label">禁用</div>
        </div>
        <el-icon class="stat-icon" color="#f56c6c"><CircleClose /></el-icon>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-value">{{ stats.hot }}</div>
          <div class="stat-label">热门</div>
        </div>
        <el-icon class="stat-icon" color="#e6a23c"><Star /></el-icon>
      </el-card>
    </div>

    <!-- 智能体表格 -->
    <el-card class="table-card" v-loading="loading">
      <el-table :data="filteredAgents" stripe style="width: 100%">
        <el-table-column type="index" label="序号" width="60" align="center"></el-table-column>
        <el-table-column label="图标" width="80" align="center">
          <template #default="{ row }">
            <div class="table-icon" :style="{ background: row.iconBg }">
              {{ row.icon }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" min-width="150"></el-table-column>
        <el-table-column prop="description" label="简介" min-width="200" show-overflow-tooltip></el-table-column>
        <el-table-column label="分类" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ categoryMap[row.category] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="标签" width="200">
          <template #default="{ row }">
            <el-tag
              v-for="tag in row.tags"
              :key="tag"
              size="small"
              type="info"
              class="table-tag"
            >
              {{ tag }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="使用量" width="100" align="right">
          <template #default="{ row }">
            {{ formatNumber(row.usageCount) }}
          </template>
        </el-table-column>
        <el-table-column label="评分" width="100" align="center">
          <template #default="{ row }">
            <el-rate
              v-model="row.rating"
              disabled
              show-score
              text-color="#ff9900"
              score-template="{value}"
            ></el-rate>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-switch
              v-model="row.status"
              active-value="enabled"
              inactive-value="disabled"
              @change="handleStatusChange(row)"
            ></el-switch>
          </template>
        </el-table-column>
        <el-table-column label="热门" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.isHot" type="danger" size="small">热门</el-tag>
            <el-tag v-else type="info" size="small">普通</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link icon="Edit" @click="openEditDialog(row)">
              编辑
            </el-button>
            <el-button type="success" link icon="Star" @click="toggleHot(row)">
              {{ row.isHot ? '取消热门' : '设为热门' }}
            </el-button>
            <el-button type="danger" link icon="Delete" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <el-empty
        v-if="filteredAgents.length === 0 && !loading"
        description="没有找到匹配的智能体"
      >
        <el-button type="primary" @click="resetFilters">重置筛选</el-button>
      </el-empty>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'add' ? '添加智能体' : '编辑智能体'"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
        class="agent-form"
      >
        <el-form-item label="名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入智能体名称" maxlength="50" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="formData.category" placeholder="请选择分类" style="width: 100%">
            <el-option label="写作助手" value="writing"></el-option>
            <el-option label="编程开发" value="coding"></el-option>
            <el-option label="学习辅导" value="learning"></el-option>
            <el-option label="生活服务" value="life"></el-option>
            <el-option label="商业分析" value="business"></el-option>
            <el-option label="创意设计" value="creative"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="简介" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入智能体简介"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="图标" prop="icon">
          <el-input v-model="formData.icon" placeholder="请输入 emoji 图标" maxlength="2">
            <template #append>
              <el-button @click="openIconPicker">选择</el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="图标背景" prop="iconBg">
          <el-select v-model="formData.iconBg" placeholder="请选择背景" style="width: 100%">
            <el-option
              v-for="bg in iconBgs"
              :key="bg.value"
              :label="bg.label"
              :value="bg.value"
            >
              <div class="bg-option">
                <div class="bg-preview" :style="{ background: bg.value }"></div>
                <span>{{ bg.label }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="标签">
          <el-select
            v-model="formData.tags"
            multiple
            filterable
            allow-create
            placeholder="请输入或选择标签"
            style="width: 100%"
          >
            <el-option
              v-for="tag in availableTags"
              :key="tag"
              :label="tag"
              :value="tag"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="使用量">
          <el-input-number v-model="formData.usageCount" :min="0" :max="999999" />
        </el-form-item>
        <el-form-item label="评分">
          <el-rate v-model="formData.rating" allow-half />
        </el-form-item>
        <el-form-item label="热门">
          <el-switch v-model="formData.isHot" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="formData.status"
            active-value="enabled"
            inactive-value="disabled"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 图标选择器 -->
    <el-dialog v-model="iconPickerVisible" title="选择图标" width="500px">
      <div class="icon-grid">
        <div
          v-for="icon in emojiList"
          :key="icon"
          class="icon-item"
          :class="{ selected: selectedIcon === icon }"
          @click="selectIcon(icon)"
        >
          {{ icon }}
        </div>
      </div>
      <template #footer>
        <el-button @click="iconPickerVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmIcon">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  Search, Plus, Refresh, Edit, Delete, Star, Grid,
  CircleCheck, CircleClose
} from '@element-plus/icons-vue'

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
  status: 'enabled' | 'disabled'
}

// 搜索关键词
const searchKeyword = ref('')

// 分类筛选
const filterCategory = ref('')

// 状态筛选
const filterStatus = ref('')

// 加载状态
const loading = ref(false)

// 对话框显示状态
const dialogVisible = ref(false)

// 对话框模式：add-添加，edit-编辑
const dialogMode = ref<'add' | 'edit'>('add')

// 提交状态
const submitting = ref(false)

// 图标选择器显示状态
const iconPickerVisible = ref(false)

// 临时选中的图标
const selectedIcon = ref('')

// 表单引用
const formRef = ref<FormInstance>()

// 智能体数据
const agents = ref<Agent[]>([])

// 删除的智能体（用于总数不变）
const deletedAgents = ref<Agent[]>([])

// 分类映射
const categoryMap: { [key: string]: string } = {
  writing: '写作助手',
  coding: '编程开发',
  learning: '学习辅导',
  life: '生活服务',
  business: '商业分析',
  creative: '创意设计'
}

// 图标背景选项
const iconBgs = [
  { label: '紫色渐变', value: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
  { label: '粉色渐变', value: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
  { label: '蓝色渐变', value: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' },
  { label: '橙色渐变', value: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' },
  { label: '青色渐变', value: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)' },
  { label: '绿色渐变', value: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)' },
  { label: '暖色渐变', value: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)' },
  { label: '天蓝渐变', value: 'linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%)' },
  { label: '紫色粉色', value: 'linear-gradient(135deg, #d299c2 0%, #fef9d7 100%)' },
  { label: '绿黄渐变', value: 'linear-gradient(135deg, #96fbc4 0%, #f9f586 100%)' },
  { label: '青绿渐变', value: 'linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)' },
  { label: '黄橙渐变', value: 'linear-gradient(135deg, #f6d365 0%, #fda085 100%)' }
]

// 可用标签
const availableTags = [
  '营销', '文案', '广告', '润色', '编辑', '校对', '邮件', '商务', '沟通',
  '代码', '开发', '多语言', '调试', '修复', '优化', '审查', '质量', '规范',
  '英语', '口语', '发音', '数学', '解题', '步骤', '历史', '知识', '文化',
  '健康', '营养', '运动', '旅行', '规划', '景点', '美食', '食谱', '烹饪',
  '数据', '分析', '报表', '市场', '调研', '竞品', '财务', '投资', '规划',
  '创意', '灵感', '设计', '配色', '色彩', 'Logo', '品牌', '视觉'
]

// Emoji 列表
const emojiList = [
  '✍️', '📝', '📧', '💻', '🔍', '📋', '🗣️', '🔢', '📚', '🏥',
  '✈️', '🍽️', '📊', '📈', '💰', '💡', '🎨', '🔮', '🤖', '🚀',
  '⚡', '🔥', '💎', '🎯', '📱', '🌟', '🎪', '🎭', '🎬', '📸'
]

// 表单数据
const formData = reactive<Partial<Agent>>({
  name: '',
  description: '',
  icon: '🤖',
  iconBg: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  category: '',
  tags: [],
  usageCount: 0,
  rating: 4.5,
  isHot: false,
  status: 'enabled'
})

// 表单验证规则
const formRules: FormRules = {
  name: [
    { required: true, message: '请输入智能体名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请输入智能体简介', trigger: 'blur' },
    { min: 10, max: 200, message: '长度在 10 到 200 个字符', trigger: 'blur' }
  ],
  icon: [
    { required: true, message: '请选择图标', trigger: 'change' }
  ],
  iconBg: [
    { required: true, message: '请选择图标背景', trigger: 'change' }
  ]
}

// 统计数据
const stats = computed(() => {
  const allAgents = [...agents.value, ...deletedAgents.value]
  return {
    total: allAgents.length,
    enabled: allAgents.filter(a => a.status === 'enabled').length,
    disabled: allAgents.filter(a => a.status === 'disabled').length,
    hot: allAgents.filter(a => a.isHot).length
  }
})

// 过滤后的智能体列表
const filteredAgents = computed(() => {
  let result = agents.value

  // 按分类过滤
  if (filterCategory.value) {
    result = result.filter(agent => agent.category === filterCategory.value)
  }

  // 按状态过滤
  if (filterStatus.value) {
    result = result.filter(agent => agent.status === filterStatus.value)
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

// 初始化智能体数据
const initAgents = () => {
  agents.value = [
    {
      id: '1',
      name: '文案生成器',
      description: '快速生成营销文案、广告语、产品介绍等，提升写作效率',
      icon: '✍️',
      iconBg: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      category: 'writing',
      tags: ['营销', '文案', '广告'],
      usageCount: 12580,
      rating: 4.8,
      isHot: true,
      status: 'enabled'
    },
    {
      id: '2',
      name: '文章润色助手',
      description: '优化文章表达、调整语言风格、修正语法错误',
      icon: '📝',
      iconBg: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      category: 'writing',
      tags: ['润色', '编辑', '校对'],
      usageCount: 8920,
      rating: 4.6,
      isHot: false,
      status: 'enabled'
    },
    {
      id: '3',
      name: '邮件撰写专家',
      description: '专业撰写商务邮件、求职信、通知等各类邮件',
      icon: '📧',
      iconBg: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      category: 'writing',
      tags: ['邮件', '商务', '沟通'],
      usageCount: 6750,
      rating: 4.7,
      isHot: false,
      status: 'enabled'
    },
    {
      id: '4',
      name: '代码生成器',
      description: '根据需求自动生成代码片段，支持多种编程语言',
      icon: '💻',
      iconBg: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
      category: 'coding',
      tags: ['代码', '开发', '多语言'],
      usageCount: 18920,
      rating: 4.9,
      isHot: true,
      status: 'enabled'
    },
    {
      id: '5',
      name: 'Bug调试助手',
      description: '快速定位和修复代码bug，提供解决方案建议',
      icon: '🔍',
      iconBg: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
      category: 'coding',
      tags: ['调试', '修复', '优化'],
      usageCount: 11200,
      rating: 4.7,
      isHot: false,
      status: 'enabled'
    },
    {
      id: '6',
      name: '代码审查专家',
      description: '进行代码质量检查，提供优化建议和最佳实践',
      icon: '📋',
      iconBg: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
      category: 'coding',
      tags: ['审查', '质量', '规范'],
      usageCount: 7340,
      rating: 4.5,
      isHot: false,
      status: 'enabled'
    },
    {
      id: '7',
      name: '英语口语教练',
      description: '提升英语口语水平，提供发音纠正和对话练习',
      icon: '🗣️',
      iconBg: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
      category: 'learning',
      tags: ['英语', '口语', '发音'],
      usageCount: 15600,
      rating: 4.8,
      isHot: true,
      status: 'enabled'
    },
    {
      id: '8',
      name: '数学解题助手',
      description: '解答数学问题，提供详细解题步骤和方法',
      icon: '🔢',
      iconBg: 'linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%)',
      category: 'learning',
      tags: ['数学', '解题', '步骤'],
      usageCount: 9870,
      rating: 4.6,
      isHot: false,
      status: 'enabled'
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
      status: 'enabled'
    },
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
      status: 'enabled'
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
      status: 'enabled'
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
      status: 'enabled'
    },
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
      status: 'enabled'
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
      status: 'enabled'
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
      status: 'enabled'
    },
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
      status: 'enabled'
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
      status: 'enabled'
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
      status: 'enabled'
    }
  ]
}

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

// 处理筛选
const handleFilter = () => {
  // 触发计算属性重新计算
}

// 重置筛选
const resetFilters = () => {
  searchKeyword.value = ''
  filterCategory.value = ''
  filterStatus.value = ''
}

// 刷新数据
const refreshData = () => {
  loading.value = true
  setTimeout(() => {
    initAgents()
    loading.value = false
    ElMessage.success('数据已刷新')
  }, 500)
}

// 打开添加对话框
const openAddDialog = () => {
  dialogMode.value = 'add'
  dialogVisible.value = true
}

// 打开编辑对话框
const openEditDialog = (agent: Agent) => {
  dialogMode.value = 'edit'
  Object.assign(formData, agent)
  dialogVisible.value = true
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  Object.assign(formData, {
    name: '',
    description: '',
    icon: '🤖',
    iconBg: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    category: '',
    tags: [],
    usageCount: 0,
    rating: 4.5,
    isHot: false,
    status: 'enabled'
  })
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    submitting.value = true

    // 模拟网络请求
    await new Promise(resolve => setTimeout(resolve, 500))

    if (dialogMode.value === 'add') {
      // 添加智能体
      const newAgent: Agent = {
        id: Date.now().toString(),
        name: formData.name || '',
        description: formData.description || '',
        icon: formData.icon || '🤖',
        iconBg: formData.iconBg || 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        category: formData.category || '',
        tags: formData.tags || [],
        usageCount: formData.usageCount || 0,
        rating: formData.rating || 4.5,
        isHot: formData.isHot || false,
        status: formData.status || 'enabled'
      }
      agents.value.unshift(newAgent)
      ElMessage.success('添加成功')
    } else {
      // 编辑智能体
      const index = agents.value.findIndex(a => a.id === formData.id)
      if (index !== -1) {
        Object.assign(agents.value[index], formData)
        ElMessage.success('编辑成功')
      }
    }

    dialogVisible.value = false
    resetForm()
  } catch (error) {
    console.error('表单验证失败:', error)
  } finally {
    submitting.value = false
  }
}

// 删除智能体
const handleDelete = async (agent: Agent) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除智能体 "${agent.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 移到已删除列表
    const index = agents.value.findIndex(a => a.id === agent.id)
    if (index !== -1) {
      deletedAgents.value.push(agents.value[index])
      agents.value.splice(index, 1)
      ElMessage.success('删除成功')
    }
  } catch {
    ElMessage.info('已取消删除')
  }
}

// 切换热门状态
const toggleHot = (agent: Agent) => {
  agent.isHot = !agent.isHot
  ElMessage.success(agent.isHot ? '已设为热门' : '已取消热门')
}

// 状态变更
const handleStatusChange = (agent: Agent) => {
  ElMessage.success(agent.status === 'enabled' ? '已启用' : '已禁用')
}

// 打开图标选择器
const openIconPicker = () => {
  iconPickerVisible.value = true
  selectedIcon.value = formData.icon || ''
}

// 选择图标
const selectIcon = (icon: string) => {
  selectedIcon.value = icon
}

// 确认图标选择
const confirmIcon = () => {
  formData.icon = selectedIcon.value
  iconPickerVisible.value = false
}

// 页面加载
const init = () => {
  loading.value = true
  setTimeout(() => {
    initAgents()
    loading.value = false
  }, 500)
}

init()
</script>

<style scoped>
.agent-manage-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 24px;
}

/* 头部区域 */
.page-header {
  text-align: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 32px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

/* 操作栏 */
.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  max-width: 1400px;
  margin-left: auto;
  margin-right: auto;
}

.action-left {
  display: flex;
  gap: 12px;
  flex: 1;
}

.search-input {
  flex-shrink: 0;
}

.filter-select {
  flex-shrink: 0;
}

.action-right {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
  max-width: 1400px;
  margin-left: auto;
  margin-right: auto;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.stat-icon {
  font-size: 48px;
  opacity: 0.2;
}

/* 表格区域 */
.table-card {
  max-width: 1400px;
  margin: 0 auto;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.table-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
}

.table-tag {
  margin-right: 4px;
  margin-bottom: 4px;
}

/* 表单 */
.agent-form {
  padding: 0 20px;
}

.bg-option {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bg-preview {
  width: 24px;
  height: 24px;
  border-radius: 4px;
}

/* 图标选择器 */
.icon-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
  padding: 16px;
}

.icon-item {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  border: 2px solid #e5e5e5;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  cursor: pointer;
  transition: all 0.2s;
}

.icon-item:hover {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.icon-item.selected {
  border-color: #409eff;
  background-color: #409eff;
  transform: scale(1.1);
}

/* 响应式 */
@media (max-width: 1200px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .agent-manage-container {
    padding: 16px;
  }

  .page-title {
    font-size: 24px;
  }

  .action-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .action-left {
    flex-direction: column;
  }

  .action-right {
    justify-content: stretch;
  }

  .action-right .el-button {
    flex: 1;
  }

  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
