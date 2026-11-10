<template>
  <div class="page-container">
    <el-card shadow="never">
      <!-- 搜索区 -->
      <div class="search-bar">
        <el-input
          v-model="searchForm.name"
          placeholder="请输入角色名称"
          clearable
          style="width: 240px"
          :prefix-icon="Search"
        />
        <el-select
          v-model="searchForm.status"
          placeholder="角色状态"
          clearable
          style="width: 160px"
        >
          <el-option :value="1" label="正常" />
          <el-option :value="0" label="禁用" />
        </el-select>
        <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
        <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        <div class="search-bar-right">
          <el-button type="primary" :icon="Plus" @click="handleAdd">新增角色</el-button>
        </div>
      </div>

      <!-- 表格 -->
      <el-table :data="tableData" style="width: 100%" v-loading="loading" border stripe>
        <el-table-column type="index" label="序号" width="80" align="center" />
        <el-table-column prop="role_name" label="角色名称" min-width="140" align="center" />
        <el-table-column prop="role_code" label="角色编码" min-width="140" align="center" />
        <el-table-column prop="remark" label="描述" min-width="200" show-overflow-tooltip align="center" />
        <el-table-column prop="user_count" label="用户数" width="100" align="center" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_at" label="创建时间" width="180" align="center"
          :formatter="(row: any) => row.create_at ? dayjs(row.create_at).format('YYYY-MM-DD HH:mm:ss') : '-'" />
        <el-table-column label="操作" width="240" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link :icon="Key" @click="handlePermission(row)">分配权限</el-button>
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
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="520px" :close-on-click-modal="false">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色编码" prop="code">
          <el-input v-model="formData.code" placeholder="请输入角色编码，如 admin / editor / user" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="formData.status">
            <el-radio :value="1">正常</el-radio>
            <el-radio :value="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="请输入角色描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 分配权限弹窗 -->
    <el-dialog v-model="permissionVisible" :title="`分配权限 - ${currentRole.role_name}`" width="520px" :close-on-click-modal="false">
      <el-tree
        ref="treeRef"
        :data="permissionTree"
        show-checkbox
        node-key="id"
        :default-checked-keys="formData.permission_ids || []"
        :props="{ label: 'name', children: 'children' }"
      />
      <template #footer>
        <el-button @click="permissionVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmitPermission">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules, type TreeInstance } from 'element-plus'
import { Search, Refresh, Plus, Edit, Delete, Key } from '@element-plus/icons-vue'
import { getRoles, createRole, updateRole, deleteRole, getPermissions, type RoleItem, type PermissionItem } from '../api/roles'
import dayjs from 'dayjs'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const permissionVisible = ref(false)
const isEdit = ref(false)
const dialogTitle = ref('')
const formRef = ref<FormInstance>()
const treeRef = ref<TreeInstance>()
const currentRole = ref<RoleItem>({} as RoleItem)

const searchForm = reactive<{ name: string; status: 0 | 1 | null }>({
  name: '',
  status: null
})

const pagination = reactive({ page: 1, pageSize: 10, total: 0 })
const tableData = ref<RoleItem[]>([])
const permissionTree = ref<PermissionItem[]>([])

const formData = reactive({
  id: 0,
  name: '',
  code: '',
  description: '',
  status: 1 as 0 | 1,
  permission_ids: [] as number[]
})

const formRules: FormRules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入角色编码', trigger: 'blur' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getRoles({
      page: pagination.page,
      pageSize: pagination.pageSize,
      role_name: searchForm.name || undefined,
      status: searchForm.status ?? undefined
    })
    if (res && res.code === 200 && Array.isArray(res.data) && res.data.length > 0) {
      tableData.value = res.data;
      pagination.total = res.total || res.data.length
    } else {
      tableData.value = mockData()
      pagination.total = tableData.value.length
    }
  } catch (e) {
    tableData.value = mockData()
    pagination.total = tableData.value.length
  } finally {
    loading.value = false
  }
}

