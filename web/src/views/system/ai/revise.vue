<template>
  <div class="document-revise-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <el-icon class="title-icon"><EditPen /></el-icon>
          文档修订管理
        </h1>
        <p class="page-subtitle">管理和追踪文档的修改历史、版本对比与审批流程</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" icon="Plus" @click="createRevision">
          新建修订
        </el-button>
        <el-button type="success" icon="DocumentCopy" @click="compareVersions">
          版本对比
        </el-button>
        <el-button type="warning" icon="Download" @click="exportRevisions">
          导出记录
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ revisionStats.totalDocuments }}</div>
              <div class="stat-label">修订文档</div>
            </div>
            <div class="stat-icon documents-icon">
              <el-icon><Document /></el-icon>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ revisionStats.totalRevisions }}</div>
              <div class="stat-label">修订次数</div>
            </div>
            <div class="stat-icon revisions-icon">
              <el-icon><EditPen /></el-icon>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ revisionStats.pendingApproval }}</div>
              <div class="stat-label">待审批</div>
            </div>
            <div class="stat-icon pending-icon">
              <el-icon><Clock /></el-icon>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ revisionStats.approved }}</div>
              <div class="stat-label">已通过</div>
            </div>
            <div class="stat-icon approved-icon">
              <el-icon><CircleCheck /></el-icon>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <el-row :gutter="20">
        <!-- 文档列表 -->
        <el-col :span="8">
          <el-card class="document-list-card">
            <template #header>
              <div class="card-header">
                <span>文档列表</span>
                <div class="header-controls">
                  <el-input
                    v-model="searchKeyword"
                    placeholder="搜索文档..."
                    prefix-icon="Search"
                    clearable
                    style="width: 150px; margin-right: 10px"
                  />
                  <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 120px">
                    <el-option label="待审批" value="pending" />
                    <el-option label="已通过" value="approved" />
                    <el-option label="已驳回" value="rejected" />
                  </el-select>
                </div>
              </div>
            </template>
            
            <div class="document-list">
              <div
                v-for="doc in filteredDocuments"
                :key="doc.id"
                :class="['document-item', { active: selectedDoc?.id === doc.id }]"
                @click="selectDocument(doc)"
              >
                <div class="doc-info">
                  <div class="doc-title">{{ doc.title }}</div>
                  <div class="doc-meta">
                    <span class="author">作者: {{ doc.author }}</span>
                    <span class="date">更新: {{ formatDate(doc.lastModified) }}</span>
                  </div>
                  <div class="doc-status">
                    <el-tag :type="getStatusType(doc.status)" size="small">
                      {{ getStatusText(doc.status) }}
                    </el-tag>
                    <span class="revision-count">修订: {{ doc.revisionCount }}次</span>
                  </div>
                </div>
                <div class="doc-actions">
                  <el-button icon="View" size="small" @click.stop="viewDocument(doc)" />
                  <el-button icon="Edit" size="small" @click.stop="editDocument(doc)" />
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 修订详情区域 -->
        <el-col :span="16">
          <el-card class="revision-detail-card">
            <template #header>
              <div class="card-header">
                <div class="detail-title">
                  <span v-if="selectedDoc">{{ selectedDoc.title }}</span>
                  <span v-else>请选择一个文档</span>
                </div>
                <div class="detail-controls" v-if="selectedDoc">
                  <el-button-group>
                    <el-button icon="Plus" @click="createNewRevision(selectedDoc)">
                      新建修订
                    </el-button>
                    <el-button icon="Compare" @click="compareWithLatest(selectedDoc)">
                      对比最新
                    </el-button>
                  </el-button-group>
                  <el-button type="primary" icon="Check" @click="approveRevision" :disabled="!canApprove">
                    通过审批
                  </el-button>
                </div>
              </div>
            </template>

            <!-- 修订历史 -->
            <div class="revision-history" v-if="selectedDoc">
              <h3>修订历史</h3>
              <el-timeline>
                <el-timeline-item
                  v-for="revision in selectedDoc.revisions"
                  :key="revision.id"
                  :timestamp="formatDateTime(revision.createdAt)"
                  :type="getRevisionType(revision.status)"
                  placement="top"
                >
                  <el-card class="revision-card">
                    <div class="revision-header">
                      <div class="revision-title">
                        <span class="version">v{{ revision.version }}</span>
                        <el-tag :type="getStatusType(revision.status)" size="small">
                          {{ getStatusText(revision.status) }}
                        </el-tag>
                      </div>
                      <div class="revision-author">
                        修订人: {{ revision.author }}
                      </div>
                    </div>
                    
                    <div class="revision-summary">
                      <h4>修订摘要</h4>
                      <p>{{ revision.summary }}</p>
                    </div>

                    <div class="revision-changes">
                      <h4>主要变更</h4>
                      <ul>
                        <li v-for="change in revision.changes" :key="change.id">
                          <el-tag size="small" :type="getChangeTypeColor(change.type)">
                            {{ getChangeTypeText(change.type) }}
                          </el-tag>
                          {{ change.description }}
                        </li>
                      </ul>
                    </div>

                    <div class="revision-comments" v-if="revision.comments.length > 0">
                      <h4>审批意见</h4>
                      <div class="comments-list">
                        <div v-for="comment in revision.comments" :key="comment.id" class="comment-item">
                          <div class="comment-author">{{ comment.author }}</div>
                          <div class="comment-content">{{ comment.content }}</div>
                          <div class="comment-time">{{ formatDateTime(comment.time) }}</div>
                        </div>
                      </div>
                    </div>

                    <div class="revision-actions">
                      <el-button size="small" @click="viewRevisionDetail(revision)">
                        查看详情
                      </el-button>
                      <el-button size="small" @click="downloadRevision(revision)">
                        下载版本
                      </el-button>
                      <el-button 
                        size="small" 
                        type="primary" 
                        v-if="revision.status === 'pending'"
                        @click="reviewRevision(revision)"
                      >
                        审批
                      </el-button>
                    </div>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
            </div>

            <!-- 空状态 -->
            <div v-else class="empty-state">
              <el-empty description="请从左侧选择一个文档查看修订历史" />
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 新建修订对话框 -->
    <el-dialog
      title="新建文档修订"
      v-model="showRevisionDialog"
      width="700px"
      @close="resetRevisionForm"
    >
      <el-form :model="revisionForm" :rules="revisionRules" ref="revisionFormRef" label-width="100px">
        <el-form-item label="文档标题" prop="title">
          <el-input v-model="revisionForm.title" placeholder="请输入文档标题" />
        </el-form-item>
        
        <el-form-item label="修订版本" prop="version">
          <el-input v-model="revisionForm.version" placeholder="如：1.2.0" />
        </el-form-item>
        
        <el-form-item label="修订摘要" prop="summary">
          <el-input
            v-model="revisionForm.summary"
            type="textarea"
            :rows="3"
            placeholder="简述本次修订的主要内容"
          />
        </el-form-item>
        
        <el-form-item label="详细变更">
          <div class="changes-input">
            <div v-for="(change, index) in revisionForm.changes" :key="index" class="change-item">
              <el-row :gutter="10">
                <el-col :span="6">
                  <el-select v-model="change.type" placeholder="变更类型">
                    <el-option label="新增" value="add" />
                    <el-option label="修改" value="modify" />
                    <el-option label="删除" value="delete" />
                    <el-option label="优化" value="optimize" />
                  </el-select>
                </el-col>
                <el-col :span="14">
                  <el-input v-model="change.description" placeholder="变更描述" />
                </el-col>
                <el-col :span="4">
                  <el-button icon="Delete" @click="removeChange(index)" type="danger" size="small" />
                </el-col>
              </el-row>
            </div>
            <el-button icon="Plus" @click="addChange" style="width: 100%; margin-top: 10px">
              添加变更项
            </el-button>
          </div>
        </el-form-item>
        
        <el-form-item label="修订内容">
          <el-input
            v-model="revisionForm.content"
            type="textarea"
            :rows="8"
            placeholder="请输入完整的修订后内容"
          />
        </el-form-item>
        
        <el-form-item label="上传附件">
          <el-upload
            :auto-upload="false"
            :on-change="handleFileChange"
            :file-list="revisionForm.attachments"
            multiple
            accept=".pdf,.doc,.docx,.txt"
          >
            <el-button icon="Upload">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">支持 PDF、Word、TXT 格式，单个文件不超过 10MB</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showRevisionDialog = false">取消</el-button>
        <el-button type="primary" @click="submitRevision" :loading="submitting">提交修订</el-button>
      </template>
    </el-dialog>

    <!-- 版本对比对话框 -->
    <el-dialog
      title="版本对比"
      v-model="showCompareDialog"
      width="90%"
      top="5vh"
    >
      <div class="compare-container" v-if="comparisonResult">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="version-selector">
              <h4>选择版本</h4>
              <el-select v-model="leftVersion" placeholder="左侧版本" @change="updateComparison">
                <el-option
                  v-for="rev in selectedDoc?.revisions"
                  :key="rev.id"
                  :label="`v${rev.version} - ${rev.author}`"
                  :value="rev.id"
                />
              </el-select>
              <el-select v-model="rightVersion" placeholder="右侧版本" @change="updateComparison" style="margin-top: 10px">
                <el-option
                  v-for="rev in selectedDoc?.revisions"
                  :key="rev.id"
                  :label="`v${rev.version} - ${rev.author}`"
                  :value="rev.id"
                />
              </el-select>
            </div>
          </el-col>
          <el-col :span="18">
            <div class="compare-result">
              <div class="compare-header">
                <span>对比结果：{{ getVersionTitle(leftVersion) }} vs {{ getVersionTitle(rightVersion) }}</span>
              </div>
              <div class="diff-content">
                <div v-html="comparisonResult.diffHtml" class="diff-html"></div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  EditPen, Document, Clock, CircleCheck, Search, Plus, 
  DocumentCopy, Download, View, Compare, Check 
} from '@element-plus/icons-vue'

