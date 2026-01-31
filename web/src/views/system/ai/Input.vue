<template>
  <div class="document-input">
    <el-card class="input-card">
      <template #header>
        <div class="card-header">
          <h2>文档输入</h2>
          <div class="header-actions">
            <el-button type="primary" icon="View" @click="previewDialogVisible = true">预览</el-button>
            <el-button type="success" icon="Check" @click="handleSubmit" :loading="submitting">保存文档</el-button>
          </div>
        </div>
      </template>

      <el-form ref="formRef" :model="documentForm" :rules="formRules" label-width="100px">
        <!-- 基本信息 -->
        <el-divider content-position="left">基本信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="文档标题" prop="title">
              <el-input v-model="documentForm.title" placeholder="请输入文档标题" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="文档类型" prop="docType">
              <el-select v-model="documentForm.docType" placeholder="选择文档类型" style="width: 100%">
                <el-option label="技术文档" value="tech" />
                <el-option label="产品文档" value="product" />
                <el-option label="操作手册" value="manual" />
                <el-option label="培训资料" value="training" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="文档分类" prop="category">
              <el-select v-model="documentForm.category" placeholder="选择分类" style="width: 100%">
                <el-option label="AI技术" value="ai-tech" />
                <el-option label="后端开发" value="backend" />
                <el-option label="前端开发" value="frontend" />
                <el-option label="数据分析" value="data-analysis" />
                <el-option label="业务流程" value="business" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="优先级" prop="priority">
              <el-radio-group v-model="documentForm.priority">
                <el-radio label="low">低</el-radio>
                <el-radio label="medium">中</el-radio>
                <el-radio label="high">高</el-radio>
                <el-radio label="urgent">紧急</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="文档摘要" prop="summary">
          <el-input
            v-model="documentForm.summary"
            type="textarea"
            :rows="3"
            placeholder="请输入文档摘要，简要描述文档内容"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="标签">
          <el-tag
            v-for="tag in documentForm.tags"
            :key="tag"
            closable
            :disable-transitions="false"
            @close="handleClose(tag)"
            style="margin-right: 10px"
          >
            {{ tag }}
          </el-tag>
          <el-input
            v-if="inputVisible"
            ref="InputRef"
            v-model="inputValue"
            class="ml-1 w-20"
            size="small"
            style="width: 120px"
            @keyup.enter="handleInputConfirm"
            @blur="handleInputConfirm"
          />
          <el-button v-else class="button-new-tag ml-1" size="small" @click="showInput">
            + 新标签
          </el-button>
        </el-form-item>

        <!-- 文件上传 -->
        <el-divider content-position="left">文件上传</el-divider>
        <el-form-item label="文档文件">
          <el-upload
            ref="uploadRef"
            class="upload-demo"
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :limit="5"
            :file-list="fileList"
            multiple
            accept=".pdf,.doc,.docx,.txt,.md,.xls,.xlsx,.ppt,.pptx"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 PDF、Word、Excel、PPT、TXT、Markdown 格式，单个文件不超过 10MB
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <!-- 文档内容编辑 -->
        <el-divider content-position="left">文档内容</el-divider>
        <el-form-item label="内容" prop="content">
          <div class="editor-container">
            <!-- 工具栏 -->
            <div class="editor-toolbar">
              <el-button-group>
                <el-button icon="Bold" @click="formatText('bold')" size="small">加粗</el-button>
                <el-button icon="Italic" @click="formatText('italic')" size="small">斜体</el-button>
                <el-button icon="Underline" @click="formatText('underline')" size="small">下划线</el-button>
              </el-button-group>
              
              <el-button-group style="margin-left: 10px">
                <el-button icon="List" @click="formatText('insertUnorderedList')" size="small">无序列表</el-button>
                <el-button icon="Rank" @click="formatText('insertOrderedList')" size="small">有序列表</el-button>
              </el-button-group>
              
              <el-button-group style="margin-left: 10px">
                <el-button icon="Picture" @click="insertImage" size="small">图片</el-button>
                <el-button icon="Link" @click="insertLink" size="small">链接</el-button>
                <el-button icon="VideoPlay" @click="insertVideo" size="small">视频</el-button>
              </el-button-group>
            </div>

            <!-- 编辑区域 -->
            <el-input
              v-model="documentForm.content"
              type="textarea"
              :rows="15"
              placeholder="请输入文档内容，支持 Markdown 格式"
              class="content-editor"
            />
          </div>
        </el-form-item>

        <!-- 附件上传 -->
        <el-divider content-position="left">附件</el-divider>
        <el-form-item label="附件">
          <el-upload
            :auto-upload="false"
            :on-change="handleAttachmentChange"
            :on-remove="handleAttachmentRemove"
            :limit="10"
            :file-list="attachmentList"
            multiple
            action="#"
          >
            <el-button icon="Upload" type="primary">上传附件</el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持任意格式附件，单个附件不超过 20MB，最多上传 10 个
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <!-- 其他设置 -->
        <el-divider content-position="left">其他设置</el-divider>
        <el-form-item label="可见范围">
          <el-radio-group v-model="documentForm.visibility">
            <el-radio label="public">公开</el-radio>
            <el-radio label="internal">内部可见</el-radio>
            <el-radio label="private">仅自己可见</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="允许评论">
          <el-switch v-model="documentForm.allowComments" />
        </el-form-item>

        <el-form-item label="允许下载">
          <el-switch v-model="documentForm.allowDownload" />
        </el-form-item>

        <el-form-item label="发布时间">
          <el-date-picker
            v-model="documentForm.publishTime"
            type="datetime"
            placeholder="选择发布时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            :disabled-date="disabledDate"
          />
        </el-form-item>
      </el-form>

      <!-- 操作按钮 -->
      <div class="form-actions">
        <el-button @click="handleReset">重置</el-button>
        <el-button type="info" @click="saveDraft">保存草稿</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">提交文档</el-button>
      </div>
    </el-card>

    <!-- 预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      title="文档预览"
      width="70%"
      center
    >
      <div class="preview-content">
        <h2>{{ documentForm.title }}</h2>
        <div class="preview-meta">
          <el-tag :type="getTagType(documentForm.docType)">{{ getTypeLabel(documentForm.docType) }}</el-tag>
          <span class="meta-item">分类：{{ getCategoryLabel(documentForm.category) }}</span>
          <span class="meta-item">优先级：{{ documentForm.priority }}</span>
        </div>
        <div class="preview-summary">{{ documentForm.summary }}</div>
        <div class="preview-tags">
          <el-tag
            v-for="tag in documentForm.tags"
            :key="tag"
            type="info"
            size="small"
            style="margin-right: 8px"
          >
            {{ tag }}
          </el-tag>
        </div>
        <div class="preview-content-text" v-html="formatContent(documentForm.content)"></div>
        <div class="preview-files" v-if="fileList.length > 0">
          <h4>文件列表</h4>
          <el-tag
            v-for="file in fileList"
            :key="file.name"
            type="success"
            style="margin: 5px"
          >
            <el-icon><Document /></el-icon>
            {{ file.name }}
          </el-tag>
        </div>
      </div>
      <template #footer>
        <el-button @click="previewDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleSubmit">确认提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled, Document } from '@element-plus/icons-vue'
