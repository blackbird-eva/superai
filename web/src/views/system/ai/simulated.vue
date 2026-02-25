<template>
  <div class="recorder-container">
    <el-card class="recorder-card">
      <template #header>
        <div class="card-header">
          <span>录音工具</span>
          <el-tag :type="recordingStatus ? 'danger' : 'success'">
            {{ recordingStatus ? '录音中' : '就绪' }}
          </el-tag>
        </div>
      </template>

      <!-- 录音控制区 -->
      <div class="recorder-controls">
        <div class="timer-display">
          <span class="timer">{{ formattedTime }}</span>
        </div>

        <div class="button-group">
          <el-button
            :type="recordingStatus ? 'danger' : 'primary'"
            :icon="recordingStatus ? 'VideoPause' : 'Microphone'"
            size="large"
            @click="toggleRecording"
            :disabled="hasNoPermission"
          >
            {{ recordingStatus ? '停止录音' : '开始录音' }}
          </el-button>

          <el-button
            v-if="!recordingStatus && currentRecording"
            type="success"
            icon="Download"
            size="large"
            @click="saveRecording"
          >
            保存录音
          </el-button>

          <el-button
            v-if="!recordingStatus && currentRecording"
            type="warning"
            icon="Delete"
            size="large"
            @click="discardRecording"
          >
            丢弃录音
          </el-button>
        </div>

        <div v-if="!hasNoPermission && currentRecording && !recordingStatus" class="preview-section">
          <el-divider>当前录音预览</el-divider>
          <audio
            ref="currentAudio"
            :src="currentRecordingUrl"
            controls
            style="width: 100%"
          ></audio>
        </div>
      </div>
    </el-card>

    <!-- 录音列表 -->
    <el-card class="recordings-list-card">
      <template #header>
        <div class="card-header">
          <span>录音记录</span>
          <el-button
            type="danger"
            size="small"
            icon="Delete"
            @click="clearAllRecordings"
            :disabled="recordings.length === 0"
          >
            清空全部
          </el-button>
        </div>
      </template>

      <div v-if="recordings.length === 0" class="empty-state">
        <el-empty description="暂无录音记录"></el-empty>
      </div>

      <div v-else class="recordings-list">
        <div
          v-for="(recording, index) in recordings"
          :key="recording.id"
          class="recording-item"
        >
          <div class="recording-info">
            <div class="recording-name">{{ recording.name }}</div>
            <div class="recording-time">{{ recording.duration }} · {{ recording.date }}</div>
          </div>

          <div class="recording-actions">
            <audio
              :src="recording.url"
              controls
              class="audio-player"
            ></audio>

            <el-button
              type="primary"
              size="small"
              icon="Download"
              @click="downloadRecording(recording)"
            >
              下载
            </el-button>

            <el-button
              type="danger"
              size="small"
              icon="Delete"
              @click="deleteRecording(index)"
            >
              删除
            </el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 权限提示 -->
    <el-dialog
      v-model="permissionDialogVisible"
      title="麦克风权限"
      width="400px"
      :close-on-click-modal="false"
    >
      <div class="permission-content">
        <el-icon :size="60" color="#E6A23C" class="permission-icon">
          <WarningFilled />
        </el-icon>
        <p>需要麦克风权限才能使用录音功能</p>
        <p class="permission-tip">请允许浏览器访问您的麦克风</p>
      </div>
      <template #footer>
        <el-button type="primary" @click="requestPermission">授予权限</el-button>
        <el-button @click="permissionDialogVisible = false">取消</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { WarningFilled } from '@element-plus/icons-vue'

interface Recording {
  id: number
  name: string
  url: string
  blob: Blob
  duration: string
  date: string
}

// 状态管理
const recordingStatus = ref(false)
const hasNoPermission = ref(false)
const permissionDialogVisible = ref(false)
const currentRecording = ref<Blob | null>(null)
const recordings = ref<Recording[]>([])
const currentAudio = ref<HTMLAudioElement | null>(null)

// 录音相关
let mediaRecorder: MediaRecorder | null = null
let audioChunks: Blob[] = []
let startTime: number = 0
let timerInterval: number | null = null

// 计时器
const recordingTime = ref(0)

const formattedTime = computed(() => {
  const minutes = Math.floor(recordingTime.value / 60)
  const seconds = recordingTime.value % 60
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})

const currentRecordingUrl = computed(() => {
  return currentRecording.value ? URL.createObjectURL(currentRecording.value) : ''
})

// 请求麦克风权限
async function requestPermission() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    hasNoPermission.value = false
    permissionDialogVisible.value = false
    ElMessage.success('麦克风权限已获取')
    // 立即停止获取的流
    stream.getTracks().forEach(track => track.stop())
  } catch (error) {
    console.error('获取麦克风权限失败:', error)
    hasNoPermission.value = true
    ElMessage.error('无法获取麦克风权限')
  }
}

