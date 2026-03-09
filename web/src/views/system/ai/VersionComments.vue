<template>
  <div class="version-comments-container">
    <!-- 统计面板 -->
    <div class="stats-panel">
      <div class="stat-item">
        <div class="stat-value">{{ comments.length }}</div>
        <div class="stat-label">总批注数</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ pendingComments }}</div>
        <div class="stat-label">待处理</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ resolvedComments }}</div>
        <div class="stat-label">已解决</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ highPriorityComments }}</div>
        <div class="stat-label">高优先级</div>
      </div>
    </div>

    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-select v-model="currentVersionId" placeholder="选择版本" style="width: 200px" @change="handleVersionChange">
          <el-option
            v-for="version in versions"
            :key="version.id"
            :label="`v${version.version}`"
            :value="version.id"
          />
        </el-select>

        <!-- 搜索框 -->
        <el-input
          v-model="searchKeyword"
          placeholder="搜索批注内容..."
          style="width: 250px"
          :prefix-icon="Search"
          clearable
        />

        <!-- 过滤器 -->
        <el-select v-model="filterCategory" placeholder="分类" style="width: 120px" clearable>
          <el-option label="全部" value="" />
          <el-option label="功能建议" value="feature" />
          <el-option label="问题反馈" value="bug" />
          <el-option label="内容建议" value="content" />
          <el-option label="翻译问题" value="translation" />
        </el-select>

        <el-select v-model="filterStatus" placeholder="状态" style="width: 120px" clearable>
          <el-option label="全部" value="" />
          <el-option label="待处理" value="pending" />
          <el-option label="已解决" value="resolved" />
          <el-option label="已关闭" value="closed" />
        </el-select>

        <el-select v-model="filterPriority" placeholder="优先级" style="width: 120px" clearable>
          <el-option label="全部" value="" />
          <el-option label="高" value="high" />
          <el-option label="中" value="medium" />
          <el-option label="低" value="low" />
        </el-select>

        <!-- 排序 -->
        <el-select v-model="sortBy" placeholder="排序" style="width: 120px">
          <el-option label="最新" value="newest" />
          <el-option label="最早" value="oldest" />
          <el-option label="优先级" value="priority" />
        </el-select>
      </div>
      <div class="toolbar-right">
        <el-tag type="info">显示: {{ filteredComments.length }} / {{ comments.length }}</el-tag>
        <el-button :icon="Download" @click="handleExport">
          导出
        </el-button>
        <el-button type="primary" :icon="Plus" @click="handleAddComment">
          添加批注
        </el-button>
      </div>
    </div>

    <!-- 批注列表 -->
    <div class="comments-list">
      <div
        v-for="comment in filteredComments"
        :key="comment.id"
        class="comment-item"
        :class="[
          `priority-${comment.priority}`,
          `status-${comment.status}`
        ]"
      >
        <!-- 批注主卡片 -->
        <div class="comment-main">
          <div class="comment-header">
            <div class="comment-author">
              <el-icon><User /></el-icon>
              <span>{{ comment.author }}</span>
              <el-tag size="small" :type="getCategoryType(comment.category)" class="category-tag">
                {{ getCategoryLabel(comment.category) }}
              </el-tag>
              <el-tag size="small" :type="getPriorityType(comment.priority)" class="priority-tag">
                {{ getPriorityLabel(comment.priority) }}
              </el-tag>
              <el-tag size="small" :type="getStatusType(comment.status)" class="status-tag">
                {{ getStatusLabel(comment.status) }}
              </el-tag>
            </div>
            <div class="comment-actions">
              <el-dropdown @command="(cmd) => handleStatusChange(comment, cmd)">
                <el-button size="small" text>
                  状态 <el-icon><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="pending">待处理</el-dropdown-item>
                    <el-dropdown-item command="resolved">已解决</el-dropdown-item>
                    <el-dropdown-item command="closed">已关闭</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              <el-button size="small" text @click="handleReplyComment(comment)">
                <el-icon><ChatDotRound /></el-icon> 回复
              </el-button>
              <el-button size="small" text @click="handleEditComment(comment)">
                编辑
              </el-button>
              <el-button size="small" text type="danger" @click="handleDeleteComment(comment)">
                删除
              </el-button>
            </div>
          </div>

          <div class="comment-content">{{ comment.content }}</div>

          <div class="comment-footer">
            <div class="comment-time">{{ comment.time }}</div>
            <div class="comment-replies" v-if="comment.replies && comment.replies.length > 0">
              <el-button text size="small" @click="toggleReplies(comment)">
                {{ comment.showReplies ? '收起' : `展开回复 (${comment.replies.length})` }}
                <el-icon :class="{ 'rotate-180': comment.showReplies }"><ArrowDown /></el-icon>
              </el-button>
            </div>
          </div>

          <!-- 回复列表 -->
          <div v-if="comment.showReplies && comment.replies" class="replies-list">
            <div v-for="reply in comment.replies" :key="reply.id" class="reply-item">
              <div class="reply-header">
                <span class="reply-author">{{ reply.author }}</span>
                <span class="reply-time">{{ reply.time }}</span>
              </div>
              <div class="reply-content">{{ reply.content }}</div>
            </div>
          </div>
        </div>
      </div>
      <div v-if="filteredComments.length === 0" class="empty-state">
        <el-icon class="empty-icon"><ChatLineRound /></el-icon>
        <p>暂无批注</p>
      </div>
    </div>

    <!-- 添加/编辑批注对话框 -->
    <el-dialog
      v-model="showCommentDialog"
      :title="dialogMode === 'add' ? '添加批注' : '编辑批注'"
      width="600px"
    >
      <el-form :model="commentForm" label-width="80px">
        <el-form-item label="批注内容">
          <el-input
            v-model="commentForm.content"
            type="textarea"
            :rows="6"
            placeholder="请输入批注内容"
          />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="commentForm.category" placeholder="请选择分类" style="width: 100%">
            <el-option label="功能建议" value="feature" />
            <el-option label="问题反馈" value="bug" />
            <el-option label="内容建议" value="content" />
            <el-option label="翻译问题" value="translation" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="commentForm.priority" placeholder="请选择优先级" style="width: 100%">
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCommentDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmComment">确定</el-button>
      </template>
    </el-dialog>

    <!-- 回复批注对话框 -->
    <el-dialog
      v-model="showReplyDialog"
      title="回复批注"
      width="500px"
    >
      <el-form :model="replyForm" label-width="80px">
        <el-form-item label="回复内容">
          <el-input
            v-model="replyForm.content"
            type="textarea"
            :rows="4"
            placeholder="请输入回复内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showReplyDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmReply">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, User, ChatLineRound, Search, ArrowDown, ChatDotRound, Download } from '@element-plus/icons-vue'

