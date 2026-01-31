<template>
  <div class="translation-workstation">
    <!-- 头部区域 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">AI 翻译工作台</h1>
        <p class="page-subtitle">专业、精准、多语种智能翻译服务</p>
      </div>
    </div>

    <!-- 模式切换 -->
    <div class="mode-tabs">
      <el-radio-group v-model="activeMode" @change="handleModeChange">
        <el-radio-button label="text">文本翻译</el-radio-button>
        <el-radio-button label="image">图片翻译</el-radio-button>
        <el-radio-button label="document">文档翻译</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 文本翻译模式 -->
    <div v-if="activeMode === 'text'" class="translation-mode">
      <div class="translation-container">
        <!-- 左侧输入区域 -->
        <div class="translation-panel input-panel">
          <div class="panel-header">
            <div class="header-left">
              <el-select
                v-model="sourceLang"
                placeholder="选择语言"
                @change="handleSourceLangChange"
                class="lang-select"
              >
                <el-option label="自动检测" value="auto"></el-option>
                <el-option label="中文" value="zh"></el-option>
                <el-option label="英语" value="en"></el-option>
                <el-option label="日语" value="ja"></el-option>
                <el-option label="韩语" value="ko"></el-option>
                <el-option label="法语" value="fr"></el-option>
                <el-option label="德语" value="de"></el-option>
                <el-option label="西班牙语" value="es"></el-option>
                <el-option label="俄语" value="ru"></el-option>
              </el-select>
              <span v-if="detectedLang && sourceLang === 'auto'" class="detected-lang">
                检测为: {{ detectedLangName }}
              </span>
            </div>
            <el-button
              text
              icon="Delete"
              @click="clearInput"
              v-if="inputText"
            >
              清空
            </el-button>
          </div>

          <el-input
            v-model="inputText"
            type="textarea"
            :rows="12"
            placeholder="请输入或粘贴需要翻译的文本..."
            class="translation-textarea"
            @input="handleInputChange"
            @paste="handlePaste"
          ></el-input>

          <div class="panel-footer">
            <div class="char-count">{{ inputText.length }} 字符</div>
            <div class="action-buttons">
              <el-button
                text
                icon="Microphone"
                @click="startSpeech"
                v-if="!isRecording"
              >
                语音输入
              </el-button>
              <el-button
                text
                type="danger"
                icon="Microphone"
                @click="stopSpeech"
                v-else
              >
                停止录音
              </el-button>
              <el-button text icon="CopyDocument" @click="copyText(inputText)">
                复制
              </el-button>
            </div>
          </div>
        </div>

        <!-- 中间操作区 -->
        <div class="translation-actions">
          <el-button
            type="primary"
            circle
            size="large"
            :loading="translating"
            @click="translate"
          >
            <el-icon><Position /></el-icon>
          </el-button>
          <el-button
            circle
            size="large"
            @click="swapLanguages"
          >
            <el-icon><Sort /></el-icon>
          </el-button>
        </div>

        <!-- 右侧输出区域 -->
        <div class="translation-panel output-panel">
          <div class="panel-header">
            <el-select
              v-model="targetLang"
              placeholder="目标语言"
              @change="handleTargetLangChange"
              class="lang-select"
            >
              <el-option label="英语" value="en"></el-option>
              <el-option label="中文" value="zh"></el-option>
              <el-option label="日语" value="ja"></el-option>
              <el-option label="韩语" value="ko"></el-option>
              <el-option label="法语" value="fr"></el-option>
              <el-option label="德语" value="de"></el-option>
              <el-option label="西班牙语" value="es"></el-option>
              <el-option label="俄语" value="ru"></el-option>
            </el-select>
          </div>

          <div class="output-content">
            <div v-if="outputText" class="translated-text">
              {{ outputText }}
            </div>
            <div v-else class="placeholder-text">
              <el-icon size="48" color="#d0d7de"><Position /></el-icon>
              <p>翻译结果将显示在这里</p>
            </div>
          </div>

          <div class="panel-footer">
            <div class="action-buttons">
              <el-button
                text
                icon="CopyDocument"
                @click="copyText(outputText)"
                :disabled="!outputText"
              >
                复制
              </el-button>
              <el-button
                text
                icon="Download"
                @click="downloadText"
                :disabled="!outputText"
              >
                下载
              </el-button>
              <el-button
                text
                icon="ChatDotRound"
                @click="playAudio"
                :disabled="!outputText"
              >
                朗读
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 历史记录 -->
      <div class="history-section" v-if="history.length > 0">
        <div class="history-header">
          <h3>历史记录</h3>
          <el-button text @click="clearHistory">清空</el-button>
        </div>
        <div class="history-list">
          <div
            v-for="(item, index) in history.slice(0, 5)"
            :key="index"
            class="history-item"
            @click="useHistory(item)"
          >
            <div class="history-source">{{ item.source }}</div>
            <div class="history-target">{{ item.target }}</div>
            <div class="history-langs">
              {{ item.sourceLang }} → {{ item.targetLang }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 图片翻译模式 -->
    <div v-if="activeMode === 'image'" class="translation-mode">
      <div class="image-translation-container">
        <div class="upload-area">
          <el-upload
            class="image-uploader"
            :show-file-list="false"
            :before-upload="beforeImageUpload"
            :on-success="handleImageSuccess"
            :drag="true"
            accept="image/*"
          >
            <div v-if="!imageUrl" class="upload-placeholder">
              <el-icon class="upload-icon"><Picture /></el-icon>
              <div class="upload-text">拖拽图片到此处或点击上传</div>
              <div class="upload-hint">支持 JPG、PNG、GIF 格式，大小不超过 10MB</div>
            </div>
            <img v-else :src="imageUrl" class="uploaded-image" alt="uploaded" />
          </el-upload>

          <div v-if="imageUrl" class="image-actions">
            <el-button type="primary" @click="translateImage" :loading="translating">
              开始翻译
            </el-button>
            <el-button @click="clearImage">重新上传</el-button>
          </div>
        </div>

        <div class="translation-result">
          <div class="result-header">
            <h3>翻译结果</h3>
            <el-button text icon="CopyDocument" @click="copyText(imageResult)">
              复制
            </el-button>
          </div>
          <div class="result-content">
            <div v-if="imageResult" class="result-text">{{ imageResult }}</div>
            <div v-else class="placeholder-text">
              <el-icon size="48" color="#d0d7de"><Position /></el-icon>
              <p>图片翻译结果将显示在这里</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 文档翻译模式 -->
    <div v-if="activeMode === 'document'" class="translation-mode">
      <div class="document-translation-container">
        <div class="upload-area">
          <el-upload
            class="document-uploader"
            :show-file-list="true"
            :before-upload="beforeDocUpload"
            :on-remove="handleDocRemove"
            :file-list="fileList"
            :drag="true"
            accept=".pdf,.doc,.docx,.txt,.xls,.xlsx"
            :limit="1"
          >
            <div v-if="fileList.length === 0" class="upload-placeholder">
              <el-icon class="upload-icon"><Document /></el-icon>
              <div class="upload-text">拖拽文档到此处或点击上传</div>
              <div class="upload-hint">支持 PDF、Word、TXT、Excel 格式，大小不超过 50MB</div>
            </div>
            <el-button v-else type="primary" icon="Upload">
              重新上传
            </el-button>
          </el-upload>

          <div v-if="fileList.length > 0" class="doc-actions">
            <el-button type="primary" @click="translateDocument" :loading="translating">
              开始翻译
            </el-button>
          </div>
        </div>

        <div class="translation-result">
          <div class="result-header">
            <h3>翻译结果</h3>
            <div v-if="docResult" class="result-actions">
              <el-button type="primary" icon="Download" @click="downloadDocument">
                下载文档
              </el-button>
              <el-button icon="View" @click="previewDocument">
                在线预览
              </el-button>
            </div>
          </div>
          <div class="result-content">
            <div v-if="docResult" class="result-preview">
              <el-alert
                title="翻译完成"
                type="success"
                :description="`文档 ${fileList[0]?.name} 已成功翻译为 ${languageMap[targetLang]}`"
                :closable="false"
              />
            </div>
            <div v-else class="placeholder-text">
              <el-icon size="48" color="#d0d7de"><Document /></el-icon>
              <p>文档翻译结果将显示在这里</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 示例文本 -->
    <div class="example-section" v-if="activeMode === 'text' && !inputText">
      <h3>示例文本</h3>
      <div class="example-list">
        <div
          v-for="(example, index) in examples"
          :key="index"
          class="example-item"
          @click="useExample(example)"
        >
          <div class="example-icon">{{ example.icon }}</div>
          <div class="example-content">
            <div class="example-title">{{ example.title }}</div>
            <div class="example-text">{{ example.text }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Position, Sort, Picture, Document, Microphone,
  CopyDocument, Download, ChatDotRound, Delete,
  Upload, View
} from '@element-plus/icons-vue'
import { Translate } from './api'

// 翻译模式
const activeMode = ref('text')

// 语言设置
const sourceLang = ref('auto')
const targetLang = ref('en')

// 输入输出
const inputText = ref('')
const outputText = ref('')

// 翻译状态
const translating = ref(false)

// 录音状态
const isRecording = ref(false)

// 检测到的语言
const detectedLang = ref('')

// 图片相关
const imageUrl = ref('')
const imageResult = ref('')

// 文档相关
const fileList = ref<any[]>([])
const docResult = ref(false)

// 历史记录
const history = ref<any[]>([])

// 语言映射
const languageMap: { [key: string]: string } = {
  auto: '自动检测',
  zh: '中文',
  en: '英语',
  ja: '日语',
  ko: '韩语',
  fr: '法语',
  de: '德语',
  es: '西班牙语',
  ru: '俄语'
}

// 示例文本
const examples = [
  {
    icon: '👋',
    title: '问候语',
    text: 'Hello, how are you today?'
  },
  {
    icon: '💼',
    title: '商务邮件',
    text: 'Dear Sir/Madam, I am writing to inquire about your products and services.'
  },
  {
    icon: '📖',
    title: '学术文本',
    text: 'Artificial intelligence has revolutionized the way we interact with technology.'
  },
  {
    icon: '🌍',
    title: '旅游用语',
    text: 'Where is the nearest train station to the city center?'
  }
]

// 模拟语言检测结果
const detectedLangName = computed(() => {
  return languageMap[detectedLang.value] || ''
})

// 模拟翻译结果
const mockTranslations: { [key: string]: { [key: string]: string } } = {
  'en->zh': {
    'hello': '你好',
    'how are you': '你好吗',
    'dear sir': '尊敬的先生',
    'artificial intelligence': '人工智能',
    'where is': '在哪里'
  },
  'zh->en': {
    '你好': 'Hello',
    '您好': 'Hello',
    '人工智能': 'Artificial Intelligence',
    '中国': 'China',
    '谢谢': 'Thank you'
  }
}

// 处理模式切换
const handleModeChange = (mode: string) => {
  // 重置状态
  inputText.value = ''
  outputText.value = ''
  imageUrl.value = ''
  imageResult.value = ''
  fileList.value = []
  docResult.value = false
}

// 处理源语言变化
const handleSourceLangChange = () => {
  detectedLang.value = ''
}

// 处理目标语言变化
const handleTargetLangChange = () => {
  // 可以在这里触发自动翻译
}

// 输入变化时检测语言
const handleInputChange = () => {
  if (sourceLang.value === 'auto' && inputText.value) {
    detectLanguage()
  }
}

// 模拟语言检测
const detectLanguage = () => {
  // 简单的语言检测逻辑
  const text = inputText.value.toLowerCase()
  if (text.match(/[\u4e00-\u9fa5]/)) {
    detectedLang.value = 'zh'
  } else if (text.match(/[a-z]/)) {
    detectedLang.value = 'en'
  } else if (text.match(/[\u3040-\u309f\u30a0-\u30ff]/)) {
    detectedLang.value = 'ja'
  } else if (text.match(/[\uac00-\ud7af]/)) {
    detectedLang.value = 'ko'
  }
}

// 粘贴处理
const handlePaste = (event: ClipboardEvent) => {
  const items = event.clipboardData?.items
  if (items) {
    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf('image') !== -1) {
        event.preventDefault()
        const blob = items[i].getAsFile()
        if (blob) {
          const reader = new FileReader()
          reader.onload = (e) => {
            imageUrl.value = e.target?.result as string
            activeMode.value = 'image'
          }
          reader.readAsDataURL(blob)
        }
        break
      }
    }
  }
}

