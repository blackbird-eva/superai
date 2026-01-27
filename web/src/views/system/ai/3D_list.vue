<template>
  <div class="3d-list-container">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button type="primary" :icon="Upload" @click="handleImport">
          导入3D文件
        </el-button>
        <el-button :icon="Refresh" @click="handleRefresh">
          刷新
        </el-button>
      </div>
      <div class="toolbar-center">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索内容..."
          prefix-icon="Search"
          style="width: 250px"
          clearable
        />
        <el-select v-model="filterType" placeholder="筛选类型" style="width: 140px" clearable>
          <el-option label="全部" value=""></el-option>
          <el-option label="模型" value="model"></el-option>
          <el-option label="场景" value="scene"></el-option>
          <el-option label="材质" value="material"></el-option>
        </el-select>
      </div>
      <div class="toolbar-right">
        <el-tag type="info">总数: {{ filteredList.length }}</el-tag>
        <el-button type="primary" :icon="Download" @click="handleExport">
          导出
        </el-button>
      </div>
    </div>

    <!-- 3D列表 -->
    <div class="list-container">
      <div
        v-for="item in filteredList"
        :key="item.id"
        class="list-item"
        :class="{ expanded: item.expanded }"
      >
        <!-- 列表项头部 -->
        <div class="item-header" @click="toggleExpand(item)">
          <div class="item-icon">
            <el-icon>
              <component :is="item.type === 'model' ? Box : Picture" />
            </el-icon>
          </div>
          <div class="item-info">
            <div class="item-title">{{ item.title }}</div>
            <div class="item-meta">
              <el-tag size="small" :type="getTypeTagType(item.type)">
                {{ getTypeText(item.type) }}
              </el-tag>
              <span class="meta-text">{{ item.createTime }}</span>
            </div>
          </div>
          <div class="item-actions">
            <el-button size="small" text @click.stop="handleView3D(item)">
              <el-icon><View /></el-icon>
            </el-button>
            <el-button size="small" text @click.stop="toggleExpand(item)">
              <el-icon>
                <component :is="item.expanded ? ArrowUp : ArrowDown" />
              </el-icon>
            </el-button>
          </div>
        </div>

        <!-- 展开内容 -->
        <div v-if="item.expanded" class="item-content">
          <!-- 原文本 -->
          <div class="content-section">
            <div class="section-title">
              <el-icon><Document /></el-icon>
              原文本
            </div>
            <div class="content-text">{{ item.originalText }}</div>
          </div>

          <!-- 翻译文本 -->
          <div class="content-section">
            <div class="section-title">
              <el-icon><ChatDotRound /></el-icon>
              翻译文本
            </div>
            <div class="content-text">{{ item.translatedText || '暂无翻译' }}</div>
          </div>

          <!-- 注释 -->
          <div class="content-section comment-section">
            <div class="section-title">
              <el-icon><ChatLineRound /></el-icon>
              注释
              <el-button size="small" text @click="handleAddComment(item)">
                <el-icon><Plus /></el-icon>
              </el-button>
            </div>
            <div v-if="item.comments && item.comments.length > 0" class="comments-list">
              <div
                v-for="(comment, idx) in item.comments"
                :key="idx"
                class="comment-item"
              >
                <div class="comment-header">
                  <span class="comment-author">{{ comment.author }}</span>
                  <span class="comment-time">{{ comment.time }}</span>
                </div>
                <div class="comment-text">{{ comment.content }}</div>
              </div>
            </div>
            <div v-else class="no-comment">暂无注释</div>
          </div>

          <!-- 标签 -->
          <div class="content-section">
            <div class="section-title">
              <el-icon><PriceTag /></el-icon>
              标签
            </div>
            <div class="tags-container">
              <el-tag
                v-for="(tag, idx) in item.tags"
                :key="idx"
                size="small"
              >
                {{ tag }}
              </el-tag>
              <el-tag v-if="!item.tags?.length" type="info" size="small">
                暂无标签
              </el-tag>
            </div>
          </div>
        </div>
      </div>

      <div v-if="filteredList.length === 0" class="empty-state">
        <el-icon class="empty-icon"><Box /></el-icon>
        <p>暂无数据</p>
      </div>
    </div>

    <!-- 添加注释对话框 -->
    <el-dialog v-model="showCommentDialog" title="添加注释" width="500px">
      <el-form :model="commentForm" label-width="80px">
        <el-form-item label="注释内容">
          <el-input
            v-model="commentForm.content"
            type="textarea"
            :rows="4"
            placeholder="请输入注释内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCommentDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmAddComment">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Upload,
  Refresh,
  Search,
  Download,
  Box,
  Picture,
  View,
  ArrowUp,
  ArrowDown,
  Document,
  ChatDotRound,
  ChatLineRound,
  PriceTag,
  Plus
} from '@element-plus/icons-vue'

// 数据状态
const searchKeyword = ref('')
const filterType = ref('')
const showCommentDialog = ref(false)
const currentItem = ref(null)

const commentForm = reactive({
  content: ''
})

