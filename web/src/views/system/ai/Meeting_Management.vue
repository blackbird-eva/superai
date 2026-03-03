<template>
  <div class="meeting-management">
    <!-- 头部区域 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">会议内容管理</h1>
        <p class="page-subtitle">会议创建 · 内容管理 · 记录归档</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" icon="Plus" @click="openCreateDialog">创建会议</el-button>
        <el-button icon="Download" @click="exportMeetings">导出数据</el-button>
        <el-button icon="Setting" @click="openSettings">设置</el-button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧：会议分类和统计 -->
      <div class="left-panel">
        <div class="panel-header">
          <h3>会议分类</h3>
          <el-button text icon="Plus" @click="addCategory" />
        </div>
        
        <div class="category-list">
          <div
            v-for="category in categories"
            :key="category.id"
            :class="['category-item', { active: selectedCategory === category.id }]"
            @click="selectCategory(category.id)"
          >
            <div class="category-info">
              <div class="category-icon" :style="{ backgroundColor: category.color }">
                <el-icon><component :is="category.icon" /></el-icon>
              </div>
              <div class="category-name">{{ category.name }}</div>
            </div>
            <el-badge :value="category.count" :max="99" class="category-badge" />
          </div>
        </div>

        <!-- 统计信息 -->
        <div class="statistics-section">
          <div class="section-header">
            <h3>数据统计</h3>
          </div>
          <div class="stat-cards">
            <div class="stat-card">
              <div class="stat-value">{{ statistics.total }}</div>
              <div class="stat-label">总会议数</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ statistics.upcoming }}</div>
              <div class="stat-label">待召开</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ statistics.ongoing }}</div>
              <div class="stat-label">进行中</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ statistics.completed }}</div>
              <div class="stat-label">已完成</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 中间：会议列表 -->
      <div class="center-panel">
        <!-- 搜索和筛选 -->
        <div class="filter-section">
          <div class="filter-row">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索会议..."
              prefix-icon="Search"
              class="search-input"
              clearable
            />
            <el-select v-model="statusFilter" placeholder="状态筛选" clearable class="filter-select">
              <el-option label="待开始" value="pending" />
              <el-option label="进行中" value="ongoing" />
              <el-option label="已结束" value="completed" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              class="date-picker"
            />
          </div>
          <div class="filter-row">
            <el-radio-group v-model="viewMode">
              <el-radio-button label="list">列表视图</el-radio-button>
              <el-radio-button label="card">卡片视图</el-radio-button>
              <el-radio-button label="calendar">日历视图</el-radio-button>
            </el-radio-group>
          </div>
        </div>

        <!-- 列表视图 -->
        <div v-if="viewMode === 'list'" class="meetings-table">
          <el-table :data="filteredMeetings" style="width: 100%" stripe>
            <el-table-column type="selection" width="55" />
            <el-table-column prop="title" label="会议标题" min-width="200">
              <template #default="{ row }">
                <div class="meeting-title">
                  <el-icon v-if="row.hasRecording" color="#409eff" style="margin-right: 8px">
                    <Microphone />
                  </el-icon>
                  <span>{{ row.title }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="category" label="分类" width="120">
              <template #default="{ row }">
                <el-tag size="small">{{ row.category }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="date" label="日期" width="120" />
            <el-table-column prop="time" label="时间" width="100" />
            <el-table-column prop="duration" label="时长" width="80" />
            <el-table-column prop="location" label="地点" width="120" />
            <el-table-column prop="organizer" label="组织者" width="100" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="participants" label="参与人数" width="100">
              <template #default="{ row }">
                {{ row.participants.length }} 人
              </template>
            </el-table-column>
            <el-table-column label="操作" width="220" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" icon="View" @click="viewMeeting(row)">查看</el-button>
                <el-button link type="primary" icon="Edit" @click="editMeeting(row)">编辑</el-button>
                <el-button link type="danger" icon="Delete" @click="deleteMeeting(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="pagination-section">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="filteredMeetings.length"
              layout="total, sizes, prev, pager, next, jumper"
            />
          </div>
        </div>

        <!-- 卡片视图 -->
        <div v-else-if="viewMode === 'card'" class="meetings-cards">
          <div
            v-for="meeting in paginatedMeetings"
            :key="meeting.id"
            class="meeting-card"
            @click="viewMeeting(meeting)"
          >
            <div class="card-header">
              <div class="card-title">{{ meeting.title }}</div>
              <el-tag :type="getStatusType(meeting.status)" size="small">
                {{ getStatusText(meeting.status) }}
              </el-tag>
            </div>
            <div class="card-body">
              <div class="card-row">
                <el-icon><Calendar /></el-icon>
                <span>{{ meeting.date }} {{ meeting.time }}</span>
              </div>
              <div class="card-row">
                <el-icon><Location /></el-icon>
                <span>{{ meeting.location }}</span>
              </div>
              <div class="card-row">
                <el-icon><User /></el-icon>
                <span>{{ meeting.organizer }}</span>
              </div>
              <div class="card-row">
                <el-icon><UserFilled /></el-icon>
                <span>{{ meeting.participants.length }} 人参与</span>
              </div>
            </div>
            <div class="card-footer">
              <div class="card-attachments">
                <el-icon v-if="meeting.hasRecording"><Microphone /></el-icon>
                <el-badge :value="meeting.attachments || 0" :max="99" />
              </div>
              <div class="card-actions">
                <el-button size="small" icon="View">查看</el-button>
                <el-button size="small" icon="Edit">编辑</el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 日历视图 -->
        <div v-else-if="viewMode === 'calendar'" class="calendar-view">
          <el-calendar v-model="calendarDate">
            <template #date-cell="{ data }">
              <div class="calendar-cell">
                <div class="cell-date">{{ data.day.split('-').slice(2).join('-') }}</div>
                <div v-for="meeting in getMeetingsByDate(data.day)" :key="meeting.id" class="cell-meeting">
                  <div class="meeting-dot" :class="'status-' + meeting.status" />
                  <span class="meeting-text">{{ meeting.title }}</span>
                </div>
              </div>
            </template>
          </el-calendar>
        </div>
      </div>

      <!-- 右侧：详情和操作 -->
      <div class="right-panel">
        <!-- 会议详情 -->
        <div class="detail-section">
          <div class="section-header">
            <h3>会议详情</h3>
            <el-button v-if="selectedMeeting" text icon="Close" @click="selectedMeeting = null" />
          </div>
          
          <div v-if="selectedMeeting" class="meeting-detail">
            <div class="detail-item">
              <div class="detail-label">会议标题</div>
              <div class="detail-value">{{ selectedMeeting.title }}</div>
            </div>
            
            <div class="detail-item">
              <div class="detail-label">分类</div>
              <el-tag>{{ selectedMeeting.category }}</el-tag>
            </div>
            
            <div class="detail-item">
              <div class="detail-label">时间</div>
              <div class="detail-value">{{ selectedMeeting.date }} {{ selectedMeeting.time }}</div>
            </div>
            
            <div class="detail-item">
              <div class="detail-label">时长</div>
              <div class="detail-value">{{ selectedMeeting.duration }}</div>
            </div>
            
            <div class="detail-item">
              <div class="detail-label">地点</div>
              <div class="detail-value">{{ selectedMeeting.location }}</div>
            </div>
            
            <div class="detail-item">
              <div class="detail-label">组织者</div>
              <div class="detail-value">{{ selectedMeeting.organizer }}</div>
            </div>
            
            <div class="detail-item">
              <div class="detail-label">状态</div>
              <el-tag :type="getStatusType(selectedMeeting.status)">
                {{ getStatusText(selectedMeeting.status) }}
              </el-tag>
            </div>
            
            <div class="detail-item">
              <div class="detail-label">参与人员</div>
              <div class="participants-list">
                <el-tag
                  v-for="person in selectedMeeting.participants"
                  :key="person"
                  size="small"
                  style="margin: 2px"
                >
                  {{ person }}
                </el-tag>
              </div>
            </div>
            
            <div class="detail-item">
              <div class="detail-label">会议议程</div>
              <div class="agenda-list">
                <div v-for="(item, index) in selectedMeeting.agenda" :key="index" class="agenda-item">
                  <span class="agenda-time">{{ item.time }}</span>
                  <span class="agenda-content">{{ item.content }}</span>
                </div>
              </div>
            </div>
            
            <div class="detail-item">
              <div class="detail-label">会议说明</div>
              <div class="detail-value">{{ selectedMeeting.description }}</div>
            </div>
          </div>
          
          <el-empty v-else description="选择会议查看详情" />
        </div>

        <!-- 快捷操作 -->
        <div class="quick-actions-section">
          <div class="section-header">
            <h3>快捷操作</h3>
          </div>
          <div class="quick-actions">
            <el-button type="primary" icon="Plus" style="width: 100%">创建会议</el-button>
            <el-button icon="Document" style="width: 100%">导入数据</el-button>
            <el-button icon="Share" style="width: 100%">分享</el-button>
            <el-button icon="Refresh" style="width: 100%">刷新列表</el-button>
          </div>
        </div>

        <!-- 最近活动 -->
        <div class="recent-section">
          <div class="section-header">
            <h3>最近活动</h3>
          </div>
          <el-timeline>
            <el-timeline-item
              v-for="(activity, index) in recentActivities"
              :key="index"
              :timestamp="activity.time"
              placement="top"
            >
              {{ activity.content }}
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </div>

    <!-- 创建/编辑会议对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '创建会议' : '编辑会议'"
      width="700px"
    >
      <el-form :model="meetingForm" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="会议标题" prop="title">
          <el-input v-model="meetingForm.title" placeholder="输入会议标题" />
        </el-form-item>
        
        <el-form-item label="会议分类" prop="category">
          <el-select v-model="meetingForm.category" placeholder="选择分类" style="width: 100%">
            <el-option
              v-for="cat in categories"
              :key="cat.name"
              :label="cat.name"
              :value="cat.name"
            />
          </el-select>
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="日期" prop="date">
              <el-date-picker
                v-model="meetingForm.date"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="时间" prop="time">
              <el-time-picker
                v-model="meetingForm.time"
                placeholder="选择时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="预计时长" prop="duration">
              <el-input-number v-model="meetingForm.duration" :min="15" :step="15" />
              <span style="margin-left: 8px">分钟</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="地点" prop="location">
              <el-input v-model="meetingForm.location" placeholder="输入地点" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="组织者" prop="organizer">
          <el-input v-model="meetingForm.organizer" placeholder="输入组织者" />
        </el-form-item>
        
        <el-form-item label="参与人员" prop="participants">
          <el-select
            v-model="meetingForm.participants"
            multiple
            placeholder="选择参与人员"
            style="width: 100%"
          >
            <el-option
              v-for="person in participantOptions"
              :key="person"
              :label="person"
              :value="person"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="会议议程">
          <div class="agenda-editor">
            <div
              v-for="(item, index) in meetingForm.agenda"
              :key="index"
              class="agenda-row"
            >
              <el-time-picker
                v-model="item.time"
                placeholder="时间"
                size="small"
                format="HH:mm"
              />
              <el-input
                v-model="item.content"
                placeholder="议程内容"
                size="small"
                style="flex: 1; margin-left: 8px"
              />
              <el-button
                icon="Delete"
                circle
                size="small"
                style="margin-left: 8px"
                @click="removeAgenda(index)"
              />
            </div>
            <el-button
              icon="Plus"
              size="small"
              style="width: 100%; margin-top: 8px"
              @click="addAgenda"
            >
              添加议程
            </el-button>
          </div>
        </el-form-item>
        
        <el-form-item label="会议说明">
          <el-input
            v-model="meetingForm.description"
            type="textarea"
            :rows="4"
            placeholder="输入会议说明"
          />
        </el-form-item>
        
        <el-form-item label="提醒设置">
          <el-checkbox-group v-model="meetingForm.reminders">
            <el-checkbox label="email">邮件提醒</el-checkbox>
            <el-checkbox label="sms">短信提醒</el-checkbox>
            <el-checkbox label="wechat">微信提醒</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Calendar, Location, User, UserFilled, Microphone
} from '@element-plus/icons-vue'

// 分类数据
const categories = ref([
  { id: 'all', name: '全部会议', icon: 'Menu', color: '#409eff', count: 24 },
  { id: 'project', name: '项目会议', icon: 'Folder', color: '#67c23a', count: 8 },
  { id: 'technical', name: '技术讨论', icon: 'Cpu', color: '#e6a23c', count: 6 },
  { id: 'review', name: '需求评审', icon: 'Document', color: '#f56c6c', count: 5 },
  { id: 'weekly', name: '周会', icon: 'Calendar', color: '#909399', count: 5 }
])

// 选中的分类
const selectedCategory = ref('all')

// 统计数据
const statistics = ref({
  total: 24,
  upcoming: 6,
  ongoing: 1,
  completed: 17
})

// 会议列表
const meetings = ref<any[]>([
  {
    id: 1,
    title: '2024年度项目规划会议',
    category: '项目会议',
    date: '2024-01-25',
    time: '14:00',
    duration: 90,
    location: '会议室A',
    organizer: '张三',
    status: 'pending',
    participants: ['张三', '李四', '王五', '赵六'],
    agenda: [
      { time: '14:00', content: '年度工作总结' },
      { time: '14:30', content: '下年度规划讨论' },
      { time: '15:00', content: '资源分配方案' },
      { time: '15:15', content: '答疑环节' }
    ],
    description: '讨论2024年度项目规划和资源分配',
    hasRecording: false,
    attachments: 2
  },
  {
    id: 2,
    title: '直升机设计方案评审',
    category: '技术讨论',
    date: '2024-01-24',
    time: '10:00',
    duration: 120,
    location: '会议室B',
    organizer: '李四',
    status: 'completed',
    participants: ['李四', '王五', '孙七', '周八'],
    agenda: [
      { time: '10:00', content: '方案介绍' },
      { time: '10:30', content: '技术评审' },
      { time: '11:30', content: '问题讨论' }
    ],
    description: '评审直升机设计方案',
    hasRecording: true,
    attachments: 5
  },
  {
    id: 3,
    title: '需求分析评审会',
    category: '需求评审',
    date: '2024-01-26',
    time: '09:30',
    duration: 60,
    location: '会议室C',
    organizer: '王五',
    status: 'pending',
    participants: ['王五', '赵六', '孙七'],
    agenda: [
      { time: '09:30', content: '需求概览' },
      { time: '10:00', content: '详细讨论' }
    ],
    description: '评审项目需求分析文档',
    hasRecording: false,
    attachments: 3
  },
  {
    id: 4,
    title: '周例会',
    category: '周会',
    date: '2024-01-22',
    time: '16:00',
    duration: 45,
    location: '会议室A',
    organizer: '张三',
    status: 'completed',
    participants: ['张三', '李四', '王五', '赵六', '孙七'],
    agenda: [
      { time: '16:00', content: '工作进展汇报' },
      { time: '16:30', content: '问题讨论' }
    ],
    description: '本周工作总结和下周计划',
    hasRecording: true,
    attachments: 1
  }
])

// 搜索关键词
const searchKeyword = ref('')

// 状态筛选
const statusFilter = ref('')

// 日期范围
const dateRange = ref<any[]>([])

// 视图模式
const viewMode = ref('list')

// 当前页
const currentPage = ref(1)

// 每页数量
const pageSize = ref(10)

// 选中的会议
const selectedMeeting = ref<any>(null)

// 对话框
const dialogVisible = ref(false)
const dialogMode = ref('create')
const submitting = ref(false)

// 表单引用
const formRef = ref()

// 会议表单
const meetingForm = reactive({
  title: '',
  category: '',
  date: new Date(),
  time: null,
  duration: 60,
  location: '',
  organizer: '',
  participants: [],
  agenda: [{ time: null, content: '' }],
  description: '',
  reminders: ['email']
})

// 表单验证规则
const formRules = {
  title: [{ required: true, message: '请输入会议标题', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  time: [{ required: true, message: '请选择时间', trigger: 'change' }],
  duration: [{ required: true, message: '请输入时长', trigger: 'blur' }],
  location: [{ required: true, message: '请输入地点', trigger: 'blur' }],
  organizer: [{ required: true, message: '请输入组织者', trigger: 'blur' }],
  participants: [{ required: true, message: '请选择参与人员', trigger: 'change' }]
}

// 参与人员选项
const participantOptions = ref([
  '张三', '李四', '王五', '赵六', '孙七', '周八', '吴九', '郑十'
])

// 日历日期
const calendarDate = ref(new Date())

// 最近活动
const recentActivities = ref([
  { time: '10分钟前', content: '创建了"2024年度项目规划会议"' },
  { time: '30分钟前', content: '编辑了"周例会"参会人员' },
  { time: '1小时前', content: '删除了"临时会议"' },
  { time: '2小时前', content: '导出了会议数据' }
])

// 过滤后的会议列表
const filteredMeetings = computed(() => {
  let result = meetings.value

  // 分类筛选
  if (selectedCategory.value !== 'all') {
    const categoryName = categories.value.find(c => c.id === selectedCategory.value)?.name
    result = result.filter(m => m.category === categoryName)
  }

  // 关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(m =>
      m.title.toLowerCase().includes(keyword) ||
      m.organizer.toLowerCase().includes(keyword) ||
      m.location.toLowerCase().includes(keyword)
    )
  }

  // 状态筛选
  if (statusFilter.value) {
    result = result.filter(m => m.status === statusFilter.value)
  }

  // 日期筛选
  if (dateRange.value && dateRange.value.length === 2) {
    const [start, end] = dateRange.value
    result = result.filter(m => {
      const date = new Date(m.date)
      return date >= start && date <= end
    })
  }

  return result
})

// 分页后的会议列表
const paginatedMeetings = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredMeetings.value.slice(start, end)
})