// 翻译功能
const translate = async () => {
  if (!inputText.value) {
    ElMessage.warning('请输入需要翻译的文本')
    return
  }

  translating.value = true

  try {
    const actualSourceLang = sourceLang.value === 'auto' ? detectedLang.value : sourceLang.value

    // 调用后端翻译API
    const response = await Translate({
      text: inputText.value,
      source_lang: actualSourceLang,
      target_lang: targetLang.value
    })

    if (response && response.data) {
      outputText.value = response.data.translated_text

      // 保存到历史
      history.value.unshift({
        source: inputText.value,
        target: outputText.value,
        sourceLang: languageMap[actualSourceLang] || languageMap[sourceLang.value],
        targetLang: languageMap[targetLang.value]
      })

      // 限制历史记录数量
      if (history.value.length > 20) {
        history.value = history.value.slice(0, 20)
      }
    } else {
      ElMessage.error('翻译失败，请重试')
    }
  } catch (error: any) {
    console.error('翻译错误:', error)
    ElMessage.error(error.message || '翻译失败，请重试')
  } finally {
    translating.value = false
  }
}

// 交换语言
const swapLanguages = () => {
  const temp = sourceLang.value
  sourceLang.value = targetLang.value
  targetLang.value = temp

  const tempText = inputText.value
  inputText.value = outputText.value
  outputText.value = tempText

  detectedLang.value = ''
}