// 响应式数据
const revisionFormRef = ref()
const showRevisionDialog = ref(false)
const showCompareDialog = ref(false)
const searchKeyword = ref('')
const statusFilter = ref('')
const selectedDoc = ref<any>(null)
const comparisonResult = ref(null)
const leftVersion = ref('')
const rightVersion = ref('')
const submitting = ref(false)

// 统计数据
const revisionStats = reactive({
  totalDocuments: 45,
  totalRevisions: 128,
  pendingApproval: 8,
  approved: 115
})

// 修订表单
const revisionForm = reactive({
  title: '',
  version: '',
  summary: '',
  content: '',
  changes: [
    { type: 'modify', description: '' }
  ],
  attachments: []
})

// 表单验证规则
const revisionRules = {
  title: [
    { required: true, message: '请输入文档标题', trigger: 'blur' }
  ],
  version: [
    { required: true, message: '请输入版本号', trigger: 'blur' }
  ],
  summary: [
    { required: true, message: '请输入修订摘要', trigger: 'blur' }
  ]
}

// 模拟文档数据
const documentList = ref([
  {
    id: 1,
    title: 'AI技术架构文档',
    author: '张三',
    lastModified: new Date('2024-01-15'),
    status: 'approved',
    revisionCount: 12,
    revisions: [
      {
        id: 1,
        version: '1.2.0',
        author: '张三',
        createdAt: new Date('2024-01-15 14:30'),
        status: 'approved',
        summary: '优化AI模型推理性能，增加GPU加速支持',
        changes: [
          { id: 1, type: 'optimize', description: '优化模型推理速度30%' },
          { id: 2, type: 'add', description: '新增GPU加速支持' },
          { id: 3, type: 'modify', description: '重构推理引擎架构' }
        ],
        comments: [
          { id: 1, author: '李四', content: '性能优化效果显著，同意发布', time: new Date('2024-01-16 09:00') }
        ]
      },
      {
        id: 2,
        version: '1.1.0',
        author: '王五',
        createdAt: new Date('2024-01-10 10:15'),
        status: 'approved',
        summary: '增加多模态AI能力支持',
        changes: [
          { id: 1, type: 'add', description: '新增图像识别模块' },
          { id: 2, type: 'add', description: '新增语音识别模块' }
        ],
        comments: []
      }
    ]
  },
  {
    id: 2,
    title: '系统安全规范',
    author: '李四',
    lastModified: new Date('2024-01-20'),
    status: 'pending',
    revisionCount: 5,
    revisions: [
      {
        id: 3,
        version: '2.0.1',
        author: '李四',
        createdAt: new Date('2024-01-20 16:45'),
        status: 'pending',
        summary: '更新数据安全合规要求',
        changes: [
          { id: 1, type: 'modify', description: '更新GDPR合规条款' },
          { id: 2, type: 'add', description: '新增数据加密标准' }
        ],
        comments: []
      }
    ]
  },
  {
    id: 3,
    title: 'API接口文档',
    author: '赵六',
    lastModified: new Date('2024-01-18'),
    status: 'approved',
    revisionCount: 8,
    revisions: []
  }
])

