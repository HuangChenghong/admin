<template>
  <div class="page-container">
    <el-card shadow="never">
      <!-- 搜索区 -->
      <div class="search-bar">
        <el-input
          v-model="searchForm.title"
          placeholder="请输入文章标题"
          clearable
          style="width: 240px"
          :prefix-icon="Search"
        />
        <el-select
          v-model="searchForm.categoryId"
          placeholder="文章分类"
          clearable
          style="width: 160px"
        >
          <el-option v-for="item in categoryOptions" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
        <el-select
          v-model="searchForm.status"
          placeholder="发布状态"
          clearable
          style="width: 140px"
        >
          <el-option label="已发布" :value="1" />
          <el-option label="草稿" :value="2" />
        </el-select>
        <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
        <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        <!-- <div class="search-bar-right">
          <el-button type="primary" :icon="Plus" @click="handleAdd">发布文章</el-button>
        </div> -->
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
        <el-table-column prop="title" label="标题" min-width="240" show-overflow-tooltip align="center">
          <template #default="{ row }">
            <el-link type="primary" :underline="false" @click="handleView(row)">
              {{ row.title }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="categoryName" label="分类" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="info" effect="plain">{{ categoryName(row.category_id) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_user_name" label="作者" width="100" align="center" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === '1' ? 'success' : 'warning'">
              {{ row.status === '1' ? '已发布' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="views" label="浏览" width="80" align="center" />
        <el-table-column prop="like_count" label="点赞" width="80" align="center" />
        <el-table-column prop="create_at" label="创建时间" width="160" align="center" >
          <template #default="{ row }">
            {{ row.create_at ? dayjs(row.create_at).format('YYYY-MM-DD HH:mm:ss') : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link :icon="View" @click="handleView(row)">查看</el-button>
            <!-- <el-button type="success" link :icon="Edit" @click="handleEdit(row)">编辑</el-button> -->
            <el-button
              :type="row.status === '1' ? 'warning' : 'success'"
              link
              @click="handleToggleStatus(row)"
            >
              {{ row.status === '1' ? '下架' : '发布' }}
            </el-button>
            <!-- <el-button type="danger" link :icon="Delete" @click="handleDelete(row)">删除</el-button> -->
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
      width="720px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="文章标题" prop="title">
          <el-input v-model="formData.title" placeholder="请输入文章标题" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="文章分类" prop="categoryId">
          <el-select v-model="formData.categoryId" style="width: 100%" placeholder="请选择分类">
            <el-option label="技术" :value="1" />
            <el-option label="生活" :value="2" />
            <el-option label="随笔" :value="3" />
            <el-option label="教程" :value="4" />
            <el-option label="资讯" :value="5" />
          </el-select>
        </el-form-item>
        <el-form-item label="发布状态" prop="status">
          <el-radio-group v-model="formData.status">
            <el-radio :value="1">立即发布</el-radio>
            <el-radio :value="0">保存草稿</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="文章摘要" prop="summary">
          <el-input
            v-model="formData.summary"
            type="textarea"
            :rows="3"
            placeholder="请输入文章摘要（200字以内）"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="文章内容" prop="content">
          <el-input
            v-model="formData.content"
            type="textarea"
            :rows="8"
            placeholder="请输入文章正文内容..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看文章详情弹窗 -->
    <el-dialog
      v-model="detailVisible"
      title="文章详情"
      width="780px"
      :close-on-click-modal="true"
    >
      <div class="article-detail" v-if="detailData">
        <h2 class="detail-title">{{ detailData.title }}</h2>
        <div class="detail-meta">
          <el-tag type="info" effect="plain" size="small">
            {{ categoryName(detailData.category_id) }}
          </el-tag>
          <span class="meta-item">作者：{{ detailData.create_user_name || '-' }}</span>
          <span class="meta-item">浏览：{{ detailData.views ?? 0 }}</span>
          <el-tag
            :type="Number(detailData.status) === 1 ? 'success' : 'warning'"
            size="small"
          >
            {{ Number(detailData.status) === 1 ? '已发布' : '草稿' }}
          </el-tag>
          <span class="meta-item" v-if="detailData.create_at">
            发布时间：{{ dayjs(detailData.create_at).format('YYYY-MM-DD HH:mm:ss') }}
          </span>
          <span class="meta-item" v-if="detailData.update_at">
            更新时间：{{ dayjs(detailData.update_at).format('YYYY-MM-DD HH:mm:ss') }}
          </span>
        </div>
        <el-divider />
        <div class="detail-section" v-if="detailData.description">
          <h4 class="section-label">摘要</h4>
          <p class="section-text">{{ detailData.description }}</p>
        </div>
        <div class="detail-section">
          <h4 class="section-label">正文</h4>
          <!-- 富文本用单个容器渲染：content 本身就是 <p><img/></p> 这样的 HTML，
               套在 <p> 里会被浏览器自动闭合打断，用 <pre> 再渲染一次又会重复一遍 -->
          <div
            class="detail-content rich-text"
            v-if="detailData.content"
            v-html="detailData.content"
          />
          <el-empty v-else description="暂无正文内容" :image-size="80" />
        </div>
      </div>
      <el-empty v-else description="暂无数据" />
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Search, Refresh, View, Edit, Delete } from '@element-plus/icons-vue'
import { getArticles, updateArticle, deleteArticle } from '../api/articles'
import { getCategories } from '../api/category'
import dayjs from 'dayjs'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const dialogTitle = ref('')
const formRef = ref<FormInstance>()

// 查看详情弹窗
const detailVisible = ref(false)
const detailData = ref<any>(null)

const searchForm = reactive({
  title: '',
  categoryId: null as number | null,
  status: null as number | null
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const tableData = ref<any[]>([])
const formData = reactive({
  id: 0,
  title: '',
  categoryId: null as number | null,
  status: 1,
  summary: '',
  content: ''
})
type category = {
  id: number
  name: string
  description: string
}
type row = {
  id: number
  title: string
  category_id: number
  status: string
}
const categoryOptions = ref<category[]>([])

// 分类 id → name 映射表，O(1) 查找，模板里直接 categoryName(id) 即可
const categoryMap = computed(() => {
  const map: Record<number, string> = {}
  for (const c of categoryOptions.value) {
    map[c.id] = c.name
  }
  return map
})
const categoryName = (id?: number) => (id != null ? (categoryMap.value[id] ?? '未分类') : '未分类')

const formRules: FormRules = {
  title: [
    { required: true, message: '请输入文章标题', trigger: 'blur' },
    { min: 5, max: 100, message: '标题长度在 5 到 100 个字符', trigger: 'blur' }
  ],
  categoryId: [{ required: true, message: '请选择文章分类', trigger: 'change' }],
  summary: [{ required: true, message: '请输入文章摘要', trigger: 'blur' }],
  content: [{ required: true, message: '请输入文章内容', trigger: 'blur' }]
}

const fetchData = async () => {
  loading.value = true
  const res = await getArticles({
    page: pagination.page,
    page_size: pagination.pageSize,
    title: searchForm.title || '',
    category_id: searchForm.categoryId || undefined,
    status: searchForm.status || undefined
  })
  if (res && res.code === 200 && Array.isArray(res.data) && res.data.length > 0) {
    tableData.value = res.data || []
    pagination.total = res.total || 0 
  } else {
    tableData.value = []
    pagination.total = 0
  }
  loading.value = false
}

const getCategory = async () => {
  const res = await getCategories({page:1, pageSize:20})
  if (res && res.code === 200 && Array.isArray(res.data) && res.data.length > 0) {
    // 接口返回的 Category 类型里 id / description 是可选的（可能 undefined），
    // categoryOptions 需要的是强类型（id 必须有，description 必须是字符串），
    // 这里手动兜底收窄类型，避免 TS 报错。
    const data: category[] = res.data.map(item => ({
      id: typeof item.id === 'number' ? item.id : 0,
      name: item.name ?? '',
      description: item.description ?? ''
    }))
    console.log(data)
    categoryOptions.value = data
  } else {
    categoryOptions.value = []
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.title = ''
  searchForm.categoryId = null
  searchForm.status = null
  pagination.page = 1
  fetchData()
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '发布文章'
  formData.id = 0
  formData.title = ''
  formData.categoryId = null
  formData.status = 1
  formData.summary = ''
  formData.content = ''
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  isEdit.value = true
  dialogTitle.value = '编辑文章'
  formData.id = row.id
  formData.title = row.title
  formData.categoryId = row.categoryId
  formData.status = row.status
  formData.summary = row.description || ''
  formData.content = row.content || '文章正文内容（编辑模式）...'
  dialogVisible.value = true
}

const handleView = (row: any) => {
  // 直接用列表行数据填充详情弹窗
  detailData.value = row
  detailVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
    }
  })
}

const handleToggleStatus = (row: row) => {
  const action = row.status === '1' ? '下架' : '发布'
  ElMessageBox.confirm(`确定要${action}文章「${row.title}」吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    await updateArticle({
      id: row.id,
      status: row.status === '1' ? 2 : 1
    })
    ElMessage.success(`${action}成功`)
    fetchData()
  }).catch(() => {})
}

const handleDelete = (row: row) => {
  ElMessageBox.confirm(`确定要删除文章「${row.title}」吗？此操作不可恢复！`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    await deleteArticle(row.id)
    ElMessage.success('删除成功')
    fetchData()
  }).catch(() => {})
}

onMounted(async () => {
  await getCategory()
  fetchData()
})
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

/* 文章详情弹窗 */
.article-detail {
  max-height: 60vh;
  overflow-y: auto;
}

.detail-title {
  margin: 0 0 12px;
  font-size: 20px;
  font-weight: 600;
  line-height: 1.5;
  color: #303133;
}

.detail-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 13px;
  color: #909399;
}

.meta-item {
  color: #606266;
}

.detail-section {
  margin-bottom: 16px;
}

.section-label {
  margin: 0 0 8px;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  border-left: 3px solid var(--el-color-primary);
  padding-left: 8px;
}

.section-text {
  margin: 0;
  color: #606266;
  line-height: 1.8;
  font-size: 14px;
  text-indent: 2em;
}

.detail-content {
  color: #303133;
  line-height: 1.8;
  font-size: 14px;
  background-color: #fafafa;
  padding: 12px 16px;
  border-radius: 4px;
  border: 1px solid #ebeef5;
  text-indent: 2em;
}

/* v-html 插入的节点不带 scoped 属性，需要用 :deep 才能命中 */
.detail-content :deep(p) {
  margin: 0 0 8px;
  word-wrap: break-word;
}

.detail-content :deep(p:last-child) {
  margin-bottom: 0;
}

/* 正文图片自适应容器宽度，避免原图尺寸撑破弹窗 */
.detail-content :deep(img) {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 8px 0;
  border-radius: 4px;
}

.detail-content :deep(img:only-child) {
  margin: 0 0 8px 2em;
}
</style>