// 选择分类
const selectCategory = (id: string) => {
  selectedCategory.value = id
}

// 添加分类
const addCategory = () => {
  ElMessage.info('添加分类功能开发中...')
}

// 获取状态类型
const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    pending: 'warning',
    ongoing: 'primary',
    completed: 'success',
    cancelled: 'info'
  }
  return types[status] || ''
}

// 获取状态文本
const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    pending: '待开始',
    ongoing: '进行中',
    completed: '已结束',
    cancelled: '已取消'
  }
  return texts[status] || ''
}

// 打开创建对话框
const openCreateDialog = () => {
  dialogMode.value = 'create'
  resetForm()
  dialogVisible.value = true
}

// 查看会议
const viewMeeting = (meeting: any) => {
  selectedMeeting.value = meeting
}

// 编辑会议
const editMeeting = (meeting: any) => {
  dialogMode.value = 'edit'
  Object.assign(meetingForm, meeting)
  dialogVisible.value = true
}

// 删除会议
const deleteMeeting = (meeting: any) => {
  ElMessageBox.confirm(`确定要删除会议"${meeting.title}"吗？`, '确认删除', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const index = meetings.value.findIndex(m => m.id === meeting.id)
    if (index > -1) {
      meetings.value.splice(index, 1)
      ElMessage.success('删除成功')
      if (selectedMeeting.value?.id === meeting.id) {
        selectedMeeting.value = null
      }
    }
  })
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate((valid: boolean) => {
    if (valid) {
      submitting.value = true
      
      setTimeout(() => {
        if (dialogMode.value === 'create') {
          const newMeeting = {
            id: meetings.value.length + 1,
            ...meetingForm,
            date: formatDate(meetingForm.date),
            time: formatTime(meetingForm.time),
            status: 'pending',
            hasRecording: false,
            attachments: 0
          }
          meetings.value.unshift(newMeeting)
          ElMessage.success('会议创建成功')
        } else {
          const index = meetings.value.findIndex(m => m.id === meetingForm.id)
          if (index > -1) {
            meetings.value[index] = {
              ...meetings.value[index],
              ...meetingForm,
              date: formatDate(meetingForm.date),
              time: formatTime(meetingForm.time)
            }
          }
          ElMessage.success('会议更新成功')
        }
        
        submitting.value = false
        dialogVisible.value = false
        resetForm()
      }, 1000)
    }
  })
}

