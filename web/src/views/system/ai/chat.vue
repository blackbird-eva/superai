<template>
  <div class="chat-container">
    <!-- 左侧对话列表 -->
    <div class="chat-sidebar">
      <div class="sidebar-header">
        <div class="logo-section">
          <div class="logo-icon">🤖</div>
          <div class="logo-text">
            <div class="logo-title">AI 助手</div>
            <div class="logo-subtitle">智能对话</div>
          </div>
        </div>
        <el-button 
          type="primary" 
          @click="createNewChat" 
          class="new-chat-btn"
          :icon="Plus"
          circle
        />
      </div>
      <div class="chat-list">
        <div
          v-for="chat in chatList"
          :key="chat.id" 
          class="chat-item"
          :class="{ active: currentChatId === chat.id }"
          @click="switchChat(chat.id)"
        >
          <div class="chat-item-content">
            <div class="chat-item-title">{{ chat.title }}</div>
            <div class="chat-item-preview">
              {{ getLastMessage(chat) }}
            </div>
          </div>
          <div class="chat-item-actions">
            <el-button 
              text 
              size="small"
              @click.stop="deleteChat(chat.id)"
              v-if="currentChatId === chat.id"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar">
            <span>👤</span>
          </div>
          <div class="user-details">
            <div class="user-name">用户</div>
            <div class="user-status">在线</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧聊天区域 -->
    <div class="chat-main">
      <!-- 顶部标题栏 -->
      <div class="chat-header">
        <div class="header-left">
          <span class="chat-title">{{ currentChat?.title || '新对话' }}</span>
          <el-tag size="small" type="info" class="model-tag">GPT-4</el-tag>
        </div>
        <div class="header-actions">
          <el-button text @click="clearChat">
            <el-icon><Delete /></el-icon>
            清空
          </el-button>
        </div>
      </div>

      <!-- 消息列表区域 -->
      <div class="messages-container" ref="messagesContainer">
        <div v-if="currentMessages.length === 0" class="empty-state">
          <div class="empty-illustration">
            <div class="floating-emoji">💬</div>
            <div class="floating-emoji">✨</div>
            <div class="floating-emoji">🚀</div>
          </div>
          <h2>开始新的对话</h2>
          <p>我可以帮你解答问题、提供建议或者进行对话</p>
          <div class="quick-replies">
            <div
              v-for="reply in quickReplies"
              :key="reply"
              class="quick-reply-card"
              @click="sendQuickReply(reply)"
            >
              <div class="quick-reply-icon">{{ getReplyIcon(reply) }}</div>
              <div class="quick-reply-text">{{ reply }}</div>
            </div>
          </div>
        </div>

        <div v-else class="messages-list">
          <div
            v-for="(message, index) in currentMessages"
            :key="index"
            class="message-item"
            :class="message.role"
          >
            <div class="message-avatar">
              <span v-if="message.role === 'user'">👤</span>
              <span v-else>🤖</span>
            </div>
            <div class="message-content">
              <div class="message-info">
                <div class="message-role">
                  {{ message.role === 'user' ? '我' : 'AI 助手' }}
                </div>
                <div class="message-time">{{ formatTime(new Date()) }}</div>
              </div>
              <div class="message-text">
                <template v-if="message.isTyping">
                  <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </template>
                <template v-else>
                  {{ message.content }}
                </template>
              </div>
              <div class="message-actions" v-if="!message.isTyping">
                <el-button 
                  text 
                  size="small" 
                  @click="copyMessage(message.content)"
                >
                  <el-icon><CopyDocument /></el-icon>
                  复制
                </el-button>
                <el-button
                  text
                  size="small"
                  @click="regenerateMessage(index)"
                  v-if="message.role === 'assistant'"
                >
                  <el-icon><Refresh /></el-icon>
                  重新生成
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-area">
        <div class="input-wrapper">
          <div class="input-box">
            <textarea
              v-model="inputMessage"
              :placeholder="isSending ? 'AI 正在思考...' : '输入消息，按 Enter 发送，Shift + Enter 换行'"
              @keydown="handleKeydown"
              class="message-input"
              :disabled="isSending"
              rows="1"
              ref="inputTextarea"
            ></textarea>
            <div class="input-actions-right">
              <el-button
                type="primary"
                :loading="isSending"
                :disabled="!inputMessage.trim() || isSending"
                @click="sendMessage"
                class="send-btn"
                circle
                :icon="Position"
              />
            </div>
          </div>
          <div class="input-footer">
            <el-text size="small" type="info">
              <el-icon><InfoFilled /></el-icon>
              支持 Markdown 格式
            </el-text>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Position, Delete, CopyDocument, Refresh, InfoFilled } from '@element-plus/icons-vue'
