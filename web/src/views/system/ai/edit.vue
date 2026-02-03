<template>
  <div > 
    3d在线显示示例
  </div>
</template>

<script setup lang="ts"> 
</script>

<style scoped>
.three-d-edit-page {
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

.main-content {
  height: calc(100vh - 200px);
}

.toolbar-card {
  height: fit-content;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar-section {
  margin-bottom: 20px;
}

.toolbar-section h4 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 14px;
  font-weight: bold;
}

.tool-buttons {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.viewer-card {
  height: 100%;
}

.viewer-title {
  font-weight: bold;
  color: #303133;
}

.viewer-controls {
  display: flex;
  gap: 10px;
}

.viewer-container {
  position: relative;
  height: 600px;
  background: #000;
  border-radius: 4px;
  overflow: hidden;
}

.three-canvas {
  width: 100%;
  height: 100%;
  display: block;
}

.empty-state {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
}

.loading-overlay p {
  margin-top: 20px;
  font-size: 16px;
}

.properties-card {
  height: fit-content;
}

.property-section {
  margin-bottom: 20px;
}

.property-section h4 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 14px;
  font-weight: bold;
  padding-bottom: 5px;
  border-bottom: 1px solid #ebeef5;
}

.upload-demo {
  width: 100%;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 20px;
  }
  
  .main-content .el-col {
    margin-bottom: 20px;
  }
}
</style>