// 数据状态
const currentVersionId = ref(1)
const showCommentDialog = ref(false)
const showReplyDialog = ref(false)
const dialogMode = ref('add') // add 或 edit
const editingCommentId = ref(null)
const replyingCommentId = ref(null)
const searchKeyword = ref('')
const filterCategory = ref('')
const filterStatus = ref('')
const filterPriority = ref('')
const sortBy = ref('newest')

const versions = ref([
  { id: 1, version: '2.1.0' },
  { id: 2, version: '2.0.5' },
  { id: 3, version: '2.0.4' },
  { id: 4, version: '2.0.3' }
])

const comments = ref([
  {
    id: 1,
    versionId: 1,
    author: '张三',
    time: '2026-01-27 14:30:00',
    content: '这个版本的产品功能介绍很详细，翻译质量很好。建议在后续版本中增加更多示例。',
    category: 'feature',
    priority: 'medium',
    status: 'pending',
    showReplies: false,
    replies: [
      {
        id: 11,
        author: '李四',
        time: '2026-01-27 15:00:00',
        content: '同意，增加示例确实能帮助用户更好地理解功能。'
      }
    ]
  },
  {
    id: 2,
    versionId: 1,
    author: '李四',
    time: '2026-01-27 15:20:00',
    content: '用户指南章节的内容清晰易懂，但是在操作步骤部分可以更详细一些。',
    category: 'content',
    priority: 'high',
    status: 'resolved',
    showReplies: false,
    replies: []
  },
  {
    id: 3,
    versionId: 1,
    author: '王五',
    time: '2026-01-27 16:10:00',
    content: '整体翻译流畅，术语使用准确。建议优化一下排版格式，使文档更加美观。',
    category: 'translation',
    priority: 'low',
    status: 'pending',
    showReplies: false,
    replies: []
  },
  {
    id: 4,
    versionId: 1,
    author: '赵六',
    time: '2026-01-28 09:30:00',
    content: '在第2章第3节发现了一个术语翻译错误，"API密钥"应该翻译为"API Key"。',
    category: 'bug',
    priority: 'high',
    status: 'pending',
    showReplies: false,
    replies: []
  }
])

const commentForm = reactive({
  content: '',
  category: 'feature',
  priority: 'medium'
})

const replyForm = reactive({
  content: ''
})

// 计算属性
const currentVersion = computed(() => {
  return versions.value.find(v => v.id === currentVersionId.value)
})

