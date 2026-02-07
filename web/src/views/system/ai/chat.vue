<template>
  <div class="chat-container">
    <!-- 左侧对话列表 -->
    <div class="chat-sidebar">
      <div class="sidebar-header">
        <el-button type="primary" icon="Plus" @click="createNewChat" class="new-chat-btn">
          新建对话
        </el-button>
      </div>
      <div class="chat-list">
        <div
          v-for="chat in chatList"
          :key="chat.id" 
          class="chat-item"
          :class="{ active: currentChatId === chat.id }"
          @click="switchChat(chat.id)"
        >
          <div class="chat-item-title">{{ chat.title }}</div>
          <div class="chat-item-time">{{ formatTime(chat.updateTime) }}</div>
        </div>
      </div>
    </div>

    <!-- 右侧聊天区域 -->
    <div class="chat-main">
      <!-- 顶部标题栏 -->
      <div class="chat-header">
        <span class="chat-title">{{ currentChat?.title || '新对话' }}</span>
        <div class="header-actions">
          <el-button text icon="Delete" @click="clearChat">清空对话</el-button>
        </div>
      </div>

      <!-- 消息列表区域 -->
      <div class="messages-container" ref="messagesContainer">
        <div v-if="currentMessages.length === 0" class="empty-state">
          <div class="empty-icon">🤖</div>
          <h3>开始新的对话</h3>
          <p>我可以帮你解答问题、提供建议或者进行对话</p>
          <div class="quick-replies">
            <el-button
              v-for="reply in quickReplies"
              :key="reply"
              class="quick-reply-btn"
              @click="sendQuickReply(reply)"
            >
              {{ reply }}
            </el-button>
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
              <div class="message-role">
                {{ message.role === 'user' ? '我' : 'AI助手' }}
              </div>
              <div class="message-text">
                <template v-if="message.isTyping">
                  <span class="typing-dots">{{ typingText }}</span>
                </template>
                <template v-else>
                  {{ message.content }}
                </template>
              </div>
              <div class="message-actions" v-if="!message.isTyping">
                <el-button text icon="CopyDocument" size="small" @click="copyMessage(message.content)">
                  复制
                </el-button>
                <el-button
                  text
                  icon="Refresh"
                  size="small"
                  @click="regenerateMessage(index)"
                  v-if="message.role === 'assistant'"
                >
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
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="3"
            placeholder="输入消息，按 Enter 发送，Shift + Enter 换行"
            @keydown="handleKeydown"
            resize="none"
            class="message-input"
          ></el-input>
          <div class="input-footer">
            <div class="input-tips">
              <el-text size="small" type="info">支持 Markdown 格式xx</el-text>
            </div>
            <el-button
              type="primary"
              :loading="isSending"
              :disabled="!inputMessage.trim()"
              @click="sendMessage"
              class="send-btn"
            >
              <template v-if="!isSending">
                发送
                <el-icon><Position /></el-icon>
              </template>
              <template v-else>
                发送中...
              </template>
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Position, Delete, CopyDocument, Refresh } from '@element-plus/icons-vue'
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

// 快捷回复
const quickReplies = [
  '你好，请介绍一下你自己',
  '如何学习编程？',
  '给我写一个 Python 函数',
  '今天的天气怎么样？',
  '讲一个笑话'
]

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
  console.log("response",response)
    if (response.code === 2000) {
      // 添加AI回复
      addMessage('assistant', response.data.answer)
    } else {
      // 如果后端返回错误，显示错误信息
      addMessage('assistant', `错误: ${response.message}`)
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
  height: 90vh;
  background-color: #f5f5f5;
}

/* 左侧边栏 */
.chat-sidebar {
  width: 260px;
  background-color: #1a1a1a;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #333;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #333;
}

.new-chat-btn {
  width: 100%;
}

.chat-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.chat-item {
  padding: 12px;
  margin-bottom: 4px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.chat-item:hover {
  background-color: #2a2a2a;
}

.chat-item.active {
  background-color: #3a3a3a;
}

.chat-item-title {
  color: #fff;
  font-size: 14px;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-item-time {
  color: #888;
  font-size: 12px;
}

/* 主聊天区域 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fff;
}

.chat-header {
  padding: 16px 24px;
  border-bottom: 1px solid #e5e5e5;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fff;
}

.chat-title {
  font-size: 18px;
  font-weight: 500;
}

/* 消息列表区域 */
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: #666;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 24px;
  margin: 0 0 8px 0;
  color: #333;
}

.empty-state p {
  font-size: 14px;
  color: #999;
  margin: 0 0 24px 0;
}

.quick-replies {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  max-width: 600px;
}

.quick-reply-btn {
  border: 1px solid #d9d9d9;
  padding: 8px 16px;
  border-radius: 20px;
  white-space: nowrap;
}

.messages-list {
  max-width: 900px;
  margin: 0 auto;
}

.message-item {
  display: flex;
  margin-bottom: 24px;
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
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
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.message-item.user .message-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  margin-left: 12px;
}

.message-item.assistant .message-avatar {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  margin-right: 12px;
}

.message-content {
  max-width: 70%;
  flex: 1;
}

.message-role {
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.message-item.user .message-role {
  text-align: right;
}

.message-text {
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.message-item.user .message-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-top-right-radius: 4px;
}

.message-item.assistant .message-text {
  background-color: #f5f5f5;
  color: #333;
  border-top-left-radius: 4px;
}

.typing-dots {
  animation: typing 1.5s infinite;
}

@keyframes typing {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

.message-actions {
  margin-top: 8px;
  display: flex;
  gap: 8px;
}

.message-item.user .message-actions {
  justify-content: flex-end;
}

/* 输入区域 */
.input-area {
  border-top: 1px solid #e5e5e5;
  background-color: #fff;
  padding: 16px 24px;
}

.input-wrapper {
  max-width: 900px;
  margin: 0 auto;
}

.message-input {
  margin-bottom: 8px;
}

:deep(.message-input .el-textarea__inner) {
  border-radius: 12px;
  padding: 12px 16px;
  resize: none;
  border: 1px solid #d9d9d9;
}

:deep(.message-input .el-textarea__inner:focus) {
  border-color: #667eea; 
}

.input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.send-btn {
  min-width: 120px;
  border-radius: 20px;
  padding: 8px 24px;
}

/* 滚动条样式 */
.messages-container::-webkit-scrollbar,
.chat-list::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-thumb,
.chat-list::-webkit-scrollbar-thumb {
  background-color: #ddd;
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-track,
.chat-list::-webkit-scrollbar-track {
  background-color: transparent;
}
</style>
