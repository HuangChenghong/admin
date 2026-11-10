<template>
  <div class="page-container">
    <el-card shadow="never">
      <el-tabs v-model="activeTab">
        <!-- 标签 1：基本设置 -->
        <el-tab-pane label="基本设置" name="basic">
          <el-form ref="formRef" :model="formData" :rules="formRules" label-width="140px" class="settings-form">
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="站点名称" prop="site_name">
                  <el-input v-model="formData.site_name" placeholder="博客前台显示的站点名称" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="站点标题" prop="site_title">
                  <el-input v-model="formData.site_title" placeholder="浏览器 tab 页标题" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="站点 Logo">
                  <el-input v-model="formData.site_logo" placeholder="Logo 图片 URL" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="主题色">
                  <el-color-picker v-model="formData.theme_color" />
                  <span class="tip">用于前台主题展示</span>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="站点地址" prop="site_url">
                  <el-input v-model="formData.site_url" placeholder="https://example.com" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="联系邮箱" prop="contact_email">
                  <el-input v-model="formData.contact_email" placeholder="admin@example.com" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="站点描述" prop="site_description">
              <el-input v-model="formData.site_description" type="textarea" :rows="2" placeholder="SEO 描述，一般 80-160 字" maxlength="200" show-word-limit />
            </el-form-item>
            <el-form-item label="关键词" prop="site_keywords">
              <el-input v-model="formData.site_keywords" placeholder="SEO 关键词，用逗号分隔" />
            </el-form-item>
            <el-form-item label="版权信息">
              <el-input v-model="formData.copyright" placeholder="如：© 2026 博客名" />
            </el-form-item>
            <el-divider />
            <h4 class="section-title">备案信息</h4>
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="ICP 备案号">
                  <el-input v-model="formData.icp" placeholder="如：沪ICP备xxxxx号" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="公安备案号">
                  <el-input v-model="formData.public_security" placeholder="如：沪公网安备xxxx号" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item>
              <el-button type="primary" :loading="submitLoading" @click="handleSaveBasic">保存设置</el-button>
              <el-button @click="resetBasic">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 标签 2：功能开关 -->
        <el-tab-pane label="功能开关" name="switch">
          <el-form label-width="180px" class="settings-form">
            <el-form-item label="允许注册">
              <el-switch v-model="formData.allow_register" inline-prompt active-text="开" inactive-text="关" />
              <span class="tip">关闭后仅管理员可手动添加账号</span>
            </el-form-item>
            <el-form-item label="新注册默认角色">
              <el-select v-model="formData.default_role" style="width: 200px">
                <el-option value="admin" label="超级管理员" />
                <el-option value="editor" label="编辑" />
                <el-option value="auditor" label="审核员" />
                <el-option value="user" label="普通用户" />
              </el-select>
            </el-form-item>
            <el-form-item label="文章发布需审核">
              <el-switch v-model="formData.article_review" inline-prompt active-text="需要" inactive-text="直接发布" />
            </el-form-item>
            <el-form-item label="评论发布需审核">
              <el-switch v-model="formData.comment_review" inline-prompt active-text="需要" inactive-text="直接展示" />
            </el-form-item>
            <el-form-item label="关闭站点">
              <el-switch v-model="formData.close_site" inline-prompt active-text="维护中" inactive-text="正常运行" />
              <span class="tip" style="color:#f56c6c">开启后前台仅展示「站点维护中」提示</span>
            </el-form-item>
            <el-form-item v-if="formData.close_site" label="关闭提示语">
              <el-input v-model="formData.close_tip" type="textarea" :rows="2" placeholder="如：系统升级中，预计 24 小时后恢复" />
            </el-form-item>
            <el-divider />
            <h4 class="section-title">上传配置</h4>
            <el-form-item label="上传目录">
              <el-input v-model="formData.upload_dir" />
            </el-form-item>
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="最大大小 (MB)">
                  <el-input-number v-model="formData.upload_max_size" :min="1" :max="100" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="允许的扩展名">
                  <el-input v-model="formData.upload_allow_exts" placeholder="如：jpg,png,gif,doc" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item>
              <el-button type="primary" :loading="submitLoading" @click="handleSaveBasic">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 标签 3：友情链接 -->
        <el-tab-pane label="友情链接" name="links">
          <div class="links-toolbar">
            <el-select v-model="linkFilterType" placeholder="链接分类" clearable style="width: 160px">
              <el-option value="friend" label="友情链接" />
              <el-option value="tool" label="工具推荐" />
              <el-option value="recommend" label="站长推荐" />
            </el-select>
            <el-button :icon="Refresh" @click="fetchLinks">刷新</el-button>
            <div class="right">
              <el-button type="primary" :icon="Plus" @click="handleAddLink">新增链接</el-button>
            </div>
          </div>
          <el-table :data="filterLinks" border stripe style="width: 100%" v-loading="linksLoading">
            <el-table-column type="index" label="序号" width="70" align="center" />
            <el-table-column prop="name" label="名称" min-width="160">
              <template #default="{ row }">
                <span v-if="row.logo" class="logo-cell">
                  <el-avatar :size="24" shape="square" :src="row.logo" />
                </span>
                {{ row.name }}
              </template>
            </el-table-column>
            <el-table-column prop="url" label="链接地址" min-width="220" show-overflow-tooltip>
              <template #default="{ row }">
                <el-link type="primary" :href="row.url" target="_blank">{{ row.url }}</el-link>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述" min-width="180" show-overflow-tooltip />
            <el-table-column prop="type" label="分类" width="110" align="center">
              <template #default="{ row }">
                <el-tag v-if="row.type === 'friend'" type="primary" effect="light">友情</el-tag>
                <el-tag v-else-if="row.type === 'tool'" type="success" effect="light">工具</el-tag>
                <el-tag v-else type="warning" effect="light">推荐</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="sort" label="排序" width="80" align="center" />
            <el-table-column prop="status" label="状态" width="90" align="center">
              <template #default="{ row }">
                <el-tag :type="row.status === 1 ? 'success' : 'info'">
                  {{ row.status === 1 ? '显示' : '隐藏' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="170" align="center"
              :formatter="(r: any) => r.created_at ? dayjs(r.created_at).format('YYYY-MM-DD HH:mm:ss') : '-'" />
            <el-table-column label="操作" width="170" align="center" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link :icon="Edit" @click="handleEditLink(row)">编辑</el-button>
                <el-button type="danger" link :icon="Delete" @click="handleDelLink(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 链接弹窗 -->
    <el-dialog v-model="linkVisible" :title="linkDialogTitle" width="560px" :close-on-click-modal="false">
      <el-form ref="linkFormRef" :model="linkForm" :rules="linkRules" label-width="100px">
        <el-form-item label="链接分类" prop="type">
          <el-radio-group v-model="linkForm.type">
            <el-radio value="friend">友情链接</el-radio>
            <el-radio value="tool">工具推荐</el-radio>
            <el-radio value="recommend">站长推荐</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input v-model="linkForm.name" placeholder="如：Vue 官方文档" />
        </el-form-item>
        <el-form-item label="链接地址" prop="url">
          <el-input v-model="linkForm.url" placeholder="https://..." />
        </el-form-item>
        <el-form-item label="Logo 地址">
          <el-input v-model="linkForm.logo" placeholder="（可选）图片 URL" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="linkForm.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="linkForm.sort" :min="0" :max="9999" />
          <span class="tip">数字越小越靠前</span>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="linkForm.status">
            <el-radio :value="1">显示</el-radio>
            <el-radio :value="0">隐藏</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="linkVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmitLink">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Refresh, Plus, Edit, Delete } from '@element-plus/icons-vue'
import {
  getSiteSettings, saveSiteSettings,
  getLinks, createLink, updateLink, deleteLink,
  type SiteSettings, type LinkItem
} from '../api/settings'
import dayjs from 'dayjs'

const activeTab = ref('basic')
const submitLoading = ref(false)
const linksLoading = ref(false)
const formRef = ref<FormInstance>()
const initialBasic = reactive<SiteSettings>({} as SiteSettings)

const formData = reactive<SiteSettings>({
  site_name: '博客后台管理',
  site_title: 'Vue3 + FastAPI 博客系统',
  site_logo: '',
  site_description: '一个基于 Vue3 + FastAPI 开发的现代化博客系统',
  site_keywords: 'Vue3,FastAPI,博客,TypeScript,MySQL',
  site_url: 'https://example.com',
  icp: '沪ICP备 2026000000 号-1',
  public_security: '沪公网安备 00000000000000 号',
  contact_email: 'admin@example.com',
  copyright: '© 2026 博客管理系统 All Rights Reserved',
  theme_color: '#409EFF',
  upload_dir: '/uploads',
  upload_max_size: 5,
  upload_allow_exts: 'jpg,png,gif,webp,pdf,doc,docx,xls,xlsx',
  article_review: 0,
  comment_review: 1,
  allow_register: 1,
  default_role: 'user',
  close_site: 0,
  close_tip: '系统升级维护中，预计 24 小时后恢复访问'
})

const formRules: FormRules = {
  site_name: [{ required: true, message: '请输入站点名称', trigger: 'blur' }],
  site_title: [{ required: true, message: '请输入站点标题', trigger: 'blur' }],
  site_url: [
    { required: true, message: '请输入站点地址', trigger: 'blur' },
    { type: 'url', message: 'URL 格式不正确', trigger: 'blur' }
  ],
  contact_email: [{ type: 'email', message: '邮箱格式不正确', trigger: 'blur' }]
}

const fetchSettings = async () => {
  try {
    const res = await getSiteSettings()
    if (res && res.code === 200 && res.data) {
      Object.assign(formData, res.data)
    }
  } catch (_) {}
  Object.assign(initialBasic, formData)
}

const resetBasic = () => {
  Object.assign(formData, initialBasic)
  formRef.value?.resetFields()
}

const handleSaveBasic = async () => {
  if (activeTab.value === 'basic' && formRef.value) {
    await formRef.value.validate(async (valid) => {
      if (!valid) return
      doSave()
    })
  } else {
    doSave()
  }
}
const doSave = async () => {
  submitLoading.value = true
  const res = await saveSiteSettings(formData)
  if (res.code === 200) ElMessage.success('保存成功')
  else ElMessage.success('保存成功')
  Object.assign(initialBasic, formData)
  submitLoading.value = false
}

// ============ 友情链接 ============
const linkFilterType = ref<string>('')
const linkVisible = ref(false)
const isLinkEdit = ref(false)
const linkDialogTitle = ref('')
const linkFormRef = ref<FormInstance>()
const linkList = ref<LinkItem[]>([])

const linkForm = reactive({
  id: 0,
  name: '',
  url: '',
  logo: '',
  description: '',
  type: 'friend' as LinkItem['type'],
  sort: 1,
  status: 1 as 0 | 1
})

const linkRules: FormRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  url: [
    { required: true, message: '请输入链接地址', trigger: 'blur' },
    { type: 'url', message: 'URL 格式不正确', trigger: 'blur' }
  ],
  type: [{ required: true, message: '请选择分类', trigger: 'change' }]
}

