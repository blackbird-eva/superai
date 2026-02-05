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

          <!-- 文本输入工具栏 -->
          <div class="input-toolbar">
            <input
              ref="textFileInputRef"
              type="file"
              accept=".txt,.md"
              style="display: none"
              @change="handleTextFileUpload"
            >
            <el-button
              text
              icon="Upload"
              @click="textFileInputRef?.click()"
              title="上传文本文件"
            >
              上传文本
            </el-button>ddddd
            <el-divider direction="vertical"></el-divider>
          </div>

          <el-input
            v-model="inputText"
            type="textarea"
            :rows="12"
            placeholder="请输入或粘贴需要翻译的文本...，也可点击上方上传文本按钮导入文本文件"
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
        <!-- 文档信息配置 -->
        <div v-if="fileList.length === 0" class="document-config">
          <div class="config-section">
            <h4>文档设置</h4>
            <div class="config-form">
              <el-form :model="docConfig" label-width="100px">
                <el-form-item label="文档类型:">
                  <el-select v-model="docConfig.type" placeholder="选择文档类型" style="width: 200px;">
                    <el-option label="Word文档 (.docx)" value="docx"></el-option>
                    <el-option label="PowerPoint (.ppt/.pptx)" value="ppt"></el-option>
                    <el-option label="PDF文档 (.pdf)" value="pdf"></el-option>
                    <el-option label="纯文本 (.txt)" value="txt"></el-option>
                    <el-option label="其他格式" value="other"></el-option>
                  </el-select>
                </el-form-item>
                
                <el-form-item label="文档简介:">
                  <el-input
                    v-model="docConfig.about_text"
                    type="textarea"
                    :rows="3"
                    placeholder="请输入文档内容简要描述（可选）"
                    style="width: 100%;"
                  ></el-input>
                </el-form-item>
                
                <el-form-item label="功能设置:">
                  <div class="feature-toggles">
                    <el-checkbox v-model="docConfig.transtask">需要翻译</el-checkbox>
                    <el-checkbox v-model="docConfig.graphtask">生成知识图谱</el-checkbox>
                    <el-checkbox v-model="docConfig.share">允许分享</el-checkbox>
                    <el-checkbox v-model="docConfig.userversion">启用版本控制</el-checkbox>
                  </div>
                </el-form-item>
              </el-form>
            </div>
          </div>
        </div>
        
        <div class="upload-area">
            <el-upload
              class="document-uploader"
              :show-file-list="true"
              :before-upload="beforeDocUpload"
              :on-remove="handleDocRemove"
              :on-change="handleDocChange"
              :file-list="fileList"
              :drag="true"
              accept=".docx,.ppt,.pptx,.pdf,.txt"
              :limit="1"
              :auto-upload="false"
              :disabled="uploadingDoc"
            >
            <div v-if="fileList.length === 0" class="upload-placeholder">
              <el-icon v-if="!uploadingDoc" class="upload-icon"><Document /></el-icon>
              <el-icon v-else class="upload-icon is-loading" :size="48">
                <Loading />
              </el-icon>
              <div v-if="!uploadingDoc" class="upload-text">拖拽文档到此处或点击上传</div>
              <div v-else class="upload-text">正在上传文档...</div>
              <div class="upload-hint">支持 DOCX、PPT、PDF、TXT 格式，大小不超过 50MB</div>
              <div v-if="docConfig.type || docConfig.about_text" class="config-summary">
                <el-tag v-if="docConfig.type" type="info" size="small">类型: {{ docConfig.type.toUpperCase() }}</el-tag>
                <el-tag v-if="docConfig.transtask" type="success" size="small">翻译</el-tag>
                <el-tag v-if="docConfig.graphtask" type="warning" size="small">知识图谱</el-tag>
                <el-tag v-if="docConfig.share" type="primary" size="small">分享</el-tag>
                <el-tag v-if="docConfig.userversion" type="info" size="small">版本控制</el-tag>
              </div>


            </div>
            <div v-else class="file-info">
              <div class="file-details">
                <el-icon class="file-icon"><Document /></el-icon>
                <div class="file-meta">
                  <div class="file-name">{{ fileList[0]?.name }}</div>
                  <div class="file-size">{{ formatFileSize(fileList[0]?.size) }}</div>
                  <div class="file-config">
                    <el-tag v-if="docConfig.type" size="small" type="info">{{ docConfig.type.toUpperCase() }}</el-tag>
                    <el-tag v-if="docConfig.transtask" size="small" type="success">翻译</el-tag>
                    <el-tag v-if="docConfig.graphtask" size="small" type="warning">知识图谱</el-tag>
                    <el-tag v-if="docConfig.share" size="small" type="primary">分享</el-tag>
                  </div>
                </div>
              </div>
              <el-button type="primary" icon="Upload" @click.stop="clearFile">
                更换文件
              </el-button>
            </div>
          </el-upload>

          <div v-if="fileList.length > 0" class="doc-actions">
            <el-button type="primary" @click="translateDocument" :loading="translating">
              {{ docConfig.transtask ? '开始翻译' : '处理文档' }}
            </el-button>
            <el-button @click="clearFile">
              清除
            </el-button>
          </div>
        </div>

        <!-- 文档选择和配置 -->
        <div v-if="fileList.length > 0" class="document-selection">
          <div class="selection-header">
            <h4>文档内容管理</h4>
            <el-button type="primary" size="small" @click="showContentEditor = !showContentEditor">
              {{ showContentEditor ? '收起编辑器' : '展开编辑器' }}
            </el-button>
          </div>
          
          <div v-if="showContentEditor" class="content-editor">
            <el-form :model="docContent" label-width="120px" class="content-form">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="文档简介:">
                    <el-input
                      v-model="docContent.about"
                      type="textarea"
                      :rows="2"
                      placeholder="文档内容简要描述"
                    ></el-input>
                  </el-form-item>
                </el-col>
                <el-col :span="6">
                  <el-form-item label="排序:">
                    <el-input-number v-model="docContent.order" :min="0" style="width: 100%"></el-input-number>
                  </el-form-item>
                </el-col>
                <el-col :span="6">
                  <el-form-item label="版本号:">
                    <el-input-number v-model="docContent.version" :min="1" style="width: 100%"></el-input-number>
                  </el-form-item>
                </el-col>
              </el-row>
              
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="标题:">
                    <el-input v-model="docContent.title" placeholder="文档标题"></el-input>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="副标题:">
                    <el-input v-model="docContent.subtitle" placeholder="文档副标题"></el-input>
                  </el-form-item>
                </el-col>
              </el-row>
              
              <el-row :gutter="20">
                <el-col :span="8">
                  <el-form-item label="标题级别:">
                    <el-select v-model="docContent.subweight" placeholder="选择级别" style="width: 100%">
                      <el-option label="正文 (0)" :value="0"></el-option>
                      <el-option label="一级标题 (1)" :value="1"></el-option>
                      <el-option label="二级标题 (2)" :value="2"></el-option>
                      <el-option label="三级标题 (3)" :value="3"></el-option>
                      <el-option label="四级标题 (4)" :value="4"></el-option>
                      <el-option label="五级标题 (5)" :value="5"></el-option>
                      <el-option label="六级标题 (6)" :value="6"></el-option>
                      <el-option label="七级标题 (7)" :value="7"></el-option>
                      <el-option label="八级标题 (8)" :value="8"></el-option>
                      <el-option label="九级标题 (9)" :value="9"></el-option>
                      <el-option label="十级标题 (10)" :value="10"></el-option>
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="翻译校对1:">
                    <el-checkbox v-model="docContent.transcheck1"></el-checkbox>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="翻译校对2:">
                    <el-checkbox v-model="docContent.transcheck2"></el-checkbox>
                  </el-form-item>
                </el-col>
              </el-row>
              
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="翻译负责人:">
                    <el-input v-model="docContent.transmanger" placeholder="翻译负责人姓名"></el-input>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="文档负责人:">
                    <el-input v-model="docContent.docmanger" placeholder="文档负责人姓名"></el-input>
                  </el-form-item>
                </el-col>
              </el-row>
              
              <el-form-item label="内容:">
                <el-input
                  v-model="docContent.content"
                  type="textarea"
                  :rows="8"
                  placeholder="请输入文档内容..."
                  style="width: 100%"
                ></el-input>
              </el-form-item>
              
              <el-form-item label="翻译内容:">
                <el-input
                  v-model="docContent.transcontent"
                  type="textarea"
                  :rows="8"
                  placeholder="请输入翻译内容..."
                  style="width: 100%"
                ></el-input>
              </el-form-item>
              
              <el-form-item label="翻译备注:">
                <el-input
                  v-model="docContent.transnote"
                  type="textarea"
                  :rows="3"
                  placeholder="翻译过程中的备注信息"
                  style="width: 100%"
                ></el-input>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="saveDocContent">保存内容</el-button>
                <el-button @click="resetDocContent">重置</el-button>
                <el-checkbox v-model="docContent.translast" style="margin-left: 20px;">
                  翻译最后确认
                </el-checkbox>
              </el-form-item>
            </el-form>
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
                预览说明
              </el-button>
            </div>
          </div>
          <div class="result-content">
            <div v-if="docResult && docTranslatedData" class="result-preview">
              <el-alert
                title="翻译完成"
                type="success"
                :description="`文档 ${fileList[0]?.name} 已成功翻译为 ${languageMap[targetLang]}，共 ${docTranslatedData.paragraph_count} 段`"
                :closable="false"
              />
              
              <!-- 文档内容预览 -->
              <div v-if="docContent.content || docContent.transcontent" class="document-content-preview">
                <h4>文档内容预览</h4>
                <div class="content-sections">
                  <div v-if="docContent.title" class="content-section">
                    <div class="section-label">标题:</div>
                    <div class="section-content title-content" :class="getTitleClass(docContent.subweight)">
                      {{ docContent.title }}
                      <el-tag v-if="docContent.subweight > 0" size="small" type="info">H{{ docContent.subweight }}</el-tag>
                    </div>
                  </div>
                  
                  <div v-if="docContent.subtitle" class="content-section">
                    <div class="section-label">副标题:</div>
                    <div class="section-content subtitle-content">{{ docContent.subtitle }}</div>
                  </div>
                  
                  <div v-if="docContent.about" class="content-section">
                    <div class="section-label">文档简介:</div>
                    <div class="section-content about-content">{{ docContent.about }}</div>
                  </div>
                  
                  <div v-if="docContent.content" class="content-section">
                    <div class="section-label">原文内容:</div>
                    <div class="section-content original-content">{{ docContent.content }}</div>
                  </div>
                  
                  <div v-if="docContent.transcontent" class="content-section">
                    <div class="section-label">翻译内容:</div>
                    <div class="section-content translated-content">{{ docContent.transcontent }}</div>
                  </div>
                  
                  <div v-if="docContent.transnote" class="content-section">
                    <div class="section-label">翻译备注:</div>
                    <div class="section-content note-content">{{ docContent.transnote }}</div>
                  </div>
                </div>
                
                <!-- 状态信息 -->
                <div class="content-status">
                  <el-descriptions :column="3" size="small">
                    <el-descriptions-item label="排序">{{ docContent.order }}</el-descriptions-item>
                    <el-descriptions-item label="版本">{{ docContent.version }}</el-descriptions-item>
                    <el-descriptions-item label="最后确认">
                      <el-tag :type="docContent.translast ? 'success' : 'info'" size="small">
                        {{ docContent.translast ? '已确认' : '待确认' }}
                      </el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="校对1">
                      <el-tag :type="docContent.transcheck1 ? 'success' : 'warning'" size="small">
                        {{ docContent.transcheck1 ? '已完成' : '待完成' }}
                      </el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="校对2">
                      <el-tag :type="docContent.transcheck2 ? 'success' : 'warning'" size="small">
                        {{ docContent.transcheck2 ? '已完成' : '待完成' }}
                      </el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="编辑时间">
                      {{ formatEditTime(docContent.contentedittime) }}
                    </el-descriptions-item>
                    <el-descriptions-item label="翻译负责人" v-if="docContent.transmanger">
                      {{ docContent.transmanger }}
                    </el-descriptions-item>
                    <el-descriptions-item label="文档负责人" v-if="docContent.docmanger">
                      {{ docContent.docmanger }}
                    </el-descriptions-item>
                  </el-descriptions>
                </div>
              </div>
              
              <div v-if="docTranslatedData.preview && docTranslatedData.preview.length > 0" class="preview-section">
                <h4>预览前 5 段翻译结果：</h4>
                <div v-for="(item, index) in docTranslatedData.preview" :key="index" class="preview-item">
                  <div class="preview-original">原文: {{ item.original }}</div>
                  <div class="preview-translated">译文: {{ item.translated }}</div>
                </div>
              </div>
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
  Upload, View, Loading
} from '@element-plus/icons-vue'
import { Translate, TranslateDocument, FileUpload } from './api'

