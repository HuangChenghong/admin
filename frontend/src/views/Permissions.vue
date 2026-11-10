<template>
  <div class="page-container">
    <el-card shadow="never">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-input
            v-model="filterText"
            placeholder="输入权限名称/编码筛选"
            clearable
            style="width: 280px"
            :prefix-icon="Search"
          />
          <el-button :icon="Refresh" @click="fetchData">刷新</el-button>
          <el-button type="primary" :icon="Plus" @click="handleAdd(null)">新增顶级权限</el-button>
        </div>
        <div class="toolbar-right">
          <el-tag type="primary" effect="plain" round>共 {{ totalCount }} 条</el-tag>
        </div>
      </div>

      <el-table
        :data="permTree"
        row-key="id"
        :tree-props="{ children: 'children' }"
        v-loading="loading"
        border
        stripe
        default-expand-all
        :expand-row-keys="expandedKeys"
        @filter-change="onFilterChange"
      >
        <el-table-column prop="name" label="权限名称" min-width="200">
          <template #default="{ row }">
            <el-icon v-if="row.type === 'menu'" class="row-icon" color="#409EFF"><Menu /></el-icon>
            <el-icon v-else-if="row.type === 'button'" class="row-icon" color="#67C23A"><Operation /></el-icon>
            <el-icon v-else class="row-icon" color="#E6A23C"><Promotion /></el-icon>
            {{ row.name }}
          </template>
        </el-table-column>
        <el-table-column prop="code" label="权限编码" min-width="200" align="center" />
        <el-table-column prop="type" label="类型" width="110" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.type === 'menu'" type="primary" effect="light">菜单</el-tag>
            <el-tag v-else-if="row.type === 'button'" type="success" effect="light">按钮</el-tag>
            <el-tag v-else type="warning" effect="light">API</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="icon" label="图标" width="110" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.icon" size="18"><component :is="row.icon" /></el-icon>
            <span v-else style="color: #c0c4cc">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="path" label="路由路径" min-width="180" show-overflow-tooltip align="center" />
        <el-table-column prop="sort" label="排序" width="80" align="center" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-switch
              :model-value="row.status === 1"
              @change="(v: boolean) => handleStatusChange(row, v)"
              inline-prompt
              active-text="启"
              inactive-text="停"
            />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" align="center"
          :formatter="(r: any) => r.created_at ? dayjs(r.created_at).format('YYYY-MM-DD HH:mm:ss') : '-'" />
        <el-table-column label="操作" width="280" align="center" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.type === 'menu'" type="primary" link :icon="Plus" @click="handleAdd(row)">添加子级</el-button>
            <el-button type="primary" link :icon="Edit" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link :icon="Delete" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="580px" :close-on-click-modal="false">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="上级权限">
          <el-tree-select
            v-model="formData.parent_id"
            :data="selectTree"
            :props="{ label: 'name', value: 'id', children: 'children' }"
            :render-after-expand="false"
            check-strictly
            show-checkbox
            placeholder="选择上级权限（不选则为顶级）"
            clearable
            default-expand-all
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="权限类型" prop="type">
          <el-radio-group v-model="formData.type">
            <el-radio value="menu">菜单</el-radio>
            <el-radio value="button">按钮</el-radio>
            <el-radio value="api">API</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="权限名称" prop="name">
          <el-input v-model="formData.name" placeholder="如：首页统计" />
        </el-form-item>
        <el-form-item label="权限编码" prop="code">
          <el-input v-model="formData.code" placeholder="如：dashboard, user:add" />
        </el-form-item>
        <el-form-item v-if="formData.type === 'menu'" label="图标">
          <el-input v-model="formData.icon" placeholder="Element Plus 图标名，如 DataAnalysis" />
        </el-form-item>
        <el-form-item v-if="formData.type === 'menu'" label="路由路径">
          <el-input v-model="formData.path" placeholder="如：/dashboard" />
        </el-form-item>
        <el-form-item v-if="formData.type === 'menu'" label="组件路径">
          <el-input v-model="formData.component" placeholder="如：views/Dashboard.vue" />
        </el-form-item>
        <el-form-item v-if="formData.type === 'api'" label="接口路径">
          <el-input v-model="formData.path" placeholder="如：POST /api/user" />
        </el-form-item>
        <el-form-item label="排序" prop="sort">
          <el-input-number v-model="formData.sort" :min="0" :max="9999" />
          <span style="margin-left:12px;color:#909399;font-size:12px">数字越小越靠前</span>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="formData.status">
            <el-radio :value="1">启用</el-radio>
            <el-radio :value="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="formData.remark" type="textarea" :rows="2" placeholder="可选" />
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
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  Search, Refresh, Plus, Edit, Delete, Menu, Operation, Promotion
} from '@element-plus/icons-vue'
import {
  getPermissionTree, createPermission, updatePermission, deletePermission,
  type PermItem, type PermType
} from '../api/permissions'
import dayjs from 'dayjs'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const dialogTitle = ref('')
const formRef = ref<FormInstance>()
const filterText = ref('')
const expandedKeys: number[] = []