// 清空输入
const clearInput = () => {
  inputText.value = ''
  outputText.value = ''
  detectedLang.value = ''
}

// 使用示例
const useExample = (example: any) => {
  inputText.value = example.text
  detectLanguage()
}

// 使用历史记录
const useHistory = (item: any) => {
  inputText.value = item.source
  outputText.value = item.target
}

// 清空历史
const clearHistory = () => {
  history.value = []
  ElMessage.success('历史记录已清空')
}

// 复制文本
const copyText = (text: string) => {
  navigator.clipboard.writeText(text)
  ElMessage.success('已复制到剪贴板')
}

// 下载文本
const downloadText = () => {
  const blob = new Blob([outputText.value], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `translation_${Date.now()}.txt`
  link.click()
  URL.revokeObjectURL(url)
  ElMessage.success('下载成功')
}

// 朗读功能
const playAudio = () => {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(outputText.value)
    utterance.lang = targetLang.value === 'zh' ? 'zh-CN' : targetLang.value
    window.speechSynthesis.speak(utterance)
    ElMessage.success('开始朗读')
  } else {
    ElMessage.error('您的浏览器不支持语音朗读功能')
  }
}

// 语音输入
const startSpeech = () => {
  if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    const recognition = new SpeechRecognition()
    recognition.lang = sourceLang.value === 'auto' ? 'zh-CN' :
                     sourceLang.value === 'en' ? 'en-US' :
                     sourceLang.value === 'ja' ? 'ja-JP' :
                     sourceLang.value === 'ko' ? 'ko-KR' : 'zh-CN'
    recognition.continuous = false
    recognition.interimResults = false

    recognition.onstart = () => {
      isRecording.value = true
      ElMessage.info('开始录音，请说话...')
    }

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript
      inputText.value += (inputText.value ? ' ' : '') + transcript
      detectLanguage()
    }

    recognition.onerror = () => {
      isRecording.value = false
      ElMessage.error('语音识别失败，请重试')
    }

    recognition.onend = () => {
      isRecording.value = false
    }

    recognition.start()
  } else {
    ElMessage.error('您的浏览器不支持语音识别功能')
  }
}