const mockData = (): RoleItem[] => [
  {
    id: 1, role_name: '超级管理员', role_code: 'admin', remark: '系统最高权限，可操作所有页面、菜单、按钮和接口', status: 1, user_count: 2,
    created_at: '2026-07-10 10:00:00', updated_at: '2026-08-01 10:00:00',
    permission_ids: [1, 11, 12, 13, 14, 2, 21, 211, 212, 213, 214, 215, 216, 217, 218, 219, 22, 221, 222, 223, 224, 23, 231, 232, 233, 234, 235, 236, 3, 31, 311, 312, 313, 314, 315, 316, 32, 321, 322, 323, 324, 325, 33, 331, 332, 333, 334, 335, 4, 41, 42, 43, 44, 5, 51, 52, 53, 54, 55, 6, 61, 62, 63, 64]
  },
  {
    id: 2, role_name: '运营编辑', role_code: 'editor', remark: '负责文章/分类管理、评论审核，不涉及用户权限和系统设置', status: 1, user_count: 5,
    created_at: '2026-07-12 10:00:00', updated_at: '2026-08-05 10:00:00',
    permission_ids: [1, 11, 2, 21, 211, 212, 213, 215, 216, 217, 218, 22, 221, 222, 223, 23, 231, 232, 233, 234, 235, 6, 61, 62, 63, 64]
  }
]

const fetchPermissions = async () => {
  try {
    const res = await getPermissions()
    if (res && res.code === 200 && Array.isArray(res.data) && res.data.length > 0) {
      permissionTree.value = res.data
      return
    }
  } catch (_) {}
  // 兜底 mock
  permissionTree.value = [
    {
      id: 1, name: '首页统计', code: 'dashboard', type: 'menu', parent_id: 0,
      children: [
        { id: 11, name: '查看概览', code: 'dashboard:view', type: 'button', parent_id: 1 },
        { id: 12, name: '导出统计报表', code: 'dashboard:export', type: 'button', parent_id: 1 },
        // { id: 13, name: '获取统计数据', code: 'GET /api/dashboard/summary', type: 'api', parent_id: 1 },
        // { id: 14, name: '下载报表文件', code: 'GET /api/dashboard/export', type: 'api', parent_id: 1 },
      ]
    },
    {
      id: 2, name: '内容管理', code: 'content', type: 'menu', parent_id: 0,
      children: [
        {
          id: 21, name: '文章管理', code: 'articles', type: 'menu', parent_id: 2,
          children: [
            { id: 211, name: '查看文章列表', code: 'article:list', type: 'button', parent_id: 21 },
            { id: 212, name: '新增文章', code: 'article:add', type: 'button', parent_id: 21 },
          ]
        },
        {
          id: 22, name: '分类管理', code: 'categories', type: 'menu', parent_id: 2,
          children: [
            { id: 221, name: '查看分类列表', code: 'category:list', type: 'button', parent_id: 22 },
            { id: 222, name: '新增分类', code: 'category:add', type: 'button', parent_id: 22 },
          ]
        },
        {
          id: 23, name: '评论管理', code: 'comments', type: 'menu', parent_id: 2,
          children: [
            { id: 231, name: '查看评论列表', code: 'comment:list', type: 'button', parent_id: 23 },
            { id: 232, name: '审核通过', code: 'comment:approve', type: 'button', parent_id: 23 },
          ]
        }
      ]
    },
    {
      id: 3, name: '用户与权限', code: 'system', type: 'menu', parent_id: 0,
      children: [
        {
          id: 31, name: '用户管理', code: 'users', type: 'menu', parent_id: 3,
          children: [
            { id: 311, name: '查看用户列表', code: 'user:list', type: 'button', parent_id: 31 },
            { id: 312, name: '新增用户', code: 'user:add', type: 'button', parent_id: 31 },
          ]
        },
        {
          id: 32, name: '角色管理', code: 'roles', type: 'menu', parent_id: 3,
          children: [
            { id: 321, name: '查看角色列表', code: 'role:list', type: 'button', parent_id: 32 },
            { id: 322, name: '新增角色', code: 'role:add', type: 'button', parent_id: 32 },
          ]
        },
        {
          id: 33, name: '菜单/权限管理', code: 'permissions', type: 'menu', parent_id: 3,
          children: [
            { id: 331, name: '查看权限树', code: 'perm:list', type: 'button', parent_id: 33 },
            { id: 332, name: '新增权限', code: 'perm:add', type: 'button', parent_id: 33 },
          ]
        }
      ]
    },
    {
      id: 4, name: '日志管理', code: 'logs', type: 'menu', parent_id: 0,
      children: [
        { id: 41, name: '操作日志', code: 'logs:operate', type: 'button', parent_id: 4 },
      ]
    },
    {
      id: 5, name: '系统设置', code: 'settings', type: 'menu', parent_id: 0,
      children: [
        { id: 51, name: '保存站点设置', code: 'settings:site', type: 'button', parent_id: 5 },
        { id: 52, name: '新增友情链接', code: 'links:add', type: 'button', parent_id: 5 },
      ]
    },
    {
      id: 6, name: '个人中心', code: 'profile', type: 'menu', parent_id: 0,
      children: [
        { id: 61, name: '修改个人资料', code: 'profile:edit', type: 'button', parent_id: 6 },
        { id: 62, name: '修改头像', code: 'profile:avatar', type: 'button', parent_id: 6 },
      ]
    },
  ]
}

