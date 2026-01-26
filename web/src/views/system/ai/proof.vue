<template>
  <div class="proof-container">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button type="primary" :icon="Upload" @click="handleImport">
          导入翻译内容
        </el-button>
        <el-button :icon="Refresh" @click="handleRefresh">
          刷新
        </el-button>
        <el-button :icon="MagicStick" @click="autoCheckAll" :loading="checking">
          智能校对全部
        </el-button>
      </div>
      <div class="toolbar-right">
        <el-tag type="info">总条数: {{ totalItems }}</el-tag>
        <el-tag type="warning">待校对: {{ pendingItems }}</el-tag>
        <el-tag type="success">已修改: {{ fixedItems }}</el-tag>
        <el-tag type="danger">错误数: {{ totalErrors }}</el-tag>
        <el-button type="primary" :icon="Check" @click="handleExport">
          导出结果
        </el-button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="content-wrapper">
      <!-- 左侧：对照展示 -->
      <div class="comparison-panel">
        <div class="panel-header">
          <h3>翻译内容对照</h3>
          <el-radio-group v-model="viewMode" size="small">
            <el-radio-button value="split">分屏模式</el-radio-button>
            <el-radio-button value="vertical">上下模式</el-radio-button>
          </el-radio-group>
        </div>

        <div :class="['comparison-content', viewMode]">
          <!-- 原文区域 -->
          <div class="section original-section">
            <div class="section-header">
              <span class="section-title">原文</span>
              <el-tag size="small" type="info">{{ sourceLang }}</el-tag>
            </div>
            <div class="content-area">
              <div
                v-for="(item, index) in items"
                :key="item.id"
                :class="['text-item', { active: selectedItem?.id === item.id, hasErrors: item.errors?.length > 0 }]"
                @click="selectItem(item)"
              >
                <span class="line-number">{{ index + 1 }}</span>
                <div class="text-content">{{ item.original }}</div>
                <el-tag
                  v-if="item.errors?.length > 0"
                  type="danger"
                  size="small"
                  class="error-badge"
                >
                  {{ item.errors.length }}
                </el-tag>
              </div>
            </div>
          </div>

          <div v-if="viewMode === 'split'" class="divider" />

          <!-- 译文区域 -->
          <div class="section translated-section">
            <div class="section-header">
              <span class="section-title">译文</span>
              <el-tag size="small" type="success">{{ targetLang }}</el-tag>
            </div>
            <div class="content-area">
              <div
                v-for="(item, index) in items"
                :key="item.id"
                :class="['text-item', { active: selectedItem?.id === item.id, hasErrors: item.errors?.length > 0 }]"
                @click="selectItem(item)"
              >
                <span class="line-number">{{ index + 1 }}</span>
                <div class="text-content">
                  <template v-for="(part, pIndex) in item.translatedParts" :key="pIndex">
                    <span
                      v-if="part.type === 'error'"
                      :class="['text-part', 'error-highlight', { selected: selectedError?.id === part.id }]"
                      @click.stop="selectError(item, part)"
                    >
                      {{ part.text }}
                    </span>
                    <span v-else class="text-part">{{ part.text }}</span>
                  </template>
                </div>
                <div v-if="item.errors?.length > 0" class="error-indicators">
                  <el-tag
                    v-for="error in item.errors"
                    :key="error.id"
                    :type="getErrorTagType(error.type)"
                    size="small"
                    @click.stop="selectError(item, error)"
                  >
                    {{ error.type }}
                  </el-tag>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：校对面板 -->
      <div class="proof-panel">
        <div class="panel-header">
          <h3>校对详情</h3>
          <el-tag v-if="selectedItem" :type="selectedItem.errors?.length > 0 ? 'danger' : 'success'">
            {{ selectedItem.errors?.length > 0 ? `${selectedItem.errors.length} 个问题` : '无问题' }}
          </el-tag>
        </div>

        <div v-if="selectedItem" class="proof-content">
          <!-- 选中项信息 -->
          <div class="item-info">
            <div class="info-row">
              <span class="label">原文:</span>
              <span class="value">{{ selectedItem.original }}</span>
            </div>
            <div class="info-row">
              <span class="label">当前译文:</span>
              <span class="value">{{ selectedItem.translation }}</span>
            </div>
          </div>

          <!-- 错误列表 -->
          <div v-if="selectedItem.errors?.length > 0" class="errors-section">
            <h4 class="section-title">
              <el-icon><Warning /></el-icon>
              发现的问题 ({{ selectedItem.errors.length }})
            </h4>

            <div class="errors-list">
              <div
                v-for="(error, eIndex) in selectedItem.errors"
                :key="error.id"
                :class="['error-card', { selected: selectedError?.id === error.id }]"
                @click="selectError(selectedItem, error)"
              >
                <div class="error-header">
                  <el-tag :type="getErrorTagType(error.type)" size="small">
                    {{ error.type }}
                  </el-tag>
                  <el-tag type="warning" size="small">置信度: {{ error.confidence }}%</el-tag>
                  <el-tag v-if="error.fixed" type="success" size="small">已修复</el-tag>
                </div>

                <div class="error-detail">
                  <div class="detail-row">
                    <span class="detail-label">原文片段:</span>
                    <span class="detail-value">{{ error.original }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">当前译文:</span>
                    <span class="detail-value error-text">{{ error.current }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">问题描述:</span>
                    <span class="detail-value description">{{ error.description }}</span>
                  </div>
                </div>

                <!-- 修改建议 -->
                <div class="suggestions-section" v-if="!error.fixed">
                  <h5 class="suggestions-title">
                    <el-icon><List /></el-icon>
                    修改建议 ({{ error.suggestions.length }})
                  </h5>
                  <div class="suggestions-list">
                    <div
                      v-for="(suggestion, sIndex) in error.suggestions"
                      :key="sIndex"
                      :class="['suggestion-item', { selected: suggestion.selected }]"
                      @click.stop="selectSuggestion(selectedItem, error, sIndex)"
                    >
                      <div class="suggestion-header">
                        <el-checkbox v-model="suggestion.selected" @change="handleSuggestionSelect(error, sIndex)">
                          选择此建议
                        </el-checkbox>
                      </div>
                      <div class="suggestion-content">
                        <div class="suggestion-text">
                          <span class="prefix">建议译文:</span>
                          <span class="text">{{ suggestion.text }}</span>
                        </div>
                        <div class="suggestion-reason">
                          <span class="prefix">理由:</span>
                          <span class="text">{{ suggestion.reason }}</span>
                        </div>
                      </div>
                      <div class="suggestion-action">
                        <el-button
                          type="primary"
                          size="small"
                          :icon="Check"
                          @click.stop="applySuggestion(selectedItem, error, sIndex)"
                        >
                          立即应用
                        </el-button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 无问题 -->
          <div v-else class="no-errors">
            <el-empty description="此段落未发现明显问题">
              <el-button type="success" :icon="Check" @click="markAsCorrect(selectedItem)">
                标记为正确
              </el-button>
            </el-empty>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="empty-state">
          <el-empty description="请选择左侧内容进行校对" />
        </div>

        <!-- 快捷操作 -->
        <div class="quick-actions" v-if="selectedItem">
          <el-button
            type="warning"
            :icon="MagicStick"
            :disabled="!selectedItem.errors?.length || selectedItem.errors.every(e => e.fixed)"
            @click="autoFixItem(selectedItem)"
          >
            一键修复全部
          </el-button>
          <el-button
            type="info"
            :icon="DocumentCopy"
            @click="copyTranslation(selectedItem)"
          >
            复制译文
          </el-button>
          <el-button
            type="success"
            :icon="Check"
            @click="markAsCorrect(selectedItem)"
          >
            确认无误
          </el-button>
        </div>
      </div>
    </div>

    <!-- 统计面板 -->
    <div class="stats-panel">
      <div class="stat-item">
        <div class="stat-icon" style="background: #f56c6c;">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ totalErrors }}</div>
          <div class="stat-label">总错误</div>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon" style="background: #e6a23c;">
          <el-icon><Edit /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ grammaticalErrors }}</div>
          <div class="stat-label">语法</div>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon" style="background: #909399;">
          <el-icon><Reading /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ wordChoiceErrors }}</div>
          <div class="stat-label">用词</div>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon" style="background: #67c23a;">
          <el-icon><Check /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ fixedItems }}</div>
          <div class="stat-label">已修复</div>
        </div>
      </div>
    </div>

    <!-- 导入对话框 -->
    <el-dialog v-model="importDialogVisible" title="导入翻译内容" width="500px">
      <el-upload
        drag
        :auto-upload="false"
        @change="handleFileChange"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 .txt, .docx, .xlsx 格式
          </div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmImport">确认导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Upload, Refresh, MagicStick, Check, Warning, List, Edit,
  Reading, DocumentCopy, UploadFilled
} from '@element-plus/icons-vue'

