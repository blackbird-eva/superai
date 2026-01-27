<template>
  <div class="term-analysis-container">
    <!-- 头部区域 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">中英文术语对照分析系统</h1>
        <p class="page-subtitle">专业术语智能识别 · 中英文对照表 · 权重评估分析</p>
      </div>
    </div>

    <!-- 功能模式切换 -->
    <div class="mode-tabs">
      <el-radio-group v-model="analysisMode">
        <el-radio-button label="compare">对照翻译</el-radio-button>
        <el-radio-button label="term">术语分析</el-radio-button>
        <el-radio-button label="weight">权重评估</el-radio-button>
        <el-radio-button label="image">图片分析</el-radio-button>
        <el-radio-button label="document">文档分析</el-radio-button>
      </el-radio-group>
      <el-button v-if="!showExampleSection && ['term', 'compare', 'weight'].includes(analysisMode)" text @click="showExampleSection = true" class="example-toggle">
        <el-icon><Document /></el-icon> 显示示例
      </el-button>
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
          <div class="example-actions">
            <el-button v-if="showExampleSection" text @click="showExampleSection = false">
              <el-icon><Hide /></el-icon> 隐藏示例
            </el-button>
            <el-button v-if="showExampleSection" text @click="loadExample">
              <el-icon><Document /></el-icon> 加载示例
            </el-button>
          </div>
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

    <!-- 图片分析模式 -->
    <div v-if="analysisMode === 'image'" class="analysis-results">
      <el-card class="image-analysis-card">
        <template #header>
          <span>图片术语分析</span>
        </template>

        <div class="image-analysis-container">
          <!-- 图片上传区域 -->
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
              <el-button type="primary" @click="analyzeImage" :loading="analyzing">
                <el-icon><DataAnalysis /></el-icon> 开始分析
              </el-button>
              <el-button @click="clearImage">重新上传</el-button>
            </div>
          </div>

          <!-- 分析结果 -->
          <div class="analysis-result" v-if="imageAnalysisResult">
            <div class="result-header">
              <h3>术语分析结果</h3>
              <el-button text icon="CopyDocument" @click="copyText(imageAnalysisResult)">
                复制
              </el-button>
            </div>
            <div class="result-content">
              <div v-html="imageAnalysisResult" class="result-text"></div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 文档分析模式 -->
    <div v-if="analysisMode === 'document'" class="analysis-results">
      <el-card class="document-analysis-card">
        <template #header>
          <span>文档术语分析</span>
        </template>

        <div class="document-analysis-container">
          <!-- 文档上传区域 -->
          <div class="upload-area">
            <el-upload
              class="document-uploader"
              :show-file-list="true"
              :before-upload="beforeDocUpload"
              :on-remove="handleDocRemove"
              :file-list="docFileList"
              :drag="true"
              accept=".pdf,.doc,.docx,.txt,.xls,.xlsx"
              :limit="1"
            >
              <div v-if="docFileList.length === 0" class="upload-placeholder">
                <el-icon class="upload-icon"><Upload /></el-icon>
                <div class="upload-text">拖拽文档到此处或点击上传</div>
                <div class="upload-hint">支持 PDF、Word、TXT、Excel 格式，大小不超过 50MB</div>
              </div>
              <el-button v-else type="primary" icon="Upload">
                重新上传
              </el-button>
            </el-upload>

            <div v-if="docFileList.length > 0" class="doc-actions">
              <el-button type="primary" @click="analyzeDocument" :loading="analyzing">
                <el-icon><DataAnalysis /></el-icon> 开始分析
              </el-button>
            </div>
          </div>

          <!-- 分析结果 -->
          <div class="analysis-result" v-if="docAnalysisResult">
            <div class="result-header">
              <h3>文档术语分析结果</h3>
              <div class="result-actions">
                <el-button type="primary" icon="Download" @click="exportDocumentResult">
                  导出结果
                </el-button>
                <el-button icon="View" @click="viewDocumentDetail">
                  查看详情
                </el-button>
              </div>
            </div>
            <div class="result-content">
              <el-alert
                title="分析完成"
                type="success"
                :description="`文档 ${docFileList[0]?.name} 已成功分析，发现 ${docAnalysisResult.totalTerms} 个术语`"
                :closable="false"
              />

              <!-- 术语对照表 -->
              <div class="document-terms-table">
                <h4>中英文术语对照表</h4>
                <el-table :data="docAnalysisResult.terms" stripe class="compare-table" border>
                  <el-table-column label="序号" type="index" width="70" align="center" fixed></el-table-column>
                  <el-table-column label="术语类型" width="130" align="center">
                    <template #default="{ row }">
                      <el-tag
                        :type="row.type === 'professional' ? 'danger' : 'info'"
                        size="large"
                        effect="dark"
                      >
                        {{ row.type === 'professional' ? '专业术语' : '普通词汇' }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="中文" min-width="180">
                    <template #default="{ row }">
                      <span class="primary-text">{{ row.zhTranslation }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column label="English" min-width="200">
                    <template #default="{ row }">
                      <span class="english-text">{{ row.enTranslation }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column label="权重" width="100" align="center">
                    <template #default="{ row }">
                      {{ row.weight }}
                    </template>
                  </el-table-column>
                  <el-table-column label="注释" min-width="250" show-overflow-tooltip>
                    <template #default="{ row }">
                      <span class="notes-text">{{ row.notes }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column label="频次" width="100" align="center">
                    <template #default="{ row }">
                      <el-tag type="warning" size="small">{{ row.frequency }} 次</el-tag>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 常驻对照翻译表 - 始终显示在下方 -->
    <div class="permanent-compare-section">
      <el-card class="compare-card permanent-card">
        <template #header>
          <div class="card-header">
            <span>
              <el-icon class="header-icon"><Document /></el-icon>
              中英文术语对照表
              <el-tag v-if="!analysisResult" type="success" size="small" class="random-badge">随机展示</el-tag>
            </span>
            <div class="header-controls">
              <el-input
                v-model="searchTerm"
                placeholder="搜索术语..."
                prefix-icon="Search"
                style="width: 180px"
                clearable
                size="small"
              />
              <el-select v-model="filterType" placeholder="筛选类型" style="width: 100px" clearable size="small">
                <el-option label="专业术语" value="professional"></el-option>
                <el-option label="普通词汇" value="common"></el-option>
              </el-select>
              <el-tag type="primary" size="default">
                共 {{ filteredTableTerms.length }} 个术语
              </el-tag>
              <el-button
                @click="refreshRandomTerms"
                v-if="!analysisResult"
                :icon="Refresh"
                size="small"
                circle
                :loading="loadingTerms"
                :title="loadedTerms.length > 0 ? '刷新术语数据' : '刷新随机术语'"
              ></el-button>
              <el-button
                type="primary"
                @click="exportTable"
                v-if="analysisResult"
                :icon="Download"
                size="small"
              >
                导出CSV
              </el-button>
            </div>
          </div>
        </template>

        <!-- 闲置提示 -->
        <el-alert
          v-if="!analysisResult"
          :title="loadedTerms.length > 0 ? '已加载翻译字典数据' : '当前展示随机专业术语示例'"
          type="info"
          :closable="false"
          class="idle-alert"
        >
          <template #default>
            <p v-if="loadedTerms.length > 0">💡 当前展示从后端加载的翻译字典数据（{{ loadedTerms.length }} 条）</p>
            <p v-else>💡 输入文本并点击"开始分析"后，将显示基于您文本的术语对照表</p>
            <p>🔄 点击右上角刷新按钮可以{{ loadedTerms.length > 0 ? '重新加载数据' : '查看更多示例术语' }}</p>
            <p v-if="loadedTerms.length > 0">📚 展示数据库中的中英文术语对照</p>
            <p v-else>📚 随机展示机械、自动化、液压等领域的常见专业术语</p>
          </template>
        </el-alert>

        <!-- 快捷筛选 -->
        <div class="quick-filters" v-if="displayTableTerms.length > 0">
          <el-button
            :type="filterType === '' ? 'primary' : 'default'"
            size="small"
            @click="filterType = ''"
          >
            全部 ({{ displayTableTerms.length }})
          </el-button>
          <el-button
            :type="filterType === 'professional' ? 'danger' : 'default'"
            size="small"
            @click="filterType = 'professional'"
          >
            专业术语 ({{ professionalCount }})
          </el-button>
          <el-button
            :type="filterType === 'common' ? 'info' : 'default'"
            size="small"
            @click="filterType = 'common'"
          >
            普通词汇 ({{ commonCount }})
          </el-button>
          <el-button
            :type="showHighWeightOnly ? 'warning' : 'default'"
            size="small"
            @click="showHighWeightOnly = !showHighWeightOnly"
          >
            高权重 (≥4)
          </el-button>
        </div>

        <!-- 对照表格 -->
        <el-table
          :data="filteredTableTerms"
          stripe
          class="compare-table"
          border
          :row-class-name="getRowClassName"
        >
          <el-table-column label="序号" type="index" width="60" align="center" fixed></el-table-column>
          <el-table-column label="类型" width="90" align="center">
            <template #default="{ row }">
              <el-tag
                :type="row.type === 'professional' ? 'danger' : 'info'"
                size="small"
                effect="dark"
              >
                {{ row.type === 'professional' ? '专业' : '普通' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="中文" min-width="150">
            <template #default="{ row }">
              <div class="table-cell source">
                <el-icon v-if="row.weight >= 4.5" class="star-icon"><StarFilled /></el-icon>
                <span class="term-text primary-text" :class="{ 'professional': row.type === 'professional' }">
                  {{ inputLang === 'zh' ? row.original : getTranslation(row, 'zh') }}
                </span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="English" min-width="180">
            <template #default="{ row }">
              <div class="table-cell translation">
                <span class="term-text english-text" :class="{ 'professional': row.type === 'professional' }">
                  {{ inputLang === 'en' ? row.original : getTranslation(row, 'en') }}
                </span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="权重" width="90" align="center">
            <template #default="{ row }">
              <el-rate
                v-model="row.weight"
                disabled
                show-score
                score-template="{value}"
                size="small"
              ></el-rate>
            </template>
          </el-table-column>
          <el-table-column label="专业注释" min-width="250" show-overflow-tooltip>
            <template #default="{ row }">
              <div class="table-cell notes">
                <el-icon class="note-icon"><Notebook /></el-icon>
                <span class="notes-text">{{ row.notes }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="频次" width="70" align="center">
            <template #default="{ row }">
              <el-tag :type="row.frequency >= 3 ? 'danger' : 'warning'" size="small">
                {{ row.frequency }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" align="center" fixed="right">
            <template #default="{ row }">
              <el-tooltip content="复制" placement="top">
                <el-button
                  type="primary"
                  link
                  :icon="CopyDocument"
                  @click="copyTerm(row)"
                  size="small"
                ></el-button>
              </el-tooltip>
              <el-tooltip content="详情" placement="top">
                <el-button
                  type="success"
                  link
                  :icon="View"
                  @click="viewTermDetail(row)"
                  size="small"
                ></el-button>
              </el-tooltip>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页组件 -->
        <el-pagination
          v-if="loadedTerms.length > 0 && !analysisResult"
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="handleCurrentChange"
          @size-change="handleSizeChange"
          class="pagination"
        />

        <!-- 统计摘要 -->
        <div class="compare-summary" v-if="analysisResult">
          <div class="summary-card">
            <div class="summary-icon">📊</div>
            <div class="summary-content">
              <div class="summary-label">术语总数</div>
              <div class="summary-value">{{ analysisResult.totalTerms }}</div>
            </div>
          </div>
          <div class="summary-card">
            <div class="summary-icon">🔴</div>
            <div class="summary-content">
              <div class="summary-label">专业术语</div>
              <div class="summary-value">{{ analysisResult.professionalTerms }}</div>
            </div>
          </div>
          <div class="summary-card">
            <div class="summary-icon">🔵</div>
            <div class="summary-content">
              <div class="summary-label">普通词汇</div>
              <div class="summary-value">{{ analysisResult.commonTerms }}</div>
            </div>
          </div>
          <div class="summary-card">
            <div class="summary-icon">⭐</div>
            <div class="summary-content">
              <div class="summary-label">复杂度</div>
              <div class="summary-value">{{ analysisResult.complexity }}</div>
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

    <!-- 图片分析模式 -->
    <div v-if="analysisMode === 'image'" class="analysis-results">
      <el-card class="image-analysis-card">
        <template #header>
          <span>图片术语分析</span>
        </template>

        <div class="image-analysis-container">
          <!-- 图片上传区域 -->
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
              <el-button type="primary" @click="analyzeImage" :loading="analyzing">
                <el-icon><DataAnalysis /></el-icon> 开始分析
              </el-button>
              <el-button @click="clearImage">重新上传</el-button>
            </div>
          </div>

          <!-- 分析结果 -->
          <div class="analysis-result" v-if="imageAnalysisResult">
            <div class="result-header">
              <h3>术语分析结果</h3>
              <el-button text icon="CopyDocument" @click="copyText(imageAnalysisResult)">
                复制
              </el-button>
            </div>
            <div class="result-content">
              <div v-html="imageAnalysisResult" class="result-text"></div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 文档分析模式 -->
    <div v-if="analysisMode === 'document'" class="analysis-results">
      <el-card class="document-analysis-card">
        <template #header>
          <span>文档术语分析</span>
        </template>

        <div class="document-analysis-container">
          <!-- 文档上传区域 -->
          <div class="upload-area">
            <el-upload
              class="document-uploader"
              :show-file-list="true"
              :before-upload="beforeDocUpload"
              :on-remove="handleDocRemove"
              :file-list="docFileList"
              :drag="true"
              accept=".pdf,.doc,.docx,.txt,.xls,.xlsx"
              :limit="1"
            >
              <div v-if="docFileList.length === 0" class="upload-placeholder">
                <el-icon class="upload-icon"><Upload /></el-icon>
                <div class="upload-text">拖拽文档到此处或点击上传</div>
                <div class="upload-hint">支持 PDF、Word、TXT、Excel 格式，大小不超过 50MB</div>
              </div>
              <el-button v-else type="primary" icon="Upload">
                重新上传
              </el-button>
            </el-upload>

            <div v-if="docFileList.length > 0" class="doc-actions">
              <el-button type="primary" @click="analyzeDocument" :loading="analyzing">
                <el-icon><DataAnalysis /></el-icon> 开始分析
              </el-button>
            </div>
          </div>

          <!-- 分析结果 -->
          <div class="analysis-result" v-if="docAnalysisResult">
            <div class="result-header">
              <h3>文档术语分析结果</h3>
              <div class="result-actions">
                <el-button type="primary" icon="Download" @click="exportDocumentResult">
                  导出结果
                </el-button>
                <el-button icon="View" @click="viewDocumentDetail">
                  查看详情
                </el-button>
              </div>
            </div>
            <div class="result-content">
              <el-alert
                title="分析完成"
                type="success"
                :description="`文档 ${docFileList[0]?.name} 已成功分析，发现 ${docAnalysisResult.totalTerms} 个术语`"
                :closable="false"
              />

              <!-- 术语对照表 -->
              <div class="document-terms-table">
                <h4>中英文术语对照表</h4>
                <el-table :data="docAnalysisResult.terms" stripe class="compare-table" border>
                  <el-table-column label="序号" type="index" width="70" align="center" fixed></el-table-column>
                  <el-table-column label="术语类型" width="130" align="center">
                    <template #default="{ row }">
                      <el-tag
                        :type="row.type === 'professional' ? 'danger' : 'info'"
                        size="large"
                        effect="dark"
                      >
                        {{ row.type === 'professional' ? '专业术语' : '普通词汇' }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="中文" min-width="180">
                    <template #default="{ row }">
                      <span class="primary-text">{{ row.zhTranslation }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column label="English" min-width="200">
                    <template #default="{ row }">
                      <span class="english-text">{{ row.enTranslation }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column label="权重" width="100" align="center">
                    <template #default="{ row }">
                      {{ row.weight }}
                    </template>
                  </el-table-column>
                  <el-table-column label="注释" min-width="250" show-overflow-tooltip>
                    <template #default="{ row }">
                      <span class="notes-text">{{ row.notes }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column label="频次" width="100" align="center">
                    <template #default="{ row }">
                      <el-tag type="warning" size="small">{{ row.frequency }} 次</el-tag>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>
          </div>
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
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { GetList } from './api'
import {
  Delete, Document, DataAnalysis, Search, Reading,
  Notebook, ChatDotRound, DataLine, Top, Bottom,
  Position, CopyDocument, Hide, Download, View, Picture, Upload, StarFilled, Refresh
} from '@element-plus/icons-vue'

// 分析模式
const analysisMode = ref('compare')

// 输入语言
const inputLang = ref('zh')

// 输入文本
const inputText = ref('')

// 分析状态
const analyzing = ref(false)

// 搜索术语
const searchTerm = ref('')

// 筛选类型
const filterType = ref('')
const showHighWeightOnly = ref(false)

// 随机术语
const randomTerms = ref<any[]>([])

// 从后端加载的术语列表
const loadedTerms = ref<any[]>([])
const loadingTerms = ref(false)

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 对照模式
const showSideBySide = ref(false)

// 目标语言（默认英语，但对照模式固定为中英文对照）
const targetLang = ref('en')

// 获取指定语言的翻译
const getTranslation = (term: any, lang: string) => {
  const trans = term.translations?.find((t: any) => t.lang === lang)
  return trans?.text || '暂无翻译'
}

// 是否显示示例区域
const showExampleSection = ref(false)

// 术语详情弹窗
const termDetailVisible = ref(false)
const selectedTerm = ref<any>(null)

// 图片分析相关
const imageUrl = ref('')
const imageAnalysisResult = ref('')

// 文档分析相关
const docFileList = ref<any[]>([])
const docAnalysisResult = ref<any>(null)

// 语言映射
const languageMap: { [key: string]: string } = {
  zh: '中文',
  en: '英语'
}

// 分析结果
const analysisResult = ref<any>(null)

// 从后端加载术语数据
const loadTerms = async () => {
  try {
    loadingTerms.value = true
    const response = await GetList({
      page: currentPage.value,
      size: pageSize.value,
      ordering: '-create_datetime'
    })

    if (response.code === 2000) {
      // 数据直接在 response.data 数组中
      const transdicts = response.data

      // 保存总数，从 response.total 获取
      total.value = response.total || 0

      // 转换数据格式，适配前端显示
      loadedTerms.value = transdicts.map((item: any) => ({
        id: item.id,
        original: item.cn,
        type: 'professional',  // 默认为专业术语
        weight: 4,  // 默认权重
        translations: [
          { lang: 'en', text: item.en }
        ],
        notes: item.note || item.infos || '',
        examples: [],
        frequency: 1,
        categories: [item.pcate_display || item.pcate || '通用'],
        pcate: item.pcate,
        cn: item.cn,
        en: item.en
      }))

      ElMessage.success(`成功加载第 ${currentPage.value} 页数据（${loadedTerms.value.length} 条），共 ${total.value} 条`)
    }
  } catch (error: any) {
    console.error('加载术语数据失败:', error)
    ElMessage.error(`加载失败: ${error.message || '未知错误'}`)
  } finally {
    loadingTerms.value = false
  }
}

// 组件挂载时加载术语
onMounted(() => {
  loadTerms()
})

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
        { lang: 'en', text: 'CNC machine tool' }
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
        { lang: 'en', text: 'spindle box' }
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
        { lang: 'en', text: 'gearbox' }
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
        { lang: 'en', text: 'hydraulic system' }
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
        { lang: 'en', text: 'transmission device' }
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
        { lang: 'en', text: 'cast iron' }
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
        { lang: 'en', text: 'heat treatment' }
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
        { lang: 'en', text: 'reduction gear' }
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
        { lang: 'en', text: 'servo proportional valve' }
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
        { lang: 'en', text: 'chain drive' }
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
        { lang: 'en', text: 'Programmable Logic Controller' }
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
        { lang: 'zh', text: '数控机床' }
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
        { lang: 'zh', text: '主轴箱' }
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
        { lang: 'zh', text: '齿轮箱' }
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
        { lang: 'zh', text: '液压系统' }
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

// 显示的表格术语（分析结果或随机术语）
const displayTableTerms = computed(() => {
  if (analysisResult.value) {
    return analysisResult.value.terms
  }
  // 优先使用从后端加载的数据，如果没有则使用随机数据
  return loadedTerms.value.length > 0 ? loadedTerms.value : randomTerms.value
})

// 过滤后的表格术语
const filteredTableTerms = computed(() => {
  // 闲置状态下，loadedTerms 已经是当前页的数据，不需要再次分页
  let terms = displayTableTerms.value

  // 按类型筛选
  if (filterType.value) {
    terms = terms.filter(t => t.type === filterType.value)
  }

  // 按权重筛选
  if (showHighWeightOnly.value) {
    terms = terms.filter(t => t.weight >= 4)
  }

  // 搜索关键词
  if (searchTerm.value) {
    const keyword = searchTerm.value.toLowerCase()
    terms = terms.filter((t: any) => {
      const original = t.original.toLowerCase()
      const zh = getTranslation(t, 'zh').toLowerCase()
      const en = getTranslation(t, 'en').toLowerCase()
      const notes = t.notes.toLowerCase()
      return original.includes(keyword) || zh.includes(keyword) || en.includes(keyword) || notes.includes(keyword)
    })
  }

  // 排序：专业术语优先，然后按权重和频次
  return terms.sort((a: any, b: any) => {
    if (a.type !== b.type) {
      return a.type === 'professional' ? -1 : 1
    }
    if (a.weight !== b.weight) {
      return b.weight - a.weight
    }
    return b.frequency - a.frequency
  })
})

// 统计计数
const professionalCount = computed(() => {
  return displayTableTerms.value.filter(t => t.type === 'professional').length
})

const commonCount = computed(() => {
  return displayTableTerms.value.filter(t => t.type === 'common').length
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

// 初始化随机术语
const initRandomTerms = () => {
  const terms = termDatabase[inputLang.value] || []
  // 随机选择8-12个术语
  const count = Math.floor(Math.random() * 5) + 8
  const shuffled = [...terms].sort(() => 0.5 - Math.random())
  randomTerms.value = shuffled.slice(0, count).map((t, i) => ({ ...t, id: i + 1000 }))
}

// 刷新随机术语
const refreshRandomTerms = () => {
  // 如果有后端加载的数据，重新加载数据
  if (loadedTerms.value.length > 0) {
    currentPage.value = 1  // 重置到第一页
    loadTerms()
  } else {
    initRandomTerms()
    ElMessage.success('已刷新随机术语示例')
  }
}

// 分页事件处理
const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadTerms()
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1  // 改变每页大小时重置到第一页
  loadTerms()
}

// 获取行样式
const getRowClassName = ({ row }: any) => {
  let className = ''
  if (row.type === 'professional') {
    className += 'professional-row '
  }
  if (row.weight >= 4.5) {
    className += 'high-weight-row '
  }
  return className.trim()
}

// 源语言对照文本
const sourceCompare = computed(() => {
  if (!analysisResult.value || !inputText.value) return ''
  return markTerms(inputText.value, analysisResult.value.terms)
})

// 目标语言对照文本
const targetCompare = computed(() => {
  if (!analysisResult.value) return ''
  let translatedText = inputText.value

  // 简单替换翻译（使用选择的目标语言）
  analysisResult.value.terms.forEach((term: any) => {
    const trans = term.translations.find((t: any) => t.lang === targetLang.value)
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

// 复制单个术语
const copyTerm = (term: any) => {
  const zhText = inputLang.value === 'zh' ? term.original : getTranslation(term, 'zh')
  const enText = inputLang.value === 'en' ? term.original : getTranslation(term, 'en')
  let text = `中文：${zhText}\nEnglish：${enText}\n类型：${term.type === 'professional' ? '专业术语' : '普通词汇'}`
  navigator.clipboard.writeText(text)
  ElMessage.success('已复制到剪贴板')
}

// 导出表格
const exportTable = () => {
  if (!analysisResult.value) return

  let csvContent = '\uFEFF' // BOM for UTF-8
  csvContent += `序号,术语类型,中文,English,权重评分,专业注释,出现频次\n`

  analysisResult.value.terms.forEach((term: any, index: number) => {
    const typeText = term.type === 'professional' ? '专业术语' : '普通词汇'
    const zhText = inputLang.value === 'zh' ? term.original : getTranslation(term, 'zh')
    const enText = inputLang.value === 'en' ? term.original : getTranslation(term, 'en')
    csvContent += `${index + 1},${typeText},"${zhText}","${enText}",${term.weight},"${term.notes}",${term.frequency}\n`
  })

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `中英文术语对照表_${Date.now()}.csv`
  link.click()
  URL.revokeObjectURL(url)
  ElMessage.success('表格导出成功')
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

// 图片上传成功
const handleImageSuccess = () => {
  ElMessage.success('图片上传成功')
}

// 图片分析
const analyzeImage = async () => {
  analyzing.value = true
  await new Promise(resolve => setTimeout(resolve, 2000))

  // 模拟图片分析结果
  const terms = termDatabase[inputLang.value] || []
  const resultText = terms.map((term: any) => {
    const zhText = inputLang.value === 'zh' ? term.original : getTranslation(term, 'zh')
    const enText = inputLang.value === 'en' ? term.original : getTranslation(term, 'en')
    return `<div class="image-term-item">
      <span class="term-original">${zhText}</span>
      <span class="term-arrow">↔</span>
      <span class="term-translation">${enText}</span>
      <span class="term-type">[${term.type === 'professional' ? '专业术语' : '普通词汇'}]</span>
    </div>`
  }).join('')

  imageAnalysisResult.value = `<div class="image-result-content">
    <h4>图片术语分析结果</h4>
    <p>从图片中识别出 ${terms.length} 个术语</p>
    <div class="terms-grid">${resultText}</div>
  </div>`

  analyzing.value = false
  ElMessage.success('图片分析完成')
}

// 清除图片
const clearImage = () => {
  imageUrl.value = ''
  imageAnalysisResult.value = ''
}

// 文档上传前验证
const beforeDocUpload = (file: File) => {
  const validTypes = ['.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx']
  const isValidType = validTypes.some(type => file.name.toLowerCase().endsWith(type))
  const isLt50M = file.size / 1024 / 1024 < 50

  if (!isValidType) {
    ElMessage.error('只能上传 PDF、Word、TXT、Excel 格式的文件!')
    return false
  }
  if (!isLt50M) {
    ElMessage.error('文件大小不能超过 50MB!')
    return false
  }

  return true
}

// 文档移除
const handleDocRemove = () => {
  docFileList.value = []
  docAnalysisResult.value = null
}

// 文档分析
const analyzeDocument = async () => {
  analyzing.value = true
  await new Promise(resolve => setTimeout(resolve, 3000))

  // 模拟文档分析结果
  const terms = termDatabase[inputLang.value] || []
  docAnalysisResult.value = {
    totalTerms: terms.length,
    professionalTerms: terms.filter((t: any) => t.type === 'professional').length,
    commonTerms: terms.filter((t: any) => t.type === 'common').length,
    terms: terms.map((term: any) => {
      const zhText = inputLang.value === 'zh' ? term.original : getTranslation(term, 'zh')
      const enText = inputLang.value === 'en' ? term.original : getTranslation(term, 'en')
      return {
        original: term.original,
        type: term.type,
        weight: term.weight,
        zhTranslation: zhText,
        enTranslation: enText,
        notes: term.notes,
        frequency: term.frequency
      }
    })
  }

  analyzing.value = false
  ElMessage.success('文档分析完成')
}

// 导出文档结果
const exportDocumentResult = () => {
  if (!docAnalysisResult.value) return

  let csvContent = '\uFEFF'
  csvContent += `序号,术语类型,中文,English,权重,注释,频次\n`

  docAnalysisResult.value.terms.forEach((term: any, index: number) => {
    const typeText = term.type === 'professional' ? '专业术语' : '普通词汇'
    csvContent += `${index + 1},${typeText},"${term.zhTranslation}","${term.enTranslation}",${term.weight},"${term.notes}",${term.frequency}\n`
  })

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `文档中英文术语对照表_${Date.now()}.csv`
  link.click()
  URL.revokeObjectURL(url)
  ElMessage.success('结果导出成功')
}

// 查看文档详情
const viewDocumentDetail = () => {
  if (!docAnalysisResult.value) return

  const detail = `
文档分析报告
===========================================
文件名: ${docFileList.value[0]?.name}
术语总数: ${docAnalysisResult.value.totalTerms}
专业术语: ${docAnalysisResult.value.professionalTerms}
普通词汇: ${docAnalysisResult.value.commonTerms}

术语详情:
-------------------------------------------
${docAnalysisResult.value.terms.map((term: any, index: number) =>
  `${index + 1}. ${term.original} (${term.type})\n   权重: ${term.weight}\n   翻译: ${term.translation}\n   注释: ${term.notes}\n   频次: ${term.frequency}`
).join('\n\n')}
  `.trim()

  const blob = new Blob([detail], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `文档分析详情_${Date.now()}.txt`
  link.click()
  URL.revokeObjectURL(url)
  ElMessage.success('详情已导出')
}

// 监听语言变化
watch(() => inputLang.value, () => {
  initRandomTerms()
})

// 组件初始化
initRandomTerms()
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
  margin-bottom: 32px;
  padding: 40px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 36px;
  font-weight: 600;
  color: white;
  margin: 0 0 12px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.page-subtitle {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  font-weight: 500;
}

/* 模式切换 */
.mode-tabs {
  max-width: 600px;
  margin: 0 auto 32px;
  padding: 8px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

:deep(.mode-tabs .el-radio-group) {
  display: flex;
  justify-content: center;
  gap: 8px;
}

:deep(.mode-tabs .el-radio-button__inner) {
  border-radius: 8px;
  font-weight: 500;
  padding: 10px 20px;
  transition: all 0.3s;
}

:deep(.mode-tabs .el-radio-button.is-active .el-radio-button__inner) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
  color: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
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

.header-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 对照表格 */
.compare-table {
  margin-top: 20px;
  border-radius: 8px;
  overflow: hidden;
}

:deep(.compare-table .el-table__header-wrapper) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

:deep(.compare-table .el-table th) {
  background: transparent;
  color: white;
  font-weight: 600;
  font-size: 14px;
}

:deep(.compare-table .el-table__row) {
  cursor: pointer;
  transition: all 0.3s;
}

:deep(.compare-table .el-table__row:hover) {
  background-color: #f0f9ff;
  transform: scale(1.01);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

:deep(.compare-table .el-table__row:nth-child(even)) {
  background-color: #fafafa;
}

:deep(.compare-table .el-table__row:nth-child(even):hover) {
  background-color: #f0f9ff;
}

.table-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.table-cell.source {
  justify-content: flex-start;
}

.table-cell.translation {
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
}

.table-cell.notes {
  align-items: flex-start;
}

.note-icon {
  color: #909399;
  margin-right: 6px;
}

.table-type-tag {
  margin-bottom: 4px;
}

.term-text {
  font-weight: 500;
  color: #303133;
  font-size: 14px;
}

.primary-text {
  color: #303133;
  font-weight: 600;
  font-size: 15px;
}

.english-text {
  color: #409eff;
  font-weight: 500;
  font-size: 14px;
  font-family: 'Arial', sans-serif;
}

.weight-display {
  display: flex;
  align-items: center;
  justify-content: center;
}

.notes-text {
  color: #606266;
  line-height: 1.6;
  font-size: 13px;
}

/* 统计摘要 */
/* 分页样式 */
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  padding: 10px 0;
}

.compare-summary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-top: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
  border-radius: 12px;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
}

.summary-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.summary-icon {
  font-size: 32px;
}

.summary-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summary-label {
  font-size: 12px;
  color: #909399;
  font-weight: 500;
}

.summary-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.example-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.example-toggle {
  margin-left: 12px;
  padding: 4px 12px;
  font-size: 13px;
}

.example-toggle:hover {
  background-color: #e8eef5;
}

.example-section {
  max-width: 1200px;
  margin: 20px auto 0;
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.example-section.hidden {
  display: none;
}

.example-section h3 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

/* 标记样式（保留用于其他模式） */
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
  display: none; /* 默认隐藏图例 */
}

.legend-section.show {
  display: block;
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

  .page-title {
    font-size: 24px;
  }

  .page-subtitle {
    font-size: 14px;
  }

  .mode-tabs {
    max-width: 100%;
  }

  .overview-stats {
    grid-template-columns: repeat(2, 1fr);
  }

  .compare-summary {
    grid-template-columns: repeat(2, 1fr);
  }

  .compare-container {
    grid-template-columns: 1fr;
  }

  .weight-charts {
    grid-template-columns: 1fr;
  }

  :deep(.compare-table) {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .compare-summary {
    grid-template-columns: 1fr;
  }

  .summary-card {
    padding: 16px;
  }
}

/* 图片分析 */
.image-analysis-card {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.image-analysis-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.image-uploader {
  width: 100%;
}

.upload-placeholder {
  padding: 40px;
  text-align: center;
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  transition: border-color 0.3s;
}

.upload-placeholder:hover {
  border-color: #409eff;
}

.upload-icon {
  font-size: 48px;
  color: #909399;
  margin-bottom: 16px;
}

.upload-text {
  font-size: 16px;
  color: #303133;
  margin-bottom: 8px;
}

.upload-hint {
  font-size: 13px;
  color: #909399;
}

.uploaded-image {
  width: 100%;
  height: 300px;
  object-fit: contain;
  border-radius: 8px;
}

.image-actions {
  margin-top: 16px;
  display: flex;
  gap: 12px;
  justify-content: center;
}

/* 文档分析 */
.document-analysis-card {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.document-analysis-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.document-uploader {
  width: 100%;
}

.doc-actions {
  margin-top: 16px;
  display: flex;
  gap: 12px;
  justify-content: center;
}

/* 分析结果 */
.analysis-result {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 20px;
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
  font-weight: 500;
  color: #303133;
}

.result-actions {
  display: flex;
  gap: 8px;
}

.result-content {
  min-height: 200px;
}

.result-text {
  line-height: 1.8;
  color: #606266;
}

.placeholder-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #909399;
}

.placeholder-text p {
  margin: 12px 0 0 0;
  font-size: 14px;
}

/* 图片分析结果 */
.image-result-content {
  line-height: 2;
}

.image-result-content h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 15px;
}

.image-result-content p {
  margin: 0 0 16px 0;
  color: #606266;
}

/* 常驻对照表 */
.permanent-compare-section {
  max-width: 1200px;
  margin: 0 auto 32px;
}

.permanent-card {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.header-icon {
  margin-right: 8px;
  font-size: 18px;
}

.random-badge {
  margin-left: 12px;
  padding: 2px 8px;
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  color: white;
}

.idle-alert {
  margin-bottom: 16px;
}

.idle-alert p {
  margin: 6px 0 0 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}

.quick-filters {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  flex-wrap: wrap;
}

.star-icon {
  color: #e6a23c;
  font-size: 16px;
}

/* 专业术语行样式 */
:deep(.professional-row) {
  background: linear-gradient(135deg, #fff5f5 0%, #fff 100%);
}

:deep(.professional-row .el-table__cell) {
  background: transparent;
}

/* 高权重行样式 */
:deep(.high-weight-row) td {
  border-left: 3px solid #e6a23c !important;
}

/* 术语专业样式 */
.term-text.professional {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 700;
  font-size: 14px;
}


.terms-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.image-term-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: white;
  border-radius: 6px;
  border-left: 3px solid #409eff;
}

.term-original {
  font-weight: 500;
  color: #303133;
}

.term-arrow {
  color: #909399;
}

.term-translation {
  flex: 1;
  color: #606266;
}

.term-type {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  background: #e8eef5;
  color: #409eff;
}

/* 文档分析结果 */
.document-terms-table {
  margin-top: 20px;
}

.document-terms-table h4 {
  margin: 0 0 12px 0;
  font-size: 15px;
  font-weight: 500;
  color: #303133;
}

/* 响应式 - 图片和文档分析 */
@media (max-width: 768px) {
  .image-analysis-container {
    grid-template-columns: 1fr;
  }

  .terms-grid {
    grid-template-columns: 1fr;
  }

  .uploaded-image {
    height: 200px;
  }
}

</style>
