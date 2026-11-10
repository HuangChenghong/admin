<template>
  <div class="page-container">
    <el-card shadow="never">
      <!-- 搜索区 -->
      <div class="search-bar">
        <el-input
          v-model="searchForm.username"
          placeholder="请输入用户名"
          clearable
          style="width: 200px"
          :prefix-icon="User"
        />
        <el-select
          v-model="searchForm.status"
          placeholder="用户状态"
          clearable
          style="width: 160px"
        >
          <el-option label="正常" :value="1" />
          <el-option label="禁用" :value="0" />
        </el-select>
        <el-date-picker
          v-model="searchForm.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          style="width: 280px"
        />
        <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
        <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        <div class="search-bar-right">
          <el-button type="primary" :icon="Plus" @click="handleAdd">新增用户</el-button>
        </div>
      </div>

      <!-- 表格 -->
      <el-table
        :data="tableData"
        style="width: 100%"
        v-loading="loading"
        border
        stripe
      >
        <el-table-column type="index" label="序号" width="80" align="center" />
        <el-table-column label="头像" width="80" align="center">
          <template #default="{ row }">
            <el-avatar :size="36" :src="`https://hch359.top${row.avater}`">
              {{ row.username?.charAt(0)?.toUpperCase() }}
            </el-avatar>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户名" min-width="120" align="center" />
        <el-table-column prop="cname" label="昵称" min-width="120" align="center" />
        <!-- <el-table-column prop="cname" label="昵称" min-width="120" align="center" /> -->
        <el-table-column prop="email" label="邮箱" min-width="200" align="center" show-overflow-tooltip />
        <el-table-column prop="role" label="角色" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.role === 1 ? 'danger' : 'info'">
              {{ row.role === 1 ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="article_count" label="文章数" width="100" align="center" />
        <el-table-column prop="created_at" label="注册时间" width="180" align="center" 
          :formatter="(row: any) => {
            return row.created_at ? dayjs(row.created_at).format('YYYY-MM-DD HH:mm:ss') : '-'
          }">
        </el-table-column>
        
        <el-table-column label="操作" width="240" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link :icon="Edit" @click="handleEdit(row)">编辑</el-button>
            <el-button
              :type="row.status === 1 ? 'warning' : 'success'"
              link
              :icon="row.status === 1 ? Lock : Unlock"
              @click="handleToggleStatus(row)"
            >
              {{ row.status === 1 ? '禁用' : '启用' }}
            </el-button>
            <el-button type="danger" link :icon="Delete" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[5, 10, 20, 50]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @size-change="fetchData"
          @current-change="fetchData"
        />
      </div>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="formData.username" placeholder="请输入用户名" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="formData.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item v-if="!isEdit" label="密码" prop="password">
          <el-input v-model="formData.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="formData.role" style="width: 100%">
            <el-option label="管理员" :value="1" />
            <el-option label="普通用户" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="formData.status">
            <el-radio :value="1">正常</el-radio>
            <el-radio :value="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Search, Refresh, Plus, Edit, Delete, Lock, Unlock, User } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

import { getUser, forbiddenUser, activeUser, deleteUser, adminCreateUser, adminUpdateUser } from '../api/user'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const dialogTitle = ref('')
const formRef = ref<FormInstance>()

const searchForm = reactive({
  username: '',
  status: null as number | null,
  dateRange: [] as string[]
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const tableData = ref<any[]>([])

const formData = reactive({
  id: 0,
  username: '',
  email: '',
  password: '',
  role: 0, // 0: 普通用户, 1: 管理员
  status: 1 // 1: 正常, 0: 禁用
})

const formRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
  ],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

const fetchData = async() => {
  loading.value = true
  const hasDateRange = searchForm.dateRange && searchForm.dateRange.length > 0
  try {
    const res = await getUser({
      username: searchForm.username,
      status: searchForm.status,
      page: pagination.page,
      pageSize: pagination.pageSize,
      start_date:  hasDateRange ? `${searchForm.dateRange[0]} 00:00:00` : null,
      end_date:  hasDateRange ? `${searchForm.dateRange[1]} 23:59:59` : null
    })
    if (res && res.code === 200 && Array.isArray(res.data)) {
      tableData.value = res.data
      pagination.total = res.total || 0
    } else {
      tableData.value = []
      pagination.total = 0
    }
  } catch (e) {
    console.error('获取用户列表失败:', e)
    tableData.value = []
    pagination.total = 0
  } finally {
    console.log('finally')
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.username = ''
  searchForm.status = null
  searchForm.dateRange = []
  pagination.page = 1
  fetchData()
}

const handleEdit = (row: any) => {
  isEdit.value = true
  dialogTitle.value = '编辑用户'
  formData.id = row.id
  formData.username = row.username
  formData.email = row.email
  formData.password = ''
  formData.role = row.role
  formData.status = row.status
  dialogVisible.value = true
  // 编辑模式：密码可选（不填则不改密码）
  formRules.password = [{ min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }]
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增用户'
  formData.id = 0
  formData.username = ''
  formData.email = ''
  formData.password = ''
  formData.role = 0 // 0: 普通用户, 1: 管理员
  formData.status = 1 // 1: 正常, 0: 禁用
  dialogVisible.value = true
  // 新增模式：密码必填
  formRules.password = [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
  ]
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    try {
      let res: any
      if (isEdit.value) {
        const payload: any = {
          email: formData.email,
          role: formData.role,
          status: formData.status
        }
        if (formData.password) payload.password = formData.password
        res = await adminUpdateUser(formData.id, payload)
      } else {
        res = await adminCreateUser({
          username: formData.username,
          password: formData.password,
          email: formData.email,
          role: formData.role,
          status: formData.status
        })
      }
      if (res && res.code === 200) {
        ElMessage.success(isEdit.value ? '修改成功' : '新增成功')
        dialogVisible.value = false
        fetchData()
      } else {
        ElMessage.error(res?.msg || (isEdit.value ? '修改失败' : '新增失败'))
      }
    } catch (e: any) {
      ElMessage.error(e?.message || (isEdit.value ? '修改失败' : '新增失败'))
    } finally {
      submitLoading.value = false
    }
  })
}

const handleToggleStatus = (row: any) => {
  const action = row.status === 1 ? '禁用' : '启用'
  ElMessageBox.confirm(`确定要${action}用户「${row.username}」吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    const res: any = row.status === 1 ? await forbiddenUser(row.id) : await activeUser(row.id)
    if (res.code === 200) {
      ElMessage.success(`${action}成功`)
      fetchData()
    }
  }).catch(() => {})
}

const handleDelete = (row: any) => {
  ElMessageBox.confirm(`确定要删除用户「${row.username}」吗？此操作不可恢复！`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    const res: any = await deleteUser(row.id)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      fetchData()
    }
  }).catch(() => {})
}

onMounted(fetchData)
</script>

<style scoped>
.page-container {
  width: 100%;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.search-bar-right {
  margin-left: auto;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