// 翻译模式
const activeMode = ref('text')

// 语言设置
const sourceLang = ref('auto')
const targetLang = ref('en')

// 输入输出
const inputText = ref('')
const outputText = ref('')

// 文本文件输入引用
const textFileInputRef = ref<HTMLInputElement | null>(null)

// 翻译状态
const translating = ref(false)

// 文档上传状态
const uploadingDoc = ref(false)

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
const docTranslatedData = ref<any>(null)

// 文档配置
const docConfig = ref({
  type: 'docx',
  about_text: '',
  transtask: true,
  graphtask: false,
  share: false,
  userversion: true
})

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
  const validTypes = ['.docx', '.ppt', '.pptx', '.pdf', '.txt']
  const isValidType = validTypes.some(type => file.name.toLowerCase().endsWith(type))
  const isLt50M = file.size / 1024 / 1024 < 50

  if (!isValidType) {
    ElMessage.error('不支持的文件格式! 支持: DOCX, PPT, PDF, TXT')
    return false
  }
  if (!isLt50M) {
    ElMessage.error('文件大小不能超过 50MB!')
    return false
  }

  return true
}

// 文本文件上传处理
const handleTextFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (!file) {
    return
  }

  // 验证文件类型
  const validTypes = ['text/plain', 'text/markdown', 'text/html']
  const fileExt = file.name.split('.').pop()?.toLowerCase()
  const validExts = ['txt', 'md', 'html']

  if (!validExts.includes(fileExt || '')) {
    ElMessage.error('不支持的文本文件格式，仅支持: TXT, MD, HTML')
    return
  }

  // 验证文件大小 (10MB)
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('文本文件大小不能超过 10MB')
    return
  }

  try {
    // 读取文件内容
    const text = await readFileContent(file)
    inputText.value = text
    ElMessage.success(`成功导入文本文件，共 ${text.length} 字符`)

    // 自动检测语言
    detectLanguage()
  } catch (error: any) {
    console.error('读取文件失败:', error)
    ElMessage.error('读取文件失败: ' + error.message)
  }

  // 清空文件输入，允许重复上传同一文件
  target.value = ''
}