// 数据
const items = ref([])
const selectedItem = ref(null)
const selectedError = ref(null)
const viewMode = ref('split')
const sourceLang = ref('中文')
const targetLang = ref('English')
const importDialogVisible = ref(false)
const checking = ref(false)

// 初始化演示数据
const initDemoData = () => {
  items.value = [
    {
      id: 1,
      original: '该设备由齿轮、轴承和联轴器组成。',
      translation: 'The device consists of gears, bearings and couplings.',
      translatedParts: [
        { text: 'The device consists of ', type: 'normal' },
        { text: 'gears', type: 'normal' },
        { text: ', ', type: 'normal' },
        { text: 'bearings', type: 'normal' },
        { text: ' and ', type: 'normal' },
        { text: 'couplings', type: 'normal' },
        { text: '.', type: 'normal' }
      ],
      errors: [
        {
          id: 'err_1_1',
          type: '语法错误',
          confidence: 85,
          original: '齿轮',
          current: 'gears',
          description: '在描述设备组成时，应该使用复数形式表示多个部件',
          suggestions: [
            {
              text: 'The equipment consists of gears, bearings, and couplings.',
              reason: '使用 equipment 替代 device 更专业，添加 and 前的逗号符合语法规范',
              selected: false
            },
            {
              text: 'The apparatus comprises gears, bearings, and couplings.',
              reason: 'comprises 比 consists of 更正式专业',
              selected: false
            }
          ],
          fixed: false
        }
      ],
      fixed: false
    },
    {
      id: 2,
      original: '机械臂的工作精度可达0.01毫米。',
      translation: 'The working precision of the mechanical arm can reach 0.01 mm.',
      translatedParts: [
        { text: 'The working precision of the mechanical arm can reach 0.01 mm.', type: 'normal' }
      ],
      errors: [],
      fixed: false
    },
    {
      id: 3,
      original: '传感器安装位置需要校准。',
      translation: 'The sensor installation position needs calibration.',
      translatedParts: [
        { text: 'The ', type: 'normal' },
        { text: 'sensor', type: 'error', id: 'err_3_1' },
        { text: ' installation position needs calibration.', type: 'normal' }
      ],
      errors: [
        {
          id: 'err_3_1',
          type: '用词不当',
          confidence: 90,
          original: '传感器',
          current: 'sensor',
          description: '在技术文档中，传感器通常使用复数形式',
          suggestions: [
            {
              text: 'The sensors installation position requires calibration.',
              reason: '使用 sensors（复数）更符合技术文档规范',
              selected: false
            },
            {
              text: 'The installation position of sensors requires calibration.',
              reason: '调整语序更符合英语表达习惯',
              selected: false
            }
          ],
          fixed: false
        }
      ],
      fixed: false
    },
    {
      id: 4,
      original: '液压系统的压力调节阀失效了。',
      translation: 'The pressure regulating valve of the hydraulic system has failed.',
      translatedParts: [
        { text: 'The pressure regulating valve of the hydraulic system ', type: 'normal' },
        { text: 'has failed', type: 'error', id: 'err_4_1' },
        { text: '.', type: 'normal' }
      ],
      errors: [
        {
          id: 'err_4_1',
          type: '语法错误',
          confidence: 80,
          original: '失效了',
          current: 'has failed',
          description: '在技术文档中，建议使用更专业的表达方式',
          suggestions: [
            {
              text: 'The pressure regulating valve of the hydraulic system has become inoperative.',
              reason: 'become inoperative 更专业正式',
              selected: false
            },
            {
              text: 'The pressure regulating valve of the hydraulic system has malfunctioned.',
              reason: 'malfunctioned 在技术文档中更常用',
              selected: false
            }
          ],
          fixed: false
        }
      ],
      fixed: false
    },
    {
      id: 5,
      original: '传动比是15:2。',
      translation: 'The transmission ratio is 15:2.',
      translatedParts: [
        { text: 'The transmission ratio is 15:2.', type: 'normal' }
      ],
      errors: [],
      fixed: false
    },
    {
      id: 6,
      original: '电机转速应该保持在3000转每分钟。',
      translation: 'The motor speed should be maintained at 3000 rpm.',
      translatedParts: [
        { text: 'The ', type: 'normal' },
        { text: 'motor', type: 'error', id: 'err_6_1' },
        { text: ' speed ', type: 'normal' },
        { text: 'should', type: 'error', id: 'err_6_2' },
        { text: ' be maintained at 3000 rpm.', type: 'normal' }
      ],
      errors: [
        {
          id: 'err_6_1',
          type: '语法错误',
          confidence: 75,
          original: '电机',
          current: 'motor',
          description: '缺少定冠词，建议使用完整的表达',
          suggestions: [
            {
              text: 'The electric motor speed shall be maintained at 3000 rpm.',
              reason: '添加 electric 使表达更明确，使用 shall 在技术标准中表示强制性要求',
              selected: false
            }
          ],
          fixed: false
        },
        {
          id: 'err_6_2',
          type: '用词不当',
          confidence: 85,
          original: '应该',
          current: 'should',
          description: '在技术规范中，should 不够正式',
          suggestions: [
            {
              text: 'The motor speed shall be maintained at 3000 rpm.',
              reason: 'shall 在技术标准中表示必须遵守的要求',
              selected: false
            }
          ],
          fixed: false
        }
      ],
      fixed: false
    },
    {
      id: 7,
      original: '控制柜内的温度传感器显示温度过高。',
      translation: 'The temperature sensor in the control cabinet shows excessive temperature.',
      translatedParts: [
        { text: 'The temperature sensor in the control cabinet shows excessive temperature.', type: 'normal' }
      ],
      errors: [
        {
          id: 'err_7_1',
          type: '语义错误',
          confidence: 88,
          original: '显示温度过高',
          current: 'shows excessive temperature',
          description: '表达不够准确，传感器是"检测"而非"显示"',
          suggestions: [
            {
              text: 'The temperature sensor in the control cabinet indicates an excessive temperature.',
              reason: 'indicates 比 shows 更准确表达传感器的检测功能',
              selected: false
            },
            {
              text: 'The temperature sensor within the control cabinet detects excessive temperature.',
              reason: 'detects 更准确，within 替代 in 更正式',
              selected: false
            }
          ],
          fixed: false
        }
      ],
      fixed: false
    },
    {
      id: 8,
      original: '请检查所有连接件是否紧固。',
      translation: 'Please check if all connectors are tightened.',
      translatedParts: [
        { text: 'Please check if all ', type: 'normal' },
        { text: 'connectors', type: 'error', id: 'err_8_1' },
        { text: ' are tightened.', type: 'normal' }
      ],
      errors: [
        {
          id: 'err_8_1',
          type: '用词不当',
          confidence: 82,
          original: '连接件',
          current: 'connectors',
          description: '在机械领域，连接件更常用 fasteners 或 connections',
          suggestions: [
            {
              text: 'Please verify that all fasteners are properly secured.',
              reason: 'fasteners 是机械领域的标准术语，properly secured 更准确',
              selected: false
            },
            {
              text: 'Please inspect all connections to ensure they are properly tightened.',
              reason: 'connections 更通用，inspect 比 check 更正式',
              selected: false
            }
          ],
          fixed: false
        }
      ],
      fixed: false
    }
  ]
}

