<template>
  <div class="version-comments-container">
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
      </div>
      <div class="toolbar-right">
        <el-tag type="info">批注数: {{ comments.length }}</el-tag>
        <el-button type="primary" :icon="Plus" @click="handleAddComment">
          添加批注
        </el-button>
      </div>
    </div>

    <!-- 批注列表 -->
    <div class="comments-list">
      <div
        v-for="comment in comments"
        :key="comment.id"
        class="comment-item"
      >
        <div class="comment-header">
          <div class="comment-author">
            <el-icon><User /></el-icon>
            <span>{{ comment.author }}</span>
          </div>
          <div class="comment-time">{{ comment.time }}</div>
        </div>
        <div class="comment-content">{{ comment.content }}</div>
        <div class="comment-actions">
          <el-button size="small" text @click="handleEditComment(comment)">
            编辑
          </el-button>
          <el-button size="small" text type="danger" @click="handleDeleteComment(comment)">
            删除
          </el-button>
        </div>
      </div>
      <div v-if="comments.length === 0" class="empty-state">
        <el-icon class="empty-icon"><ChatLineRound /></el-icon>
        <p>暂无批注</p>
      </div>
    </div>

    <!-- 添加/编辑批注对话框 -->
    <el-dialog
      v-model="showCommentDialog"
      :title="dialogMode === 'add' ? '添加批注' : '编辑批注'"
      width="500px"
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
      </el-form>
      <template #footer>
        <el-button @click="showCommentDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmComment">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, User, ChatLineRound } from '@element-plus/icons-vue'

// 数据状态
const currentVersionId = ref(1)
const showCommentDialog = ref(false)
const dialogMode = ref('add') // add 或 edit
const editingCommentId = ref(null)

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
    content: '这个版本的产品功能介绍很详细，翻译质量很好。建议在后续版本中增加更多示例。'
  },
  {
    id: 2,
    versionId: 1,
    author: '李四',
    time: '2026-01-27 15:20:00',
    content: '用户指南章节的内容清晰易懂，但是在操作步骤部分可以更详细一些。'
  },
  {
    id: 3,
    versionId: 1,
    author: '王五',
    time: '2026-01-27 16:10:00',
    content: '整体翻译流畅，术语使用准确。建议优化一下排版格式，使文档更加美观。'
  }
])

const commentForm = reactive({
  content: ''
})

// 计算属性
const currentVersion = computed(() => {
  return versions.value.find(v => v.id === currentVersionId.value)
})

const versionComments = computed(() => {
  return comments.value.filter(c => c.versionId === currentVersionId.value)
})

// 方法
const handleVersionChange = () => {
  ElMessage.success(`已切换到版本 v${currentVersion.value.version}`)
}

const handleAddComment = () => {
  dialogMode.value = 'add'
  editingCommentId.value = null
  commentForm.content = ''
  showCommentDialog.value = true
}

const handleEditComment = (comment) => {
  dialogMode.value = 'edit'
  editingCommentId.value = comment.id
  commentForm.content = comment.content
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
      id: comments.value.length + 1,
      versionId: currentVersionId.value,
      author: '当前用户',
      time: now,
      content: commentForm.content
    }
    comments.value.unshift(newComment)
    ElMessage.success('批注添加成功')
  } else {
    const comment = comments.value.find(c => c.id === editingCommentId.value)
    if (comment) {
      comment.content = commentForm.content
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
</script>

<style scoped>
.version-comments-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  gap: 12px;
  align-items: center;
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
  border-radius: 8px;
  padding: 16px;
  border-left: 3px solid #409eff;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.comment-author {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
  font-size: 14px;
  color: #333;
}

.comment-time {
  font-size: 12px;
  color: #999;
}

.comment-content {
  font-size: 14px;
  line-height: 1.6;
  color: #666;
  margin-bottom: 12px;
}

.comment-actions {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
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
  font-size: 64px;
  margin-bottom: 16px;
  color: #d9d9d9;
}

.empty-state p {
  font-size: 14px;
  margin: 0;
}
</style>
