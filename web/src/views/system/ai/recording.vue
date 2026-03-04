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
        <div class="transcription-section">
          <div class="section-header">
            <h3>实时转录</h3>
            <el-tag v-if="transcriptionStatus === 'idle'" type="info">等待录音</el-tag>
            <el-tag v-else-if="transcriptionStatus === 'transcribing'" type="warning">
              <el-icon class="is-loading"><Loading /></el-icon>
              转录中
            </el-tag>
            <el-tag v-else-if="transcriptionStatus === 'completed'" type="success">
              <el-icon><Select /></el-icon>
              已完成
            </el-tag>
            <el-tag v-else-if="transcriptionStatus === 'failed'" type="danger">
              <el-icon><CircleClose /></el-icon>
              转录失败
            </el-tag>
          </div>

          <!-- 状态提示 -->
          <div v-if="transcriptionStatus === 'idle'" class="transcription-status idle">
            <el-icon><Microphone /></el-icon>
            <span>开始录音后，语音内容将实时转换为文本</span>
          </div>

          <div v-else-if="transcriptionStatus === 'transcribing'" class="transcription-status transcribing">
            <div class="loading-animation">
              <div class="pulse-dot"></div>
              <div class="pulse-dot"></div>
              <div class="pulse-dot"></div>
            </div>
            <span>正在将语音转换为文本...</span>
          </div>

          <div v-else-if="transcriptionStatus === 'failed'" class="transcription-status failed">
            <el-icon><CircleClose /></el-icon>
            <span>转录失败: {{ transcriptionError || '未知错误' }}</span>
          </div>

          <!-- 转录内容 -->
          <div class="realtime-transcription">
            <el-empty v-if="realtimeTranscription.length === 0 && transcriptionStatus === 'idle'" description="暂无转录内容" />

            <div
              v-for="(segment, index) in realtimeTranscription"
              :key="index"
              class="transcription-segment"
            >
              <span class="segment-time">{{ formatTime(segment.time) }}</span>
              <span class="segment-speaker">{{ segment.speaker }}:</span>
              <span class="segment-text">{{ segment.text }}</span>
            </div>

            <div v-if="transcriptionStatus === 'completed' && realtimeTranscription.length > 0" class="transcription-complete-tip">
              <el-icon><Select /></el-icon>
              <span>转录完成，共 {{ realtimeTranscription.length }} 条记录</span>
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
            <div class="header-actions">
              <el-button
                v-if="selectedMeeting && (selectedMeeting.status === 'completed' || realtimeTranscription.length > 0)"
                type="primary"
                size="small"
                icon="MagicStick"
                :loading="generatingSummary"
                @click="generateSummary"
              >
                生成摘要
              </el-button>
              <el-button
                v-if="selectedMeeting && selectedMeeting.summary"
                size="small"
                icon="CopyDocument"
                @click="copySummary"
              >
                复制
              </el-button>
            </div>
          </div>
          
          <div v-if="selectedMeeting && selectedMeeting.summary" class="summary-content">
            <!-- 会议主题 -->
            <div class="summary-item">
              <div class="item-title">
                <el-icon><Document /></el-icon>
                会议主题
              </div>
              <div class="item-content">{{ selectedMeeting.summary.topic }}</div>
            </div>
            
            <!-- 参与人员 -->
            <div v-if="selectedMeeting.summary.participants && selectedMeeting.summary.participants.length > 0" class="summary-item">
              <div class="item-title">
                <el-icon><User /></el-icon>
                参与人员
              </div>
              <div class="item-content">
                <el-tag
                  v-for="(person, index) in selectedMeeting.summary.participants"
                  :key="index"
                  size="small"
                  style="margin: 4px"
                >
                  {{ person }}
                </el-tag>
              </div>
            </div>
            
            <!-- 关键词 -->
            <div v-if="selectedMeeting.summary.keywords && selectedMeeting.summary.keywords.length > 0" class="summary-item">
              <div class="item-title">
                <el-icon><TrendCharts /></el-icon>
                关键词
              </div>
              <div class="item-content">
                <el-tag
                  v-for="(keyword, index) in selectedMeeting.summary.keywords"
                  :key="index"
                  type="warning"
                  size="small"
                  effect="plain"
                  style="margin: 4px"
                >
                  {{ keyword }}
                </el-tag>
              </div>
            </div>
            
            <!-- 讨论要点 -->
            <div class="summary-item">
              <div class="item-title">
                <el-icon><ChatDotRound /></el-icon>
                讨论要点 ({{ selectedMeeting.summary.points?.length || 0 }})
              </div>
              <ul class="item-list">
                <li v-for="(point, index) in selectedMeeting.summary.points" :key="index">
                  {{ point }}
                </li>
              </ul>
            </div>
            
            <!-- 决策事项 -->
            <div class="summary-item">
              <div class="item-title">
                <el-icon><Select /></el-icon>
                决策事项 ({{ selectedMeeting.summary.decisions?.length || 0 }})
              </div>
              <ul class="item-list decision-list">
                <li v-for="(decision, index) in selectedMeeting.summary.decisions" :key="index">
                  {{ decision }}
                </li>
              </ul>
            </div>
            
            <!-- 待办事项 -->
            <div v-if="selectedMeeting.summary.action_items && selectedMeeting.summary.action_items.length > 0" class="summary-item">
              <div class="item-title">
                <el-icon><List /></el-icon>
                待办事项 ({{ selectedMeeting.summary.action_items.length }})
              </div>
              <ul class="item-list action-list">
                <li v-for="(item, index) in selectedMeeting.summary.action_items" :key="index">
                  {{ item }}
                </li>
              </ul>
            </div>
            
            <!-- 问题和风险 -->
            <div v-if="selectedMeeting.summary.issues && selectedMeeting.summary.issues.length > 0" class="summary-item">
              <div class="item-title">
                <el-icon><Warning /></el-icon>
                问题和风险 ({{ selectedMeeting.summary.issues.length }})
              </div>
              <ul class="item-list issue-list">
                <li v-for="(issue, index) in selectedMeeting.summary.issues" :key="index">
                  {{ issue }}
                </li>
              </ul>
            </div>
            
            <!-- 完整转录文本 -->
            <div v-if="selectedMeeting.summary.transcription_text" class="summary-item full-transcription">
              <div class="item-title">
                <el-icon><DocumentCopy /></el-icon>
                完整转录文本
                <el-button
                  text
                  size="small"
                  icon="Download"
                  @click="downloadTranscription"
                >
                  导出
                </el-button>
              </div>
              <div class="item-content transcription-text">
                {{ selectedMeeting.summary.transcription_text }}
              </div>
            </div>
          </div>
          
          <el-empty v-else-if="realtimeTranscription.length > 0" description='点击"生成摘要"按钮，基于转录内容生成会议记录' />
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

    <!-- 设置对话框 -->
    <el-dialog
      v-model="settingsDialogVisible"
      title="设置"
      width="500px"
    >
      <el-form :model="settingsForm" label-width="100px">
        <el-form-item label="API Key">
          <el-input
            v-model="settingsForm.apiKey"
            type="password"
            placeholder="请输入 SiliconFlow API Key"
            show-password
            clearable
          />
          <div style="margin-top: 8px; font-size: 12px; color: #909399;">
            用于语音转文本功能的 SiliconFlow API Key
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="settingsDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveSettings">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Microphone, VideoPlay, VideoPause, Calendar, Clock, Location, User,
  VideoCamera, SwitchButton, TrendCharts, Files, Loading, Select, CircleClose,
  Document, CopyDocument, ChatDotRound, List, Warning, DocumentCopy
} from '@element-plus/icons-vue'
import {
  StartRecording, PauseRecording, ResumeRecording, StopRecording, AddRecordingMark,
  SaveRecordingFile, DownloadRecordingFile, TranscribeAudio
} from './apimeeting'