initDemoData()

// 计算属性
const totalItems = computed(() => items.value.length)
const pendingItems = computed(() => items.value.filter(item => !item.fixed).length)
const fixedItems = computed(() => items.value.filter(item => item.fixed).length)
const totalErrors = computed(() => items.value.reduce((sum, item) => sum + (item.errors?.length || 0), 0))
const grammaticalErrors = computed(() => items.value.reduce((sum, item) => sum + (item.errors?.filter(e => e.type === '语法错误').length || 0), 0))
const wordChoiceErrors = computed(() => items.value.reduce((sum, item) => sum + (item.errors?.filter(e => e.type === '用词不当').length || 0), 0))

// 方法
const selectItem = (item) => {
  selectedItem.value = item
  selectedError.value = null
}

const selectError = (item, error) => {
  selectedItem.value = item
  selectedError.value = error
}

const selectSuggestion = (item, error, sIndex) => {
  error.suggestions.forEach((s, idx) => {
    s.selected = idx === sIndex
  })
}

const handleSuggestionSelect = (error, sIndex) => {
  // 选择建议时不需要额外操作，由 checkbox v-model 处理
}

const applySuggestion = (item, error, sIndex) => {
  const suggestion = error.suggestions[sIndex]

  // 更新译文
  item.translation = suggestion.text

  // 更新分段（简化处理，重新创建）
  item.translatedParts = [
    { text: suggestion.text, type: 'normal' }
  ]

  // 标记为已修复
  error.fixed = true

  // 检查是否全部修复
  const allFixed = item.errors.every(e => e.fixed)
  if (allFixed) {
    item.fixed = true
  }

  ElMessage.success('修改已应用')

  // 刷新选中项
  selectedItem.value = { ...item }
}