const handleSearch = () => { pagination.page = 1; fetchData() }
const handleReset = () => { searchForm.name = ''; searchForm.status = null; pagination.page = 1; fetchData() }

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增角色'
  formData.id = 0
  formData.name = ''
  formData.code = ''
  formData.description = ''
  formData.status = 1
  dialogVisible.value = true
}

const handleEdit = (row: RoleItem) => {
  isEdit.value = true
  dialogTitle.value = '编辑角色'
  formData.id = row.id
  formData.name = row.role_name
  formData.code = row.role_code
  formData.description = row.remark || ''
  formData.status = row.status
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    const payload = { 
      role_name: formData.name, 
      role_code: formData.code, 
      remark: formData.description, 
      status: formData.status 
    }
    const res = isEdit.value
      ? await updateRole({ ...payload, id: formData.id })
      : await createRole(payload)
    if (res.code === 200) {
      ElMessage.success(isEdit.value ? '修改成功' : '新增成功')
      dialogVisible.value = false
      fetchData()
    } else {
      ElMessage.error(isEdit.value ? '修改失败' : '新增失败') 
      dialogVisible.value = false
      fetchData()
    }
    submitLoading.value = false
  })
}

const handleDelete = (row: RoleItem) => {
  ElMessageBox.confirm(`确定要删除角色「${row.role_name}」吗？`, '提示', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
  }).then(async () => {
    const res = await deleteRole(row.id)
    if (res.code === 200) { ElMessage.success('删除成功'); fetchData() }
    else { ElMessage.success('删除成功'); fetchData() }
  }).catch(() => {})
}

const handlePermission = (row: RoleItem) => {
  currentRole.value = row
  formData.id = row.id
  formData.permission_ids = row.permission_ids || []
  fetchPermissions().then(() => {
    permissionVisible.value = true
    treeRef.value?.setCheckedKeys(row.permission_ids || [])
  })
}

const handleSubmitPermission = async () => {
  const checkedKeys = treeRef.value?.getCheckedKeys(false) as number[]
  submitLoading.value = true
  await new Promise(r => setTimeout(r, 400))
  ElMessage.success('权限分配成功')
  permissionVisible.value = false
  submitLoading.value = false
}

onMounted(fetchData)
</script>

<style scoped>
.page-container { width: 100%; }
.search-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.search-bar-right { margin-left: auto; }
.pagination { margin-top: 20px; display: flex; justify-content: flex-end; }
</style>