import { AIChat } from './api'

// 消息类型
interface Message {
  role: 'user' | 'assistant'
  content: string
  isTyping?: boolean
}

// 对话类型
interface Chat {
  id: string
  title: string
  messages: Message[]
  updateTime: Date
}

// 当前对话ID
const currentChatId = ref('')

// 对话列表
const chatList = ref<Chat[]>([])

// 输入消息
const inputMessage = ref('')

// 是否正在发送
const isSending = ref(false)

// 打字机效果文本
const typingText = ref('')

// 消息容器引用
const messagesContainer = ref<HTMLElement>()

// 输入框引用
const inputTextarea = ref<HTMLTextAreaElement>()

// 快捷回复
const quickReplies = [
  '你好，请介绍一下你自己',
  '如何学习编程？',
  '给我写一个 Python 函数',
  '今天的天气怎么样？',
  '讲一个笑话'
]

// 回复图标映射
const replyIcons = {
  '你好': '👋',
  '编程': '💻',
  'Python': '🐍',
  '天气': '☀️',
  '笑话': '😄',
  'default': '💡'
}

// 当前对话
const currentChat = computed(() => {
  return chatList.value.find(chat => chat.id === currentChatId.value)
})

// 当前消息列表
const currentMessages = computed(() => {
  return currentChat.value?.messages || []
})

// 模拟AI回复库
const mockResponses: { [key: string]: string } = {
  '你好': '你好！我是AI助手，很高兴为你服务。有什么我可以帮助你的吗？',
  '介绍': '我是一个基于大语言模型的AI助手，可以回答问题、提供建议、协助编程等。虽然我现在只是一个模拟演示，但未来可以接入真实的AI接口。',
  '编程': '学习编程的建议：1. 选择一门语言开始（Python、JavaScript等）；2. 多做练习项目；3. 阅读优质代码；4. 参与开源社区。需要我帮你开始某个编程项目吗？',
  'Python': '当然可以！这是一个简单的Python函数示例：\n\ndef greet(name):\n    return f"Hello, {name}!"\n\nprint(greet("World"))\n\n你想要什么类型的Python函数？',
  '天气': '很抱歉，我现在是一个模拟系统，没有接入天气API。但在实际应用中，可以调用第三方天气服务来获取实时天气信息。',
  '笑话': '程序员最讨厌的四件事：写注释、写文档、别人不写注释、别人不写文档 😄'
}

// 初始化
onMounted(() => {
  if (chatList.value.length === 0) {
    createNewChat()
  }
})

// 创建新对话
const createNewChat = () => {
  const newChat: Chat = {
    id: Date.now().toString(),
    title: '新对话',
    messages: [],
    updateTime: new Date()
  }
  chatList.value.unshift(newChat)
  currentChatId.value = newChat.id
  scrollToBottom()
}

// 切换对话
const switchChat = (chatId: string) => {
  currentChatId.value = chatId
  scrollToBottom()
}

// 删除对话
const deleteChat = (chatId: string) => {
  const index = chatList.value.findIndex(chat => chat.id === chatId)
  if (index !== -1) {
    chatList.value.splice(index, 1)
    
    // 如果删除的是当前对话，切换到第一个对话或创建新对话
    if (currentChatId.value === chatId) {
      if (chatList.value.length > 0) {
        currentChatId.value = chatList.value[0].id
      } else {
        createNewChat()
      }
    }
  }
}