// 计算属性
const filteredDocuments = computed(() => {
  let filtered = documentList.value
  
  // 关键词搜索
  if (searchKeyword.value) {
    filtered = filtered.filter(doc => 
      doc.title.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      doc.author.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  
  // 状态筛选
  if (statusFilter.value) {
    filtered = filtered.filter(doc => doc.status === statusFilter.value)
  }
  
  return filtered
})

const canApprove = computed(() => {
  return selectedDoc.value?.revisions?.some((rev: any) => rev.status === 'pending')
})

// 方法
const selectDocument = (doc: any) => {
  selectedDoc.value = doc
}

const createRevision = () => {
  selectedDoc.value = null
  showRevisionDialog.value = true
}

const createNewRevision = (doc: any) => {
  selectedDoc.value = doc
  Object.assign(revisionForm, {
    title: doc.title,
    version: '',
    summary: '',
    content: '',
    changes: [{ type: 'modify', description: '' }],
    attachments: []
  })
  showRevisionDialog.value = true
}

const submitRevision = async () => {
  if (!revisionFormRef.value) return
  
  try {
    await revisionFormRef.value.validate()
    submitting.value = true
    
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // 创建新修订记录
    const newRevision = {
      id: Date.now(),
      version: revisionForm.version,
      author: '当前用户',
      createdAt: new Date(),
      status: 'pending',
      summary: revisionForm.summary,
      changes: revisionForm.changes.filter((c: any) => c.description.trim()),
      comments: [],
      content: revisionForm.content,
      attachments: revisionForm.attachments
    }
    
    if (selectedDoc.value) {
      selectedDoc.value.revisions.unshift(newRevision)
      selectedDoc.value.revisionCount++
    } else {
      // 创建新文档
      const newDoc = {
        id: Date.now(),
        title: revisionForm.title,
        author: '当前用户',
        lastModified: new Date(),
        status: 'pending',
        revisionCount: 1,
        revisions: [newRevision]
      }
      documentList.value.unshift(newDoc)
    }
    
    ElMessage.success('修订提交成功，等待审批')
    showRevisionDialog.value = false
    resetRevisionForm()
    
  } catch (error) {
    ElMessage.error('请检查表单填写')
  } finally {
    submitting.value = false
  }
}

const resetRevisionForm = () => {
  Object.assign(revisionForm, {
    title: '',
    version: '',
    summary: '',
    content: '',
    changes: [{ type: 'modify', description: '' }],
    attachments: []
  })
  revisionFormRef.value?.resetFields()
}

const addChange = () => {
  revisionForm.changes.push({ type: 'modify', description: '' })
}

const removeChange = (index: number) => {
  if (revisionForm.changes.length > 1) {
    revisionForm.changes.splice(index, 1)
  }
}

const compareVersions = () => {
  if (!selectedDoc.value) {
    ElMessage.warning('请先选择一个文档')
    return
  }
  showCompareDialog.value = true
  
  // 默认选择最新的两个版本进行对比
  if (selectedDoc.value.revisions.length >= 2) {
    leftVersion.value = selectedDoc.value.revisions[1].id
    rightVersion.value = selectedDoc.value.revisions[0].id
    updateComparison()
  }
}

const compareWithLatest = (doc: any) => {
  selectedDoc.value = doc
  compareVersions()
}

const updateComparison = () => {
  // 模拟对比结果
  comparisonResult.value = {
    diffHtml: `
      <div class="diff-line added">+ 新增GPU加速支持</div>
      <div class="diff-line modified">~ 优化模型推理速度30%</div>
      <div class="diff-line removed">- 移除旧版推理引擎</div>
    `}
  }
}

const getVersionTitle = (versionId: string) => {
  const rev = selectedDoc.value?.revisions.find((r: any) => r.id == versionId)
  return rev ? `v${rev.version}` : ''
}

const reviewRevision = (revision: any) => {
  ElMessageBox.prompt('请输入审批意见：', '审批修订', {
    confirmButtonText: '通过',
    cancelButtonText: '驳回',
    distinguishCancelAndClose: true,
    inputPlaceholder: '请输入审批意见...'
  }).then(({ value }) => {
    revision.status = 'approved'
    revision.comments.push({
      id: Date.now(),
      author: '当前用户',
      content: value || '同意发布',
      time: new Date()
    })
    ElMessage.success('修订已通过')
  }).catch(action => {
    if (action === 'cancel') {
      revision.status = 'rejected'
      ElMessage.warning('修订已驳回')
    }
  })
}

const approveRevision = () => {
  if (!selectedDoc.value) return
  
  const pendingRevision = selectedDoc.value.revisions.find((rev: any) => rev.status === 'pending')
  if (pendingRevision) {
    reviewRevision(pendingRevision)
  }
}

const viewDocument = (doc: any) => {
  ElMessage.info(`查看文档: ${doc.title}`)
}

const editDocument = (doc: any) => {
  ElMessage.info(`编辑文档: ${doc.title}`)
}

const viewRevisionDetail = (revision: any) => {
  ElMessage.info(`查看修订详情: v${revision.version}`)
}

const downloadRevision = (revision: any) => {
  ElMessage.info(`下载版本: v${revision.version}`)
}

const exportRevisions = () => {
  ElMessage.info('导出功能开发中...')
}

const handleFileChange = (file: any) => {
  ElMessage.success(`已添加文件: ${file.name}`)
}

// 工具方法
const formatDate = (date: Date) => {
  return date.toLocaleDateString('zh-CN')
}

const formatDateTime = (date: Date) => {
  return date.toLocaleString('zh-CN')
}

const getStatusType = (status: string) => {
  const types: { [key: string]: string } = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts: { [key: string]: string } = {
    pending: '待审批',
    approved: '已通过',
    rejected: '已驳回'
  }
  return texts[status] || status
}

const getRevisionType = (status: string) => {
  return getStatusType(status)
}

const getChangeTypeColor = (type: string) => {
  const colors: { [key: string]: string } = {
    add: 'success',
    modify: 'warning',
    delete: 'danger',
    optimize: 'primary'
  }
  return colors[type] || ''
}

const getChangeTypeText = (type: string) => {
  const texts: { [key: string]: string } = {
    add: '新增',
    modify: '修改',
    delete: '删除',
    optimize: '优化'
  }
  return texts[type] || type
}

// 生命周期
onMounted(() => {
  // 默认选择第一个文档
  if (documentList.value.length > 0) {
    selectDocument(documentList.value[0])
  }
})
</script>

<style scoped>
.document-revise-page {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header-content {
  flex: 1;
}

.page-title {
  margin: 0;
  font-size: 28px;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-icon {
  font-size: 32px;
  color: #409eff;
}

.page-subtitle {
  margin: 5px 0 0 0;
  color: #909399;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.stats-section {
  margin-bottom: 20px;
}

.stat-card {
  position: relative;
  overflow: hidden;
}

.stat-content {
  position: relative;
  z-index: 2;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
}

.stat-label {
  margin-top: 8px;
  color: #909399;
  font-size: 14px;
}

.stat-icon {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 40px;
  opacity: 0.3;
  z-index: 1;
}

.documents-icon { color: #409eff; }
.revisions-icon { color: #67c23a; }
.pending-icon { color: #e6a23c; }
.approved-icon { color: #f56c6c; }

.main-content {
  height: calc(100vh - 300px);
}

.document-list-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-controls {
  display: flex;
  align-items: center;
}

.document-list {
  max-height: 600px;
  overflow-y: auto;
}

.document-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 15px;
  margin-bottom: 10px;
  background: #f8f9fa;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.document-item:hover {
  background: #e9ecef;
  transform: translateX(5px);
}

.document-item.active {
  background: #409eff;
  color: white;
}

.doc-info {
  flex: 1;
}

.doc-title {
  font-weight: bold;
  margin-bottom: 8px;
  line-height: 1.4;
}

.doc-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
}

.document-item.active .doc-meta {
  color: rgba(255,255,255,0.8);
}

.doc-status {
  display: flex;
  align-items: center;
  gap: 10px;
}

.revision-count {
  font-size: 12px;
  color: #999;
}

.document-item.active .revision-count {
  color: rgba(255,255,255,0.7);
}

.doc-actions {
  display: flex;
  gap: 5px;
}

.revision-detail-card {
  height: 100%;
}

.detail-title {
  font-size: 18px;
  font-weight: bold;
}

.detail-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.revision-history h3 {
  margin: 0 0 20px 0;
  color: #303133;
}

.revision-card {
  margin-bottom: 20px;
}

.revision-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.revision-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.version {
  font-weight: bold;
  font-size: 16px;
}

.revision-author {
  font-size: 14px;
  color: #666;
}

.revision-summary h4,
.revision-changes h4,
.revision-comments h4 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 14px;
}

.revision-summary p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.revision-changes ul {
  margin: 0;
  padding-left: 20px;
}

.revision-changes li {
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.comments-list {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
}

.comment-item {
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.comment-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.comment-author {
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.comment-content {
  color: #606266;
  margin-bottom: 5px;
}

.comment-time {
  font-size: 12px;
  color: #909399;
}

.revision-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.changes-input {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 15px;
}

.change-item {
  margin-bottom: 10px;
}

.compare-container {
  max-height: 70vh;
}

.version-selector {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 6px;
  height: fit-content;
}

.version-selector h4 {
  margin: 0 0 15px 0;
  color: #303133;
}

.compare-result {
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  overflow: hidden;
}

.compare-header {
  background: #f8f9fa;
  padding: 15px;
  border-bottom: 1px solid #dcdfe6;
  font-weight: bold;
}

.diff-content {
  padding: 20px;
  max-height: 500px;
  overflow-y: auto;
}

.diff-html {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
}

.diff-line.added {
  color: #67c23a;
  background: #f0f9ff;
  padding: 2px 4px;
}

.diff-line.modified {
  color: #e6a23c;
  background: #fffbf0;
  padding: 2px 4px;
}

.diff-line.removed {
  color: #f56c6c;
  background: #fef0f0;
  padding: 2px 4px;
  text-decoration: line-through;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 20px;
  }
  
  .main-content .el-col {
    margin-bottom: 20px;
  }
  
  .revision-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>