// 切换录音状态
async function toggleRecording() {
  if (recordingStatus.value) {
    stopRecording()
  } else {
    await startRecording()
  }
}

// 开始录音
async function startRecording() {
  try {
    // 检查权限
    if (hasNoPermission.value) {
      permissionDialogVisible.value = true
      return
    }

    // 获取音频流
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

    // 创建 MediaRecorder
    mediaRecorder = new MediaRecorder(stream, {
      mimeType: 'audio/webm;codecs=opus'
    })

    audioChunks = []

    // 处理数据可用事件
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data)
      }
    }

    // 处理录音结束事件
    mediaRecorder.onstop = () => {
      const blob = new Blob(audioChunks, { type: 'audio/webm' })
      currentRecording.value = blob
      stream.getTracks().forEach(track => track.stop())
    }

    // 开始录音
    mediaRecorder.start()
    recordingStatus.value = true

    // 开始计时
    startTime = Date.now()
    recordingTime.value = 0
    timerInterval = setInterval(() => {
      recordingTime.value = Math.floor((Date.now() - startTime) / 1000)
    }, 1000)

    ElMessage.success('开始录音')
  } catch (error) {
    console.error('录音启动失败:', error)
    hasNoPermission.value = true
    permissionDialogVisible.value = true
  }
}

// 停止录音
function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
    recordingStatus.value = false

    // 停止计时
    if (timerInterval) {
      clearInterval(timerInterval)
      timerInterval = null
    }

    ElMessage.success('录音已完成')
  }
}

// 保存录音
function saveRecording() {
  if (!currentRecording.value) {
    ElMessage.warning('没有录音可保存')
    return
  }

  const now = new Date()
  const recording: Recording = {
    id: Date.now(),
    name: `录音_${recordings.value.length + 1}`,
    url: URL.createObjectURL(currentRecording.value),
    blob: currentRecording.value,
    duration: formattedTime.value,
    date: now.toLocaleString('zh-CN')
  }

  recordings.value.unshift(recording)
  ElMessage.success('录音已保存')

  // 清空当前录音
  currentRecording.value = null
}

// 丢弃录音
function discardRecording() {
  ElMessageBox.confirm('确定要丢弃当前录音吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    currentRecording.value = null
    ElMessage.success('录音已丢弃')
  }).catch(() => {})
}

// 下载录音
function downloadRecording(recording: Recording) {
  const a = document.createElement('a')
  a.href = recording.url
  a.download = `${recording.name}.webm`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  ElMessage.success('开始下载')
}

// 删除录音
function deleteRecording(index: number) {
  ElMessageBox.confirm('确定要删除这条录音吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const recording = recordings.value[index]
    URL.revokeObjectURL(recording.url)
    recordings.value.splice(index, 1)
    ElMessage.success('录音已删除')
  }).catch(() => {})
}

// 清空所有录音
function clearAllRecordings() {
  ElMessageBox.confirm('确定要清空所有录音吗？此操作不可恢复', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'error'
  }).then(() => {
    recordings.value.forEach(recording => {
      URL.revokeObjectURL(recording.url)
    })
    recordings.value = []
    ElMessage.success('已清空所有录音')
  }).catch(() => {})
}

// 组件卸载时清理资源
onBeforeUnmount(() => {
  // 停止录音
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
  }

  // 清理计时器
  if (timerInterval) {
    clearInterval(timerInterval)
  }

  // 释放所有 URL 对象
  recordings.value.forEach(recording => {
    URL.revokeObjectURL(recording.url)
  })
})
</script>

<style scoped lang="scss">
.recorder-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.recorder-card,
.recordings-list-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  font-size: 16px;
}

.recorder-controls {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.timer-display {
  display: flex;
  justify-content: center;
  padding: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  margin-bottom: 20px;
}

.timer {
  font-size: 72px;
  font-weight: bold;
  color: white;
  font-family: 'Courier New', monospace;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.button-group {
  display: flex;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap;
}

.preview-section {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.empty-state {
  padding: 40px 0;
}

.recordings-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.recording-item {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 20px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    border-color: #d1d5db;
  }
}

.recording-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.recording-name {
  font-weight: bold;
  font-size: 15px;
  color: #303133;
}

.recording-time {
  font-size: 13px;
  color: #909399;
}

.recording-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.audio-player {
  flex: 1;
  min-width: 200px;
  max-width: 400px;
}

.permission-content {
  text-align: center;
  padding: 20px;
}

.permission-icon {
  margin-bottom: 20px;
}

.permission-content p {
  margin: 10px 0;
  font-size: 14px;
}

.permission-tip {
  color: #909399;
  font-size: 12px;
}

// 响应式设计
@media (max-width: 768px) {
  .recorder-container {
    padding: 10px;
  }

  .timer {
    font-size: 48px;
  }

  .button-group {
    flex-direction: column;
    align-items: stretch;
  }

  .recording-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .audio-player {
    max-width: 100%;
  }
}
</style>