// 读取文件内容
const readFileContent = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const content = e.target?.result as string
      if (content) {
        resolve(content)
      } else {
        reject(new Error('文件内容为空'))
      }
    }
    reader.onerror = () => {
      reject(new Error('读取文件失败'))
    }
    reader.readAsText(file, 'utf-8')
  })
}

// 文档移除
const handleDocRemove = () => {
  fileList.value = []
  docResult.value = false
  docTranslatedData.value = null
}

// 文档选择变化
const handleDocChange = async (file: any, fileList: any[]) => {
  // 保存文件对象
  file.raw = file.raw || file

  // 验证文件
  if (!file.raw) {
    ElMessage.error('文件对象无效')
    return
  }

  try {
    uploadingDoc.value = true

    // 创建 FormData 对象
    const formData = new FormData()
    formData.append('file', file.raw)
    formData.append('source_lang', sourceLang.value)
    formData.append('target_lang', targetLang.value)
    formData.append('type', docConfig.value.type)
    formData.append('about_text', docConfig.value.about_text || '')
    formData.append('transtask', String(docConfig.value.transtask))
    formData.append('graphtask', String(docConfig.value.graphtask))
    formData.append('share', String(docConfig.value.share))
    formData.append('userversion', String(docConfig.value.userversion))

    // 调用文件上传 API
    const response = await FileUpload(formData)

    console.log('FileUpload API 响应:', response)
    console.log('response.data:', response?.data)
    console.log('response.code:', response?.code)

    // 检查响应结构，支持多种可能的格式
    let isSuccess = false
    let uploadData = null
    let message = ''

    // 格式1: response.data.code === 2000 (request 未解包)
    if (response?.data?.code === 2000) {
      isSuccess = true
      uploadData = response.data.data
      message = response.data.msg
      console.log('使用格式1: response.data.code')
    }
    // 格式2: response.code === 2000 (request 已解包)
    else if (response?.code === 2000) {
      isSuccess = true
      uploadData = response.data
      message = response.msg
      console.log('使用格式2: response.code')
    }
    // 其他情况，视为失败
    else {
      isSuccess = false
      message = response?.data?.msg || response?.msg || '上传失败，未知错误'
      console.log('响应格式不支持或失败')
    }

    if (isSuccess) {
      console.log('上传成功，数据:', uploadData)

      // 保存上传结果
      file.id = uploadData.id
      file.uploaded = true
      file.file_path = uploadData.file_path

      ElMessage.success(`文档上传成功！文件类型: ${uploadData.type_display}, 大小: ${formatFileSize(uploadData.file_size)}`)

      // 加载该文件的保存内容
      await loadSavedDocContent()
    } else {
      console.error('上传失败:', message)
      ElMessage.error(message)
      // 上传失败，清空文件列表
      clearFile()
    }
  } catch (error: any) {
    console.error('文档上传错误:', error)
    ElMessage.error(error.response?.data?.msg || error.message || '文档上传失败')
    clearFile()
  } finally {
    uploadingDoc.value = false
  }
}