const autoFixItem = (item) => {
  if (!item.errors?.length) return

  ElMessageBox.confirm(
    '将自动选择最佳建议并应用所有修改，是否继续？',
    '自动修复',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    item.errors.forEach(error => {
      if (!error.fixed && error.suggestions.length > 0) {
        applySuggestion(item, error, 0)
      }
    })
    ElMessage.success('全部问题已修复')
  }).catch(() => {})
}

const markAsCorrect = (item) => {
  item.fixed = true
  ElMessage.success('已标记为正确')
}

const copyTranslation = (item) => {
  navigator.clipboard.writeText(item.translation)
  ElMessage.success('译文已复制到剪贴板')
}

const handleImport = () => {
  importDialogVisible.value = true
}

const handleFileChange = (file) => {
  console.log('文件已选择:', file.name)
}

const confirmImport = () => {
  importDialogVisible.value = false
  ElMessage.success('内容导入成功')
}

const handleRefresh = () => {
  ElMessage.info('刷新功能已触发')
}

const handleExport = () => {
  ElMessage.success('校对结果导出成功')
}

const autoCheckAll = () => {
  checking.value = true
  setTimeout(() => {
    checking.value = false
    ElMessage.success('智能校对完成')
  }, 1500)
}

const getErrorTagType = (type) => {
  const typeMap = {
    '语法错误': 'danger',
    '用词不当': 'warning',
    '语义错误': 'danger',
    '格式错误': 'info'
  }
  return typeMap[type] || 'info'
}
</script>