// 重置表单
const resetForm = () => {
  Object.assign(meetingForm, {
    title: '',
    category: '',
    date: new Date(),
    time: null,
    duration: 60,
    location: '',
    organizer: '',
    participants: [],
    agenda: [{ time: null, content: '' }],
    description: '',
    reminders: ['email']
  })
  formRef.value?.clearValidate()
}

// 添加议程
const addAgenda = () => {
  meetingForm.agenda.push({ time: null, content: '' })
}

// 删除议程
const removeAgenda = (index: number) => {
  if (meetingForm.agenda.length > 1) {
    meetingForm.agenda.splice(index, 1)
  }
}

// 获取日期的会议
const getMeetingsByDate = (dateStr: string) => {
  return filteredMeetings.value.filter(m => m.date === dateStr)
}

// 导出数据
const exportMeetings = () => {
  ElMessage.info('正在导出会议数据...')
  setTimeout(() => {
    ElMessage.success('导出成功')
  }, 1500)
}

// 设置
const openSettings = () => {
  ElMessage.info('设置功能开发中...')
}

// 格式化日期
const formatDate = (date: Date) => {
  return date.toISOString().split('T')[0]
}

// 格式化时间
const formatTime = (time: any) => {
  if (!time) return ''
  const hours = time.getHours().toString().padStart(2, '0')
  const minutes = time.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}
