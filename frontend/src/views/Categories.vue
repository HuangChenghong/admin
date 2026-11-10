<template>
  <div class="page-container">
    <el-card shadow="never">
      <!-- 搜索区 -->
      <div class="search-bar">
        <el-input
          v-model="searchForm.name"
          placeholder="请输入分类名称"
          clearable
          style="width: 240px"
          :prefix-icon="Search"
        />
        <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
        <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        <div class="search-bar-right">
          <el-button type="primary" :icon="Plus" @click="handleAdd">新增分类</el-button>
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
        <el-table-column prop="create_user_name" label="创建人" min-width="160" align="center"/>
        <el-table-column prop="name" label="分类名称" min-width="160" align="center"/>
        <el-table-column prop="description" label="分类描述" min-width="240" show-overflow-tooltip align="center"/>
        <el-table-column prop="article_count" label="文章数" width="100" align="center" />
        <el-table-column prop="create_at" label="创建时间" width="180" align="center" 
          :formatter="(row: any) => {
            return row.create_at ? dayjs(row.create_at).format('YYYY-MM-DD HH:mm:ss') : '-'
        }" />
        <el-table-column label="操作" width="180" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link :icon="Edit" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link :icon="Delete" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
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
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="分类描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入分类描述"
          />
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
import { Search, Refresh, Plus, Edit, Delete } from '@element-plus/icons-vue'
import { getCategories, createCategory, updateCategory, deleteCategory } from '../api/category'
import dayjs from 'dayjs'



const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const dialogTitle = ref('')
const formRef = ref<FormInstance>()

const searchForm = reactive({
  name: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const tableData = ref<any[]>([])

const formData = reactive({
  id: 0,
  name: '',
  description: ''
})

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 2, max: 20, message: '名称长度在 2 到 20 个字符', trigger: 'blur' }
  ]
}

const fetchData = async() => {
  loading.value = true
  try {
    const data = { 
      page: pagination.page,
      pageSize: pagination.pageSize,
      name: searchForm.name || '' 
    }
    const res = await getCategories(data)
    if (res && res.code === 200 && Array.isArray(res.data) && res.data.length > 0) {
      tableData.value = res.data || []
      pagination.total = res.total || 0 
    }
  } catch (error) {
    ElMessage.error('获取分类失败')
  }
  finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.name = ''
  pagination.page = 1
  fetchData()
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增分类'
  formData.id = 0
  formData.name = ''
  formData.description = ''
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  isEdit.value = true
  dialogTitle.value = '编辑分类'
  formData.id = row.id
  formData.name = row.name
  formData.description = row.description
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      if (isEdit.value) {
        const res = await updateCategory(formData)
        if (res.code === 200) {
          ElMessage.success('修改成功')
        }
      } else {
        console.log(formData, 'formData')
        const data = {
          name: formData.name,
          description: formData.description || ''
        }
        const res = await createCategory(data)
        if (res.code === 200) {
          ElMessage.success('新增成功')
        }
      }
      dialogVisible.value = false
      submitLoading.value = false
      fetchData()
    }
  })
}

const handleDelete = (row: any) => {
  ElMessageBox.confirm(`确定要删除分类「${row.name}」吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    const res = await deleteCategory(row.id)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      fetchData()
    } else {
      ElMessage.error(res.msg)
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