const listData = ref([
  {
    id: 1,
    type: 'model',
    title: '产品主模型',
    createTime: '2026-01-27 14:30:00',
    originalText: '3D Product Model - Main structure with 2000 polygons, optimized for real-time rendering. Contains detailed textures and materials.',
    translatedText: '3D产品模型 - 包含2000个多边形的主结构，经过优化可用于实时渲染。包含详细的纹理和材质。',
    expanded: false,
    tags: ['主模型', '优化', '实时渲染'],
    comments: [
      {
        author: '张三',
        time: '2026-01-27 15:20:00',
        content: '模型质量很高，多边形数量控制得很好。'
      }
    ]
  },
  {
    id: 2,
    type: 'scene',
    title: '展示场景',
    createTime: '2026-01-27 15:00:00',
    originalText: 'Exhibition Scene - Complete environment setup with lighting, camera setup and background elements.',
    translatedText: '展示场景 - 完整的环境设置，包括灯光、摄像机设置和背景元素。',
    expanded: false,
    tags: ['场景', '光照'],
    comments: []
  },
  {
    id: 3,
    type: 'material',
    title: '金属材质',
    createTime: '2026-01-27 15:30:00',
    originalText: 'Metal Material - High-quality PBR material with metallic roughness workflow. Includes albedo, normal, and roughness maps.',
    translatedText: '金属材质 - 高质量PBR材质，使用金属粗糙度工作流。包含反照率、法线和粗糙度贴图。',
    expanded: false,
    tags: ['材质', 'PBR'],
    comments: [
      {
        author: '李四',
        time: '2026-01-27 16:10:00',
        content: '材质参数设置准确，渲染效果很好。'
      },
      {
        author: '王五',
        time: '2026-01-27 16:30:00',
        content: '建议增加环境光遮蔽贴图以提升细节。'
      }
    ]
  },
  {
    id: 4,
    type: 'model',
    title: '配件模型',
    createTime: '2026-01-27 16:00:00',
    originalText: 'Accessory Model - Detailed component model for assembly. Optimized mesh topology with UV mapping.',
    translatedText: '配件模型 - 用于组装的详细组件模型。优化的网格拓扑和UV映射。',
    expanded: false,
    tags: ['配件', 'UV'],
    comments: []
  },
  {
    id: 5,
    type: 'scene',
    title: '测试场景',
    createTime: '2026-01-27 16:45:00',
    originalText: 'Test Scene - Simple scene for testing materials and lighting setup.',
    translatedText: '测试场景 - 用于测试材质和灯光设置的简单场景。',
    expanded: false,
    tags: ['测试', '场景'],
    comments: [
      {
        author: '张三',
        time: '2026-01-27 17:00:00',
        content: '测试场景简洁实用，方便验证效果。'
      }
    ]
  }
])

// 计算属性
const filteredList = computed(() => {
  let result = listData.value

  if (searchKeyword.value) {
    result = result.filter(item =>
      item.title.includes(searchKeyword.value) ||
      item.originalText.includes(searchKeyword.value) ||
      item.translatedText?.includes(searchKeyword.value)
    )
  }

  if (filterType.value) {
    result = result.filter(item => item.type === filterType.value)
  }

  return result
})

// 方法
const handleImport = () => {
  ElMessage.info('导入3D文件功能开发中...')
}

const handleRefresh = () => {
  ElMessage.success('数据已刷新')
}

const handleExport = () => {
  ElMessage.success('导出功能开发中...')
}

const handleView3D = (item) => {
  ElMessage.success(`正在查看3D视图: ${item.title}`)
}

const toggleExpand = (item) => {
  item.expanded = !item.expanded
}

const handleAddComment = (item) => {
  currentItem.value = item
  commentForm.content = ''
  showCommentDialog.value = true
}

const confirmAddComment = () => {
  if (!commentForm.content.trim()) {
    ElMessage.warning('请输入注释内容')
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

  if (currentItem.value) {
    currentItem.value.comments = currentItem.value.comments || []
    currentItem.value.comments.unshift({
      author: '当前用户',
      time: now,
      content: commentForm.content
    })
    ElMessage.success('注释添加成功')
    showCommentDialog.value = false
  }
}

const getTypeTagType = (type) => {
  const types = {
    model: 'primary',
    scene: 'success',
    material: 'warning'
  }
  return types[type] || 'info'
}

const getTypeText = (type) => {
  const texts = {
    model: '模型',
    scene: '场景',
    material: '材质'
  }
  return texts[type] || '未知'
}
</script>

<style scoped>
.3d-list-container {
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
.toolbar-center,
.toolbar-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* 列表容器 */
.list-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.list-item {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s;
  border: 1px solid #e0e0e0;
}

.list-item.expanded {
  border-color: #409eff;
}

.item-header {
  display: flex;
  align-items: center;
  padding: 16px;
  cursor: pointer;
  gap: 12px;
}

.item-header:hover {
  background: #f5f5f5;
}

.item-icon {
  font-size: 24px;
  color: #409eff;
}

.item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.item-title {
  font-size: 15px;
  font-weight: 500;
  color: #333;
}

.item-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.meta-text {
  font-size: 12px;
  color: #999;
}

.item-actions {
  display: flex;
  gap: 4px;
}

.item-content {
  padding: 16px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.content-section {
  background: #f9f9f9;
  border-radius: 6px;
  padding: 12px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #333;
}

.section-title .el-icon {
  color: #409eff;
}

.content-text {
  font-size: 14px;
  line-height: 1.6;
  color: #666;
  word-break: break-word;
}

.comment-section {
  background: #f0f9ff;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.comment-item {
  background: white;
  border-radius: 4px;
  padding: 10px;
  border-left: 3px solid #409eff;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 12px;
}

.comment-author {
  font-weight: 500;
  color: #333;
}

.comment-time {
  color: #999;
}

.comment-text {
  font-size: 13px;
  color: #666;
  line-height: 1.5;
}

.no-comment {
  text-align: center;
  color: #999;
  font-size: 13px;
  padding: 12px 0;
}

.tags-container {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
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
}

.empty-state p {
  font-size: 14px;
  margin: 0;
}
</style>