</script>

<style scoped>
.meeting-management {
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
  grid-template-columns: 260px minmax(0, 1fr) 320px;
  gap: 20px;
  overflow: hidden;
}

/* 左右面板 */
.left-panel, .right-panel {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  max-height: calc(100vh - 140px);
  overflow-y: auto;
  overflow-x: hidden;
}

/* 中间面板 */
.center-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-height: calc(100vh - 140px);
  overflow-y: auto;
  overflow-x: hidden;
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

/* 分类列表 */
.category-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.category-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  background: #f9fafb;
}

.category-item:hover {
  background: #e5e7eb;
}

.category-item.active {
  background: #ecf5ff;
  border: 2px solid #409eff;
}

.category-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.category-icon {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
}

.category-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

/* 统计区域 */
.statistics-section {
  margin-top: 20px;
}

.stat-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.stat-card {
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  text-align: center;
  color: white;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  opacity: 0.9;
}

/* 筛选区域 */
.filter-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.filter-row {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.search-input {
  flex: 1;
}

.filter-select,
.date-picker {
  width: 200px;
}

/* 会议表格 */
.meetings-table {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.meeting-title {
  display: flex;
  align-items: center;
}

.pagination-section {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

/* 会议卡片 */
.meetings-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.meeting-card {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.meeting-card:hover {
  border-color: #409eff;
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.2);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.card-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #606266;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e5e7eb;
}

.card-attachments {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-actions {
  display: flex;
  gap: 8px;
}

/* 日历视图 */
.calendar-view {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.calendar-cell {
  height: 80px;
  overflow: hidden;
}

.cell-date {
  font-size: 14px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 4px;
}

.cell-meeting {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #303133;
  margin-bottom: 2px;
  cursor: pointer;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.cell-meeting:hover {
  color: #409eff;
}

.meeting-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.meeting-dot.status-pending {
  background: #e6a23c;
}

.meeting-dot.status-ongoing {
  background: #409eff;
}

.meeting-dot.status-completed {
  background: #67c23a;
}

.meeting-dot.status-cancelled {
  background: #909399;
}

.meeting-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 详情区域 */
.detail-section,
.quick-actions-section,
.recent-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
}

.meeting-detail {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-item {
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 6px;
}

.detail-value {
  font-size: 14px;
  color: #303133;
  line-height: 1.6;
}

.participants-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.agenda-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.agenda-item {
  display: flex;
  gap: 12px;
  font-size: 14px;
}

.agenda-time {
  min-width: 60px;
  color: #909399;
  font-family: monospace;
}

.agenda-content {
  flex: 1;
  color: #303133;
}

/* 快捷操作 */
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 议程编辑器 */
.agenda-editor {
  width: 100%;
}

.agenda-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
