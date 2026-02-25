<template>
  <div class="recording-management">
    <!-- 头部区域 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">会议录音管理</h1>
        <p class="page-subtitle">实时录音 · 内容转录 · 会议记录</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" icon="FolderOpened" @click="exportRecord">导出记录</el-button>
        <el-button icon="Setting" @click="openSettings">设置</el-button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧：会议列表 -->
      <div class="left-panel">
        <div class="panel-header">
          <h3>会议列表</h3>
          <el-tag type="info">{{ meetings.length }} 个会议</el-tag>
        </div>
        
        <el-input
          v-model="searchKeyword"
          placeholder="搜索会议..."
          prefix-icon="Search"
          class="search-input"
          clearable
        />

        <div class="meetings-list">
          <div
            v-for="meeting in filteredMeetings"
            :key="meeting.id"
            :class="['meeting-item', { active: selectedMeeting?.id === meeting.id, recording: meeting.isRecording }]"
            @click="selectMeeting(meeting)"
          >
            <div class="meeting-icon">
              <el-icon v-if="meeting.isRecording"><VideoPause /></el-icon>
              <el-icon v-else><VideoCamera /></el-icon>
            </div>
            <div class="meeting-info">
              <div class="meeting-header">
                <div class="meeting-title">{{ meeting.title }}</div>
                <el-tag v-if="meeting.isRecording" type="danger" size="small" effect="dark">
                  录音中
                </el-tag>
              </div>
              <div class="meeting-meta">
                <span>{{ meeting.date }}</span>
                <el-divider direction="vertical" />
                <span>{{ meeting.duration }}</span>
              </div>
              <el-tag size="small" :type="getMeetingStatusType(meeting.status)">
                {{ getMeetingStatusText(meeting.status) }}
              </el-tag>
            </div>
          </div>
        </div>

        <el-button type="primary" icon="Plus" style="width: 100%; margin-top: 16px;" @click="createNewMeeting">
          新建会议
        </el-button>
      </div>

      <!-- 中间：录音控制区 -->
      <div class="center-panel">
        <!-- 当前会议信息 -->
        <div v-if="selectedMeeting" class="current-meeting-section">
          <div class="section-header">
            <h3>{{ selectedMeeting.title }}</h3>
            <el-tag v-if="isRecording" type="danger" effect="dark">
              <el-icon><Microphone /></el-icon>
              录音中 {{ recordingTime }}
            </el-tag>
            <el-tag v-else-if="isPaused" type="warning" effect="dark">
              <el-icon><VideoPause /></el-icon>
              已暂停
            </el-tag>
          </div>
          
          <div class="meeting-details">
            <div class="detail-row">
              <el-icon><Calendar /></el-icon>
              <span>{{ selectedMeeting.date }}</span>
            </div>
            <div class="detail-row">
              <el-icon><Clock /></el-icon>
              <span>{{ selectedMeeting.startTime || '--:--' }}</span>
            </div>
            <div class="detail-row">
              <el-icon><Location /></el-icon>
              <span>{{ selectedMeeting.location }}</span>
            </div>
            <div class="detail-row">
              <el-icon><User /></el-icon>
              <span>{{ selectedMeeting.participants.join(', ') }}</span>
            </div>
          </div>
        </div>

        <!-- 录音控制区 -->
        <div class="recording-control-section">
          <div class="section-header">
            <h3>录音控制</h3>
          </div>
          
          <div v-if="selectedMeeting" class="recording-area">
            <!-- 录音波形显示 -->
            <div class="waveform-container">
              <canvas ref="waveformCanvas" class="waveform-canvas"></canvas>
            </div>
            
            <!-- 录音控制按钮 -->
            <div class="recording-controls">
              <el-button
                v-if="!isRecording && !isPaused"
                type="danger"
                size="large"
                class="start-button"
                @click="startRecording"
              >
                <el-icon><Microphone /></el-icon>
                <span>开始录音</span>
              </el-button>
              
              <el-button
                v-else-if="isRecording"
                type="warning"
                size="large"
                class="pause-button"
                @click="pauseRecording"
              >
                <el-icon><VideoPause /></el-icon>
                <span>暂停录音</span>
              </el-button>
              
              <el-button
                v-else-if="isPaused"
                type="success"
                size="large"
                class="resume-button"
                @click="resumeRecording"
              >
                <el-icon><VideoPlay /></el-icon>
                <span>继续录音</span>
              </el-button>
              
              <el-button
                v-if="isRecording || isPaused"
                type="danger"
                size="large"
                class="stop-button"
                @click="stopRecording"
              >
                <el-icon><SwitchButton /></el-icon>
                <span>结束录音</span>
              </el-button>
            </div>
            
            <!-- 录音信息 -->
            <div v-if="isRecording || isPaused" class="recording-info">
              <div class="info-item">
                <el-icon><Clock /></el-icon>
                <span>录音时长：{{ recordingTime }}</span>
              </div>
              <div class="info-item">
                <el-icon><TrendCharts /></el-icon>
                <span>音频质量：{{ audioQuality }}</span>
              </div>
              <div class="info-item">
                <el-icon><Files /></el-icon>
                <span>文件大小：{{ fileSize }}</span>
              </div>
            </div>
            
            <!-- 快捷标记 -->
            <div class="mark-section">
              <div class="mark-header">
                <span>快捷标记</span>
                <el-button text icon="Plus" @click="addMark">添加</el-button>
              </div>
              <div class="marks-list">
                <el-tag
                  v-for="(mark, index) in marks"
                  :key="index"
                  closable
                  @close="removeMark(index)"
                  style="margin: 4px"
                >
                  {{ mark.time }} - {{ mark.label }}
                </el-tag>
              </div>
            </div>
          </div>
          
          <el-empty v-else description="请选择会议开始录音" />
        </div>

        <!-- 实时转录 -->
        <div v-if="selectedMeeting && (isRecording || isPaused)" class="transcription-section">
          <div class="section-header">
            <h3>实时转录</h3>
            <el-tag type="success">AI实时</el-tag>
          </div>
          
          <div class="realtime-transcription">
            <div
              v-for="(segment, index) in realtimeTranscription"
              :key="index"
              class="transcription-segment"
            >
              <span class="segment-time">{{ formatTime(segment.time) }}</span>
              <span class="segment-speaker">{{ segment.speaker }}:</span>
              <span class="segment-text">{{ segment.text }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：会议详情 -->
      <div class="right-panel">
        <!-- 会议基本信息 -->
        <div class="meeting-info-section">
          <div class="section-header">
            <h3>会议信息</h3>
            <el-button v-if="selectedMeeting && !isRecording && !isPaused" text icon="Edit" @click="editMeeting">
              编辑
            </el-button>
          </div>
          
          <el-form v-if="selectedMeeting" :model="selectedMeeting" label-width="80px" size="small">
            <el-form-item label="会议标题">
              <el-input v-model="selectedMeeting.title" :disabled="isRecording" />
            </el-form-item>
            
            <el-form-item label="会议时间">
              <el-date-picker
                v-model="selectedMeeting.date"
                type="datetime"
                placeholder="选择时间"
                style="width: 100%"
                :disabled="isRecording"
              />
            </el-form-item>
            
            <el-form-item label="参与人员">
              <el-select
                v-model="selectedMeeting.participants"
                multiple
                placeholder="选择参与人员"
                style="width: 100%"
                :disabled="isRecording"
              >
                <el-option
                  v-for="person in participantOptions"
                  :key="person"
                  :label="person"
                  :value="person"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="会议地点">
              <el-input v-model="selectedMeeting.location" placeholder="输入会议地点" :disabled="isRecording" />
            </el-form-item>
            
            <el-form-item label="会议类型">
              <el-select v-model="selectedMeeting.type" placeholder="选择类型" style="width: 100%" :disabled="isRecording">
                <el-option label="项目会议" value="project" />
                <el-option label="技术讨论" value="technical" />
                <el-option label="需求评审" value="review" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-form>
          
          <el-empty v-else description="请选择会议" />
        </div>

        <!-- 会议摘要 -->
        <div class="summary-section">
          <div class="section-header">
            <h3>会议摘要</h3>
            <el-button
              v-if="selectedMeeting && selectedMeeting.status === 'completed'"
              type="primary"
              size="small"
              icon="MagicStick"
              :loading="generatingSummary"
              @click="generateSummary"
            >
              生成摘要
            </el-button>
          </div>
          
          <div v-if="selectedMeeting && selectedMeeting.summary" class="summary-content">
            <div class="summary-item">
              <div class="item-title">会议主题</div>
              <div class="item-content">{{ selectedMeeting.summary.topic }}</div>
            </div>
            
            <div class="summary-item">
              <div class="item-title">讨论要点</div>
              <ul class="item-list">
                <li v-for="(point, index) in selectedMeeting.summary.points" :key="index">
                  {{ point }}
                </li>
              </ul>
            </div>
            
            <div class="summary-item">
              <div class="item-title">决策事项</div>
              <ul class="item-list">
                <li v-for="(decision, index) in selectedMeeting.summary.decisions" :key="index">
                  {{ decision }}
                </li>
              </ul>
            </div>
          </div>
          
          <el-empty v-else description="会议结束后可生成摘要" />
        </div>

        <!-- 会议笔记 -->
        <div class="notes-section">
          <div class="section-header">
            <h3>会议笔记</h3>
          </div>
          
          <el-input
            v-model="meetingNotes"
            type="textarea"
            :rows="6"
            placeholder="记录会议要点和备注..."
            class="notes-input"
          />
          
          <el-button type="primary" @click="saveNotes" style="width: 100%; margin-top: 12px;">
            保存笔记
          </el-button>
        </div>

        <!-- 录音历史 -->
        <div v-if="selectedMeeting && selectedMeeting.recordings.length > 0" class="recordings-history">
          <div class="section-header">
            <h3>录音历史</h3>
          </div>
          
          <div class="history-list">
            <div
              v-for="(rec, index) in selectedMeeting.recordings"
              :key="index"
              class="history-item"
            >
              <div class="history-info">
                <span class="history-time">{{ rec.time }}</span>
                <span class="history-duration">{{ rec.duration }}</span>
              </div>
              <div class="history-actions">
                <el-button size="small" icon="VideoPlay" @click="playRecording(rec)">播放</el-button>
                <el-button size="small" icon="Download" @click="downloadRecording(rec)">下载</el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 新建会议对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      title="新建会议"
      width="500px"
    >
      <el-form :model="newMeetingForm" label-width="80px">
        <el-form-item label="会议标题" required>
          <el-input v-model="newMeetingForm.title" placeholder="输入会议标题" />
        </el-form-item>
        
        <el-form-item label="会议时间" required>
          <el-date-picker
            v-model="newMeetingForm.date"
            type="datetime"
            placeholder="选择时间"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="参与人员">
          <el-select
            v-model="newMeetingForm.participants"
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
        
        <el-form-item label="会议地点">
          <el-input v-model="newMeetingForm.location" placeholder="输入会议地点" />
        </el-form-item>
        
        <el-form-item label="会议类型">
          <el-select v-model="newMeetingForm.type" placeholder="选择类型" style="width: 100%">
            <el-option label="项目会议" value="project" />
            <el-option label="技术讨论" value="technical" />
            <el-option label="需求评审" value="review" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateMeeting">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Microphone, VideoPlay, VideoPause, Calendar, Clock, Location, User,
  VideoCamera, SwitchButton, TrendCharts, Files
} from '@element-plus/icons-vue'
import {
  StartRecording, PauseRecording, ResumeRecording, StopRecording, AddRecordingMark
} from './apimeeting'