// 获取最后一条消息预览
const getLastMessage = (chat: Chat): string => {
  if (chat.messages.length === 0) return '暂无消息'
  const lastMessage = chat.messages[chat.messages.length - 1]
  return lastMessage.content.substring(0, 30) + (lastMessage.content.length > 30 ? '...' : '')
}

// 获取回复图标
const getReplyIcon = (reply: string): string => {
  for (const [key, icon] of Object.entries(replyIcons)) {
    if (reply.includes(key)) return icon
  }
  return replyIcons.default
}

// 获取模拟回复
const getMockResponse = (userMessage: string): string => {
  const lowerMessage = userMessage.toLowerCase()

  // 查找关键词匹配
  for (const [keyword, response] of Object.entries(mockResponses)) {
    if (lowerMessage.includes(keyword.toLowerCase())) {
      return response
    }
  }

  // 默认回复
  const defaultResponses = [
    '我理解了你的问题。这是一个很好的话题！',
    '有意思！你能告诉我更多细节吗？',
    '我在思考这个问题，稍等片刻...',
    '这个问题很有深度，让我来分析一下。',
    '收到！让我来帮你解答。'
  ]
  return defaultResponses[Math.floor(Math.random() * defaultResponses.length)]
}

// 发送消息
const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message || isSending.value) return

  isSending.value = true

  // 添加用户消息
  addMessage('user', message)

  // 清空输入
  inputMessage.value = ''

  try {
    // 调用后端AI聊天接口
    const response = await AIChat(message)
    console.log("response", response)
    
    // 兼容两种响应格式
    // 格式1: response.code === 2000 (request 已解包)
    // 格式2: response.data.code === 2000 (request 未解包)
    let data = null
    let responseMessage = ''
    
    if (response?.code === 2000) {
      data = response.data
      responseMessage = response.message
    } else if (response?.data?.code === 2000) {
      data = response.data.data
      responseMessage = response.data.message
    }
    
    console.log("data", data)
    console.log("responseMessage", responseMessage)
    
    if (data && data.answer) {
      // 添加AI回复
      addMessage('assistant', data.answer)
    } else {
      // 如果后端返回错误，显示错误信息
      console.error('响应数据格式错误:', response)
      addMessage('assistant', `错误: ${responseMessage || '响应数据格式错误'}`)
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    // 如果接口调用失败，显示错误信息
    addMessage('assistant', '发送消息失败，请稍后再试')
  }

  isSending.value = false
}

// 发送快捷回复
const sendQuickReply = (reply: string) => {
  inputMessage.value = reply
  sendMessage()
}

// 添加消息
const addMessage = (role: 'user' | 'assistant', content: string, isTyping = false) => {
  if (!currentChat.value) return

  currentChat.value.messages.push({ role, content, isTyping })

  // 更新对话标题（如果是第一条用户消息）
  if (currentChat.value.messages.length === 2 && role === 'user') {
    currentChat.value.title = content.substring(0, 20) + (content.length > 20 ? '...' : '')
    currentChat.value.updateTime = new Date()
  }

  scrollToBottom()
}

// 模拟AI回复
const simulateAIResponse = async (userMessage: string) => {
  // 先显示打字状态
  addMessage('assistant', '', true)

  // 模拟网络延迟
  await new Promise(resolve => setTimeout(resolve, 1000))

  // 获取回复
  const response = getMockResponse(userMessage)

  // 移除打字状态的消息
  if (currentChat.value) {
    currentChat.value.messages.pop()
  }

  // 打字机效果显示回复
  await typewriterEffect(response)
}