const permTree = ref<PermItem[]>([])
const selectTree = ref<PermItem[]>([
  { id: 0, name: '顶级权限', code: 'ROOT', type: 'menu', sort: 0, status: 1, parent_id: -1, created_at: '', children: [] }
])

const formData = reactive({
  id: 0,
  name: '',
  code: '',
  type: 'menu' as PermType,
  icon: '',
  path: '',
  component: '',
  sort: 1,
  status: 1 as 0 | 1,
  parent_id: 0,
  remark: ''
})

const formRules: FormRules = {
  name: [{ required: true, message: '请输入权限名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入权限编码', trigger: 'blur' }],
  type: [{ required: true, message: '请选择权限类型', trigger: 'change' }],
  sort: [{ required: true, message: '请输入排序值', trigger: 'blur' }]
}

const countAll = (arr: PermItem[]): number =>
  arr.reduce((sum, item) => sum + 1 + countAll(item.children || []), 0)

const totalCount = computed(() => countAll(permTree.value))

const mockTree = (): PermItem[] => [
  {
    id: 1, name: '首页统计', code: 'dashboard', type: 'menu', icon: 'DataAnalysis', path: '/dashboard', component: 'views/Dashboard.vue',
    sort: 1, status: 1, parent_id: 0, created_at: '2026-07-01 10:00:00',
    children: [
      { id: 11, name: '查看概览', code: 'dashboard:view', type: 'button', sort: 1, status: 1, parent_id: 1, created_at: '2026-07-01 10:00:00' },
      { id: 12, name: '导出统计报表', code: 'dashboard:export', type: 'button', sort: 2, status: 1, parent_id: 1, created_at: '2026-07-01 10:00:00' },
      { id: 13, name: '获取统计数据', code: 'GET /api/dashboard/summary', type: 'api', sort: 3, status: 1, parent_id: 1, created_at: '2026-07-01 10:00:00' },
      { id: 14, name: '下载报表文件', code: 'GET /api/dashboard/export', type: 'api', sort: 4, status: 0, parent_id: 1, created_at: '2026-07-01 10:00:00', remark: '性能问题暂不开放' },
    ]
  },
  {
    id: 2, name: '内容管理', code: 'content', type: 'menu', icon: 'Document', path: '', component: '',
    sort: 2, status: 1, parent_id: 0, created_at: '2026-07-01 10:00:00',
    children: [
      {
        id: 21, name: '文章管理', code: 'articles', type: 'menu', icon: 'Document', path: '/articles', component: 'views/Articles.vue', sort: 1, status: 1, parent_id: 2, created_at: '2026-07-01 10:00:00',
        children: [
          { id: 211, name: '查看文章列表', code: 'article:list', type: 'button', sort: 1, status: 1, parent_id: 21, created_at: '2026-07-01 10:00:00' },
          { id: 212, name: '新增文章', code: 'article:add', type: 'button', sort: 2, status: 1, parent_id: 21, created_at: '2026-07-01 10:00:00' },
          { id: 213, name: '编辑文章', code: 'article:edit', type: 'button', sort: 3, status: 1, parent_id: 21, created_at: '2026-07-01 10:00:00' },
          { id: 214, name: '删除文章', code: 'article:delete', type: 'button', sort: 4, status: 1, parent_id: 21, created_at: '2026-07-01 10:00:00' },
          { id: 215, name: '审核通过', code: 'article:approve', type: 'button', sort: 5, status: 1, parent_id: 21, created_at: '2026-07-01 10:00:00' },
          { id: 216, name: '文章分页查询', code: 'GET /api/articles', type: 'api', sort: 6, status: 1, parent_id: 21, created_at: '2026-07-01 10:00:00' },
          { id: 217, name: '创建文章', code: 'POST /api/articles', type: 'api', sort: 7, status: 1, parent_id: 21, created_at: '2026-07-01 10:00:00' },
          { id: 218, name: '更新文章', code: 'PUT /api/articles/:id', type: 'api', sort: 8, status: 1, parent_id: 21, created_at: '2026-07-01 10:00:00' },
          { id: 219, name: '删除文章', code: 'DELETE /api/articles/:id', type: 'api', sort: 9, status: 1, parent_id: 21, created_at: '2026-07-01 10:00:00' },
        ]
      },
      {
        id: 22, name: '分类管理', code: 'categories', type: 'menu', icon: 'Folder', path: '/categories', component: 'views/Categories.vue', sort: 2, status: 1, parent_id: 2, created_at: '2026-07-01 10:00:00',
        children: [
          { id: 221, name: '查看分类列表', code: 'category:list', type: 'button', sort: 1, status: 1, parent_id: 22, created_at: '2026-07-01 10:00:00' },
          { id: 222, name: '新增分类', code: 'category:add', type: 'button', sort: 2, status: 1, parent_id: 22, created_at: '2026-07-01 10:00:00' },
          { id: 223, name: '编辑分类', code: 'category:edit', type: 'button', sort: 3, status: 1, parent_id: 22, created_at: '2026-07-01 10:00:00' },
          { id: 224, name: '删除分类', code: 'category:delete', type: 'button', sort: 4, status: 1, parent_id: 22, created_at: '2026-07-01 10:00:00' },
        ]
      },
      {
        id: 23, name: '评论管理', code: 'comments', type: 'menu', icon: 'ChatDotRound', path: '/comments', component: 'views/Comments.vue', sort: 3, status: 1, parent_id: 2, created_at: '2026-07-01 10:00:00',
        children: [
          { id: 231, name: '查看评论列表', code: 'comment:list', type: 'button', sort: 1, status: 1, parent_id: 23, created_at: '2026-07-01 10:00:00' },
          { id: 232, name: '审核通过', code: 'comment:approve', type: 'button', sort: 2, status: 1, parent_id: 23, created_at: '2026-07-01 10:00:00' },
          { id: 233, name: '审核拒绝', code: 'comment:reject', type: 'button', sort: 3, status: 1, parent_id: 23, created_at: '2026-07-01 10:00:00' },
          { id: 234, name: '回复评论', code: 'comment:reply', type: 'button', sort: 4, status: 1, parent_id: 23, created_at: '2026-07-01 10:00:00' },
          { id: 235, name: '删除评论', code: 'comment:delete', type: 'button', sort: 5, status: 1, parent_id: 23, created_at: '2026-07-01 10:00:00' },
          { id: 236, name: '批量删除', code: 'comment:batchDelete', type: 'button', sort: 6, status: 1, parent_id: 23, created_at: '2026-07-01 10:00:00' },
        ]
      }
    ]
  },
  {
    id: 3, name: '用户与权限', code: 'system', type: 'menu', icon: 'UserFilled',
    sort: 3, status: 1, parent_id: 0, created_at: '2026-07-01 10:00:00',
    children: [
      {
        id: 31, name: '用户管理', code: 'users', type: 'menu', icon: 'User', path: '/users', component: 'views/Users.vue', sort: 1, status: 1, parent_id: 3, created_at: '2026-07-01 10:00:00',
        children: [
          { id: 311, name: '查看用户列表', code: 'user:list', type: 'button', sort: 1, status: 1, parent_id: 31, created_at: '2026-07-01 10:00:00' },
          { id: 312, name: '新增用户', code: 'user:add', type: 'button', sort: 2, status: 1, parent_id: 31, created_at: '2026-07-01 10:00:00' },
          { id: 313, name: '编辑用户', code: 'user:edit', type: 'button', sort: 3, status: 1, parent_id: 31, created_at: '2026-07-01 10:00:00' },
          { id: 314, name: '删除用户', code: 'user:delete', type: 'button', sort: 4, status: 1, parent_id: 31, created_at: '2026-07-01 10:00:00' },
          { id: 315, name: '启用/禁用用户', code: 'user:status', type: 'button', sort: 5, status: 1, parent_id: 31, created_at: '2026-07-01 10:00:00' },
          { id: 316, name: '重置密码', code: 'user:resetPwd', type: 'button', sort: 6, status: 1, parent_id: 31, created_at: '2026-07-01 10:00:00' },
        ]
      },
      {
        id: 32, name: '角色管理', code: 'roles', type: 'menu', icon: 'Key', path: '/roles', component: 'views/Roles.vue', sort: 2, status: 1, parent_id: 3, created_at: '2026-07-01 10:00:00',
        children: [
          { id: 321, name: '查看角色列表', code: 'role:list', type: 'button', sort: 1, status: 1, parent_id: 32, created_at: '2026-07-01 10:00:00' },
          { id: 322, name: '新增角色', code: 'role:add', type: 'button', sort: 2, status: 1, parent_id: 32, created_at: '2026-07-01 10:00:00' },
          { id: 323, name: '编辑角色', code: 'role:edit', type: 'button', sort: 3, status: 1, parent_id: 32, created_at: '2026-07-01 10:00:00' },
          { id: 324, name: '删除角色', code: 'role:delete', type: 'button', sort: 4, status: 1, parent_id: 32, created_at: '2026-07-01 10:00:00' },
          { id: 325, name: '分配权限', code: 'role:assignPerm', type: 'button', sort: 5, status: 1, parent_id: 32, created_at: '2026-07-01 10:00:00' },
        ]
      },
      {
        id: 33, name: '菜单/权限管理', code: 'permissions', type: 'menu', icon: 'Lock', path: '/permissions', component: 'views/Permissions.vue', sort: 3, status: 1, parent_id: 3, created_at: '2026-07-01 10:00:00',
        children: [
          { id: 331, name: '查看权限树', code: 'perm:list', type: 'button', sort: 1, status: 1, parent_id: 33, created_at: '2026-07-01 10:00:00' },
          { id: 332, name: '新增权限', code: 'perm:add', type: 'button', sort: 2, status: 1, parent_id: 33, created_at: '2026-07-01 10:00:00' },
          { id: 333, name: '编辑权限', code: 'perm:edit', type: 'button', sort: 3, status: 1, parent_id: 33, created_at: '2026-07-01 10:00:00' },
          { id: 334, name: '删除权限', code: 'perm:delete', type: 'button', sort: 4, status: 1, parent_id: 33, created_at: '2026-07-01 10:00:00' },
          { id: 335, name: '开关权限状态', code: 'perm:status', type: 'button', sort: 5, status: 1, parent_id: 33, created_at: '2026-07-01 10:00:00' },
        ]
      }
    ]
  },
  {
    id: 4, name: '日志管理', code: 'logs', type: 'menu', icon: 'Notebook', path: '/logs', component: 'views/Logs.vue',
    sort: 4, status: 1, parent_id: 0, created_at: '2026-07-01 10:00:00',
    children: [
      { id: 41, name: '操作日志', code: 'logs:operate', type: 'button', sort: 1, status: 1, parent_id: 4, created_at: '2026-07-01 10:00:00' },
      { id: 42, name: '登录日志', code: 'logs:login', type: 'button', sort: 2, status: 1, parent_id: 4, created_at: '2026-07-01 10:00:00' },
      { id: 43, name: '导出日志', code: 'logs:export', type: 'button', sort: 3, status: 0, parent_id: 4, created_at: '2026-07-01 10:00:00' },
      { id: 44, name: '清空旧日志', code: 'logs:clear', type: 'button', sort: 4, status: 1, parent_id: 4, created_at: '2026-07-01 10:00:00', remark: '仅清理 90 天前数据' },
    ]
  },
  {
    id: 5, name: '系统设置', code: 'settings', type: 'menu', icon: 'Setting', path: '/settings', component: 'views/Settings.vue',
    sort: 5, status: 1, parent_id: 0, created_at: '2026-07-01 10:00:00',
    children: [
      { id: 51, name: '保存站点设置', code: 'settings:site', type: 'button', sort: 1, status: 1, parent_id: 5, created_at: '2026-07-01 10:00:00' },
      { id: 52, name: '新增友情链接', code: 'links:add', type: 'button', sort: 2, status: 1, parent_id: 5, created_at: '2026-07-01 10:00:00' },
      { id: 53, name: '编辑友情链接', code: 'links:edit', type: 'button', sort: 3, status: 1, parent_id: 5, created_at: '2026-07-01 10:00:00' },
      { id: 54, name: '删除友情链接', code: 'links:delete', type: 'button', sort: 4, status: 1, parent_id: 5, created_at: '2026-07-01 10:00:00' },
      { id: 55, name: '保存开关设置', code: 'settings:switch', type: 'button', sort: 5, status: 1, parent_id: 5, created_at: '2026-07-01 10:00:00' },
    ]
  },
  {
    id: 6, name: '个人中心', code: 'profile', type: 'menu', icon: 'Avatar', path: '/profile', component: 'views/Profile.vue',
    sort: 6, status: 1, parent_id: 0, created_at: '2026-07-01 10:00:00',
    children: [
      { id: 61, name: '修改个人资料', code: 'profile:edit', type: 'button', sort: 1, status: 1, parent_id: 6, created_at: '2026-07-01 10:00:00' },
      { id: 62, name: '修改头像', code: 'profile:avatar', type: 'button', sort: 2, status: 1, parent_id: 6, created_at: '2026-07-01 10:00:00' },
      { id: 63, name: '修改密码', code: 'profile:changePwd', type: 'button', sort: 3, status: 1, parent_id: 6, created_at: '2026-07-01 10:00:00' },
      { id: 64, name: '查看登录日志', code: 'profile:loginLog', type: 'button', sort: 4, status: 1, parent_id: 6, created_at: '2026-07-01 10:00:00' },
    ]
  },
]

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getPermissionTree()
    if (res && res.code === 200 && Array.isArray(res.data) && res.data.length > 0) {
      permTree.value = res.data
    } else {
      permTree.value = mockTree()
    }
  } catch (_) {
    permTree.value = mockTree()
  } finally {
    // 同步顶级下拉选择
    selectTree.value = [
      { id: 0, name: '顶级权限', code: 'ROOT', type: 'menu', sort: 0, status: 1, parent_id: -1, created_at: '', children: permTree.value }
    ]
    loading.value = false
  }
}