// 文档翻译
const translateDocument = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先上传文档')
    return
  }

  // 检查文件是否已上传
  if (!fileList.value[0].uploaded) {
    ElMessage.warning('文件正在上传或上传失败，请稍候')
    return
  }

  translating.value = true

  try {
    // 创建 FormData 对象，包含配置信息
    const formData = new FormData()
    formData.append('file', fileList.value[0].raw)
    formData.append('source_lang', targetLang.value === 'zh' ? 'en' : 'auto') // 简化处理
    formData.append('target_lang', targetLang.value)
    formData.append('type', docConfig.value.type)
    formData.append('about_text', docConfig.value.about_text || '')
    formData.append('transtask', String(docConfig.value.transtask))
    formData.append('graphtask', String(docConfig.value.graphtask))
    formData.append('share', String(docConfig.value.share))
    formData.append('userversion', String(docConfig.value.userversion))

    let response

    // 根据是否需要翻译选择不同的API
    if (docConfig.value.transtask) {
      // 需要翻译，调用翻译API
      response = await TranslateDocument(formData)
    } else {
      // 只需要上传和处理，调用上传API
      response = await FileUpload(formData)
    }

    if (response && response.data) {
      if (response.data.code === 200 || response.data.code === 2000) {
        if (docConfig.value.transtask) {
          // 翻译结果
          docTranslatedData.value = response.data.data
          docResult.value = true
          ElMessage.success(`文档翻译完成，共 ${response.data.data.paragraph_count} 段`)
        } else {
          // 上传结果
          ElMessage.success('文档上传成功!')
          // 可以在这里处理上传成功的逻辑
        }
      } else {
        ElMessage.error(response.data.msg || '操作失败，请重试')
      }
    } else {
      ElMessage.error('操作失败，请重试')
    }
  } catch (error: any) {
    console.error('文档处理错误:', error)
    ElMessage.error(error.message || '文档处理失败，请重试')
  } finally {
    translating.value = false
  }
}