// 停止录音
const stopSpeech = () => {
  isRecording.value = false
  ElMessage.info('录音已停止')
}

// 图片上传前验证
const beforeImageUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('图片大小不能超过 10MB!')
    return false
  }

  const reader = new FileReader()
  reader.onload = (e) => {
    imageUrl.value = e.target?.result as string
  }
  reader.readAsDataURL(file)
  return false // 阻止自动上传
}

// 图片翻译
const translateImage = async () => {
  translating.value = true
  await new Promise(resolve => setTimeout(resolve, 2000))
  imageResult.value = '[模拟图片翻译结果]\n\n这是一张示例图片的翻译结果。在实际应用中，这里会显示通过OCR识别的文字翻译。'
  translating.value = false
}

// 清除图片
const clearImage = () => {
  imageUrl.value = ''
  imageResult.value = ''
}

// 文档上传前验证
const beforeDocUpload = (file: File) => {
  const validTypes = ['.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx']
  const isValidType = validTypes.some(type => file.name.toLowerCase().endsWith(type))
  const isLt50M = file.size / 1024 / 1024 < 50

  if (!isValidType) {
    ElMessage.error('只能上传 PDF、Word、TXT、Excel 格式的文件!')
    return false
  }
  if (!isLt50M) {
    ElMessage.error('文件大小不能超过 50MB!')
    return false
  }

  return true
}

// 文档移除
const handleDocRemove = () => {
  fileList.value = []
  docResult.value = false
}