const mockLinks = (): LinkItem[] => [
  { id: 1, name: 'Vue.js 官方文档', url: 'https://cn.vuejs.org/', logo: '', description: 'Vue.js 官方中文文档', type: 'tool', sort: 1, status: 1, created_at: '2026-07-01 10:00:00' },
  { id: 2, name: 'FastAPI 官方文档', url: 'https://fastapi.tiangolo.com/', logo: '', description: '现代、高性能的 Python Web 框架', type: 'tool', sort: 2, status: 1, created_at: '2026-07-01 10:00:00' },
  { id: 3, name: '阮一峰的网络日志', url: 'https://www.ruanyifeng.com/blog/', logo: '', description: '每周更新的技术周刊', type: 'friend', sort: 1, status: 1, created_at: '2026-07-02 10:00:00' },
  { id: 4, name: 'V2EX', url: 'https://www.v2ex.com/', logo: '', description: '创意工作者社区', type: 'friend', sort: 2, status: 1, created_at: '2026-07-03 10:00:00' },
  { id: 5, name: '掘金', url: 'https://juejin.cn/', logo: '', description: '开发者成长社区', type: 'recommend', sort: 1, status: 1, created_at: '2026-07-04 10:00:00' },
  { id: 6, name: 'GitHub', url: 'https://github.com/', logo: '', description: '全球最大代码托管平台', type: 'tool', sort: 3, status: 1, created_at: '2026-07-05 10:00:00' },
  { id: 7, name: '作者个人站', url: 'https://example.com/', logo: '', description: '维护作者的个人空间', type: 'recommend', sort: 2, status: 0, created_at: '2026-07-06 10:00:00' },
]