// 下载文档
const downloadDocument = async () => {
  if (!docTranslatedData.value || !docTranslatedData.value.translated_path) {
    ElMessage.warning('没有可下载的文档')
    return
  }

  try {
    // 使用后端下载接口
    const file_path = docTranslatedData.value.translated_path
    const downloadUrl = `/api/system/transdicts/document/download/?file_path=${encodeURIComponent(file_path)}`

    // 创建下载链接
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = docTranslatedData.value.translated_filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    ElMessage.success('文档下载中...')
  } catch (error: any) {
    console.error('下载文档错误:', error)
    ElMessage.error(error.message || '下载文档失败')
  }
}

// 预览文档
const previewDocument = () => {
  if (!docTranslatedData.value || !docTranslatedData.value.preview) {
    ElMessage.warning('没有可预览的内容')
    return
  }

  ElMessage.info('预览功能：请下载文档后使用 Word 打开查看完整内容')
}

// 内容编辑器显示状态
const showContentEditor = ref(false)

// 文档内容数据
const docContent = ref({
  // 基础信息
  about: '',
  order: 0,
  title: '',
  subtitle: '',
  subweight: 0,
  content: '',
  contentedittime: '',
  contentedituser: '',
  
  // 翻译相关
  transcontent: '',
  transnote: '',
  transcheck1: false,
  transcheck2: false,
  translast: false,
  transmanger: '',
  docmanger: '',
  
  // 版本控制
  version: 1
})

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 格式化编辑时间
const formatEditTime = (timeStr: string): string => {
  if (!timeStr) return '-'
  try {
    const date = new Date(timeStr)
    return date.toLocaleString('zh-CN')
  } catch {
    return timeStr
  }
}

