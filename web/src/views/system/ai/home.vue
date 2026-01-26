<template>
  <div class="ai-home-container">
    <!-- 头部欢迎卡片 -->
    <el-card class="welcome-card" shadow="hover">
      <h2>🤖 AI 系统管理</h2>
      <p>这是一个简单的 ElementUI 示例页面</p>
    </el-card>

    <!-- 按钮示例 -->
    <el-card class="button-card" shadow="hover">
      <template #header>
        <span>按钮示例</span>
      </template>
      <div class="button-group">
        <el-button type="primary">主要按钮</el-button>
        <el-button type="success">成功按钮</el-button>
        <el-button type="warning">警告按钮</el-button>
        <el-button type="danger">危险按钮</el-button>
        <el-button type="info">信息按钮</el-button>
      </div>
      <div class="button-group">
        <el-button plain>朴素按钮</el-button>
        <el-button round>圆角按钮</el-button>
        <el-button circle icon="el-icon-search"></el-button>
        <el-button type="primary" :loading="loading">加载中</el-button>
      </div>
    </el-card>

    <!-- 表格示例 -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <span>表格示例</span>
      </template>
      <el-table :data="tableData" style="width: 100%" border stripe>
        <el-table-column type="selection" width="55"></el-table-column>
        <el-table-column prop="date" label="日期" width="180"></el-table-column>
        <el-table-column prop="name" label="姓名" width="120"></el-table-column>
        <el-table-column prop="address" label="地址"></el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 表单示例 -->
    <el-card class="form-card" shadow="hover">
      <template #header>
        <span>表单示例</span>
      </template>
      <el-form :model="form" label-width="80px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用户名">
              <el-input v-model="form.username" placeholder="请输入用户名"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱">
              <el-input v-model="form.email" placeholder="请输入邮箱"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="性别">
          <el-radio-group v-model="form.gender">
            <el-radio label="male">男</el-radio>
            <el-radio label="female">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="兴趣爱好">
          <el-checkbox-group v-model="form.hobbies">
            <el-checkbox label="阅读">阅读</el-checkbox>
            <el-checkbox label="运动">运动</el-checkbox>
            <el-checkbox label="音乐">音乐</el-checkbox>
            <el-checkbox label="旅行">旅行</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="个人简介">
          <el-input v-model="form.bio" type="textarea" :rows="3" placeholder="请输入个人简介"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm">提交</el-button>
          <el-button @click="resetForm">重置</el-button>
          <el-button type="success" @click="openDialog">打开对话框</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 对话框 -->
    <el-dialog v-model="dialogVisible" title="提示" width="30%">
      <span>这是一个简单的 ElementUI 对话框示例</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="dialogVisible = false">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 消息提示容器 -->
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 加载状态
const loading = ref(false)

// 表格数据
const tableData = ref([
  {
    date: '2026-01-26',
    name: '张三',
    address: '北京市朝阳区'
  },
  {
    date: '2026-01-25',
    name: '李四',
    address: '上海市浦东新区'
  },
  {
    date: '2026-01-24',
    name: '王五',
    address: '广州市天河区'
  },
  {
    date: '2026-01-23',
    name: '赵六',
    address: '深圳市南山区'
  }
])

// 表单数据
const form = reactive({
  username: '',
  email: '',
  gender: 'male',
  hobbies: [],
  bio: ''
})

// 对话框显示状态
const dialogVisible = ref(false)

// 编辑操作
const handleEdit = (row: any) => {
  ElMessage.success(`编辑: ${row.name}`)
}

// 删除操作
const handleDelete = (row: any) => {
  ElMessageBox.confirm('确认删除该条数据吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('删除成功')
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

// 提交表单
const submitForm = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('表单提交成功！')
    console.log('提交的数据:', form)
  }, 1000)
}

// 重置表单
const resetForm = () => {
  form.username = ''
  form.email = ''
  form.gender = 'male'
  form.hobbies = []
  form.bio = ''
  ElMessage.info('表单已重置')
}

// 打开对话框
const openDialog = () => {
  dialogVisible.value = true
}
</script>

<style scoped>
.ai-home-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card {
  margin-bottom: 20px;
  text-align: center;
}

.welcome-card h2 {
  margin: 0 0 10px 0;
  color: #409eff;
}

.welcome-card p {
  margin: 0;
  color: #666;
}

.button-card,
.table-card,
.form-card {
  margin-bottom: 20px;
}

.button-group {
  margin-bottom: 15px;
}

.button-group:last-child {
  margin-bottom: 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