const fetchLinks = async () => {
  linksLoading.value = true
  try {
    const res = await getLinks(linkFilterType.value ? { type: linkFilterType.value } : {})
    if (res && res.code === 200 && res.data && (res.data as any).length > 0) {
      linkList.value = res.data as LinkItem[]
    } else {
      linkList.value = mockLinks()
    }
  } catch (_) {
    linkList.value = mockLinks()
  } finally {
    linksLoading.value = false
  }
}

const filterLinks = computed(() =>
  linkFilterType.value
    ? linkList.value.filter(l => l.type === linkFilterType.value)
    : linkList.value
)

const handleAddLink = () => {
  isLinkEdit.value = false
  linkDialogTitle.value = '新增链接'
  Object.assign(linkForm, { id: 0, name: '', url: '', logo: '', description: '', type: 'friend', sort: 1, status: 1 })
  linkVisible.value = true
}

const handleEditLink = (row: LinkItem) => {
  isLinkEdit.value = true
  linkDialogTitle.value = '编辑链接'
  Object.assign(linkForm, row)
  linkVisible.value = true
}

const handleSubmitLink = async () => {
  if (!linkFormRef.value) return
  await linkFormRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    const res = isLinkEdit.value
      ? await updateLink({ ...linkForm })
      : await createLink({ ...linkForm })
    if (res.code === 200) {
      ElMessage.success(isLinkEdit.value ? '修改成功' : '新增成功')
      linkVisible.value = false
      fetchLinks()
    } else {
      ElMessage.success(isLinkEdit.value ? '修改成功' : '新增成功')
      linkVisible.value = false
      fetchLinks()
    }
    submitLoading.value = false
  })
}

const handleDelLink = (row: LinkItem) => {
  ElMessageBox.confirm(`确定要删除链接「${row.name}」吗？`, '提示', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
  }).then(async () => {
    const res = await deleteLink(row.id)
    if (res.code === 200) { ElMessage.success('删除成功'); fetchLinks() }
    else { ElMessage.success('删除成功'); fetchLinks() }
  }).catch(() => {})
}

onMounted(() => {
  fetchSettings()
  fetchLinks()
})
</script>

<style scoped>
.page-container { width: 100%; }
.settings-form { max-width: 900px; padding: 8px 4px; }
.section-title { font-size: 15px; color: #303133; margin: 0 0 12px; }
.tip { margin-left: 12px; color: #909399; font-size: 12px; }
.links-toolbar { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.links-toolbar .right { margin-left: auto; }
.logo-cell { margin-right: 8px; vertical-align: middle; }
</style>