const versionComments = computed(() => {
  return comments.value.filter(c => c.versionId === currentVersionId.value)
})

const pendingComments = computed(() => {
  return comments.value.filter(c => c.status === 'pending').length
})

const resolvedComments = computed(() => {
  return comments.value.filter(c => c.status === 'resolved').length
})

const highPriorityComments = computed(() => {
  return comments.value.filter(c => c.priority === 'high').length
})

const filteredComments = computed(() => {
  let result = versionComments.value

  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(c =>
      c.content.toLowerCase().includes(keyword) ||
      c.author.toLowerCase().includes(keyword)
    )
  }

  // 分类过滤
  if (filterCategory.value) {
    result = result.filter(c => c.category === filterCategory.value)
  }

  // 状态过滤
  if (filterStatus.value) {
    result = result.filter(c => c.status === filterStatus.value)
  }

  // 优先级过滤
  if (filterPriority.value) {
    result = result.filter(c => c.priority === filterPriority.value)
  }

  // 排序
  if (sortBy.value === 'newest') {
    result = [...result].sort((a, b) => new Date(b.time) - new Date(a.time))
  } else if (sortBy.value === 'oldest') {
    result = [...result].sort((a, b) => new Date(a.time) - new Date(b.time))
  } else if (sortBy.value === 'priority') {
    const priorityOrder = { high: 0, medium: 1, low: 2 }
    result = [...result].sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority])
  }

  return result
})

// 辅助方法
const getCategoryLabel = (category) => {
  const labels = {
    feature: '功能建议',
    bug: '问题反馈',
    content: '内容建议',
    translation: '翻译问题'
  }
  return labels[category] || category
}

const getCategoryType = (category) => {
  const types = {
    feature: 'success',
    bug: 'danger',
    content: 'info',
    translation: 'warning'
  }
  return types[category] || ''
}

const getPriorityLabel = (priority) => {
  const labels = {
    high: '高',
    medium: '中',
    low: '低'
  }
  return labels[priority] || priority
}

const getPriorityType = (priority) => {
  const types = {
    high: 'danger',
    medium: 'warning',
    low: 'info'
  }
  return types[priority] || ''
}

const getStatusLabel = (status) => {
  const labels = {
    pending: '待处理',
    resolved: '已解决',
    closed: '已关闭'
  }
  return labels[status] || status
}

const getStatusType = (status) => {
  const types = {
    pending: 'warning',
    resolved: 'success',
    closed: 'info'
  }
  return types[status] || ''
}

// 主要方法
const handleVersionChange = () => {
  ElMessage.success(`已切换到版本 v${currentVersion.value.version}`)
}

const handleAddComment = () => {
  dialogMode.value = 'add'
  editingCommentId.value = null
  commentForm.content = ''
  commentForm.category = 'feature'
  commentForm.priority = 'medium'
  showCommentDialog.value = true
}

const handleEditComment = (comment) => {
  dialogMode.value = 'edit'
  editingCommentId.value = comment.id
  commentForm.content = comment.content
  commentForm.category = comment.category
  commentForm.priority = comment.priority
  showCommentDialog.value = true
}

const confirmComment = () => {
  if (!commentForm.content.trim()) {
    ElMessage.warning('请输入批注内容')
    return
  }

  const now = new Date().toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  })

  if (dialogMode.value === 'add') {
    const newComment = {
      id: Date.now(),
      versionId: currentVersionId.value,
      author: '当前用户',
      time: now,
      content: commentForm.content,
      category: commentForm.category,
      priority: commentForm.priority,
      status: 'pending',
      showReplies: false,
      replies: []
    }
    comments.value.unshift(newComment)
    ElMessage.success('批注添加成功')
  } else {
    const comment = comments.value.find(c => c.id === editingCommentId.value)
    if (comment) {
      comment.content = commentForm.content
      comment.category = commentForm.category
      comment.priority = commentForm.priority
      ElMessage.success('批注修改成功')
    }
  }

  showCommentDialog.value = false
}

const handleDeleteComment = (comment) => {
  ElMessageBox.confirm(
    '确定要删除这条批注吗？',
    '删除批注',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    const index = comments.value.findIndex(c => c.id === comment.id)
    if (index !== -1) {
      comments.value.splice(index, 1)
      ElMessage.success('批注删除成功')
    }
  }).catch(() => {})
}

const handleStatusChange = (comment, status) => {
  comment.status = status
  ElMessage.success(`状态已更新为${getStatusLabel(status)}`)
}

const handleReplyComment = (comment) => {
  replyingCommentId.value = comment.id
  replyForm.content = ''
  showReplyDialog.value = true
}