// 获取标题样式类
const getTitleClass = (level: number): string => {
  const classes = ['title-level-0', 'title-level-1', 'title-level-2', 'title-level-3', 'title-level-4', 
                  'title-level-5', 'title-level-6', 'title-level-7', 'title-level-8', 'title-level-9', 'title-level-10']
  return classes[level] || 'title-level-0'
}

// 保存文档内容
const saveDocContent = async () => {
  try {
    // 更新编辑时间和用户（这里简化处理，实际应从用户信息获取）
    docContent.value.contentedittime = new Date().toISOString()
    docContent.value.contentedituser = '当前用户' // 实际应用中应从登录信息获取
    
    // 这里应该调用API保存到后端
    // await SaveDocContent({ ...docContent.value, docxfile_id: currentDocId.value })
    
    ElMessage.success('文档内容保存成功！')
    
    // 模拟保存到本地存储
    localStorage.setItem(`doc_content_${fileList.value[0]?.name}`, JSON.stringify(docContent.value))
    
  } catch (error: any) {
    console.error('保存文档内容错误:', error)
    ElMessage.error(error.message || '保存失败，请重试')
  }
}

// 重置文档内容
const resetDocContent = () => {
  // 保留基本信息，清空内容
  const basicInfo = {
    about: docContent.value.about,
    order: docContent.value.order,
    title: docContent.value.title,
    subtitle: docContent.value.subtitle,
    subweight: docContent.value.subweight,
    version: docContent.value.version,
    transmanger: docContent.value.transmanger,
    docmanger: docContent.value.docmanger
  }
  
  // 重置内容相关字段
  Object.assign(docContent.value, {
    ...basicInfo,
    content: '',
    transcontent: '',
    transnote: '',
    transcheck1: false,
    transcheck2: false,
    translast: false,
    contentedittime: '',
    contentedituser: ''
  })
  
  ElMessage.info('文档内容已重置')
}

// 加载已保存的文档内容
const loadSavedDocContent = () => {
  if (fileList.value.length > 0) {
    const fileName = fileList.value[0]?.name
    const saved = localStorage.getItem(`doc_content_${fileName}`)
    if (saved) {
      try {
        const savedData = JSON.parse(saved)
        Object.assign(docContent.value, savedData)
      } catch (error) {
        console.warn('加载保存的文档内容失败:', error)
      }
    }
  }
}

// 清除文件
const clearFile = () => {
  fileList.value = []
  docResult.value = false
  docTranslatedData.value = null
  docContent.value = {
    about: '',
    order: 0,
    title: '',
    subtitle: '',
    subweight: 0,
    content: '',
    contentedittime: '',
    contentedituser: '',
    transcontent: '',
    transnote: '',
    transcheck1: false,
    transcheck2: false,
    translast: false,
    transmanger: '',
    docmanger: '',
    version: 1
  }
  showContentEditor.value = false
  // 保留配置供下次使用
}

// 修改第998行的 handleDocChange 函数，在函数末尾添加加载内容功能

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

