<template>
  <div class="meeting-ai">
    <!-- 头部区域 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">会议AI智能系统</h1>
        <p class="page-subtitle">AI驱动 · 智能分析 · 自动化处理</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" icon="MagicStick" @click="openAISettings">AI设置</el-button>
        <el-button icon="TrendCharts" @click="viewAnalytics">数据分析</el-button>
        <el-button icon="Document" @click="exportReport">导出报告</el-button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧：AI功能导航 -->
      <div class="left-panel">
        <div class="panel-header">
          <h3>AI功能</h3>
        </div>
        
        <div class="ai-functions">
          <div
            v-for="func in aiFunctions"
            :key="func.id"
            :class="['function-item', { active: selectedFunction === func.id }]"
            @click="selectFunction(func.id)"
          >
            <div class="function-icon" :style="{ backgroundColor: func.color }">
              <el-icon><component :is="func.icon" /></el-icon>
            </div>
            <div class="function-info">
              <div class="function-name">{{ func.name }}</div>
              <div class="function-desc">{{ func.desc }}</div>
            </div>
          </div>
        </div>

        <!-- AI状态 -->
        <div class="ai-status-section">
          <div class="section-header">
            <h3>AI状态</h3>
          </div>
          <div class="status-cards">
            <div class="status-card">
              <div class="status-icon" style="color: #67c23a">
                <el-icon><SuccessFilled /></el-icon>
              </div>
              <div class="status-info">
                <div class="status-label">AI模型</div>
                <div class="status-value">运行中</div>
              </div>
            </div>
            <div class="status-card">
              <div class="status-icon" style="color: #409eff">
                <el-icon><DataLine /></el-icon>
              </div>
              <div class="status-info">
                <div class="status-label">处理队列</div>
                <div class="status-value">3 个任务</div>
              </div>
            </div>
            <div class="status-card">
              <div class="status-icon" style="color: #e6a23c">
                <el-icon><Clock /></el-icon>
              </div>
              <div class="status-info">
                <div class="status-label">响应时间</div>
                <div class="status-value">0.8 秒</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 中间：AI功能面板 -->
      <div class="center-panel">
        <!-- 智能转录 -->
        <div v-if="selectedFunction === 'transcription'" class="function-panel">
          <div class="panel-section">
            <div class="section-header">
              <h3>智能转录</h3>
              <el-tag type="success">AI Powered</el-tag>
            </div>
            
            <div class="transcription-upload">
              <el-upload
                drag
                action="#"
                :auto-upload="false"
                :on-change="handleAudioUpload"
                accept=".mp3,.wav,.m4a"
              >
                <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
                <div class="el-upload__text">
                  拖拽音频文件到此处，或<em>点击上传</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">
                    支持 mp3、wav、m4a 格式，AI将自动进行智能转录
                  </div>
                </template>
              </el-upload>
            </div>
            
            <div v-if="transcriptionResult" class="transcription-result">
              <div class="result-header">
                <span>转录结果</span>
                <el-button type="primary" size="small" icon="Download" @click="downloadTranscription">
                  下载
                </el-button>
              </div>
              <div class="result-content">
                <div
                  v-for="(segment, index) in transcriptionResult.segments"
                  :key="index"
                  class="transcription-segment"
                >
                  <span class="segment-time">[{{ formatTime(segment.start) }}]</span>
                  <span class="segment-speaker">{{ segment.speaker }}:</span>
                  <span class="segment-text">{{ segment.text }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 自动摘要 -->
        <div v-else-if="selectedFunction === 'summary'" class="function-panel">
          <div class="panel-section">
            <div class="section-header">
              <h3>自动摘要生成</h3>
              <el-tag type="success">AI Generated</el-tag>
            </div>
            
            <el-form :model="summaryForm" label-width="100px">
              <el-form-item label="会议内容">
                <el-input
                  v-model="summaryForm.content"
                  type="textarea"
                  :rows="6"
                  placeholder="输入会议内容或选择已有会议..."
                />
              </el-form-item>
              
              <el-form-item label="摘要长度">
                <el-radio-group v-model="summaryForm.length">
                  <el-radio label="brief">简短</el-radio>
                  <el-radio label="normal">标准</el-radio>
                  <el-radio label="detailed">详细</el-radio>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item label="包含内容">
                <el-checkbox-group v-model="summaryForm.include">
                  <el-checkbox label="topic">会议主题</el-checkbox>
                  <el-checkbox label="points">讨论要点</el-checkbox>
                  <el-checkbox label="decisions">决策事项</el-checkbox>
                  <el-checkbox label="actions">后续行动</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
            </el-form>
            
            <el-button
              type="primary"
              icon="MagicStick"
              :loading="generatingSummary"
              @click="generateSummary"
              style="width: 100%"
            >
              生成摘要
            </el-button>
            
            <div v-if="summaryResult" class="summary-result">
              <div class="result-header">
                <span>生成的摘要</span>
                <el-button type="primary" size="small" icon="CopyDocument" @click="copySummary">
                  复制
                </el-button>
              </div>
              <div class="summary-content">
                <div v-if="summaryResult.topic" class="summary-item">
                  <div class="item-title">会议主题</div>
                  <div class="item-text">{{ summaryResult.topic }}</div>
                </div>
                <div v-if="summaryResult.points" class="summary-item">
                  <div class="item-title">讨论要点</div>
                  <ul class="item-list">
                    <li v-for="(point, index) in summaryResult.points" :key="index">
                      {{ point }}
                    </li>
                  </ul>
                </div>
                <div v-if="summaryResult.decisions" class="summary-item">
                  <div class="item-title">决策事项</div>
                  <ul class="item-list">
                    <li v-for="(decision, index) in summaryResult.decisions" :key="index">
                      {{ decision }}
                    </li>
                  </ul>
                </div>
                <div v-if="summaryResult.actions" class="summary-item">
                  <div class="item-title">后续行动</div>
                  <ul class="item-list">
                    <li v-for="(action, index) in summaryResult.actions" :key="index">
                      {{ action }}
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 智能问答 -->
        <div v-else-if="selectedFunction === 'qa'" class="function-panel">
          <div class="panel-section">
            <div class="section-header">
              <h3>智能问答</h3>
              <el-tag type="success">AI Chat</el-tag>
            </div>
            
            <div class="qa-chat-container">
              <div class="chat-messages">
                <div
                  v-for="(msg, index) in chatMessages"
                  :key="index"
                  :class="['chat-message', msg.role]"
                >
                  <div class="message-avatar">
                    <el-icon v-if="msg.role === 'user'"><User /></el-icon>
                    <el-icon v-else><Cpu /></el-icon>
                  </div>
                  <div class="message-content">
                    <div class="message-sender">{{ msg.role === 'user' ? '您' : 'AI助手' }}</div>
                    <div class="message-text">{{ msg.content }}</div>
                  </div>
                </div>
              </div>
              
              <div class="chat-input">
                <el-input
                  v-model="chatInput"
                  type="textarea"
                  :rows="3"
                  placeholder="输入您的问题..."
                  @keydown.ctrl.enter="sendMessage"
                />
                <div class="input-actions">
                  <el-button type="primary" icon="Position" :loading="sendingChat" @click="sendMessage">
                    发送
                  </el-button>
                  <el-button icon="Refresh" @click="clearChat">清空</el-button>
                </div>
              </div>
            </div>
            
            <div class="quick-questions">
              <div class="quick-title">快捷问题</div>
              <div class="quick-buttons">
                <el-button
                  v-for="(question, index) in quickQuestions"
                  :key="index"
                  size="small"
                  @click="askQuickQuestion(question)"
                >
                  {{ question }}
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 情感分析 -->
        <div v-else-if="selectedFunction === 'sentiment'" class="function-panel">
          <div class="panel-section">
            <div class="section-header">
              <h3>情感分析</h3>
              <el-tag type="success">AI Analysis</el-tag>
            </div>
            
            <el-form :model="sentimentForm" label-width="100px">
              <el-form-item label="分析内容">
                <el-input
                  v-model="sentimentForm.content"
                  type="textarea"
                  :rows="6"
                  placeholder="输入需要分析情感的内容..."
                />
              </el-form-item>
            </el-form>
            
            <el-button
              type="primary"
              icon="TrendCharts"
              :loading="analyzingSentiment"
              @click="analyzeSentiment"
              style="width: 100%"
            >
              开始分析
            </el-button>
            
            <div v-if="sentimentResult" class="sentiment-result">
              <div class="sentiment-overview">
                <div class="sentiment-main">
                  <div class="main-label">整体情感</div>
                  <div class="main-value" :class="'sentiment-' + sentimentResult.overall">
                    {{ getSentimentText(sentimentResult.overall) }}
                  </div>
                  <el-progress
                    :percentage="sentimentResult.confidence"
                    :color="getSentimentColor(sentimentResult.overall)"
                    :stroke-width="8"
                  />
                  <div class="confidence-label">置信度: {{ sentimentResult.confidence }}%</div>
                </div>
              </div>
              
              <div class="sentiment-details">
                <div class="detail-item">
                  <div class="detail-label">积极情感</div>
                  <el-progress :percentage="sentimentResult.positive" color="#67c23a" :stroke-width="10" />
                </div>
                <div class="detail-item">
                  <div class="detail-label">中性情感</div>
                  <el-progress :percentage="sentimentResult.neutral" color="#909399" :stroke-width="10" />
                </div>
                <div class="detail-item">
                  <div class="detail-label">消极情感</div>
                  <el-progress :percentage="sentimentResult.negative" color="#f56c6c" :stroke-width="10" />
                </div>
              </div>
              
              <div class="sentiment-keywords">
                <div class="keywords-title">情感关键词</div>
                <div class="keywords-tags">
                  <el-tag
                    v-for="(keyword, index) in sentimentResult.keywords"
                    :key="index"
                    :type="getKeywordType(keyword.type)"
                  >
                    {{ keyword.word }} ({{ keyword.type }})
                  </el-tag>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 关键词提取 -->
        <div v-else-if="selectedFunction === 'keywords'" class="function-panel">
          <div class="panel-section">
            <div class="section-header">
              <h3>关键词提取</h3>
              <el-tag type="success">AI Extract</el-tag>
            </div>
            
            <el-form :model="keywordForm" label-width="100px">
              <el-form-item label="提取内容">
                <el-input
                  v-model="keywordForm.content"
                  type="textarea"
                  :rows="6"
                  placeholder="输入需要提取关键词的内容..."
                />
              </el-form-item>
              
              <el-form-item label="提取数量">
                <el-input-number v-model="keywordForm.count" :min="5" :max="50" />
              </el-form-item>
            </el-form>
            
            <el-button
              type="primary"
              icon="Key"
              :loading="extractingKeywords"
              @click="extractKeywords"
              style="width: 100%"
            >
              提取关键词
            </el-button>
            
            <div v-if="keywordResult" class="keyword-result">
              <div class="result-header">
                <span>关键词</span>
                <el-button type="primary" size="small" icon="CopyDocument" @click="copyKeywords">
                  复制
                </el-button>
              </div>
              <div class="keywords-cloud">
                <div
                  v-for="(keyword, index) in keywordResult"
                  :key="index"
                  class="keyword-item"
                  :style="{ fontSize: Math.max(12, 24 - index * 2) + 'px' }"
                >
                  {{ keyword.word }}
                  <span class="keyword-score">{{ keyword.score.toFixed(2) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 任务提取 -->
        <div v-else-if="selectedFunction === 'tasks'" class="function-panel">
          <div class="panel-section">
            <div class="section-header">
              <h3>任务提取</h3>
              <el-tag type="success">AI Auto</el-tag>
            </div>
            
            <el-form :model="taskForm" label-width="100px">
              <el-form-item label="会议内容">
                <el-input
                  v-model="taskForm.content"
                  type="textarea"
                  :rows="6"
                  placeholder="输入会议内容，AI将自动提取任务..."
                />
              </el-form-item>
            </el-form>
            
            <el-button
              type="primary"
              icon="List"
              :loading="extractingTasks"
              @click="extractTasks"
              style="width: 100%"
            >
              提取任务
            </el-button>
            
            <div v-if="taskResult" class="task-result">
              <div class="result-header">
                <span>提取的任务</span>
                <el-button type="success" size="small" icon="Check" @click="createTasks">
                  创建任务
                </el-button>
              </div>
              <div class="task-list">
                <div v-for="(task, index) in taskResult" :key="index" class="task-item">
                  <div class="task-header">
                    <el-checkbox v-model="task.selected">{{ task.title }}</el-checkbox>
                    <el-tag :type="getPriorityType(task.priority)" size="small">
                      {{ task.priority }}
                    </el-tag>
                  </div>
                  <div class="task-details">
                    <div class="task-assignee">
                      <el-icon><User /></el-icon>
                      <span>{{ task.assignee }}</span>
                    </div>
                    <div class="task-deadline">
                      <el-icon><Calendar /></el-icon>
                      <span>{{ task.deadline }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：AI分析和建议 -->
      <div class="right-panel">
        <!-- 会议质量分析 -->
        <div class="analysis-section">
          <div class="section-header">
            <h3>会议质量分析</h3>
          </div>
          
          <div class="quality-metrics">
            <div class="metric-card">
              <div class="metric-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
                <el-icon><DataAnalysis /></el-icon>
              </div>
              <div class="metric-info">
                <div class="metric-value">{{ qualityMetrics.efficiency }}</div>
                <div class="metric-label">效率评分</div>
              </div>
            </div>
            
            <div class="metric-card">
              <div class="metric-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%)">
                <el-icon><ChatDotRound /></el-icon>
              </div>
              <div class="metric-info">
                <div class="metric-value">{{ qualityMetrics.participation }}</div>
                <div class="metric-label">参与度</div>
              </div>
            </div>
            
            <div class="metric-card">
              <div class="metric-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)">
                <el-icon><Document /></el-icon>
              </div>
              <div class="metric-info">
                <div class="metric-value">{{ qualityMetrics.completion }}</div>
                <div class="metric-label">完成率</div>
              </div>
            </div>
          </div>
          
          <div class="quality-chart">
            <div class="chart-title">历史趋势</div>
            <div class="chart-placeholder">
              <el-icon><TrendCharts /></el-icon>
              <p>会议质量趋势图</p>
            </div>
          </div>
        </div>

        <!-- AI建议 -->
        <div class="suggestions-section">
          <div class="section-header">
            <h3>AI建议</h3>
            <el-tag type="warning">智能推荐</el-tag>
          </div>
          
          <div class="suggestions-list">
            <div v-for="(suggestion, index) in aiSuggestions" :key="index" class="suggestion-item">
              <div class="suggestion-icon" :style="{ backgroundColor: suggestion.color }">
                <el-icon><component :is="suggestion.icon" /></el-icon>
              </div>
              <div class="suggestion-content">
                <div class="suggestion-title">{{ suggestion.title }}</div>
                <div class="suggestion-desc">{{ suggestion.desc }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- AI能力 -->
        <div class="capabilities-section">
          <div class="section-header">
            <h3>AI能力</h3>
          </div>
          
          <div class="capability-list">
            <div class="capability-item">
              <div class="capability-header">
                <span class="capability-name">语音识别</span>
                <el-tag type="success" size="small">98.5%</el-tag>
              </div>
              <el-progress :percentage="98.5" :stroke-width="6" />
            </div>
            
            <div class="capability-item">
              <div class="capability-header">
                <span class="capability-name">语义理解</span>
                <el-tag type="success" size="small">96.2%</el-tag>
              </div>
              <el-progress :percentage="96.2" :stroke-width="6" />
            </div>
            
            <div class="capability-item">
              <div class="capability-header">
                <span class="capability-name">摘要生成</span>
                <el-tag type="success" size="small">94.8%</el-tag>
              </div>
              <el-progress :percentage="94.8" :stroke-width="6" />
            </div>
            
            <div class="capability-item">
              <div class="capability-header">
                <span class="capability-name">情感分析</span>
                <el-tag type="warning" size="small">92.3%</el-tag>
              </div>
              <el-progress :percentage="92.3" :stroke-width="6" color="#e6a23c" />
            </div>
          </div>
        </div>

        <!-- 最近处理 -->
        <div class="recent-section">
          <div class="section-header">
            <h3>最近处理</h3>
          </div>
          
          <el-timeline>
            <el-timeline-item
              v-for="(item, index) in recentProcesses"
              :key="index"
              :timestamp="item.time"
              placement="top"
            >
              <div class="process-item">
                <el-tag :type="item.type" size="small">{{ item.type === 'success' ? '完成' : '处理中' }}</el-tag>
                <span>{{ item.content }}</span>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </div>

    <!-- AI设置对话框 -->
    <el-dialog v-model="settingsDialogVisible" title="AI设置" width="600px">
      <el-form :model="aiSettings" label-width="120px">
        <el-form-item label="AI模型">
          <el-select v-model="aiSettings.model" placeholder="选择模型" style="width: 100%">
            <el-option label="GPT-4" value="gpt-4" />
            <el-option label="GPT-3.5" value="gpt-3.5" />
            <el-option label="Claude" value="claude" />
            <el-option label="Custom Model" value="custom" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="API密钥">
          <el-input v-model="aiSettings.apiKey" type="password" placeholder="输入API密钥" />
        </el-form-item>
        
        <el-form-item label="语言">
          <el-select v-model="aiSettings.language" placeholder="选择语言" style="width: 100%">
            <el-option label="中文" value="zh" />
            <el-option label="English" value="en" />
            <el-option label="自动检测" value="auto" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="输出格式">
          <el-radio-group v-model="aiSettings.outputFormat">
            <el-radio label="text">文本</el-radio>
            <el-radio label="json">JSON</el-radio>
            <el-radio label="markdown">Markdown</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="置信度阈值">
          <el-slider v-model="aiSettings.confidence" :min="0" :max="100" />
          <span style="margin-left: 12px">{{ aiSettings.confidence }}%</span>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="settingsDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveSettings">保存设置</el-button>
      </template>
    </el-dialog>

    <!-- 悬浮AI助手 -->
    <div class="floating-ai-assistant">
      <!-- 悬浮球 -->
      <div
        v-if="!assistantExpanded"
        class="floating-ball"
        @click="toggleAssistant"
        @mousedown="startDragBall"
      >
        <div class="ball-icon">
          <el-icon><ChatDotSquare /></el-icon>
        </div>
        <div class="ball-ripple"></div>
        <div class="ball-ripple delay-1"></div>
        <div class="ball-ripple delay-2"></div>
      </div>

      <!-- 对话窗口 -->
      <div
        v-show="assistantExpanded"
        class="assistant-window"
        :style="{ left: windowPos.x + 'px', top: windowPos.y + 'px' }"
      >
        <!-- 标题栏 -->
        <div class="window-header" @mousedown="startDragWindow">
          <div class="header-title">
            <el-icon class="ai-icon"><Cpu /></el-icon>
            <span>AI 智能助手</span>
            <el-tag v-if="currentMode !== 'chat'" size="small" type="success" style="margin-left: 8px">
              {{ getModeLabel(currentMode) }}
            </el-tag>
          </div>
          <div class="header-actions">
            <el-button
              text
              circle
              size="small"
              icon="Minus"
              @click="minimizeAssistant"
              title="最小化"
            />
            <el-button
              text
              circle
              size="small"
              icon="Close"
              @click="closeAssistant"
              title="关闭"
            />
          </div>
        </div>

        <!-- 功能菜单 -->
        <div class="function-menu">
          <div
            v-for="mode in assistantModes"
            :key="mode.id"
            :class="['menu-item', { active: currentMode === mode.id }]"
            @click="switchMode(mode.id)"
          >
            <el-icon><component :is="mode.icon" /></el-icon>
            <span>{{ mode.name }}</span>
          </div>
        </div>

        <!-- 内容区域 -->
        <div class="assistant-content">
          <!-- 普通聊天 -->
          <div v-if="currentMode === 'chat'" class="chat-area">
            <div class="messages-container" ref="messagesContainer">
              <div
                v-for="(msg, index) in assistantMessages"
                :key="index"
                :class="['message', msg.role]"
              >
                <div class="message-avatar">
                  <el-icon v-if="msg.role === 'user'"><User /></el-icon>
                  <el-icon v-else><Cpu /></el-icon>
                </div>
                <div class="message-body">
                  <div class="message-content">{{ msg.content }}</div>
                </div>
              </div>
              <div v-if="isTyping" class="message ai">
                <div class="message-avatar">
                  <el-icon><Cpu /></el-icon>
                </div>
                <div class="message-body">
                  <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 网页翻译 -->
          <div v-else-if="currentMode === 'translate'" class="tool-area">
            <div class="translate-header">
              <el-select v-model="translateFrom" size="small" style="width: 120px">
                <el-option label="中文" value="zh" />
                <el-option label="English" value="en" />
                <el-option label="日本語" value="ja" />
                <el-option label="한국어" value="ko" />
              </el-select>
              <el-icon class="translate-arrow"><Right /></el-icon>
              <el-select v-model="translateTo" size="small" style="width: 120px">
                <el-option label="English" value="en" />
                <el-option label="中文" value="zh" />
                <el-option label="日本語" value="ja" />
                <el-option label="한국어" value="ko" />
              </el-select>
            </div>
            <el-input
              v-model="translateInput"
              type="textarea"
              :rows="4"
              placeholder="输入需要翻译的文本..."
              class="translate-input"
            />
            <el-button
              type="primary"
              :loading="translating"
              @click="handleTranslate"
              style="width: 100%; margin-top: 12px"
            >
              翻译
            </el-button>
            <div v-if="translateResult" class="translate-result">
              <div class="result-label">翻译结果：</div>
              <div class="result-text">{{ translateResult }}</div>
              <el-button size="small" text icon="CopyDocument" @click="copyText(translateResult)">
                复制
              </el-button>
            </div>
          </div>

          <!-- 内容总结 -->
          <div v-else-if="currentMode === 'summary'" class="tool-area">
            <el-input
              v-model="summaryInput"
              type="textarea"
              :rows="6"
              placeholder="粘贴需要总结的内容..."
              class="summary-input"
            />
            <div class="summary-options">
              <el-radio-group v-model="summaryLength" size="small">
                <el-radio-button label="brief">简短</el-radio-button>
                <el-radio-button label="normal">标准</el-radio-button>
                <el-radio-button label="detailed">详细</el-radio-button>
              </el-radio-group>
            </div>
            <el-button
              type="primary"
              :loading="summarizing"
              @click="handleSummary"
              style="width: 100%; margin-top: 12px"
            >
              生成摘要
            </el-button>
            <div v-if="summaryOutput" class="summary-result">
              <div class="result-label">摘要：</div>
              <div class="result-text">{{ summaryOutput }}</div>
              <el-button size="small" text icon="CopyDocument" @click="copyText(summaryOutput)">
                复制
              </el-button>
            </div>
          </div>

          <!-- 会议实时转录 -->
          <div v-else-if="currentMode === 'transcribe'" class="tool-area">
            <div class="transcribe-status">
              <div v-if="!isTranscribing" class="status-idle">
                <el-icon class="mic-icon"><Microphone /></el-icon>
                <p>点击开始实时转录</p>
              </div>
              <div v-else class="status-active">
                <div class="recording-indicator">
                  <div class="recording-dot"></div>
                  <span>正在录音...</span>
                </div>
                <div class="transcribe-time">{{ transcribeTime }}</div>
              </div>
            </div>
            <el-button
              v-if="!isTranscribing"
              type="primary"
              icon="Microphone"
              @click="startTranscribe"
              style="width: 100%"
            >
              开始转录
            </el-button>
            <el-button
              v-else
              type="danger"
              icon="VideoPause"
              @click="stopTranscribe"
              style="width: 100%"
            >
              停止转录
            </el-button>
            <div v-if="transcribeResult" class="transcribe-result">
              <div class="result-label">转录结果：</div>
              <div class="result-text">{{ transcribeResult }}</div>
              <el-button size="small" text icon="CopyDocument" @click="copyText(transcribeResult)">
                复制
              </el-button>
            </div>
          </div>

          <!-- 写作润色 -->
          <div v-else-if="currentMode === 'polish'" class="tool-area">
            <el-input
              v-model="polishInput"
              type="textarea"
              :rows="6"
              placeholder="输入需要润色的文本..."
              class="polish-input"
            />
            <div class="polish-options">
              <el-select v-model="polishStyle" placeholder="选择风格" size="small">
                <el-option label="正式商务" value="formal" />
                <el-option label="轻松活泼" value="casual" />
                <el-option label="学术严谨" value="academic" />
                <el-option label="简洁明了" value="concise" />
              </el-select>
            </div>
            <el-button
              type="primary"
              :loading="polishing"
              @click="handlePolish"
              style="width: 100%; margin-top: 12px"
            >
              润色文本
            </el-button>
            <div v-if="polishResult" class="polish-result">
              <div class="result-label">润色结果：</div>
              <div class="result-text">{{ polishResult }}</div>
              <el-button size="small" text icon="CopyDocument" @click="copyText(polishResult)">
                复制
              </el-button>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="assistant-input">
          <el-input
            v-model="userInput"
            type="textarea"
            :rows="2"
            placeholder="输入消息... (Ctrl+Enter 发送)"
            @keydown.ctrl.enter="handleSend"
            resize="none"
          />
          <div class="input-actions">
            <el-button
              circle
              size="small"
              :type="isRecording ? 'danger' : 'default'"
              icon="Microphone"
              @click="toggleVoiceInput"
              title="语音输入"
            />
            <el-button
              type="primary"
              circle
              size="small"
              icon="Position"
              @click="handleSend"
              :loading="sendingMessage"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  SuccessFilled, DataLine, Clock, UploadFilled, MagicStick, TrendCharts,
  User, Cpu, Position, Refresh, Key, List, DataAnalysis, ChatDotRound,
  Document, ChatDotSquare, Microphone, Star, Notification, WarningFilled,
  Right
} from '@element-plus/icons-vue'

// AI功能列表
const aiFunctions = ref([
  { id: 'transcription', name: '智能转录', desc: '音频转文字，自动识别说话人', icon: 'Microphone', color: '#ff6b6b' },
  { id: 'summary', name: '自动摘要', desc: '提取关键信息，生成会议摘要', icon: 'Document', color: '#4ecdc4' },
  { id: 'qa', name: '智能问答', desc: '会议内容智能问答', icon: 'ChatDotSquare', color: '#f39c12' },
  { id: 'sentiment', name: '情感分析', desc: '分析会议情感倾向', icon: 'Star', color: '#9b59b6' },
  { id: 'keywords', name: '关键词提取', desc: '提取会议关键词和主题', icon: 'Key', color: '#3498db' },
  { id: 'tasks', name: '任务提取', desc: '自动提取待办任务', icon: 'List', color: '#1abc9c' }
])

// 选中的功能
const selectedFunction = ref('transcription')

// 转录结果
const transcriptionResult = ref<any>(null)

// 摘要表单
const summaryForm = reactive({
  content: '',
  length: 'normal',
  include: ['topic', 'points', 'decisions', 'actions']
})

const generatingSummary = ref(false)
const summaryResult = ref<any>(null)

// 聊天
const chatMessages = ref<any[]>([
  { role: 'ai', content: '您好！我是会议AI助手，可以帮您分析会议内容、生成摘要、提取任务等。有什么可以帮您的吗？' }
])
const chatInput = ref('')
const sendingChat = ref(false)

const quickQuestions = ref([
  '会议的主要议题是什么？',
  '有哪些决策需要执行？',
  '参与者有哪些人？',
  '总结一下会议内容'
])

// 情感分析
const sentimentForm = reactive({ content: '' })
const analyzingSentiment = ref(false)
const sentimentResult = ref<any>(null)

// 关键词提取
const keywordForm = reactive({ content: '', count: 10 })
const extractingKeywords = ref(false)
const keywordResult = ref<any[]>([])

// 任务提取
const taskForm = reactive({ content: '' })
const extractingTasks = ref(false)
const taskResult = ref<any[]>([])

// 质量指标
const qualityMetrics = ref({
  efficiency: 85,
  participation: 92,
  completion: 88
})

// AI建议
const aiSuggestions = ref([
  { icon: 'Clock', title: '优化会议时长', desc: '当前会议平均时长较长，建议控制在45分钟内', color: '#ff6b6b' },
  { icon: 'User', title: '提高参与度', desc: '建议增加互动环节，让更多成员参与讨论', color: '#4ecdc4' },
  { icon: 'Document', title: '完善记录', desc: '建议增加会议记录的详细程度', color: '#f39c12' }
])

// 最近处理
const recentProcesses = ref([
  { time: '10分钟前', content: '完成"项目周会"的摘要生成', type: 'success' },
  { time: '20分钟前', content: '正在进行"技术评审"的情感分析', type: 'warning' },
  { time: '30分钟前', content: '完成"需求讨论"的关键词提取', type: 'success' }
])

// AI设置
const settingsDialogVisible = ref(false)
const aiSettings = reactive({
  model: 'gpt-4',
  apiKey: '',
  language: 'zh',
  outputFormat: 'text',
  confidence: 85
})

// 选择功能
const selectFunction = (id: string) => {
  selectedFunction.value = id
}

// 处理音频上传
const handleAudioUpload = (file: any) => {
  ElMessage.success('上传成功，正在开始智能转录...')
  setTimeout(() => {
    transcriptionResult.value = {
      segments: [
        { start: 0, speaker: '主持人', text: '各位好，欢迎参加今天的会议。' },
        { start: 15, speaker: '张三', text: '我先介绍一下项目进展。' },
        { start: 45, speaker: '李四', text: '关于技术方案，我有几点建议。' },
        { start: 90, speaker: '主持人', text: '好的，大家还有什么意见吗？' }
      ]
    }
    ElMessage.success('转录完成')
  }, 3000)
}

// 生成摘要
const generateSummary = () => {
  if (!summaryForm.content) {
    ElMessage.warning('请输入会议内容')
    return
  }
  
  generatingSummary.value = true
  
  setTimeout(() => {
    summaryResult.value = {
      topic: '2024年度项目规划会议',
      points: ['讨论了年度工作目标', '确定了技术方案', '制定了实施计划'],
      decisions: ['采用新的技术架构', '成立专项工作组'],
      actions: ['张三负责技术方案设计', '李四负责资源配置']
    }
    generatingSummary.value = false
    ElMessage.success('摘要生成成功')
  }, 2000)
}

// 复制摘要
const copySummary = () => {
  ElMessage.success('已复制到剪贴板')
}

// 发送消息
const sendMessage = () => {
  if (!chatInput.value.trim()) {
    ElMessage.warning('请输入问题')
    return
  }
  
  chatMessages.value.push({ role: 'user', content: chatInput.value })
  const question = chatInput.value
  chatInput.value = ''
  
  sendingChat.value = true
  
  setTimeout(() => {
    const responses = [
      '根据会议内容，主要议题是项目规划和资源分配。',
      '会议中达成的决策包括采用新技术架构和成立工作组。',
      '参与会议的主要成员有张三、李四、王五等人。',
      '会议总结：完成了年度规划讨论，明确了下一步工作方向。'
    ]
    
    const response = responses[Math.floor(Math.random() * responses.length)]
    chatMessages.value.push({ role: 'ai', content: response })
    sendingChat.value = false
  }, 1500)
}

// 快捷问题
const askQuickQuestion = (question: string) => {
  chatInput.value = question
  sendMessage()
}

// 清空聊天
const clearChat = () => {
  chatMessages.value = [
    { role: 'ai', content: '您好！我是会议AI助手，可以帮您分析会议内容、生成摘要、提取任务等。有什么可以帮您的吗？' }
  ]
  ElMessage.success('已清空对话')
}

// 分析情感
const analyzeSentiment = () => {
  if (!sentimentForm.content) {
    ElMessage.warning('请输入分析内容')
    return
  }
  
  analyzingSentiment.value = true
  
  setTimeout(() => {
    sentimentResult.value = {
      overall: 'positive',
      confidence: 87,
      positive: 65,
      neutral: 25,
      negative: 10,
      keywords: [
        { word: '满意', type: '积极' },
        { word: '赞同', type: '积极' },
        { word: '建议', type: '中性' },
        { word: '担心', type: '消极' }
      ]
    }
    analyzingSentiment.value = false
    ElMessage.success('情感分析完成')
  }, 2000)
}

// 获取情感文本
const getSentimentText = (sentiment: string) => {
  const texts: Record<string, string> = {
    positive: '积极',
    neutral: '中性',
    negative: '消极'
  }
  return texts[sentiment] || sentiment
}

// 获取情感颜色
const getSentimentColor = (sentiment: string) => {
  const colors: Record<string, string> = {
    positive: '#67c23a',
    neutral: '#909399',
    negative: '#f56c6c'
  }
  return colors[sentiment] || '#409eff'
}

// 获取关键词类型
const getKeywordType = (type: string) => {
  const types: Record<string, string> = {
    '积极': 'success',
    '中性': 'info',
    '消极': 'danger'
  }
  return types[type] || ''
}

// 提取关键词
const extractKeywords = () => {
  if (!keywordForm.content) {
    ElMessage.warning('请输入提取内容')
    return
  }
  
  extractingKeywords.value = true
  
  setTimeout(() => {
    keywordResult.value = [
      { word: '项目规划', score: 0.95 },
      { word: '技术方案', score: 0.88 },
      { word: '资源配置', score: 0.82 },
      { word: '实施计划', score: 0.76 },
      { word: '团队协作', score: 0.71 }
    ]
    extractingKeywords.value = false
    ElMessage.success('关键词提取成功')
  }, 1500)
}

// 复制关键词
const copyKeywords = () => {
  ElMessage.success('已复制到剪贴板')
}

// 提取任务
const extractTasks = () => {
  if (!taskForm.content) {
    ElMessage.warning('请输入会议内容')
    return
  }
  
  extractingTasks.value = true
  
  setTimeout(() => {
    taskResult.value = [
      { title: '完成技术方案设计', assignee: '张三', deadline: '2024-02-01', priority: '高', selected: true },
      { title: '资源配置方案制定', assignee: '李四', deadline: '2024-02-05', priority: '中', selected: true },
      { title: '项目计划编写', assignee: '王五', deadline: '2024-02-10', priority: '低', selected: false }
    ]
    extractingTasks.value = false
    ElMessage.success('任务提取成功')
  }, 2000)
}

// 获取优先级类型
const getPriorityType = (priority: string) => {
  const types: Record<string, string> = {
    '高': 'danger',
    '中': 'warning',
    '低': 'info'
  }
  return types[priority] || ''
}

// 创建任务
const createTasks = () => {
  const selected = taskResult.value.filter(t => t.selected)
  if (selected.length === 0) {
    ElMessage.warning('请选择要创建的任务')
    return
  }
  ElMessage.success(`已创建 ${selected.length} 个任务`)
}

// 下载转录
const downloadTranscription = () => {
  ElMessage.success('正在下载...')
}

// AI设置
const openAISettings = () => {
  settingsDialogVisible.value = true
}

const saveSettings = () => {
  ElMessage.success('设置已保存')
  settingsDialogVisible.value = false
}

// 数据分析
const viewAnalytics = () => {
  ElMessage.info('数据分析功能开发中...')
}

// 导出报告
const exportReport = () => {
  ElMessage.info('正在导出报告...')
  setTimeout(() => {
    ElMessage.success('导出成功')
  }, 1500)
}

// 格式化时间
const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// ========== 悬浮AI助手相关 ==========
// 悬浮球状态
const assistantExpanded = ref(false)
const currentMode = ref('chat')
const userInput = ref('')
const isRecording = ref(false)
const isTyping = ref(false)
const sendingMessage = ref(false)

// 窗口位置
const windowPos = reactive({
  x: window.innerWidth - 440,
  y: window.innerHeight - 620
})

// 拖动状态
const dragging = ref(false)
const dragOffset = reactive({ x: 0, y: 0 })

// 聊天消息
const assistantMessages = ref([
  { role: 'ai', content: '您好！我是您的 AI 智能助手。我可以帮您翻译文本、总结内容、实时转录会议、润色写作等。有什么可以帮您的吗？' }
])

const messagesContainer = ref<HTMLElement | null>(null)

// 功能模式
const assistantModes = [
  { id: 'chat', name: '智能对话', icon: 'ChatDotSquare' },
  { id: 'translate', name: '网页翻译', icon: 'Position' },
  { id: 'summary', name: '内容总结', icon: 'Document' },
  { id: 'transcribe', name: '实时转录', icon: 'Microphone' },
  { id: 'polish', name: '写作润色', icon: 'MagicStick' }
]

// 翻译功能
const translateFrom = ref('zh')
const translateTo = ref('en')
const translateInput = ref('')
const translateResult = ref('')
const translating = ref(false)

// 总结功能
const summaryInput = ref('')
const summaryLength = ref('normal')
const summaryOutput = ref('')
const summarizing = ref(false)

// 转录功能
const isTranscribing = ref(false)
const transcribeResult = ref('')
const transcribeTime = ref('00:00')
const transcribeTimer = ref<any>(null)
const transcribeSeconds = ref(0)

// 润色功能
const polishInput = ref('')
const polishStyle = ref('formal')
const polishResult = ref('')
const polishing = ref(false)

// 切换助手显示
const toggleAssistant = () => {
  assistantExpanded.value = !assistantExpanded.value
}

// 最小化助手
const minimizeAssistant = () => {
  assistantExpanded.value = false
}

// 关闭助手
const closeAssistant = () => {
  assistantExpanded.value = false
  assistantMessages.value = [
    { role: 'ai', content: '您好！我是您的 AI 智能助手。我可以帮您翻译文本、总结内容、实时转录会议、润色写作等。有什么可以帮您的吗？' }
  ]
}

// 切换功能模式
const switchMode = (mode: string) => {
  currentMode.value = mode
}

// 获取模式标签
const getModeLabel = (mode: string) => {
  const modeLabels: Record<string, string> = {
    translate: '翻译',
    summary: '总结',
    transcribe: '转录',
    polish: '润色'
  }
  return modeLabels[mode] || ''
}

// 开始拖动悬浮球
const startDragBall = (e: MouseEvent) => {
  // 悬浮球可以拖动，但这里简单实现点击展开
  e.preventDefault()
}

// 开始拖动窗口
const startDragWindow = (e: MouseEvent) => {
  if ((e.target as HTMLElement).closest('.header-actions')) {
    return
  }
  dragging.value = true
  dragOffset.x = e.clientX - windowPos.x
  dragOffset.y = e.clientY - windowPos.y
  
  document.addEventListener('mousemove', handleDrag)
  document.addEventListener('mouseup', stopDrag)
}

// 处理拖动
const handleDrag = (e: MouseEvent) => {
  if (!dragging.value) return
  
  const newX = e.clientX - dragOffset.x
  const newY = e.clientY - dragOffset.y
  
  // 限制窗口在屏幕范围内
  windowPos.x = Math.max(0, Math.min(newX, window.innerWidth - 400))
  windowPos.y = Math.max(0, Math.min(newY, window.innerHeight - 600))
}

// 停止拖动
const stopDrag = () => {
  dragging.value = false
  document.removeEventListener('mousemove', handleDrag)
  document.removeEventListener('mouseup', stopDrag)
}

// 发送消息
const handleSend = async () => {
  if (!userInput.value.trim()) return
  
  const message = userInput.value.trim()
  assistantMessages.value.push({ role: 'user', content: message })
  userInput.value = ''
  
  // 滚动到底部
  await nextTick()
  scrollToBottom()
  
  // 模拟AI回复
  isTyping.value = true
  sendingMessage.value = true
  
  setTimeout(() => {
    const responses = [
      '好的，我已经理解您的需求。让我帮您处理一下。',
      '根据您的描述，我建议您可以这样做...',
      '这是一个很好的问题，我来为您解答。',
      '我已经为您准备好了相关的解决方案。',
      '让我帮您分析一下这个问题的要点。'
    ]
    
    const response = responses[Math.floor(Math.random() * responses.length)]
    assistantMessages.value.push({ role: 'ai', content: response })
    isTyping.value = false
    sendingMessage.value = false
    
    nextTick(() => scrollToBottom())
  }, 1500)
}

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 切换语音输入
const toggleVoiceInput = () => {
  isRecording.value = !isRecording.value
  
  if (isRecording.value) {
    ElMessage.info('语音输入已开启，请说话...')
    // 这里可以集成实际的语音识别API
    setTimeout(() => {
      if (isRecording.value) {
        userInput.value = '这是语音识别的测试内容'
        isRecording.value = false
        ElMessage.success('语音识别完成')
      }
    }, 3000)
  } else {
    ElMessage.info('语音输入已关闭')
  }
}

// 翻译功能
const handleTranslate = () => {
  if (!translateInput.value.trim()) {
    ElMessage.warning('请输入需要翻译的文本')
    return
  }
  
  translating.value = true
  
  setTimeout(() => {
    // 模拟翻译结果
    const translations: Record<string, string> = {
      'en': 'This is the translation result.',
      'zh': '这是翻译结果。',
      'ja': 'これは翻訳結果です。',
      'ko': '이것은 번역 결과입니다.'
    }
    
    translateResult.value = translations[translateTo.value] || '翻译结果'
    translating.value = false
    ElMessage.success('翻译完成')
  }, 1500)
}

// 总结功能
const handleSummary = () => {
  if (!summaryInput.value.trim()) {
    ElMessage.warning('请输入需要总结的内容')
    return
  }
  
  summarizing.value = true
  
  setTimeout(() => {
    const lengthTexts: Record<string, string> = {
      brief: '本文主要讨论了相关主题的核心内容，提出了几个关键观点和解决方案。',
      normal: '本文详细阐述了主题的背景和现状，分析了存在的问题，并提出了相应的解决方案。主要内容包括：问题分析、方案设计、实施步骤和预期效果。通过系统性的方法，可以有效解决当前面临的挑战。',
      detailed: '本文全面深入地探讨了相关主题，首先介绍了背景和现状，分析了存在的问题和挑战。然后，详细阐述了解决方案的设计思路、实施步骤和关键技术点。最后，总结了实施效果和未来展望。本文内容丰富、逻辑清晰，对于理解和解决相关问题具有重要参考价值。'
    }
    
    summaryOutput.value = lengthTexts[summaryLength.value]
    summarizing.value = false
    ElMessage.success('摘要生成完成')
  }, 2000)
}

// 开始转录
const startTranscribe = () => {
  isTranscribing.value = true
  transcribeSeconds.value = 0
  transcribeResult.value = ''
  
  transcribeTimer.value = setInterval(() => {
    transcribeSeconds.value++
    transcribeTime.value = formatTime(transcribeSeconds.value)
    
    // 模拟实时转录内容
    if (transcribeSeconds.value % 5 === 0) {
      const texts = [
        '大家好，今天我们来讨论一下项目进展。',
        '目前项目进展顺利，主要功能已经完成。',
        '接下来我们需要关注性能优化问题。',
        '希望大家能够按时完成各自的任务。'
      ]
      transcribeResult.value += texts[Math.floor(transcribeSeconds.value / 5) % texts.length] + '\n'
    }
  }, 1000)
  
  ElMessage.success('开始实时转录')
}

// 停止转录
const stopTranscribe = () => {
  isTranscribing.value = false
  if (transcribeTimer.value) {
    clearInterval(transcribeTimer.value)
    transcribeTimer.value = null
  }
  ElMessage.success('转录已停止')
}

// 润色功能
const handlePolish = () => {
  if (!polishInput.value.trim()) {
    ElMessage.warning('请输入需要润色的文本')
    return
  }
  
  polishing.value = true
  
  setTimeout(() => {
    const styleTexts: Record<string, string> = {
      formal: '经审慎评估，我们认为该项目具有重要的战略意义，建议予以批准并积极推进。',
      casual: '这个项目看起来挺不错的，我觉得可以做，大家一起加油！',
      academic: '基于系统性的分析框架，本研究对相关议题进行了深入探讨，研究结果表明该方法具有显著的理论价值和实践意义。',
      concise: '项目可行，建议批准。'
    }
    
    polishResult.value = styleTexts[polishStyle.value]
    polishing.value = false
    ElMessage.success('润色完成')
  }, 1500)
}

// 复制文本
const copyText = (text: string) => {
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('已复制到剪贴板')
  })
}

// 生命周期
onMounted(() => {
  // 初始化
})

onUnmounted(() => {
  if (transcribeTimer.value) {
    clearInterval(transcribeTimer.value)
  }
})
</script>

<style scoped>
.meeting-ai {
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

/* AI功能列表 */
.ai-functions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.function-item {
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

.function-item:hover {
  background: #e5e7eb;
  transform: translateX(4px);
}

.function-item.active {
  border-color: #409eff;
  background: #ecf5ff;
}

.function-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  flex-shrink: 0;
}

.function-info {
  flex: 1;
  min-width: 0;
}

.function-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.function-desc {
  font-size: 12px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* AI状态 */
.ai-status-section {
  margin-top: 20px;
}

.status-cards {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 6px;
}

.status-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.status-info {
  flex: 1;
}

.status-label {
  font-size: 12px;
  color: #909399;
}

.status-value {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

/* 功能面板 */
.function-panel {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

/* 转录结果 */
.transcription-result {
  margin-top: 20px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.result-content {
  max-height: 400px;
  overflow-y: auto;
}

.transcription-segment {
  display: flex;
  gap: 8px;
  padding: 8px;
  margin-bottom: 8px;
  background: white;
  border-radius: 4px;
}

.segment-time {
  font-size: 12px;
  color: #909399;
  min-width: 60px;
}

.segment-speaker {
  font-size: 12px;
  color: #409eff;
  min-width: 60px;
}

.segment-text {
  flex: 1;
  font-size: 14px;
  color: #303133;
  line-height: 1.6;
}

/* 摘要结果 */
.summary-result {
  margin-top: 20px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
}

.summary-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.summary-item {
  padding: 12px;
  background: white;
  border-radius: 6px;
}

.item-title {
  font-size: 13px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 8px;
}

.item-text {
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

/* 智能问答 */
.qa-chat-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chat-messages {
  flex: 1;
  max-height: 400px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-message {
  display: flex;
  gap: 12px;
}

.chat-message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #ecf5ff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #409eff;
  font-size: 20px;
  flex-shrink: 0;
}

.chat-message.ai .message-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.message-content {
  max-width: 70%;
}

.message-sender {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.chat-message.user .message-sender {
  text-align: right;
}

.message-text {
  padding: 12px;
  background: white;
  border-radius: 8px;
  font-size: 14px;
  color: #303133;
  line-height: 1.6;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.chat-message.user .message-text {
  background: #409eff;
  color: white;
}

.chat-input {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-actions {
  display: flex;
  gap: 8px;
}

.quick-questions {
  margin-top: 16px;
}

.quick-title {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.quick-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* 情感分析结果 */
.sentiment-result {
  margin-top: 20px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
}

.sentiment-overview {
  margin-bottom: 20px;
}

.sentiment-main {
  text-align: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
}

.main-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 12px;
}

.main-value {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 16px;
}

.main-value.sentiment-positive {
  color: #67c23a;
}

.main-value.sentiment-neutral {
  color: #909399;
}

.main-value.sentiment-negative {
  color: #f56c6c;
}

.confidence-label {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.sentiment-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.detail-item {
  padding: 12px;
  background: white;
  border-radius: 6px;
}

.detail-label {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.sentiment-keywords {
  padding: 12px;
  background: white;
  border-radius: 6px;
}

.keywords-title {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.keywords-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* 关键词结果 */
.keyword-result {
  margin-top: 20px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
}

.keywords-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding: 16px;
  background: white;
  border-radius: 6px;
}

.keyword-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 6px;
  color: white;
}

.keyword-score {
  font-size: 11px;
  opacity: 0.8;
}

/* 任务结果 */
.task-result {
  margin-top: 20px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-item {
  padding: 12px;
  background: white;
  border-radius: 6px;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.task-details {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #606266;
}

.task-assignee,
.task-deadline {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 右侧面板 */
.analysis-section,
.suggestions-section,
.capabilities-section,
.recent-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
}

/* 质量指标 */
.quality-metrics {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 6px;
}

.metric-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

.metric-info {
  flex: 1;
}

.metric-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.metric-label {
  font-size: 12px;
  color: #909399;
}

.quality-chart {
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.chart-placeholder {
  height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
}

.chart-placeholder p {
  margin-top: 12px;
  font-size: 14px;
}

/* AI建议 */
.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.suggestion-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 6px;
}

.suggestion-icon {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  flex-shrink: 0;
}

.suggestion-content {
  flex: 1;
}

.suggestion-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.suggestion-desc {
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}

/* AI能力 */
.capability-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.capability-item {
  padding: 12px;
  background: #f9fafb;
  border-radius: 6px;
}

.capability-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.capability-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

/* 最近处理 */
.process-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
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

/* ========== 悬浮AI助手样式 ========== */
.floating-ai-assistant {
  position: fixed;
  z-index: 9999;
}

/* 悬浮球 */
.floating-ball {
  position: fixed;
  right: 30px;
  bottom: 30px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  z-index: 10000;
}

.floating-ball:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 30px rgba(102, 126, 234, 0.6);
}

.floating-ball:active {
  transform: scale(0.95);
}

.ball-icon {
  color: white;
  font-size: 28px;
  z-index: 1;
}

/* 涟漪效果 */
.ball-ripple {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: rgba(102, 126, 234, 0.3);
  animation: ripple 2s infinite;
}

.ball-ripple.delay-1 {
  animation-delay: 0.5s;
}

.ball-ripple.delay-2 {
  animation-delay: 1s;
}

@keyframes ripple {
  0% {
    transform: scale(1);
    opacity: 0.6;
  }
  100% {
    transform: scale(2);
    opacity: 0;
  }
}

/* 助手窗口 */
.assistant-window {
  position: fixed;
  width: 400px;
  max-height: 600px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 10001;
  animation: slideIn 0.3s ease;
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

/* 窗口标题栏 */
.window-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  cursor: move;
  user-select: none;
}

.header-title {
  display: flex;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
}

.ai-icon {
  font-size: 20px;
  margin-right: 8px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.header-actions .el-button {
  color: white !important;
}

/* 功能菜单 */
.function-menu {
  display: flex;
  gap: 4px;
  padding: 8px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.menu-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 12px;
  color: #606266;
}

.menu-item:hover {
  background: white;
  color: #409eff;
}

.menu-item.active {
  background: white;
  color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.menu-item .el-icon {
  font-size: 18px;
}

/* 内容区域 */
.assistant-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

/* 聊天区域 */
.chat-area {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-right: 4px;
}

.message {
  display: flex;
  gap: 12px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 18px;
}

.message.ai .message-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.message.user .message-avatar {
  background: #e5e7eb;
  color: #606266;
}

.message-body {
  max-width: 70%;
}

.message-content {
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
  font-size: 14px;
}

.message.ai .message-content {
  background: #f3f4f6;
  color: #303133;
}

.message.user .message-content {
  background: #409eff;
  color: white;
}

/* 打字指示器 */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  background: #f3f4f6;
  border-radius: 12px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #909399;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-8px);
    opacity: 1;
  }
}

/* 工具区域 */
.tool-area {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.translate-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
}

.translate-arrow {
  font-size: 16px;
  color: #909399;
}

.translate-input,
.summary-input,
.polish-input {
  margin-top: 8px;
}

.summary-options,
.polish-options {
  display: flex;
  justify-content: center;
  margin-top: 8px;
}

.result-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.result-text {
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
  white-space: pre-wrap;
}

.translate-result,
.summary-result,
.polish-result,
.transcribe-result {
  margin-top: 12px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
}

/* 转录状态 */
.transcribe-status {
  padding: 20px;
  background: #f9fafb;
  border-radius: 8px;
  text-align: center;
  margin-bottom: 12px;
}

.status-idle .mic-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 12px;
}

.status-idle p {
  font-size: 14px;
  color: #606266;
  margin: 0;
}

.status-active {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.recording-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #303133;
}

.recording-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #f56c6c;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.transcribe-time {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  font-family: monospace;
}

/* 输入区域 */
.assistant-input {
  display: flex;
  gap: 8px;
  padding: 16px 20px;
  background: white;
  border-top: 1px solid #e5e7eb;
}

.assistant-input .el-textarea {
  flex: 1;
}

.input-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  justify-content: flex-end;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .assistant-window {
    width: calc(100vw - 40px);
    max-height: calc(100vh - 100px);
    right: 20px !important;
    left: 20px !important;
    bottom: 80px !important;
    top: auto !important;
  }
  
  .floating-ball {
    width: 50px;
    height: 50px;
    right: 20px;
    bottom: 20px;
  }
  
  .ball-icon {
    font-size: 24px;
  }
}
</style>