<style scoped lang="scss">
.proof-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 16px;
  box-sizing: border-box;
  gap: 12px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 12px 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

  .toolbar-left,
  .toolbar-right {
    display: flex;
    align-items: center;
    gap: 10px;

    .el-tag {
      margin-right: 4px;
    }
  }
}

.content-wrapper {
  flex: 1;
  display: flex;
  gap: 16px;
  overflow: hidden;
}

.comparison-panel {
  flex: 1;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.panel-header {
  padding: 12px 20px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;

  h3 {
    margin: 0;
    font-size: 16px;
    color: #303133;
  }
}

.comparison-content {
  flex: 1;
  display: flex;
  overflow: hidden;

  &.vertical {
    flex-direction: column;

    .divider {
      width: 100%;
      height: 2px;
      background: linear-gradient(to right, transparent, #dcdfe6 20%, #dcdfe6 80%, transparent);
    }
  }
}

.section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  &.original-section {
    border-right: 1px solid #e4e7ed;
  }
}

.section-header {
  padding: 10px 20px;
  background: #fafafa;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;

  .section-title {
    font-weight: 600;
    color: #606266;
    font-size: 14px;
  }
}

.content-area {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.text-item {
  display: flex;
  align-items: flex-start;
  padding: 10px 12px;
  margin-bottom: 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;

  &:hover {
    background: #f5f7fa;
  }

  &.active {
    background: #ecf5ff;
    border-color: #b3d8ff;
  }

  &.hasErrors {
    border-left: 3px solid #f56c6c;
  }

  .line-number {
    min-width: 32px;
    color: #909399;
    font-size: 12px;
    margin-right: 10px;
    text-align: right;
  }

  .text-content {
    flex: 1;
    color: #303133;
    line-height: 1.6;
    font-size: 14px;
  }

  .error-badge {
    margin-left: 8px;
  }

  .error-part {
    background: #fef0f0;
    color: #f56c6c;
    padding: 2px 4px;
    border-radius: 3px;
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      background: #fde2e2;
    }

    &.selected {
      background: #f56c6c;
      color: white;
    }
  }

  .error-highlight {
    background: #fef0f0;
    color: #f56c6c;
    border-bottom: 2px solid #f56c6c;
    padding: 2px 4px;
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      background: #fde2e2;
    }

    &.selected {
      background: #f56c6c;
      color: white;
    }
  }

  .error-indicators {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-top: 4px;

    .el-tag {
      cursor: pointer;

      &:hover {
        opacity: 0.8;
      }
    }
  }
}