// 文档翻译
const translateDocument = async () => {
  translating.value = true
  await new Promise(resolve => setTimeout(resolve, 3000))
  docResult.value = true
  translating.value = false
  ElMessage.success('文档翻译完成')
}

// 下载文档
const downloadDocument = () => {
  ElMessage.success('文档下载中...')
}

// 预览文档
const previewDocument = () => {
  ElMessage.info('正在打开预览...')
}

// 图片上传成功（模拟）
const handleImageSuccess = () => {
  ElMessage.success('图片上传成功')
}
</script>

<style scoped>
.translation-workstation {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
  padding: 24px;
}

/* 头部区域 */
.page-header {
  text-align: center;
  margin-bottom: 24px;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
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

/* 模式切换 */
.mode-tabs {
  max-width: 400px;
  margin: 0 auto 24px;
}

/* 翻译容器 */
.translation-container {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  gap: 16px;
}

.translation-panel {
  flex: 1;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e5e5e5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.lang-select {
  width: 180px;
}

.detected-lang {
  font-size: 12px;
  color: #67c23a;
  background: #f0f9ff;
  padding: 2px 8px;
  border-radius: 4px;
}

.translation-textarea {
  flex: 1;
  padding: 20px;
  border: none;
  resize: none;
}

:deep(.translation-textarea .el-textarea__inner) {
  border: none;
  box-shadow: none;
  font-size: 16px;
  line-height: 1.8;
}

.output-content {
  flex: 1;
  padding: 20px;
  min-height: 300px;
}

.translated-text {
  font-size: 16px;
  line-height: 1.8;
  color: #303133;
}

.placeholder-text {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
}

.placeholder-text p {
  margin-top: 12px;
  font-size: 14px;
}

.panel-footer {
  padding: 12px 20px;
  border-top: 1px solid #e5e5e5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.char-count {
  font-size: 12px;
  color: #909399;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

/* 中间操作区 */
.translation-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  justify-content: center;
  align-items: center;
  padding: 20px 0;
}

/* 历史记录 */
.history-section {
  max-width: 1400px;
  margin: 24px auto 0;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.history-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  padding: 12px 16px;
  border-radius: 8px;
  background: #f5f7fa;
  cursor: pointer;
  transition: all 0.2s;
}

.history-item:hover {
  background: #e8eef5;
  transform: translateX(4px);
}

.history-source {
  font-size: 14px;
  color: #303133;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-target {
  font-size: 14px;
  color: #606266;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-langs {
  font-size: 12px;
  color: #909399;
}

/* 图片翻译 */
.image-translation-container {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.upload-area {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.image-uploader,
.document-uploader {
  width: 100%;
}

:deep(.el-upload-dragger) {
  width: 100%;
  min-height: 300px;
  border-radius: 8px;
}

.upload-placeholder {
  padding: 40px 20px;
  text-align: center;
}

.upload-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 16px;
}

.upload-text {
  font-size: 16px;
  color: #303133;
  margin-bottom: 8px;
}

.upload-hint {
  font-size: 12px;
  color: #909399;
}

.uploaded-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
}

.image-actions {
  margin-top: 20px;
  display: flex;
  gap: 12px;
  justify-content: center;
}

.translation-result {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e5e5e5;
}

.result-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.result-content {
  flex: 1;
  min-height: 300px;
}

.result-text {
  font-size: 16px;
  line-height: 1.8;
  color: #303133;
  white-space: pre-wrap;
}

.result-preview {
  padding: 20px;
}

/* 文档翻译 */
.document-translation-container {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.doc-actions {
  margin-top: 20px;
  text-align: center;
}

.result-actions {
  display: flex;
  gap: 12px;
}

/* 示例文本 */
.example-section {
  max-width: 1200px;
  margin: 24px auto 0;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.example-section h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #303133;
}

.example-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.example-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  background: #f5f7fa;
  cursor: pointer;
  transition: all 0.2s;
}

.example-item:hover {
  background: #e8eef5;
  transform: translateX(4px);
}

.example-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.example-content {
  flex: 1;
}

.example-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.example-text {
  font-size: 12px;
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 响应式 */
@media (max-width: 768px) {
  .translation-workstation {
    padding: 16px;
  }

  .page-title {
    font-size: 24px;
  }

  .translation-container {
    flex-direction: column;
  }

  .translation-actions {
    flex-direction: row;
    padding: 12px 0;
  }

  .image-translation-container,
  .document-translation-container {
    grid-template-columns: 1fr;
  }

  .example-list {
    grid-template-columns: 1fr;
  }
}
</style>