// 搜索关键词
const searchKeyword = ref('')

// 会议列表
const meetings = ref<any[]>([
  {
    id: 1,
    title: '2024年度项目规划会议',
    date: '2024-01-25',
    startTime: '14:00',
    duration: '0:00:00',
    location: '会议室A',
    participants: ['张三', '李四', '王五', '赵六'],
    type: 'project',
    status: 'pending',
    isRecording: false,
    isPaused: false,
    recordStartTime: null,
    totalRecordingTime: 0,
    marks: [],
    transcription: [],
    summary: null
  },
  {
    id: 2,
    title: '直升机设计方案讨论',
    date: '2024-01-24',
    startTime: '10:00',
    duration: '1:12:45',
    location: '会议室B',
    participants: ['李四', '王五', '孙七', '周八'],
    type: 'technical',
    status: 'completed',
    isRecording: false,
    isPaused: false,
    recordStartTime: null,
    totalRecordingTime: 0,
    recordings: [
      { time: '10:00', duration: '1:12:45' }
    ],
    summary: {
      topic: '直升机设计方案评审',
      points: ['讨论了主旋翼设计', '分析了动力系统配置', '评估了结构强度'],
      decisions: ['采用4叶铰接式旋翼', '使用涡轴-8C发动机']
    }
  },
  {
    id: 3,
    title: '需求分析评审会',
    date: '2024-01-26',
    startTime: '09:30',
    duration: '0:00:00',
    location: '会议室C',
    participants: ['王五', '赵六', '孙七'],
    type: 'review',
    status: 'pending',
    isRecording: false,
    isPaused: false,
    recordStartTime: null,
    totalRecordingTime: 0,
    recordings: [],
    summary: null
  }
])