// 打字机效果
const typewriterEffect = async (text: string): Promise<void> => {
  const chat = chatList.value.find(c => c.id === currentChatId.value)
  if (!chat) return

  let displayedText = ''
  const chars = text.split('')

  // 添加空消息用于打字效果
  chat.messages.push({ role: 'assistant', content: '' })
  const messageIndex = chat.messages.length - 1

  for (let i = 0; i < chars.length; i++) {
    displayedText += chars[i]
    chat.messages[messageIndex].content = displayedText
    await new Promise(resolve => setTimeout(resolve, 30))
    scrollToBottom()
  }

  // 更新时间
  chat.updateTime = new Date()
}

// 复制消息
const copyMessage = (content: string) => {
  navigator.clipboard.writeText(content)
  ElMessage.success('已复制到剪贴板')
}

// 重新生成消息
const regenerateMessage = async (index: number) => {
  if (!currentChat.value || isSending.value) return

  // 找到这条AI回复之前的用户消息
  const userMessageIndex = index - 1
  if (userMessageIndex < 0) return

  const userMessage = currentChat.value.messages[userMessageIndex]

  // 删除这条AI回复及之后的所有消息
  currentChat.value.messages = currentChat.value.messages.slice(0, index)

  // 重新生成
  isSending.value = true

  try {
    // 调用后端AI聊天接口
    const response = await AIChat(userMessage.content)

    if (response.code === 200) {
      // 添加AI回复
      addMessage('assistant', response.data.answer)
    } else {
      // 如果后端返回错误，显示错误信息
      addMessage('assistant', `错误: ${response.message}`)
    }
  } catch (error) {
    console.error('重新生成消息失败:', error)
    // 如果接口调用失败，显示错误信息
    addMessage('assistant', '重新生成消息失败，请稍后再试')
  }

  isSending.value = false
}