// 搜索关键词
const searchKeyword = ref('')

// 会议列表
const meetings = ref<any[]>([
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

// 转录状态
const transcriptionStatus = ref<'idle' | 'transcribing' | 'completed' | 'failed'>('idle')
const transcriptionError = ref('')

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

// API Key 设置对话框
const settingsDialogVisible = ref(false)
const settingsForm = ref({
  apiKey: ''
})

// 波形画布
const waveformCanvas = ref<HTMLCanvasElement | null>(null)
const animationFrame = ref<any>(null)
const audioContext = ref<any>(null)
const analyser = ref<any>(null)
const microphone = ref<any>(null)
const dataArray = ref<any>(null)

// MediaRecorder 相关
const mediaRecorder = ref<any>(null)
const audioChunks = ref<Blob[]>([])
const audioBlob = ref<Blob | null>(null)
const audioUrl = ref<string>('')
const audioStream = ref<MediaStream | null>(null)
const stopRecordingPromise = ref<Promise<Blob> | null>(null)

// SiliconFlow API Key
const siliconflowApiKey = ref('')

// 选择会议
const selectMeeting = (meeting: any) => {
  console.log('selectMeeting 被调用:', meeting)

  // 检查是否正在录音其他会议
  if (isRecording.value && selectedMeeting.value?.id !== meeting.id) {
    console.log('阻止选择：当前有会议正在录音')
    ElMessage.warning('当前有会议正在录音，请先结束录音')
    return
  }

  console.log('选择会议:', meeting.id, meeting.title)
  selectedMeeting.value = meeting

  // 恢复录音状态
  if (meeting.isRecording && !meeting.isPaused) {
    console.log('恢复录音状态：录音中')
    isRecording.value = true
    isPaused.value = false
    recordingStartTime.value = Date.now() - meeting.totalRecordingTime * 1000
    startRecordingTimer()
  } else if (meeting.isPaused) {
    console.log('恢复录音状态：已暂停')
    isRecording.value = false
    isPaused.value = true
    recordingStartTime.value = meeting.recordStartTime
    totalRecordingTime.value = meeting.totalRecordingTime
  } else {
    console.log('恢复录音状态：未录音')
    isRecording.value = false
    isPaused.value = false
    recordingStartTime.value = 0
    totalRecordingTime.value = meeting.totalRecordingTime
  }

  // 加载标记和转录
  marks.value = meeting.marks || []
  realtimeTranscription.value = meeting.transcription || []

  // 根据转录内容设置状态
  if (realtimeTranscription.value.length > 0) {
    transcriptionStatus.value = 'completed'
    transcriptionError.value = ''
  } else {
    transcriptionStatus.value = 'idle'
    transcriptionError.value = ''
  }

  console.log('会议选择完成')
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
    audioStream.value = await navigator.mediaDevices.getUserMedia({ audio: true })
    audioContext.value = new (window.AudioContext || (window as any).webkitAudioContext)()
    analyser.value = audioContext.value.createAnalyser()
    microphone.value = audioContext.value.createMediaStreamSource(audioStream.value)
    
    analyser.value.fftSize = 256
    microphone.value.connect(analyser.value)
    
    dataArray.value = new Uint8Array(analyser.value.frequencyBinCount)
    
    // 初始化 MediaRecorder
    audioChunks.value = []
    mediaRecorder.value = new MediaRecorder(audioStream.value)
    
    // 创建停止录音的 Promise
    stopRecordingPromise.value = new Promise((resolve) => {
      mediaRecorder.value.onstop = () => {
        // 合并音频数据为 Blob
        const blob = new Blob(audioChunks.value, { type: 'audio/wav' })
        audioBlob.value = blob
        audioUrl.value = URL.createObjectURL(blob)
        resolve(blob)
      }
    })
    
    // 处理录音数据
    mediaRecorder.value.ondataavailable = (event: any) => {
      if (event.data.size > 0) {
        audioChunks.value.push(event.data)
      }
    }
    
    // 开始录音
    mediaRecorder.value.start()
    
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

    // 重置转录状态
    transcriptionStatus.value = 'idle'
    transcriptionError.value = ''

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

  // 暂停 MediaRecorder
  if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
    mediaRecorder.value.pause()
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

  // 继续 MediaRecorder
  if (mediaRecorder.value && mediaRecorder.value.state === 'paused') {
    mediaRecorder.value.resume()
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

  // 停止 MediaRecorder 并等待生成 Blob
  let blob: Blob | null = null
  if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive' && stopRecordingPromise.value) {
    mediaRecorder.value.stop()
    blob = await stopRecordingPromise.value
  }
  
  if (animationFrame.value) {
    cancelAnimationFrame(animationFrame.value)
  }
  
  stopRecordingTimer()
  
  if (audioContext.value) {
    audioContext.value.close()
  }
  
  if (audioStream.value) {
    audioStream.value.getTracks().forEach((track: any) => track.stop())
  }
  
  if (selectedMeeting.value) {
    // 保存录音记录
    const recordingEntry = {
      time: formatTime(recordingStartTime.value / 1000),
      duration: formatRecordingTime(totalRecordingTime.value),
      audioBlob: blob || audioBlob.value,
      audioUrl: audioUrl.value
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

    // 调用保存录音文件接口
    if (blob) {
      try {
        ElMessage.info('正在上传录音文件，请稍候...')
        
        // 将 Blob 转换为 Base64
        const reader = new FileReader()
        reader.readAsDataURL(blob)
        
        reader.onloadend = async () => {
          const base64data = reader.result as string
          try {
            const response = await SaveRecordingFile({
              meeting_id: selectedMeeting.value.id,
              title: selectedMeeting.value.title,
              recording_time: recordingTime.value,
              file_data: base64data
            })
            
            // 如果上传成功，保存返回的文件路径到录音记录
            if (response.data) {
              const lastRecording = selectedMeeting.value.recordings[selectedMeeting.value.recordings.length - 1]
              if (lastRecording) {
                lastRecording.file_path = response.data.file_path
                lastRecording.file_url = response.data.file_url
              }
            }
            
            ElMessage.success(`录音已保存，文件大小: ${response.data?.file_size || '未知'}`)

            // 上传成功后，调用语音转文本 API
            if (siliconflowApiKey.value) {
              try {
                // 设置转录状态为"转录中"
                transcriptionStatus.value = 'transcribing'
                transcriptionError.value = ''

                ElMessage.info('正在转换为文本，请稍候...')
                const transcribeResult = await TranscribeAudio(blob, siliconflowApiKey.value)

                console.log('语音转文本 API 返回结果:', transcribeResult)

                // 尝试从不同格式中提取文本
                let recognizedText = ''

                if (typeof transcribeResult === 'string') {
                  // 如果返回的是纯文本字符串
                  recognizedText = transcribeResult
                } else if (typeof transcribeResult === 'object' && transcribeResult !== null) {
                  // 尝试多种可能的字段名
                  // 优先检查 text 字段
                  if (transcribeResult.text !== undefined && transcribeResult.text !== null) {
                    recognizedText = String(transcribeResult.text)
                  } else if (transcribeResult.transcription !== undefined && transcribeResult.transcription !== null) {
                    recognizedText = String(transcribeResult.transcription)
                  } else if (transcribeResult.result?.text !== undefined && transcribeResult.result?.text !== null) {
                    recognizedText = String(transcribeResult.result.text)
                  } else if (transcribeResult.result?.transcription !== undefined && transcribeResult.result?.transcription !== null) {
                    recognizedText = String(transcribeResult.result.transcription)
                  } else if (transcribeResult.data?.text !== undefined && transcribeResult.data?.text !== null) {
                    recognizedText = String(transcribeResult.data.text)
                  } else if (transcribeResult.data?.transcription !== undefined && transcribeResult.data?.transcription !== null) {
                    recognizedText = String(transcribeResult.data.transcription)
                  } else if (transcribeResult.output !== undefined && transcribeResult.output !== null) {
                    recognizedText = String(transcribeResult.output)
                  }
                  
                  // 如果还是空，尝试查找对象中的第一个字符串类型的值
                  if (!recognizedText) {
                    for (const key in transcribeResult) {
                      if (typeof transcribeResult[key] === 'string' && transcribeResult[key].trim()) {
                        recognizedText = transcribeResult[key]
                        console.log(`从字段 "${key}" 提取到文本:`, recognizedText)
                        break
                      }
                    }
                  }
                }

                if (recognizedText && recognizedText.trim()) {
                  // 将转录结果添加到实时转录列表
                  const currentTime = totalRecordingTime.value
                  realtimeTranscription.value.push({
                    time: currentTime,
                    speaker: '语音识别',
                    text: recognizedText.trim()
                  })

                  // 保存转录结果到会议记录
                  if (selectedMeeting.value) {
                    selectedMeeting.value.transcription = realtimeTranscription.value
                  }

                  // 设置转录状态为"完成"
                  transcriptionStatus.value = 'completed'
                  ElMessage.success('语音转文本成功！')
                } else {
                  // 未找到识别文本，输出详细错误信息
                  console.error('未找到识别文本，返回结果:', transcribeResult)
                  transcriptionStatus.value = 'failed'
                  
                  // 提供更详细的调试信息
                  let debugInfo = ''
                  if (typeof transcribeResult === 'object' && transcribeResult !== null) {
                    const keys = Object.keys(transcribeResult)
                    debugInfo = `返回字段: ${keys.join(', ')}`
                    
                    // 显示每个字段的值
                    const fieldValues = keys.map(key => {
                      const value = transcribeResult[key]
                      const valueStr = typeof value === 'string' ? `"${value}"` : typeof value
                      return `${key}=${valueStr}`
                    }).join(', ')
                    
                    console.log('字段值详情:', fieldValues)
                    transcriptionError.value = `未返回有效文本 (${debugInfo})`
                  } else {
                    transcriptionError.value = '未返回识别结果'
                  }
                  
                  ElMessage.warning(`语音转文本未返回结果。${debugInfo ? debugInfo : '请检查API返回格式'}`)
                }
              } catch (error: any) {
                console.error('语音转文本失败:', error)
                console.error('错误详情:', error.message, error.stack)
                // 设置转录状态为"失败"
                transcriptionStatus.value = 'failed'
                transcriptionError.value = error.message || '未知错误'
                ElMessage.error(`语音转文本失败: ${error.message || '未知错误'}`)
              }
            } else {
              ElMessage.warning('未设置 SiliconFlow API Key，跳过语音转文本')
            }
          } catch (error: any) {
            console.error('保存录音文件失败:', error)
            ElMessage.error(error.msg || '上传录音文件失败，但文件已保存在本地')
          }
        }
        
        reader.onerror = () => {
          console.error('读取音频文件失败')
          ElMessage.warning('读取音频文件失败，但文件已保存在本地')
        }
      } catch (error: any) {
        console.error('处理录音文件失败:', error)
        ElMessage.warning('处理录音文件失败，但文件已保存在本地')
      }
    }
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
const generateSummary = async () => {
  if (!selectedMeeting.value) {
    ElMessage.warning('请选择会议')
    return
  }
  
  // 检查是否有转录内容
  if (!realtimeTranscription.value || realtimeTranscription.value.length === 0) {
    ElMessage.warning('没有会议转录内容，无法生成摘要')
    return
  }
  
  generatingSummary.value = true
  
  try {
    // 合并所有转录文本
    const fullTranscriptionText = realtimeTranscription.value
      .map(seg => `[${formatTime(seg.time)}] ${seg.speaker}：${seg.text}`)
      .join('\n')
    
    // 提取纯文本用于分析
    const pureText = realtimeTranscription.value
      .map(seg => seg.text)
      .join(' ')
    
    console.log('开始生成会议摘要，转录文本长度:', pureText.length, '字符')
    
    // 使用简单的关键词提取和文本分析生成摘要
    const summary = analyzeTranscriptionAndGenerateSummary(
      selectedMeeting.value.title,
      pureText,
      realtimeTranscription.value
    )
    
    // 保存完整的转录文本到 summary 中
    summary.transcription_text = fullTranscriptionText
    
    selectedMeeting.value.summary = summary
    generatingSummary.value = false
    ElMessage.success('会议摘要生成成功！')
  } catch (error: any) {
    console.error('生成摘要失败:', error)
    generatingSummary.value = false
    ElMessage.error(`生成摘要失败: ${error.message || '未知错误'}`)
  }
}

// 分析转录文本并生成摘要
const analyzeTranscriptionAndGenerateSummary = (meetingTitle: string, transcriptionText: string, segments: any[]) => {
  console.log('分析转录文本...')
  
  // 提取关键词（简单实现：基于词汇频率）
  const keywords = extractKeywords(transcriptionText)
  
  // 识别讨论要点（基于转录段落和关键词）
  const points = extractDiscussionPoints(segments, keywords)
  
  // 识别决策事项（查找包含"决定"、"同意"、"确定"等词汇的句子）
  const decisions = extractDecisions(segments)
  
  // 识别待办事项（查找包含"需要"、"安排"、"计划"等词汇的句子）
  const actionItems = extractActionItems(segments)
  
  // 识别问题和风险
  const issues = extractIssues(segments)
  
  // 识别参与人员
  const participants = [...new Set(segments.map(s => s.speaker))]
    .filter(s => s !== '语音识别' && s)
  
  console.log('摘要分析完成:', {
    topic: meetingTitle,
    pointsCount: points.length,
    decisionsCount: decisions.length,
    actionItemsCount: actionItems.length,
    issuesCount: issues.length,
    participants
  })
  
  return {
    topic: meetingTitle,
    transcription_text: '', // 会在调用时填充
    points: points.length > 0 ? points : ['暂无明确的讨论要点'],
    decisions: decisions.length > 0 ? decisions : ['暂无明确的决策事项'],
    action_items: actionItems.length > 0 ? actionItems : [],
    issues: issues.length > 0 ? issues : [],
    participants: participants.length > 0 ? participants : [],
    keywords: keywords.slice(0, 10), // 取前10个关键词
    duration: segments.length > 0 ? formatTime(segments[segments.length - 1].time) : '0:00'
  }
}

// 提取关键词
const extractKeywords = (text: string): string[] => {
  // 简单的关键词提取算法
  const stopWords = ['的', '了', '是', '在', '和', '与', '或', '但', '而', '等', '很', '也', '都', '就', '这', '那', '我', '你', '他', '她', '它', '我们', '你们', '他们']
  const words = text.split(/[\s,。！？，、；：""''（）\[\]]+/)
    .filter(word => word.length > 1 && !stopWords.includes(word))
  
  // 统计词频
  const wordCount = new Map<string, number>()
  words.forEach(word => {
    wordCount.set(word, (wordCount.get(word) || 0) + 1)
  })
  
  // 按频率排序
  return Array.from(wordCount.entries())
    .sort((a, b) => b[1] - a[1])
    .map(([word]) => word)
}

// 提取讨论要点
const extractDiscussionPoints = (segments: any[], keywords: string[]): string[] => {
  const points: string[] = []
  const usedSegments = new Set<number>()
  
  // 根据关键词和时间段提取讨论要点
  segments.forEach((seg, index) => {
    if (usedSegments.has(index)) return
    
    const text = seg.text
    const time = formatTime(seg.time)
    
    // 检查是否包含关键词
    const hasKeyword = keywords.some(kw => text.includes(kw))
    
    // 检查是否是独立的讨论段落（长度适中）
    if (hasKeyword && text.length > 5 && text.length < 100) {
      points.push(`[${time}] ${seg.speaker}: ${text}`)
      usedSegments.add(index)
      
      // 标记相邻的短片段为已使用
      if (index + 1 < segments.length && segments[index + 1].text.length < 20) {
        usedSegments.add(index + 1)
      }
    }
  })
  
  // 如果没有提取到要点，返回一些默认的
  if (points.length === 0) {
    const keySegments = segments.filter(seg => seg.text.length > 10)
    keySegments.slice(0, 3).forEach(seg => {
      points.push(`[${formatTime(seg.time)}] ${seg.speaker}: ${seg.text}`)
    })
  }
  
  return points.slice(0, 8) // 最多返回8个要点
}

// 提取决策事项
const extractDecisions = (segments: any[]): string[] => {
  const decisionKeywords = ['决定', '同意', '确定', '选定', '批准', '通过', '采纳', '采用', '确认', '认可']
  const decisions: string[] = []
  
  segments.forEach(seg => {
    const text = seg.text
    
    // 查找包含决策关键词的句子
    decisionKeywords.forEach(keyword => {
      if (text.includes(keyword) && text.length > 3) {
        const time = formatTime(seg.time)
        // 提取完整的决策句子
        const sentences = text.split(/[。！？\n]/)
        sentences.forEach((sentence: string) => {
          if (sentence.includes(keyword) && sentence.trim().length > 2) {
            const decision = `[${time}] ${seg.speaker} ${sentence.trim()}`
            if (!decisions.includes(decision)) {
              decisions.push(decision)
            }
          }
        })
      }
    })
  })
  
  return decisions.slice(0, 5) // 最多返回5个决策
}

// 提取待办事项
const extractActionItems = (segments: any[]): string[] => {
  const actionKeywords = ['需要', '安排', '计划', '要', '应该', '必须', '准备', '完成', '负责', '跟进', '处理', '解决']
  const actions: string[] = []
  
  segments.forEach(seg => {
    const text = seg.text
    
    actionKeywords.forEach(keyword => {
      if (text.includes(keyword) && text.length > 3) {
        const time = formatTime(seg.time)
        const sentences = text.split(/[。！？\n]/)
        sentences.forEach((sentence: string) => {
          if (sentence.includes(keyword) && sentence.trim().length > 2) {
            const action = `[${time}] ${seg.speaker} ${sentence.trim()}`
            if (!actions.includes(action)) {
              actions.push(action)
            }
          }
        })
      }
    })
  })
  
  return actions.slice(0, 6) // 最多返回6个待办事项
}

// 提取问题和风险
const extractIssues = (segments: any[]): string[] => {
  const issueKeywords = ['问题', '困难', '挑战', '风险', '担心', '疑虑', '不足', '缺陷', '错误', '故障', '影响']
  const issues: string[] = []
  
  segments.forEach(seg => {
    const text = seg.text
    
    issueKeywords.forEach(keyword => {
      if (text.includes(keyword) && text.length > 3) {
        const time = formatTime(seg.time)
        const sentences = text.split(/[。！？\n]/)
        sentences.forEach((sentence: string) => {
          if (sentence.includes(keyword) && sentence.trim().length > 2) {
            const issue = `[${time}] ${seg.speaker} ${sentence.trim()}`
            if (!issues.includes(issue)) {
              issues.push(issue)
            }
          }
        })
      }
    })
  })
  
  return issues.slice(0, 5) // 最多返回5个问题
}

// 复制摘要
const copySummary = () => {
  if (!selectedMeeting.value || !selectedMeeting.value.summary) {
    ElMessage.warning('没有可复制的摘要')
    return
  }
  
  const summary = selectedMeeting.value.summary
  let summaryText = `会议摘要\n${'='.repeat(50)}\n\n`
  summaryText += `会议主题：${summary.topic}\n`
  
  if (summary.participants && summary.participants.length > 0) {
    summaryText += `\n参与人员：${summary.participants.join('、')}\n`
  }
  
  if (summary.keywords && summary.keywords.length > 0) {
    summaryText += `\n关键词：${summary.keywords.join('、')}\n`
  }
  
  if (summary.points && summary.points.length > 0) {
    summaryText += `\n讨论要点：\n`
    summary.points.forEach((point: string, index: number) => {
      summaryText += `${index + 1}. ${point}\n`
    })
  }
  
  if (summary.decisions && summary.decisions.length > 0) {
    summaryText += `\n决策事项：\n`
    summary.decisions.forEach((decision: string, index: number) => {
      summaryText += `${index + 1}. ${decision}\n`
    })
  }
  
  if (summary.action_items && summary.action_items.length > 0) {
    summaryText += `\n待办事项：\n`
    summary.action_items.forEach((item: string, index: number) => {
      summaryText += `${index + 1}. [ ] ${item}\n`
    })
  }
  
  if (summary.issues && summary.issues.length > 0) {
    summaryText += `\n问题和风险：\n`
    summary.issues.forEach((issue: string, index: number) => {
      summaryText += `${index + 1}. ${issue}\n`
    })
  }
  
  if (summary.transcription_text) {
    summaryText += `\n\n${'='.repeat(50)}\n完整转录文本：\n${summary.transcription_text}\n`
  }
  
  // 复制到剪贴板
  try {
    navigator.clipboard.writeText(summaryText).then(() => {
      ElMessage.success('摘要已复制到剪贴板')
    }).catch(() => {
      // 降级方案
      const textarea = document.createElement('textarea')
      textarea.value = summaryText
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
      ElMessage.success('摘要已复制到剪贴板')
    })
  } catch (error) {
    ElMessage.error('复制失败')
    console.error('复制失败:', error)
  }
}

// 导出转录文本
const downloadTranscription = () => {
  if (!selectedMeeting.value || !selectedMeeting.value.summary?.transcription_text) {
    ElMessage.warning('没有可导出的转录文本')
    return
  }
  
  const transcriptionText = selectedMeeting.value.summary.transcription_text
  const filename = `会议转录_${selectedMeeting.value.title}_${new Date().toISOString().slice(0, 10)}.txt`
  
  try {
    // 创建 Blob
    const blob = new Blob([transcriptionText], { type: 'text/plain;charset=utf-8' })
    
    // 创建下载链接
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    ElMessage.success('转录文本已导出')
  } catch (error) {
    ElMessage.error('导出失败')
    console.error('导出失败:', error)
  }
}

// 保存笔记
const saveNotes = () => {
  if (selectedMeeting.value) {
    selectedMeeting.value.notes = meetingNotes.value
  }
  ElMessage.success('笔记已保存')
}

// 播放录音
const playRecording = async (rec: any) => {
  if (!selectedMeeting.value) {
    ElMessage.warning('请选择会议')
    return
  }

  try {
    let audioUrl = null

    // 优先使用本地的 audioBlob
    if (rec.audioBlob) {
      audioUrl = URL.createObjectURL(rec.audioBlob)
    } else if (rec.audioUrl) {
      audioUrl = rec.audioUrl
    } else if (rec.file_url) {
      // 如果有后台的 file_url，直接使用
      audioUrl = rec.file_url
    } else if (rec.file_path) {
      // 如果有 file_path，从后台下载
      try {
        ElMessage.info('正在从服务器加载录音...')
        const response = await DownloadRecordingFile(rec.file_path)
        // 创建 Blob URL
        const blob = new Blob([response], { type: 'audio/wav' })
        audioUrl = URL.createObjectURL(blob)
        // 保存到录音记录中，避免重复下载
        rec.audioBlob = blob
      } catch (error: any) {
        console.error('下载录音失败:', error)
        ElMessage.error('从服务器下载录音失败')
        return
      }
    }

    if (audioUrl) {
      const audio = new Audio(audioUrl)
      audio.play()
      ElMessage.success(`正在播放录音: ${rec.time}`)
      
      // 如果是临时创建的 URL，在播放结束后释放
      if (rec.audioBlob || rec.file_path) {
        audio.onended = () => {
          URL.revokeObjectURL(audioUrl)
        }
      }
    } else {
      ElMessage.warning('该录音没有可用的音频文件')
    }
  } catch (error: any) {
    console.error('播放录音失败:', error)
    ElMessage.error('播放录音失败')
  }
}

// 下载录音
const downloadRecording = async (rec: any) => {
  if (!selectedMeeting.value) {
    ElMessage.warning('请选择会议')
    return
  }

  try {
    let blob = null
    let filename = `meeting_${selectedMeeting.value.id}_${rec.time.replace(':', '-')}.wav`

    // 优先使用本地的 audioBlob
    if (rec.audioBlob) {
      blob = rec.audioBlob
    } else if (rec.file_url) {
      // 如果有后台的 file_url，直接通过链接下载
      try {
        ElMessage.info('正在从服务器下载录音...')
        const response = await DownloadRecordingFile(rec.file_url)
        blob = new Blob([response], { type: 'audio/wav' })
      } catch (error: any) {
        console.error('从 file_url 下载录音失败:', error)
        ElMessage.error('从服务器下载录音失败')
        return
      }
    } else if (rec.file_path) {
      // 如果有 file_path，从后台下载
      try {
        ElMessage.info('正在从服务器下载录音...')
        const response = await DownloadRecordingFile(rec.file_path)
        blob = new Blob([response], { type: 'audio/wav' })
      } catch (error: any) {
        console.error('下载录音失败:', error)
        ElMessage.error('从服务器下载录音失败')
        return
      }
    } else {
      ElMessage.warning('该录音没有可下载的音频文件')
      return
    }

    // 触发下载
    if (blob) {
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      ElMessage.success(`下载录音: ${rec.time}`)
    } else {
      ElMessage.warning('该录音没有可用的音频文件')
    }
  } catch (error: any) {
    console.error('下载录音失败:', error)
    ElMessage.error('下载录音失败')
  }
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
  settingsForm.value.apiKey = siliconflowApiKey.value
  settingsDialogVisible.value = true
}

// 保存设置
const saveSettings = () => {
  siliconflowApiKey.value = settingsForm.value.apiKey
  localStorage.setItem('siliconflow_api_key', siliconflowApiKey.value)
  settingsDialogVisible.value = false
  ElMessage.success('API Key 已保存')
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

  // 从 localStorage 读取 API Key
  const savedApiKey = localStorage.getItem('siliconflow_api_key')
  if (savedApiKey) {
    siliconflowApiKey.value = savedApiKey
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
  pointer-events: auto;
  user-select: none;
}

.meeting-item:hover {
  background: #e5e7eb;
  transform: translateX(4px);
}

.meeting-item:active {
  transform: translateX(2px);
  background: #d9d9d9;
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

/* 转录状态提示 */
.transcription-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 20px;
  background: #f9fafb;
  border-radius: 6px;
  margin-bottom: 12px;
  font-size: 14px;
  color: #606266;
}

.transcription-status.idle {
  color: #909399;
  background: #f5f7fa;
  border: 2px dashed #e4e7ed;
}

.transcription-status.transcribing {
  color: #e6a23c;
  background: #fdf6ec;
  border: 1px solid #faecd8;
}

.transcription-status.failed {
  color: #f56c6c;
  background: #fef0f0;
  border: 1px solid #fde2e2;
}

/* 转录中动画 */
.loading-animation {
  display: flex;
  gap: 6px;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #e6a23c;
  animation: pulse 1.5s ease-in-out infinite;
}

.pulse-dot:nth-child(2) {
  animation-delay: 0.3s;
}

.pulse-dot:nth-child(3) {
  animation-delay: 0.6s;
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.3;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.2);
  }
}

/* 转录完成提示 */
.transcription-complete-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  margin-top: 12px;
  background: #f0f9ff;
  border: 1px solid #d1fae5;
  border-radius: 6px;
  color: #67c23a;
  font-size: 13px;
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

/* 摘要部分的新样式 */
.section-header .header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.item-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 8px;
}

.item-title .el-icon {
  font-size: 16px;
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

/* 决策事项列表 */
.decision-list li {
  position: relative;
  padding-left: 16px;
}

.decision-list li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #67c23a;
  font-weight: bold;
}

/* 待办事项列表 */
.action-list li {
  position: relative;
  padding-left: 24px;
}

.action-list li::before {
  content: '☐';
  position: absolute;
  left: 0;
  color: #409eff;
  font-weight: bold;
}

/* 问题列表 */
.issue-list li {
  position: relative;
  padding-left: 16px;
  color: #e6a23c;
}

.issue-list li::before {
  content: '!';
  position: absolute;
  left: 0;
  color: #f56c6c;
  font-weight: bold;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #fef0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  line-height: 1;
}

/* 完整转录文本 */
.full-transcription {
  margin-top: 16px;
}

.full-transcription .item-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.transcription-text {
  background: #f9fafb;
  padding: 16px;
  border-radius: 6px;
  border-left: 4px solid #409eff;
  max-height: 400px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 13px;
  line-height: 1.8;
  color: #606266;
}

.transcription-text::-webkit-scrollbar {
  width: 6px;
}

.transcription-text::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.transcription-text::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

/* 响应式调整 */
@media (max-width: 1400px) {
  .main-content {
    grid-template-columns: 280px 1fr 320px;
  }
}

@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .left-panel,
  .right-panel {
    height: auto;
  }
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