.input-toolbar {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 12px;
}

.input-toolbar .el-button {
  color: #606266;
}

.input-toolbar .el-button:hover {
  color: #409eff;
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

.upload-icon.is-loading {
  animation: rotate 1.5s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
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

.preview-section {
  margin-top: 20px;
}

.preview-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #303133;
}

.preview-item {
  margin-bottom: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
}

.preview-original {
  font-size: 13px;
  color: #606266;
  margin-bottom: 4px;
}

.preview-translated {
  font-size: 13px;
  color: #409eff;
  font-weight: 500;
}

/* 文档翻译 */
.document-translation-container {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

/* 文档配置区域 */
.document-config {
  grid-column: 1 / -1;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
}

.config-section h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #303133;
  font-weight: 600;
}

.config-form {
  width: 100%;
}

.feature-toggles {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.config-summary {
  margin-top: 12px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* 文件信息显示 */
.file-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 2px dashed #dcdfe6;
}

.file-details {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.file-icon {
  font-size: 32px;
  color: #409eff;
}

.file-meta {
  flex: 1;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.file-size {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.file-config {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.doc-actions {
  margin-top: 20px;
  text-align: center;
  display: flex;
  gap: 12px;
  justify-content: center;
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

/* 文档选择和内容编辑器 */
.document-selection {
  grid-column: 1 / -1;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
}

.selection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.selection-header h4 {
  margin: 0;
  font-size: 16px;
  color: #303133;
  font-weight: 600;
}

.content-editor {
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  padding: 20px;
  background: #fafbfc;
}

.content-form .el-form-item {
  margin-bottom: 18px;
}

/* 文档内容预览 */
.document-content-preview {
  margin-top: 20px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e5e5e5;
}

.document-content-preview h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #303133;
  font-weight: 600;
  border-bottom: 2px solid #409eff;
  padding-bottom: 8px;
}

.content-sections {
  margin-bottom: 20px;
}

.content-section {
  margin-bottom: 16px;
}

.section-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.section-content {
  padding: 12px;
  border-radius: 6px;
  border-left: 4px solid #409eff;
  background: #f8f9fa;
  line-height: 1.6;
}

.title-content {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 12px;
}

.subtitle-content {
  font-size: 16px;
  font-weight: 500;
  color: #606266;
  font-style: italic;
}

.about-content {
  color: #606266;
  background: #f0f9ff;
  border-left-color: #67c23a;
}

.original-content {
  color: #303133;
  background: #fff;
  border-left-color: #909399;
  white-space: pre-wrap;
}

.translated-content {
  color: #409eff;
  background: #f0f9ff;
  border-left-color: #409eff;
  white-space: pre-wrap;
  font-weight: 500;
}

.note-content {
  color: #e6a23c;
  background: #fdf6ec;
  border-left-color: #e6a23c;
  font-size: 14px;
}

/* 标题级别样式 */
.title-level-0 { font-size: 14px; }
.title-level-1 { font-size: 24px; color: #303133; }
.title-level-2 { font-size: 20px; color: #409eff; }
.title-level-3 { font-size: 18px; color: #67c23a; }
.title-level-4 { font-size: 16px; color: #e6a23c; }
.title-level-5 { font-size: 15px; color: #f56c6c; }
.title-level-6 { font-size: 14px; color: #909399; }
.title-level-7 { font-size: 14px; color: #c0c4cc; }
.title-level-8 { font-size: 13px; color: #dcdfe6; }
.title-level-9 { font-size: 13px; color: #e4e7ed; }
.title-level-10 { font-size: 12px; color: #f2f6fc; }

/* 内容状态信息 */
.content-status {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e5e5e5;
}

.content-status :deep(.el-descriptions__label) {
  font-weight: 500;
  color: #606266;
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
  
  /* 移动端文档内容编辑器适配 */
  .content-editor .el-row {
    margin: 0;
  }
  
  .content-editor .el-col {
    padding: 0;
    margin-bottom: 12px;
  }
  
  .document-content-preview {
    padding: 12px;
  }
  
  .section-content {
    padding: 8px;
  }
  
  .title-content {
    font-size: 16px;
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