import type { FormInstance, FormRules, UploadUserFile } from 'element-plus'

// 表单引用
const formRef = ref<FormInstance>()
const uploadRef = ref()
const InputRef = ref()

// 表单数据
const documentForm = reactive({
  title: '',
  docType: '',
  category: '',
  summary: '',
  content: '',
  tags: ['技术文档'],
  priority: 'medium',
  visibility: 'internal',
  allowComments: true,
  allowDownload: true,
  publishTime: ''
})

// 文件列表
const fileList = ref<UploadUserFile[]>([])
const attachmentList = ref<UploadUserFile[]>([])

// 标签输入
const inputVisible = ref(false)
const inputValue = ref('')

// 状态
const submitting = ref(false)
const previewDialogVisible = ref(false)

// 表单验证规则
const formRules: FormRules = {
  title: [
    { required: true, message: '请输入文档标题', trigger: 'blur' },
    { min: 2, max: 100, message: '标题长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  docType: [
    { required: true, message: '请选择文档类型', trigger: 'change' }
  ],
  category: [
    { required: true, message: '请选择文档分类', trigger: 'change' }
  ],
  summary: [
    { required: true, message: '请输入文档摘要', trigger: 'blur' },
    { min: 10, max: 500, message: '摘要长度在 10 到 500 个字符', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入文档内容', trigger: 'blur' },
    { min: 50, message: '内容至少 50 个字符', trigger: 'blur' }
  ]
}

// 关闭标签
const handleClose = (tag: string) => {
  documentForm.tags.splice(documentForm.tags.indexOf(tag), 1)
}

// 显示标签输入框
const showInput = () => {
  inputVisible.value = true
  nextTick(() => {
    InputRef.value!.focus()
  })
}

// 确认添加标签
const handleInputConfirm = () => {
  if (inputValue.value) {
    documentForm.tags.push(inputValue.value)
  }
  inputVisible.value = false
  inputValue.value = ''
}

// 文件变更
const handleFileChange = (file: UploadUserFile) => {
  // 文件大小验证
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB')
    return false
  }
  ElMessage.success(`已添加文件：${file.name}`)
}

// 移除文件
const handleFileRemove = (file: UploadUserFile) => {
  ElMessage.info(`已移除文件：${file.name}`)
}

// 附件变更
const handleAttachmentChange = (file: UploadUserFile) => {
  const isLt20M = file.size / 1024 / 1024 < 20
  if (!isLt20M) {
    ElMessage.error('附件大小不能超过 20MB')
    return false
  }
}

// 移除附件
const handleAttachmentRemove = (file: UploadUserFile) => {
  ElMessage.info(`已移除附件：${file.name}`)
}

// 格式化文本
const formatText = (command: string) => {
  ElMessage.info(`应用格式：${command}`)
  // 这里可以集成富文本编辑器
}

// 插入图片
const insertImage = () => {
  ElMessage.info('插入图片功能')
}

// 插入链接
const insertLink = () => {
  ElMessage.info('插入链接功能')
}

// 插入视频
const insertVideo = () => {
  ElMessage.info('插入视频功能')
}

// 格式化内容预览
const formatContent = (content: string) => {
  return content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>')
    .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
}

// 获取标签类型
const getTagType = (type: string) => {
  const types: { [key: string]: any } = {
    tech: 'primary',
    product: 'success',
    manual: 'warning',
    training: 'info',
    other: ''
  }
  return types[type] || ''
}

// 获取类型标签
const getTypeLabel = (type: string) => {
  const labels: { [key: string]: string } = {
    tech: '技术文档',
    product: '产品文档',
    manual: '操作手册',
    training: '培训资料',
    other: '其他'
  }
  return labels[type] || type
}

// 获取分类标签
const getCategoryLabel = (category: string) => {
  const labels: { [key: string]: string } = {
    'ai-tech': 'AI技术',
    backend: '后端开发',
    frontend: '前端开发',
    'data-analysis': '数据分析',
    business: '业务流程'
  }
  return labels[category] || category
}

// 禁用日期
const disabledDate = (time: Date) => {
  return time.getTime() < Date.now() - 8.64e7
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    // 模拟提交
    setTimeout(() => {
      ElMessage.success('文档提交成功！')
      submitting.value = false
      previewDialogVisible.value = false
      
      // 可以在这里添加提交到后端的逻辑
      console.log('提交的数据:', {
        ...documentForm,
        files: fileList.value.map(f => f.name),
        attachments: attachmentList.value.map(f => f.name)
      })
    }, 1500)
  } catch (error) {
    ElMessage.error('请检查表单填写是否正确')
  }
}