.divider {
  width: 2px;
  background: linear-gradient(to bottom, transparent, #dcdfe6 20%, #dcdfe6 80%, transparent);
}

.proof-panel {
  width: 420px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.proof-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.item-info {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 16px;

  .info-row {
    display: flex;
    margin-bottom: 8px;
    font-size: 13px;

    &:last-child {
      margin-bottom: 0;
    }

    .label {
      min-width: 70px;
      color: #909399;
      font-weight: 500;
    }

    .value {
      flex: 1;
      color: #303133;
      line-height: 1.5;
    }
  }
}

.errors-section {
  h4 {
    margin: 0 0 16px 0;
    color: #f56c6c;
    font-size: 15px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 6px;
  }
}

.errors-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.error-card {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: #409eff;
    box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
  }

  &.selected {
    border-color: #409eff;
    box-shadow: 0 2px 12px rgba(64, 158, 255, 0.15);
  }
}

.error-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.error-detail {
  margin-bottom: 12px;

  .detail-row {
    display: flex;
    margin-bottom: 6px;
    font-size: 13px;

    &:last-child {
      margin-bottom: 0;
    }

    .detail-label {
      min-width: 80px;
      color: #909399;
    }

    .detail-value {
      flex: 1;
      color: #303133;
      line-height: 1.5;

      &.error-text {
        color: #f56c6c;
        text-decoration: line-through;
      }

      &.description {
        color: #e6a23c;
      }
    }
  }
}

.suggestions-section {
  border-top: 1px solid #e4e7ed;
  padding-top: 12px;

  h5 {
    margin: 0 0 10px 0;
    color: #409eff;
    font-size: 14px;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 4px;
  }
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.suggestion-item {
  background: #f0f9ff;
  border: 1px solid #b3d8ff;
  border-radius: 6px;
  padding: 10px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: #409eff;
    background: #e6f7ff;
  }

  &.selected {
    border-color: #67c23a;
    background: #f0f9ff;
  }
}

.suggestion-header {
  margin-bottom: 8px;
}

.suggestion-content {
  margin-bottom: 10px;

  .suggestion-text,
  .suggestion-reason {
    display: flex;
    margin-bottom: 6px;
    font-size: 13px;

    &:last-child {
      margin-bottom: 0;
    }

    .prefix {
      min-width: 60px;
      color: #909399;
    }

    .text {
      flex: 1;
      color: #303133;
      line-height: 1.5;
    }
  }

  .suggestion-text .text {
    color: #409eff;
    font-weight: 500;
  }
}

.suggestion-action {
  display: flex;
  justify-content: flex-end;
}

.no-errors,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 20px;
}

.quick-actions {
  padding: 12px 16px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  gap: 8px;

  .el-button {
    flex: 1;
  }
}

.stats-panel {
  display: flex;
  gap: 16px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 12px 24px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  align-items: center;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 16px;
  border-right: 1px solid #e4e7ed;

  &:last-child {
    border-right: none;
  }

  .stat-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 18px;
  }

  .stat-info {
    .stat-value {
      font-size: 20px;
      font-weight: bold;
      color: #303133;
      line-height: 1;
      margin-bottom: 4px;
    }

    .stat-label {
      font-size: 12px;
      color: #909399;
    }
  }
}

.upload-demo {
  width: 100%;
}
</style>