// 当前选中的会议
const selectedMeeting = ref<any>(null)

// 过滤后的会议列表
const filteredMeetings = computed(() => {
  if (!searchKeyword.value) return meetings.value
  return meetings.value.filter(m =>
    m.title.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
    m.date.includes(searchKeyword.value) ||
    m.location.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

// 录音状态
const isRecording = ref(false)
const isPaused = ref(false)
const recordingStartTime = ref(0)
const totalRecordingTime = ref(0)
const recordingTimer = ref<any>(null)

// 录音时间
const recordingTime = computed(() => formatRecordingTime(totalRecordingTime.value))

// 音频质量
const audioQuality = ref('优秀')

// 文件大小
const fileSize = ref('0 MB')

// 快捷标记
const marks = ref<any[]>([])

// 实时转录
const realtimeTranscription = ref<any[]>([])

// 会议笔记
const meetingNotes = ref('')

// 生成摘要状态
const generatingSummary = ref(false)

// 参与人员选项
const participantOptions = ref([
  '张三', '李四', '王五', '赵六', '孙七', '周八', '吴九', '郑十'
])

// 新建会议对话框
const createDialogVisible = ref(false)
const newMeetingForm = ref({
  title: '',
  date: new Date(),
  participants: [],
  location: '',
  type: 'project'
})

// 波形画布
const waveformCanvas = ref<HTMLCanvasElement | null>(null)
const animationFrame = ref<any>(null)
const audioContext = ref<any>(null)
const analyser = ref<any>(null)
const microphone = ref<any>(null)
const dataArray = ref<any>(null)

// 选择会议
const selectMeeting = (meeting: any) => {
  if (isRecording.value && selectedMeeting.value?.id !== meeting.id) {
    ElMessage.warning('当前有会议正在录音，请先结束录音')
    return
  }
  
  selectedMeeting.value = meeting
  
  // 恢复录音状态
  if (meeting.isRecording && !meeting.isPaused) {
    isRecording.value = true
    isPaused.value = false
    recordingStartTime.value = Date.now() - meeting.totalRecordingTime * 1000
    startRecordingTimer()
  } else if (meeting.isPaused) {
    isRecording.value = false
    isPaused.value = true
    recordingStartTime.value = meeting.recordStartTime
    totalRecordingTime.value = meeting.totalRecordingTime
  } else {
    isRecording.value = false
    isPaused.value = false
    recordingStartTime.value = 0
    totalRecordingTime.value = meeting.totalRecordingTime
  }
  
  // 加载标记和转录
  marks.value = meeting.marks || []
  realtimeTranscription.value = meeting.transcription || []
}

// 新建会议
const createNewMeeting = () => {
  newMeetingForm.value = {
    title: '',
    date: new Date(),
    participants: [],
    location: '',
    type: 'project'
  }
  createDialogVisible.value = true
}

// 处理创建会议
const handleCreateMeeting = () => {
  if (!newMeetingForm.value.title) {
    ElMessage.warning('请输入会议标题')
    return
  }
  
  const newMeeting = {
    id: meetings.value.length + 1,
    title: newMeetingForm.value.title,
    date: formatDate(newMeetingForm.value.date),
    startTime: '',
    duration: '0:00:00',
    location: newMeetingForm.value.location || '未设置',
    participants: newMeetingForm.value.participants || [],
    type: newMeetingForm.value.type,
    status: 'pending',
    isRecording: false,
    isPaused: false,
    recordStartTime: null,
    totalRecordingTime: 0,
    recordings: [],
    summary: null
  }
  
  meetings.value.unshift(newMeeting)
  createDialogVisible.value = false
  selectedMeeting.value = newMeeting
  ElMessage.success('会议创建成功')
}

// 编辑会议
const editMeeting = () => {
  ElMessage.info('编辑会议功能')
}

// 开始录音
const startRecording = async () => {
  if (!selectedMeeting.value) {
    ElMessage.warning('请选择会议')
    return
  }

  // 调用后台接口
  try {
    await StartRecording({
      meeting_id: selectedMeeting.value.id,
      title: selectedMeeting.value.title
    })
  } catch (error: any) {
    ElMessage.error(error.msg || '调用录音接口失败')
    return
  }
  
  try {
    // 初始化音频上下文
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    audioContext.value = new (window.AudioContext || (window as any).webkitAudioContext)()
    analyser.value = audioContext.value.createAnalyser()
    microphone.value = audioContext.value.createMediaStreamSource(stream)
    
    analyser.value.fftSize = 256
    microphone.value.connect(analyser.value)
    
    dataArray.value = new Uint8Array(analyser.value.frequencyBinCount)
    
    // 开始绘制波形
    drawWaveform()
    
    // 更新会议状态
    selectedMeeting.value.isRecording = true
    selectedMeeting.value.isPaused = false
    selectedMeeting.value.recordStartTime = Date.now()
    selectedMeeting.value.startTime = new Date().toLocaleTimeString()
    selectedMeeting.value.status = 'ongoing'
    
    isRecording.value = true
    isPaused.value = false
    recordingStartTime.value = Date.now()
    totalRecordingTime.value = 0
    
    startRecordingTimer()
    
    // 开始实时转录模拟
    simulateRealtimeTranscription()
    
    ElMessage.success('录音已开始')
  } catch (error) {
    ElMessage.error('无法访问麦克风，请检查权限设置')
    console.error('录音错误:', error)
  }
}

// 暂停录音
const pauseRecording = async () => {
  if (!selectedMeeting.value) {
    return
  }

  // 调用后台接口
  try {
    await PauseRecording({
      meeting_id: selectedMeeting.value.id,
      recording_time: recordingTime.value
    })
  } catch (error: any) {
    ElMessage.error(error.msg || '调用暂停录音接口失败')
    return
  }

  if (animationFrame.value) {
    cancelAnimationFrame(animationFrame.value)
  }
  
  stopRecordingTimer()
  
  if (selectedMeeting.value) {
    selectedMeeting.value.isRecording = false
    selectedMeeting.value.isPaused = true
    selectedMeeting.value.totalRecordingTime = totalRecordingTime.value
  }
  
  isRecording.value = false
  isPaused.value = true
  
  ElMessage.info('录音已暂停')
}

// 继续录音
const resumeRecording = async () => {
  if (!selectedMeeting.value) {
    return
  }

  // 调用后台接口
  try {
    await ResumeRecording({
      meeting_id: selectedMeeting.value.id
    })
  } catch (error: any) {
    ElMessage.error(error.msg || '调用继续录音接口失败')
    return
  }

  if (selectedMeeting.value) {
    selectedMeeting.value.isRecording = true
    selectedMeeting.value.isPaused = false
    selectedMeeting.value.recordStartTime = Date.now() - selectedMeeting.value.totalRecordingTime * 1000
  }
  
  isRecording.value = true
  isPaused.value = false
  
  startRecordingTimer()
  drawWaveform()
  
  ElMessage.success('录音已继续')
}

// 停止录音
const stopRecording = async () => {
  if (!selectedMeeting.value) {
    return
  }

  // 调用后台接口
  try {
    await StopRecording({
      meeting_id: selectedMeeting.value.id,
      title: selectedMeeting.value.title,
      recording_time: recordingTime.value
    })
  } catch (error: any) {
    ElMessage.error(error.msg || '调用停止录音接口失败')
    return
  }

  if (animationFrame.value) {
    cancelAnimationFrame(animationFrame.value)
  }
  
  stopRecordingTimer()
  
  if (audioContext.value) {
    audioContext.value.close()
  }
  
  if (selectedMeeting.value) {
    // 保存录音记录
    const recordingEntry = {
      time: formatTime(recordingStartTime.value / 1000),
      duration: formatRecordingTime(totalRecordingTime.value)
    }
    
    if (!selectedMeeting.value.recordings) {
      selectedMeeting.value.recordings = []
    }
    selectedMeeting.value.recordings.push(recordingEntry)
    selectedMeeting.value.duration = recordingEntry.duration
    selectedMeeting.value.isRecording = false
    selectedMeeting.value.isPaused = false
    selectedMeeting.value.status = 'completed'
    selectedMeeting.value.marks = marks.value
    selectedMeeting.value.transcription = realtimeTranscription.value
    selectedMeeting.value.totalRecordingTime = totalRecordingTime.value
  }
  
  isRecording.value = false
  isPaused.value = false
  recordingStartTime.value = 0
  
  ElMessage.success('录音已结束')
}

// 开始录音计时器
const startRecordingTimer = () => {
  recordingTimer.value = setInterval(() => {
    totalRecordingTime.value = Math.floor((Date.now() - recordingStartTime.value) / 1000)
    
    // 更新文件大小（假设每分钟1MB）
    fileSize.value = (totalRecordingTime.value / 60).toFixed(2) + ' MB'
  }, 1000)
}

// 停止录音计时器
const stopRecordingTimer = () => {
  if (recordingTimer.value) {
    clearInterval(recordingTimer.value)
    recordingTimer.value = null
  }
}

// 绘制波形
const drawWaveform = () => {
  if (!analyser.value || !waveformCanvas.value) return

  const canvas = waveformCanvas.value
  const ctx = canvas.getContext('2d')

  if (!ctx) return

  canvas.width = canvas.offsetWidth
  canvas.height = 150

  analyser.value.getByteFrequencyData(dataArray.value)

  ctx.fillStyle = '#f5f7fa'
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  const barWidth = (canvas.width / dataArray.value.length) * 2.5
  let x = 0

  for (let i = 0; i < dataArray.value.length; i++) {
    const barHeight = dataArray.value[i] / 2

    // 创建渐变色
    const gradient = ctx.createLinearGradient(0, canvas.height, 0, canvas.height - barHeight)
    gradient.addColorStop(0, '#409eff')
    gradient.addColorStop(1, '#67c23a')

    ctx.fillStyle = gradient
    ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight)

    x += barWidth + 1
  }

  animationFrame.value = requestAnimationFrame(drawWaveform)
}

// 模拟实时转录
const simulateRealtimeTranscription = () => {
  const sampleTexts = [
    { time: 0, speaker: '主持人', text: '各位好，欢迎参加今天的会议。' },
    { time: 30, speaker: '张三', text: '我先介绍一下项目进展情况。' },
    { time: 60, speaker: '李四', text: '关于技术方案，我有些建议。' }
  ]
  
  let index = 0
  const interval = setInterval(() => {
    if (!isRecording.value || index >= sampleTexts.length) {
      clearInterval(interval)
      return
    }
    
    realtimeTranscription.value.push(sampleTexts[index])
    index++
  }, 30000) // 每30秒添加一条转录
}

// 添加标记
const addMark = () => {
  if (!selectedMeeting.value) {
    return
  }

  const markTime = formatRecordingTime(totalRecordingTime.value)
  ElMessageBox.prompt('请输入标记内容', '添加标记', {
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(async ({ value }) => {
    if (value) {
      // 调用后台接口
      try {
        await AddRecordingMark({
          meeting_id: selectedMeeting.value.id,
          mark_time: markTime,
          label: value
        })
      } catch (error: any) {
        ElMessage.error(error.msg || '调用添加标记接口失败')
        return
      }

      marks.value.push({
        time: markTime,
        label: value
      })
      if (selectedMeeting.value) {
        selectedMeeting.value.marks = marks.value
      }
      ElMessage.success('标记已添加')
    }
  }).catch(() => {})
}

// 删除标记
const removeMark = (index: number) => {
  marks.value.splice(index, 1)
  if (selectedMeeting.value) {
    selectedMeeting.value.marks = marks.value
  }
}

// 生成摘要
const generateSummary = () => {
  if (!selectedMeeting.value) {
    ElMessage.warning('请选择会议')
    return
  }
  
  generatingSummary.value = true
  
  setTimeout(() => {
    selectedMeeting.value.summary = {
      topic: selectedMeeting.value.title,
      points: [
        '讨论了项目规划和资源分配',
        '分析了技术方案的可行性',
        '确定了下一阶段的工作重点'
      ],
      decisions: [
        '同意采用新技术架构',
        '决定成立专项工作组',
        '确定下周进行技术评审'
      ]
    }
    generatingSummary.value = false
    ElMessage.success('摘要生成成功')
  }, 2000)
}

// 保存笔记
const saveNotes = () => {
  if (selectedMeeting.value) {
    selectedMeeting.value.notes = meetingNotes.value
  }
  ElMessage.success('笔记已保存')
}

// 播放录音
const playRecording = (rec: any) => {
  ElMessage.info(`播放录音: ${rec.time}`)
}

// 下载录音
const downloadRecording = (rec: any) => {
  ElMessage.info(`下载录音: ${rec.time}`)
}

// 导出记录
const exportRecord = () => {
  ElMessage.info('正在导出会议记录...')
  setTimeout(() => {
    ElMessage.success('导出成功')
  }, 1500)
}

// 打开设置
const openSettings = () => {
  ElMessage.info('设置功能开发中...')
}

// 获取会议状态类型
const getMeetingStatusType = (status: string) => {
  const types: Record<string, string> = {
    pending: 'warning',
    ongoing: 'danger',
    completed: 'success',
    cancelled: 'info'
  }
  return types[status] || ''
}

// 获取会议状态文本
const getMeetingStatusText = (status: string) => {
  const texts: Record<string, string> = {
    pending: '待开始',
    ongoing: '进行中',
    completed: '已结束',
    cancelled: '已取消'
  }
  return texts[status] || ''
}

// 格式化录音时间（秒 -> HH:MM:SS）
const formatRecordingTime = (seconds: number) => {
  const hours = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 格式化时间（秒 -> MM:SS）
const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 格式化日期
const formatDate = (date: Date) => {
  return date.toISOString().split('T')[0]
}

onMounted(() => {
  // 初始化画布大小
  if (waveformCanvas.value) {
    waveformCanvas.value.width = waveformCanvas.value.offsetWidth
    waveformCanvas.value.height = 150
  }
})

onUnmounted(() => {
  // 清理定时器和动画
  if (recordingTimer.value) {
    clearInterval(recordingTimer.value)
  }
  if (animationFrame.value) {
    cancelAnimationFrame(animationFrame.value)
  }
  if (audioContext.value) {
    audioContext.value.close()
  }
})
</script>

<style scoped>
.recording-management {
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
  grid-template-columns: 320px 1fr 360px;
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

/* 搜索输入 */
.search-input {
  margin-bottom: 16px;
}

/* 会议列表 */
.meetings-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 600px;
  overflow-y: auto;
}

.meeting-item {
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

.meeting-item:hover {
  background: #e5e7eb;
  transform: translateX(4px);
}

.meeting-item.active {
  border-color: #409eff;
  background: #ecf5ff;
}

.meeting-item.recording {
  border-color: #f56c6c;
  background: #fef0f0;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(245, 108, 108, 0.4);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(245, 108, 108, 0);
  }
}

.meeting-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  flex-shrink: 0;
}

.meeting-info {
  flex: 1;
  min-width: 0;
}

.meeting-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.meeting-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.meeting-meta {
  font-size: 12px;
  color: #909399;
  margin-bottom: 6px;
}

/* 当前会议信息区 */
.current-meeting-section,
.recording-control-section,
.transcription-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.meeting-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}

/* 录音控制区 */
.recording-area {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.waveform-container {
  background: #1a1a2e;
  border-radius: 8px;
  overflow: hidden;
}

.waveform-canvas {
  width: 100%;
  height: 150px;
  display: block;
}

.recording-controls {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 20px;
  background: #f9fafb;
  border-radius: 8px;
}

.start-button,
.pause-button,
.resume-button,
.stop-button {
  min-width: 160px;
  height: 50px;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.start-button {
  background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
  border: none;
  font-size: 18px;
  font-weight: bold;
  padding: 0 40px;
  height: 60px;
  box-shadow: 0 6px 20px rgba(245, 87, 108, 0.4);
  animation: startButtonGlow 2s ease-in-out infinite;
}

@keyframes startButtonGlow {
  0%, 100% {
    box-shadow: 0 0 20px rgba(245, 87, 108, 0.4), 0 6px 20px rgba(245, 87, 108, 0.3);
  }
  50% {
    box-shadow: 0 0 40px rgba(245, 87, 108, 0.6), 0 6px 20px rgba(245, 87, 108, 0.5);
  }
}

.start-button:hover {
  transform: scale(1.08);
  box-shadow: 0 0 30px rgba(245, 87, 108, 0.7), 0 8px 30px rgba(245, 87, 108, 0.5);
}

.start-button:active {
  transform: scale(1.02);
}

.stop-button {
  border-color: #f56c6c;
}

/* 录音信息 */
.recording-info {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
}

.info-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: white;
  border-radius: 6px;
}

.info-item span {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}

/* 快捷标记区 */
.mark-section {
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
}

.mark-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.mark-header span {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.marks-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  min-height: 40px;
  align-items: center;
}

/* 实时转录区 */
.realtime-transcription {
  max-height: 300px;
  overflow-y: auto;
  padding: 12px;
  background: #f9fafb;
  border-radius: 6px;
}

.realtime-transcription .transcription-segment {
  background: white;
  border-radius: 4px;
  margin-bottom: 8px;
}

.realtime-transcription .segment-time {
  color: #409eff;
  font-weight: 600;
}

.realtime-transcription .segment-speaker {
  color: #67c23a;
  font-weight: 600;
}

.realtime-transcription .segment-text {
  color: #303133;
}

.transcription-segment {
  display: flex;
  gap: 8px;
  padding: 8px;
  border-radius: 4px;
  font-size: 14px;
}

/* 右侧面板 */
.meeting-info-section,
.summary-section,
.notes-section,
.recordings-history {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
}

/* 摘要内容 */
.summary-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.summary-item {
  padding: 12px;
  background: #f9fafb;
  border-radius: 6px;
}

.item-title {
  font-size: 13px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 8px;
}

.item-content {
  font-size: 14px;
  color: #303133;
  line-height: 1.6;
}

.item-list {
  margin: 0;
  padding-left: 20px;
  font-size: 14px;
  color: #303133;
  line-height: 1.8;
}

.item-list li {
  margin-bottom: 6px;
}

/* 笔记输入 */
.notes-input {
  margin-bottom: 12px;
}

/* 录音历史 */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f9fafb;
  border-radius: 6px;
}

.history-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.history-time {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
}

.history-duration {
  font-size: 12px;
  color: #909399;
}

.history-actions {
  display: flex;
  gap: 8px;
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