// 清空对话
const clearChat = async () => {
  if (!currentChat.value) return

  try {
    await ElMessageBox.confirm('确定要清空当前对话的所有消息吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    currentChat.value.messages = []
    currentChat.value.title = '新对话'
    currentChat.value.updateTime = new Date()

    ElMessage.success('已清空对话')
  } catch {
    // 用户取消
  }
}

// 处理键盘事件
const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 格式化时间
const formatTime = (date: Date): string => {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`

  return date.toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.chat-container {
  display: flex;
  height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* 左侧边栏 */
.chat-sidebar {
  width: 280px;
  background: linear-gradient(180deg, #1a1f2e 0%, #161b25 100%);
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.1);
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.logo-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.logo-text {
  flex: 1;
}

.logo-title {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 4px;
}

.logo-subtitle {
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
}

.new-chat-btn {
  width: 100%;
  height: 44px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
}

.new-chat-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.chat-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.chat-item {
  display: flex;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.chat-item:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateX(4px);
}

.chat-item.active {
  background: rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.3);
}

.chat-item-content {
  flex: 1;
  min-width: 0;
}

.chat-item-title {
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-item-preview {
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-item-actions {
  opacity: 0;
  transition: opacity 0.2s ease;
}

.chat-item:hover .chat-item-actions {
  opacity: 1;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  border-radius: 8px;
  transition: background 0.2s ease;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.05);
}

.user-avatar {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.user-details {
  flex: 1;
}

.user-name {
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 2px;
}

.user-status {
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
}

/* 主聊天区域 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  position: relative;
}

.chat-header {
  padding: 16px 24px;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  backdrop-filter: blur(10px);
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chat-title {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.model-tag {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: #fff;
}

.header-actions :deep(.el-button) {
  color: #666;
  transition: all 0.2s ease;
}

.header-actions :deep(.el-button:hover) {
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
}

/* 消息列表区域 */
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: linear-gradient(180deg, #fafbfc 0%, #ffffff 100%);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: #666;
  animation: fadeIn 0.6s ease;
}

.empty-illustration {
  position: relative;
  width: 200px;
  height: 200px;
  margin-bottom: 24px;
}

.floating-emoji {
  position: absolute;
  font-size: 48px;
  animation: float 3s ease-in-out infinite;
}

.floating-emoji:nth-child(1) {
  top: 20%;
  left: 20%;
  animation-delay: 0s;
}

.floating-emoji:nth-child(2) {
  top: 30%;
  right: 25%;
  animation-delay: 1s;
}

.floating-emoji:nth-child(3) {
  bottom: 25%;
  left: 50%;
  transform: translateX(-50%);
  animation-delay: 2s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

.empty-state h2 {
  font-size: 28px;
  margin: 0 0 12px 0;
  color: #1a1a1a;
  font-weight: 600;
}

.empty-state p {
  font-size: 15px;
  color: #888;
  margin: 0 0 32px 0;
  line-height: 1.6;
}

.quick-replies {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  max-width: 800px;
  width: 100%;
}

.quick-reply-card {
  padding: 16px 20px;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.quick-reply-card:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.2);
}

.quick-reply-icon {
  font-size: 24px;
}

.quick-reply-text {
  font-size: 14px;
  color: #333;
  font-weight: 500;
  text-align: left;
  flex: 1;
}

.messages-list {
  max-width: 900px;
  margin: 0 auto;
  padding-bottom: 24px;
}

.message-item {
  display: flex;
  margin-bottom: 32px;
  animation: slideIn 0.4s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.message-item.user .message-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  margin-left: 16px;
}

.message-item.assistant .message-avatar {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  margin-right: 16px;
}

.message-content {
  max-width: 75%;
  flex: 1;
}

.message-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.message-role {
  font-size: 13px;
  font-weight: 600;
  color: #666;
}

.message-item.user .message-role {
  text-align: right;
  margin-left: auto;
}

.message-time {
  font-size: 12px;
  color: #999;
}

.message-text {
  padding: 14px 18px;
  border-radius: 16px;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.message-item.user .message-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-top-right-radius: 4px;
  border-bottom-right-radius: 4px;
}

.message-item.assistant .message-text {
  background: #fff;
  color: #333;
  border: 1px solid #e8e8e8;
  border-top-left-radius: 4px;
  border-bottom-left-radius: 4px;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 12px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #999;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: 0s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.6);
    opacity: 0.4;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.message-actions {
  margin-top: 12px;
  display: flex;
  gap: 4px;
}

.message-item.user .message-actions {
  justify-content: flex-end;
}

.message-actions :deep(.el-button) {
  padding: 4px 8px;
  height: 28px;
  font-size: 12px;
  color: #888;
  border: none;
}

.message-actions :deep(.el-button:hover) {
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
}

/* 输入区域 */
.input-area {
  border-top: 1px solid #e8e8e8;
  background: #fff;
  padding: 16px 24px 24px;
  box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.04);
}

.input-wrapper {
  max-width: 900px;
  margin: 0 auto;
}

.input-box {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  background: #fafbfc;
  border: 2px solid #e8e8e8;
  border-radius: 16px;
  padding: 8px;
  transition: all 0.3s ease;
}

.input-box:focus-within {
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
  background: #fff;
}

.message-input {
  flex: 1;
  border: none;
  background: transparent;
  resize: none;
  font-size: 14px;
  line-height: 1.6;
  padding: 8px 12px;
  min-height: 24px;
  max-height: 120px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.message-input:focus {
  outline: none;
}

.message-input::placeholder {
  color: #999;
}

.input-actions-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.send-btn {
  width: 40px;
  height: 40px;
  padding: 0;
  font-size: 18px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
}

.send-btn:not(:disabled):hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.5);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.input-footer {
  display: flex;
  justify-content: center;
  margin-top: 12px;
}

.input-footer :deep(.el-text) {
  color: #999;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 滚动条样式 */
.messages-container::-webkit-scrollbar,
.chat-list::-webkit-scrollbar {
  width: 8px;
}

.messages-container::-webkit-scrollbar-thumb,
.chat-list::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

.messages-container::-webkit-scrollbar-thumb:hover,
.chat-list::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}

.messages-container::-webkit-scrollbar-track,
.chat-list::-webkit-scrollbar-track {
  background: transparent;
}

/* 动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