// 保存草稿
const saveDraft = () => {
  ElMessage.success('草稿已保存')
}

// 重置表单
const handleReset = () => {
  formRef.value?.resetFields()
  documentForm.tags = ['技术文档']
  fileList.value = []
  attachmentList.value = []
  ElMessage.info('表单已重置')
}
</script>

<style scoped>
.document-input {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.input-card {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  color: #303133;
  font-size: 20px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.editor-container {
  width: 100%;
}

.editor-toolbar {
  display: flex;
  gap: 10px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 10px;
}

.content-editor {
  font-family: 'Courier New', Courier, monospace;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.preview-content {
  padding: 20px;
  background: #fff;
  border-radius: 4px;
}

.preview-content h2 {
  margin: 0 0 20px 0;
  color: #303133;
  text-align: center;
}

.preview-meta {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 20px;
  color: #606266;
}

.meta-item {
  margin-left: 20px;
}

.preview-summary {
  padding: 15px;
  background: #f5f7fa;
  border-left: 4px solid #409eff;
  margin-bottom: 20px;
  color: #606266;
  line-height: 1.6;
}

.preview-tags {
  margin-bottom: 20px;
}

.preview-content-text {
  line-height: 1.8;
  color: #303133;
  margin-bottom: 20px;
}

.preview-files h4 {
  margin: 20px 0 10px 0;
  color: #303133;
}

.el-divider {
  margin: 24px 0;
}
</style>