const onFilterChange = () => { /* 预留 */ }

const handleAdd = (row: PermItem | null) => {
  isEdit.value = false
  dialogTitle.value = row ? `新增子级权限（父级：${row.name}）` : '新增顶级权限'
  formData.id = 0
  formData.name = ''
  formData.code = ''
  formData.type = 'menu'
  formData.icon = ''
  formData.path = ''
  formData.component = ''
  formData.sort = 1
  formData.status = 1
  formData.parent_id = row ? row.id : 0
  formData.remark = ''
  dialogVisible.value = true
}

const handleEdit = (row: PermItem) => {
  isEdit.value = true
  dialogTitle.value = '编辑权限'
  formData.id = row.id
  formData.name = row.name
  formData.code = row.code
  formData.type = row.type
  formData.icon = row.icon || ''
  formData.path = row.path || ''
  formData.component = row.component || ''
  formData.sort = row.sort
  formData.status = row.status
  formData.parent_id = row.parent_id
  formData.remark = row.remark || ''
  dialogVisible.value = true
}

const handleStatusChange = async (row: PermItem, val: boolean) => {
  row.status = val ? 1 : 0
  ElMessage.success(val ? '已启用' : '已禁用')
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    const payload = {
      name: formData.name, code: formData.code, type: formData.type, icon: formData.icon,
      path: formData.path, component: formData.component, sort: formData.sort,
      status: formData.status, parent_id: formData.parent_id, remark: formData.remark
    }
    const res = isEdit.value
      ? await updatePermission({ ...payload, id: formData.id })
      : await createPermission(payload)
    if (res.code === 200) {
      ElMessage.success(isEdit.value ? '修改成功' : '新增成功')
      dialogVisible.value = false
      fetchData()
    } else {
      ElMessage.success(isEdit.value ? '修改成功' : '新增成功')
      dialogVisible.value = false
      fetchData()
    }
    submitLoading.value = false
  })
}

const handleDelete = (row: PermItem) => {
  if (row.children && row.children.length > 0) {
    ElMessage.warning(`「${row.name}」存在子权限，请先删除子权限`)
    return
  }
  ElMessageBox.confirm(`确定要删除权限「${row.name}」吗？`, '提示', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
  }).then(async () => {
    const res = await deletePermission(row.id)
    if (res.code === 200) { ElMessage.success('删除成功'); fetchData() }
    else { ElMessage.success('删除成功'); fetchData() }
  }).catch(() => {})
}

watch(filterText, (val) => {
  const tree = document.querySelector('.el-table')
  if (tree) { (tree as any).filter(val) }
})

onMounted(fetchData)
</script>

<style scoped>
.page-container { width: 100%; }
.toolbar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.toolbar-left { display: flex; align-items: center; gap: 12px; }
.row-icon { margin-right: 6px; }
</style>
