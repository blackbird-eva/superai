<template>
  <div class="term-analysis-container">
    <!-- 头部区域 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">AI 术语分析工作台</h1>
        <p class="page-subtitle">专业术语分析、权重评估、多语言对照</p>
      </div>
    </div>

    <!-- 功能模式切换 -->
    <div class="mode-tabs">
      <el-radio-group v-model="analysisMode">
        <el-radio-button label="term">术语分析</el-radio-button>
        <el-radio-button label="compare">对照翻译</el-radio-button>
        <el-radio-button label="weight">权重评估</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 输入区域 -->
    <div class="input-section">
      <el-card class="input-card">
        <template #header>
          <div class="card-header">
            <span>输入文本</span>
            <div class="header-actions">
              <el-select v-model="inputLang" placeholder="选择语言" style="width: 120px">
                <el-option label="中文" value="zh"></el-option>
                <el-option label="英语" value="en"></el-option>
                <el-option label="日语" value="ja"></el-option>
              </el-select>
              <el-button text @click="clearInput" v-if="inputText">
                <el-icon><Delete /></el-icon> 清空
              </el-button>
            </div>
          </div>
        </template>
        <el-input
          v-model="inputText"
          type="textarea"
          :rows="6"
          placeholder="请输入需要分析的文本..."
          class="analysis-input"
        ></el-input>
        <div class="input-actions">
          <el-button type="primary" @click="analyze" :loading="analyzing">
            <el-icon><DataAnalysis /></el-icon> 开始分析
          </el-button>
          <el-button @click="loadExample">
            <el-icon><Document /></el-icon> 加载示例
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 术语分析模式 -->
    <div v-if="analysisMode === 'term'" class="analysis-results">
      <!-- 分析概览 -->
      <el-card class="overview-card" v-if="analysisResult">
        <template #header>
          <span>分析概览</span>
        </template>
        <div class="overview-stats">
          <div class="stat-item">
            <div class="stat-value">{{ analysisResult.totalTerms }}</div>
            <div class="stat-label">术语总数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ analysisResult.professionalTerms }}</div>
            <div class="stat-label">专业术语</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ analysisResult.commonTerms }}</div>
            <div class="stat-label">普通词汇</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ analysisResult.complexity }}</div>
            <div class="stat-label">复杂度</div>
          </div>
        </div>
      </el-card>

      <!-- 术语列表 -->
      <el-card class="terms-card" v-if="analysisResult">
        <template #header>
          <div class="card-header">
            <span>术语详细列表</span>
            <el-input
              v-model="searchTerm"
              placeholder="搜索术语..."
              prefix-icon="Search"
              style="width: 200px"
              clearable
            />
          </div>
        </template>

        <div class="terms-list">
          <div
            v-for="term in filteredTerms"
            :key="term.id"
            class="term-item"
            :class="term.type"
          >
            <div class="term-header">
              <div class="term-main">
                <el-tag
                  :type="term.type === 'professional' ? 'danger' : 'info'"
                  size="small"
                  class="term-type-tag"
                >
                  {{ term.type === 'professional' ? '专业术语' : '普通词汇' }}
                </el-tag>
                <h3 class="term-text">{{ term.original }}</h3>
              </div>
              <div class="term-weight">
                <el-rate
                  v-model="term.weight"
                  disabled
                  show-score
                  text-color="#ff9900"
                  score-template="{value}"
                ></el-rate>
              </div>
            </div>

            <div class="term-content">
              <div class="term-section">
                <div class="section-label">
                  <el-icon><Reading /></el-icon> 翻译对照
                </div>
                <div class="term-translations">
                  <div
                    v-for="trans in term.translations"
                    :key="trans.lang"
                    class="translation-item"
                  >
                    <span class="trans-lang">{{ languageMap[trans.lang] }}</span>
                    <span class="trans-text">{{ trans.text }}</span>
                  </div>
                </div>
              </div>

              <div class="term-section">
                <div class="section-label">
                  <el-icon><Notebook /></el-icon> 专业注释
                </div>
                <div class="term-notes">
                  <el-alert
                    :title="term.notes"
                    type="info"
                    :closable="false"
                    class="note-alert"
                  />
                </div>
              </div>

              <div class="term-section" v-if="term.examples && term.examples.length > 0">
                <div class="section-label">
                  <el-icon><ChatDotRound /></el-icon> 使用示例
                </div>
                <div class="term-examples">
                  <div
                    v-for="(example, index) in term.examples"
                    :key="index"
                    class="example-item"
                  >
                    <span class="example-mark">•</span>
                    <span class="example-text">{{ example }}</span>
                  </div>
                </div>
              </div>

              <div class="term-section">
                <div class="section-label">
                  <el-icon><DataLine /></el-icon> 统计信息
                </div>
                <div class="term-stats">
                  <div class="stat-row">
                    <span class="stat-label-small">出现频次:</span>
                    <span class="stat-value-small">{{ term.frequency }}</span>
                  </div>
                  <div class="stat-row">
                    <span class="stat-label-small">相关词汇:</span>
                    <span class="stat-value-small">{{ term.relatedTerms?.join('、') || '无' }}</span>
                  </div>
                  <div class="stat-row">
                    <span class="stat-label-small">领域分类:</span>
                    <el-tag
                      v-for="category in term.categories"
                      :key="category"
                      size="small"
                      type="warning"
                      class="category-tag"
                    >
                      {{ category }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 对照翻译模式 -->
    <div v-if="analysisMode === 'compare'" class="analysis-results">
      <el-card class="compare-card" v-if="analysisResult">
        <template #header>
          <div class="card-header">
            <span>中英文对照</span>
            <el-button text @click="toggleCompare">
              <el-icon>
                <component :is="showSideBySide ? 'Top' : 'Bottom'" />
              </el-icon>
              {{ showSideBySide ? '上下对照' : '左右对照' }}
            </el-button>
          </div>
        </template>

        <div class="compare-container" :class="{ sideBySide: showSideBySide }">
          <div class="compare-section">
            <div class="compare-header">
              <span class="compare-lang">{{ inputLang === 'zh' ? '中文' : 'English' }}</span>
              <el-button text icon="CopyDocument" @click="copyText(sourceCompare)">
                复制
              </el-button>
            </div>
            <div class="compare-content marked-text" v-html="sourceCompare"></div>
          </div>

          <div class="compare-divider" v-if="!showSideBySide">
            <el-icon><Position /></el-icon>
          </div>

          <div class="compare-section">
            <div class="compare-header">
              <span class="compare-lang">{{ inputLang === 'zh' ? 'English' : '中文' }}</span>
              <el-button text icon="CopyDocument" @click="copyText(targetCompare)">
                复制
              </el-button>
            </div>
            <div class="compare-content marked-text" v-html="targetCompare"></div>
          </div>
        </div>

        <!-- 术语图例 -->
        <div class="legend-section">
          <div class="legend-title">术语标记说明</div>
          <div class="legend-items">
            <div class="legend-item">
              <span class="legend-mark professional"></span>
              <span>专业术语</span>
            </div>
            <div class="legend-item">
              <span class="legend-mark common"></span>
              <span>普通词汇</span>
            </div>
            <div class="legend-item">
              <span class="legend-mark high"></span>
              <span>高权重术语</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 权重评估模式 -->
    <div v-if="analysisMode === 'weight'" class="analysis-results">
      <el-card class="weight-card" v-if="analysisResult">
        <template #header>
          <span>权重评估分析</span>
        </template>

        <!-- 权重分布图 -->
        <div class="weight-charts">
          <div class="chart-section">
            <h3 class="chart-title">权重分布</h3>
            <div class="weight-bars">
              <div
                v-for="term in highWeightTerms"
                :key="term.id"
                class="weight-bar-item"
              >
                <div class="bar-label">{{ term.original }}</div>
                <div class="bar-track">
                  <div
                    class="bar-fill"
                    :style="{ width: `${term.weight * 20}%` }"
                  ></div>
                </div>
                <div class="bar-value">{{ term.weight }}</div>
              </div>
            </div>
          </div>

          <div class="chart-section">
            <h3 class="chart-title">术语类型分布</h3>
            <div class="type-pie">
              <div class="pie-chart">
                <div
                  class="pie-segment professional"
                  :style="{
                    background: `conic-gradient(#f56c6c 0% ${professionalPercent}%, #909399 ${professionalPercent}% 100%)`
                  }"
                ></div>
              </div>
              <div class="pie-legend">
                <div class="pie-legend-item">
                  <span class="legend-dot professional"></span>
                  <span>专业术语 ({{ professionalPercent }}%)</span>
                </div>
                <div class="pie-legend-item">
                  <span class="legend-dot common"></span>
                  <span>普通词汇 ({{ 100 - professionalPercent }}%)</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 权重详细列表 -->
        <div class="weight-table">
          <h3 class="table-title">详细权重列表</h3>
          <el-table :data="analysisResult.terms" stripe>
            <el-table-column prop="original" label="术语" width="200"></el-table-column>
            <el-table-column label="类型" width="120">
              <template #default="{ row }">
                <el-tag
                  :type="row.type === 'professional' ? 'danger' : 'info'"
                  size="small"
                >
                  {{ row.type === 'professional' ? '专业术语' : '普通词汇' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="weight" label="权重" width="120" align="center">
              <template #default="{ row }">
                <el-rate v-model="row.weight" disabled show-score score-template="{value}"></el-rate>
              </template>
            </el-table-column>
            <el-table-column prop="frequency" label="频次" width="100" align="center"></el-table-column>
            <el-table-column label="翻译" min-width="200">
              <template #default="{ row }">
                <el-tag
                  v-for="trans in row.translations"
                  :key="trans.lang"
                  size="small"
                  type="success"
                  class="trans-tag"
                >
                  {{ trans.text }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="注释" min-width="250" show-overflow-tooltip>
              <template #default="{ row }">
                {{ row.notes }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>
    </div>

    <!-- 高权重术语弹窗 -->
    <el-dialog
      v-model="termDetailVisible"
      title="术语详情"
      width="600px"
    >
      <div v-if="selectedTerm" class="term-detail">
        <div class="detail-header">
          <el-tag
            :type="selectedTerm.type === 'professional' ? 'danger' : 'info'"
            size="large"
          >
            {{ selectedTerm.type === 'professional' ? '专业术语' : '普通词汇' }}
          </el-tag>
          <h2 class="detail-term">{{ selectedTerm.original }}</h2>
          <el-rate v-model="selectedTerm.weight" disabled show-score score-template="权重: {value}"></el-rate>
        </div>

        <div class="detail-section">
          <div class="detail-title">
            <el-icon><Reading /></el-icon> 翻译对照
          </div>
          <div class="detail-translations">
            <div v-for="trans in selectedTerm.translations" :key="trans.lang" class="detail-trans-item">
              <span class="trans-lang-label">{{ languageMap[trans.lang] }}</span>
              <span class="trans-text-label">{{ trans.text }}</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <div class="detail-title">
            <el-icon><Notebook /></el-icon> 专业注释
          </div>
          <div class="detail-notes">{{ selectedTerm.notes }}</div>
        </div>

        <div class="detail-section" v-if="selectedTerm.examples && selectedTerm.examples.length">
          <div class="detail-title">
            <el-icon><ChatDotRound /></el-icon> 使用示例
          </div>
          <div class="detail-examples">
            <div v-for="(ex, i) in selectedTerm.examples" :key="i" class="detail-example">
              {{ ex }}
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="termDetailVisible = false">关闭</el-button>
        <el-button type="primary" @click="copyTermDetail">复制详情</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Delete, Document, DataAnalysis, Search, Reading,
  Notebook, ChatDotRound, DataLine, Top, Bottom,
  Position, CopyDocument
} from '@element-plus/icons-vue'

// 分析模式
const analysisMode = ref('term')

// 输入语言
const inputLang = ref('zh')

// 输入文本
const inputText = ref('')

// 分析状态
const analyzing = ref(false)

// 搜索术语
const searchTerm = ref('')

// 对照模式
const showSideBySide = ref(false)

// 术语详情弹窗
const termDetailVisible = ref(false)
const selectedTerm = ref<any>(null)

// 语言映射
const languageMap: { [key: string]: string } = {
  zh: '中文',
  en: '英语',
  ja: '日语'
}

// 分析结果
const analysisResult = ref<any>(null)

// 机械零部件示例文本
const exampleTexts = {
  zh: `本产品采用高精度数控机床加工，主要零件包括主轴箱、齿轮箱、液压系统和传动装置。主轴箱采用高强度铸铁材料，经过精密加工和热处理工艺。齿轮箱内配置多级减速齿轮，传动效率达到98%以上。液压系统采用伺服比例阀控制，响应速度快、精度高。传动装置采用链条传动，具有结构紧凑、传动平稳的特点。

该设备适用于重型机械加工，可以满足各种复杂零件的加工需求。控制系统采用西门子PLC，支持多种编程语言和通信协议。`,
  en: `This product is manufactured using high-precision CNC machine tools, with main components including the spindle box, gearbox, hydraulic system, and transmission device. The spindle box is made of high-strength cast iron, undergoing precision machining and heat treatment processes. The gearbox is equipped with multi-stage reduction gears, achieving transmission efficiency of over 98%. The hydraulic system uses servo proportional valve control, providing fast response and high precision. The transmission device uses chain drive, featuring compact structure and smooth transmission.

This equipment is suitable for heavy-duty machining and can meet the processing requirements of various complex parts. The control system uses Siemens PLC, supporting multiple programming languages and communication protocols.`
}

// 术语数据库
const termDatabase: { [key: string]: any[] } = {
  zh: [
    {
      original: '数控机床',
      type: 'professional',
      weight: 5,
      translations: [
        { lang: 'en', text: 'CNC machine tool' },
        { lang: 'ja', text: 'NC工作機械' }
      ],
      notes: '数控机床是数字控制机床的简称，是一种装有程序控制系统的自动化机床',
      examples: ['本产品采用高精度数控机床加工', '数控机床能提高生产效率'],
      frequency: 2,
      categories: ['机械制造', '加工设备']
    },
    {
      original: '主轴箱',
      type: 'professional',
      weight: 4.5,
      translations: [
        { lang: 'en', text: 'spindle box' },
        { lang: 'ja', text: '主軸箱' }
      ],
      notes: '主轴箱是机床的重要部件，用于安装主轴和传动齿轮',
      examples: ['主轴箱采用高强度铸铁材料'],
      frequency: 2,
      categories: ['机床部件', '传动系统']
    },
    {
      original: '齿轮箱',
      type: 'professional',
      weight: 4.5,
      translations: [
        { lang: 'en', text: 'gearbox' },
        { lang: 'ja', text: '歯車箱' }
      ],
      notes: '齿轮箱是用于传递动力和改变转速的装置',
      examples: ['齿轮箱内配置多级减速齿轮'],
      frequency: 1,
      categories: ['传动系统', '机械部件']
    },
    {
      original: '液压系统',
      type: 'professional',
      weight: 4.5,
      translations: [
        { lang: 'en', text: 'hydraulic system' },
        { lang: 'ja', text: '油圧システム' }
      ],
      notes: '利用液体压力能进行能量传递和控制的系统',
      examples: ['液压系统采用伺服比例阀控制'],
      frequency: 1,
      categories: ['液压技术', '控制系统']
    },
    {
      original: '传动装置',
      type: 'professional',
      weight: 4,
      translations: [
        { lang: 'en', text: 'transmission device' },
        { lang: 'ja', text: '伝動装置' }
      ],
      notes: '用于传递动力和运动的机械装置',
      examples: ['传动装置采用链条传动'],
      frequency: 1,
      categories: ['机械传动', '动力系统']
    },
    {
      original: '铸铁',
      type: 'professional',
      weight: 3.5,
      translations: [
        { lang: 'en', text: 'cast iron' },
        { lang: 'ja', text: '鋳鉄' }
      ],
      notes: '一种含碳量较高的铁碳合金，具有良好的铸造性能',
      examples: ['主轴箱采用高强度铸铁材料'],
      frequency: 1,
      categories: ['材料', '金属材料']
    },
    {
      original: '热处理',
      type: 'professional',
      weight: 4,
      translations: [
        { lang: 'en', text: 'heat treatment' },
        { lang: 'ja', text: '熱処理' }
      ],
      notes: '通过加热、保温和冷却工艺，改变材料性能的工艺方法',
      examples: ['经过精密加工和热处理工艺'],
      frequency: 1,
      categories: ['工艺技术', '材料处理']
    },
    {
      original: '减速齿轮',
      type: 'professional',
      weight: 4,
      translations: [
        { lang: 'en', text: 'reduction gear' },
        { lang: 'ja', text: '減速歯車' }
      ],
      notes: '用于降低转速、增加扭矩的齿轮',
      examples: ['齿轮箱内配置多级减速齿轮'],
      frequency: 1,
      categories: ['齿轮传动', '机械部件']
    },
    {
      original: '伺服比例阀',
      type: 'professional',
      weight: 5,
      translations: [
        { lang: 'en', text: 'servo proportional valve' },
        { lang: 'ja', text: 'サーボ比例弁' }
      ],
      notes: '能够根据输入信号按比例控制流量或压力的液压控制阀',
      examples: ['液压系统采用伺服比例阀控制'],
      frequency: 1,
      categories: ['液压元件', '控制系统']
    },
    {
      original: '链条传动',
      type: 'professional',
      weight: 3.5,
      translations: [
        { lang: 'en', text: 'chain drive' },
        { lang: 'ja', text: 'チェーンドライブ' }
      ],
      notes: '利用链条和链轮传递动力的传动方式',
      examples: ['传动装置采用链条传动'],
      frequency: 1,
      categories: ['传动方式', '机械设计']
    },
    {
      original: 'PLC',
      type: 'professional',
      weight: 4.5,
      translations: [
        { lang: 'en', text: 'Programmable Logic Controller' },
        { lang: 'ja', text: 'プログラマブルロジックコントローラ' }
      ],
      notes: '可编程逻辑控制器，一种用于工业自动化控制的电子装置',
      examples: ['控制系统采用西门子PLC'],
      frequency: 1,
      categories: ['自动化', '控制系统']
    }
  ],
  en: [
    {
      original: 'CNC machine tool',
      type: 'professional',
      weight: 5,
      translations: [
        { lang: 'zh', text: '数控机床' },
        { lang: 'ja', text: 'NC工作機械' }
      ],
      notes: 'Computer Numerical Control machine tool, an automated machine tool with program control system',
      examples: ['This product is manufactured using high-precision CNC machine tools'],
      frequency: 1,
      categories: ['Manufacturing', 'Machining Equipment']
    },
    {
      original: 'spindle box',
      type: 'professional',
      weight: 4.5,
      translations: [
        { lang: 'zh', text: '主轴箱' },
        { lang: 'ja', text: '主軸箱' }
      ],
      notes: 'Important component of machine tool, used to install spindle and transmission gears',
      examples: ['The spindle box is made of high-strength cast iron'],
      frequency: 1,
      categories: ['Machine Tool Component', 'Transmission System']
    },
    {
      original: 'gearbox',
      type: 'professional',
      weight: 4.5,
      translations: [
        { lang: 'zh', text: '齿轮箱' },
        { lang: 'ja', text: '歯車箱' }
      ],
      notes: 'Device used for power transmission and speed change',
      examples: ['The gearbox is equipped with multi-stage reduction gears'],
      frequency: 1,
      categories: ['Transmission System', 'Mechanical Component']
    },
    {
      original: 'hydraulic system',
      type: 'professional',
      weight: 4.5,
      translations: [
        { lang: 'zh', text: '液压系统' },
        { lang: 'ja', text: '油圧システム' }
      ],
      notes: 'System using fluid pressure for energy transmission and control',
      examples: ['The hydraulic system uses servo proportional valve control'],
      frequency: 1,
      categories: ['Hydraulic Technology', 'Control System']
    }
  ]
}

// 过滤后的术语列表
const filteredTerms = computed(() => {
  if (!analysisResult.value) return []

  let terms = analysisResult.value.terms

  if (searchTerm.value) {
    const keyword = searchTerm.value.toLowerCase()
    terms = terms.filter((term: any) =>
      term.original.toLowerCase().includes(keyword) ||
      term.translations.some((t: any) => t.text.toLowerCase().includes(keyword)) ||
      term.notes.toLowerCase().includes(keyword)
    )
  }

  // 按权重排序
  return terms.sort((a: any, b: any) => b.weight - a.weight)
})

// 高权重术语
const highWeightTerms = computed(() => {
  if (!analysisResult.value) return []
  return [...analysisResult.value.terms]
    .sort((a: any, b: any) => b.weight - a.weight)
    .slice(0, 8)
})

// 专业术语百分比
const professionalPercent = computed(() => {
  if (!analysisResult.value) return 0
  const total = analysisResult.value.terms.length
  const professional = analysisResult.value.terms.filter((t: any) => t.type === 'professional').length
  return Math.round((professional / total) * 100)
})

// 源语言对照文本
const sourceCompare = computed(() => {
  if (!analysisResult.value || !inputText.value) return ''
  return markTerms(inputText.value, analysisResult.value.terms)
})

// 目标语言对照文本
const targetCompare = computed(() => {
  if (!analysisResult.value) return ''
  const targetLangCode = inputLang.value === 'zh' ? 'en' : 'zh'
  let translatedText = inputText.value

  // 简单替换翻译
  analysisResult.value.terms.forEach((term: any) => {
    const trans = term.translations.find((t: any) => t.lang === targetLangCode)
    if (trans) {
      translatedText = translatedText.replace(new RegExp(term.original, 'g'), trans.text)
    }
  })

  return markTerms(translatedText, analysisResult.value.terms, true)
})

// 标记术语
const markTerms = (text: string, terms: any[], isTarget = false) => {
  let markedText = text

  terms.forEach(term => {
    const searchTerm = isTarget
      ? term.translations.find((t: any) => t.lang === (inputLang.value === 'zh' ? 'en' : 'zh'))?.text
      : term.original

    if (searchTerm) {
      const markerClass = term.type === 'professional'
        ? `term-mark professional ${term.weight >= 4.5 ? 'high' : ''}`
        : 'term-mark common'
      markedText = markedText.replace(
        new RegExp(searchTerm, 'g'),
        `<span class="${markerClass}">${searchTerm}</span>`
      )
    }
  })

  return markedText
}

// 分析功能
const analyze = async () => {
  if (!inputText.value.trim()) {
    ElMessage.warning('请输入需要分析的文本')
    return
  }

  analyzing.value = true

  // 模拟分析延迟
  await new Promise(resolve => setTimeout(resolve, 1500))

  // 根据语言选择术语库
  const terms = termDatabase[inputLang.value] || []

  // 计算文本统计
  const professionalTerms = terms.filter(t => t.type === 'professional').length
  const commonTerms = terms.filter(t => t.type === 'common').length
  const complexity = terms.length > 8 ? '高' : terms.length > 4 ? '中' : '低'

  analysisResult.value = {
    totalTerms: terms.length,
    professionalTerms,
    commonTerms,
    complexity,
    terms: terms.map((t, i) => ({ ...t, id: i }))
  }

  analyzing.value = false
  ElMessage.success('分析完成')
}

// 加载示例
const loadExample = () => {
  inputText.value = exampleTexts[inputLang.value]
  ElMessage.success('示例文本已加载')
}

// 清空输入
const clearInput = () => {
  inputText.value = ''
  analysisResult.value = null
}

// 切换对照模式
const toggleCompare = () => {
  showSideBySide.value = !showSideBySide.value
}

// 复制文本
const copyText = (text: string) => {
  // 移除HTML标签
  const plainText = text.replace(/<[^>]*>/g, '')
  navigator.clipboard.writeText(plainText)
  ElMessage.success('已复制到剪贴板')
}

// 复制术语详情
const copyTermDetail = () => {
  if (!selectedTerm.value) return

  let detail = `术语: ${selectedTerm.value.original}\n`
  detail += `类型: ${selectedTerm.value.type === 'professional' ? '专业术语' : '普通词汇'}\n`
  detail += `权重: ${selectedTerm.value.weight}\n\n`
  detail += '翻译对照:\n'
  selectedTerm.value.translations.forEach((t: any) => {
    detail += `  ${languageMap[t.lang]}: ${t.text}\n`
  })
  detail += `\n注释:\n${selectedTerm.value.notes}`

  navigator.clipboard.writeText(detail)
  ElMessage.success('详情已复制')
}

// 查看术语详情
const viewTermDetail = (term: any) => {
  selectedTerm.value = term
  termDetailVisible.value = true
}
</script>

<style scoped>
.term-analysis-container {
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

/* 输入区域 */
.input-section {
  max-width: 1200px;
  margin: 0 auto 24px;
}

.input-card {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.analysis-input {
  font-size: 16px;
  line-height: 1.8;
}

:deep(.analysis-input .el-textarea__inner) {
  border: none;
  box-shadow: none;
  font-family: 'Courier New', monospace;
}

.input-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e5e5e5;
}

/* 分析结果区域 */
.analysis-results {
  max-width: 1200px;
  margin: 0 auto;
}

/* 概览卡片 */
.overview-card {
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.overview-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

/* 术语列表 */
.terms-card {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.terms-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.term-item {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.2s;
  cursor: pointer;
  border-left: 4px solid #409eff;
}

.term-item:hover {
  background: #e8eef5;
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.term-item.professional {
  border-left-color: #f56c6c;
}

.term-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e5e5;
}

.term-main {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.term-text {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  color: #303133;
}

.term-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.term-section {
  background: white;
  padding: 12px;
  border-radius: 6px;
}

.section-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
}

.term-translations {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.translation-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 12px;
  background: #f0f9ff;
  border-radius: 4px;
}

.trans-lang {
  font-weight: 500;
  color: #409eff;
  min-width: 60px;
}

.trans-text {
  color: #606266;
  flex: 1;
}

.term-examples {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.example-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px;
  background: #f9f0f0;
  border-radius: 4px;
}

.example-mark {
  color: #f56c6c;
  font-weight: bold;
}

.example-text {
  color: #606266;
  flex: 1;
}

.term-stats {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stat-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.stat-label-small {
  color: #909399;
  min-width: 80px;
}

.stat-value-small {
  color: #303133;
  font-weight: 500;
}

.category-tag {
  margin-right: 6px;
}

/* 对照翻译 */
.compare-card {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.compare-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.compare-container.sideBySide {
  grid-template-columns: 1fr;
  gap: 12px;
}

.compare-section {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 20px;
}

.compare-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e5e5e5;
}

.compare-lang {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.compare-content {
  font-size: 15px;
  line-height: 2;
  color: #606266;
  white-space: pre-wrap;
}

.compare-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #409eff;
  font-size: 24px;
}

/* 标记样式 */
.marked-text :deep(.term-mark) {
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.marked-text :deep(.term-mark.professional) {
  background: #fef0f0;
  color: #f56c6c;
  border: 1px solid #f56c6c;
}

.marked-text :deep(.term-mark.professional.high) {
  background: #f56c6c;
  color: white;
  box-shadow: 0 2px 8px rgba(245, 108, 108, 0.3);
}

.marked-text :deep(.term-mark.common) {
  background: #f0f9ff;
  color: #409eff;
  border: 1px solid #409eff;
}

.marked-text :deep(.term-mark:hover) {
  transform: scale(1.05);
}

/* 图例 */
.legend-section {
  margin-top: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.legend-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 12px;
}

.legend-items {
  display: flex;
  gap: 24px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #606266;
}

.legend-mark {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 1px solid;
}

.legend-mark.professional {
  background: #fef0f0;
  border-color: #f56c6c;
}

.legend-mark.common {
  background: #f0f9ff;
  border-color: #409eff;
}

.legend-mark.high {
  background: #f56c6c;
  border-color: #f56c6c;
}

/* 权重分析 */
.weight-card {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.weight-charts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.chart-section {
  background: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
}

.chart-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin: 0 0 16px 0;
}

.weight-bars {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.weight-bar-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bar-label {
  width: 100px;
  font-size: 13px;
  color: #606266;
}

.bar-track {
  flex: 1;
  height: 24px;
  background: #e5e5e5;
  border-radius: 12px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #409eff 0%, #67c23a 50%, #f56c6c 100%);
  border-radius: 12px;
  transition: width 0.5s ease;
}

.bar-value {
  width: 40px;
  text-align: right;
  font-weight: 600;
  color: #303133;
}

.type-pie {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.pie-chart {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  position: relative;
}

.pie-legend {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.pie-legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #606266;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-dot.professional {
  background: #f56c6c;
}

.legend-dot.common {
  background: #909399;
}

/* 权重表格 */
.weight-table {
  margin-top: 20px;
}

.table-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin: 0 0 16px 0;
}

.trans-tag {
  margin-right: 4px;
  margin-bottom: 4px;
}

/* 术语详情弹窗 */
.term-detail {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-header {
  text-align: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
}

.detail-term {
  font-size: 24px;
  font-weight: 600;
  margin: 12px 0;
  color: white;
}

.detail-section {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
}

.detail-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 12px;
}

.detail-translations {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-trans-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  background: white;
  border-radius: 4px;
}

.trans-lang-label {
  font-weight: 500;
  color: #409eff;
  min-width: 80px;
}

.trans-text-label {
  color: #303133;
  flex: 1;
}

.detail-notes {
  color: #606266;
  line-height: 1.8;
  padding: 12px;
  background: white;
  border-radius: 4px;
}

.detail-examples {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-example {
  padding: 10px;
  background: white;
  border-radius: 4px;
  color: #606266;
  border-left: 3px solid #f56c6c;
}

/* 响应式 */
@media (max-width: 768px) {
  .term-analysis-container {
    padding: 16px;
  }

  .overview-stats {
    grid-template-columns: repeat(2, 1fr);
  }

  .compare-container {
    grid-template-columns: 1fr;
  }

  .weight-charts {
    grid-template-columns: 1fr;
  }
}
</style>