const confirmReply = () => {
  if (!replyForm.content.trim()) {
    ElMessage.warning('请输入回复内容')
    return
  }

  const comment = comments.value.find(c => c.id === replyingCommentId.value)
  if (comment) {
    const now = new Date().toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    })

    const newReply = {
      id: Date.now(),
      author: '当前用户',
      time: now,
      content: replyForm.content
    }

    if (!comment.replies) {
      comment.replies = []
    }
    comment.replies.push(newReply)
    comment.showReplies = true
    ElMessage.success('回复添加成功')
  }

  showReplyDialog.value = false
}

const toggleReplies = (comment) => {
  comment.showReplies = !comment.showReplies
}

const handleExport = () => {
  const data = filteredComments.value.map(comment => ({
    ID: comment.id,
    作者: comment.author,
    时间: comment.time,
    分类: getCategoryLabel(comment.category),
    优先级: getPriorityLabel(comment.priority),
    状态: getStatusLabel(comment.status),
    内容: comment.content,
    回复数: comment.replies ? comment.replies.length : 0
  }))

  // 创建CSV内容
  const headers = Object.keys(data[0]).join(',')
  const rows = data.map(row => Object.values(row).map(v => `"${v}"`).join(','))
  const csv = [headers, ...rows].join('\n')

  // 创建下载链接
  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `批注列表_v${currentVersion.value.version}_${new Date().toLocaleDateString('zh-CN')}.csv`
  link.click()
  URL.revokeObjectURL(url)

  ElMessage.success('导出成功')
}
</script>

<style scoped>
.version-comments-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
  overflow: hidden;
}

/* 统计面板 */
.stats-panel {
  display: flex;
  gap: 20px;
  padding: 20px 24px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  flex-shrink: 0;
}

.stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.stat-item:hover {
  transform: translateY(-2px);
}

.stat-item:nth-child(2) {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-item:nth-child(3) {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-item:nth-child(4) {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  line-height: 1;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  flex-shrink: 0;
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

/* 批注列表 */
.comments-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comment-item {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
  border-left: 4px solid #409eff;
}

.comment-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

/* 优先级样式 */
.comment-item.priority-high {
  border-left-color: #f56c6c;
}

.comment-item.priority-medium {
  border-left-color: #e6a23c;
}

.comment-item.priority-low {
  border-left-color: #909399;
}

/* 状态样式 */
.comment-item.status-pending {
  border-top: 2px solid #e6a23c;
}

.comment-item.status-resolved {
  border-top: 2px solid #67c23a;
}

.comment-item.status-closed {
  border-top: 2px solid #909399;
  opacity: 0.7;
}

.comment-main {
  width: 100%;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.comment-author {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  font-size: 14px;
  color: #333;
  flex-wrap: wrap;
}

.comment-author .el-icon {
  font-size: 16px;
  color: #409eff;
}

.category-tag,
.priority-tag,
.status-tag {
  margin-left: 4px;
}

.comment-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.comment-content {
  font-size: 15px;
  line-height: 1.8;
  color: #555;
  margin-bottom: 16px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 3px solid #409eff;
}

.comment-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.comment-time {
  font-size: 12px;
  color: #999;
}

.comment-replies {
  display: flex;
  align-items: center;
}

.rotate-180 {
  transform: rotate(180deg);
}

/* 回复列表 */
.replies-list {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 2px solid #f0f0f0;
}

.reply-item {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 12px;
  border-left: 3px solid #67c23a;
}

.reply-item:last-child {
  margin-bottom: 0;
}

.reply-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.reply-author {
  font-weight: 500;
  font-size: 13px;
  color: #333;
}

.reply-time {
  font-size: 11px;
  color: #999;
}

.reply-content {
  font-size: 14px;
  line-height: 1.6;
  color: #666;
}

/* 空状态 */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #999;
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 20px;
  color: #d9d9d9;
}

.empty-state p {
  font-size: 15px;
  margin: 0;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-panel {
    padding: 16px;
    gap: 10px;
  }

  .stat-value {
    font-size: 24px;
  }

  .stat-label {
    font-size: 12px;
  }

  .toolbar {
    padding: 12px 16px;
  }

  .toolbar-left,
  .toolbar-right {
    width: 100%;
    justify-content: center;
  }

  .comments-list {
    padding: 12px 16px;
  }

  .comment-item {
    padding: 16px;
  }

  .comment-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .comment-content {
    font-size: 14px;
  }
}

/* 滚动条样式 */
.comments-list::-webkit-scrollbar {
  width: 8px;
}

.comments-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.comments-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.comments-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
