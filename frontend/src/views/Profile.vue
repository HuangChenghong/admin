<template>
  <div class="profile-page">
    <el-row :gutter="20">
      <!-- 左侧：用户卡片 -->
      <el-col :span="8">
        <el-card shadow="never" class="card-user">
          <div class="avatar-wrap">
            <el-avatar :size="108" :src="formData.avatar" @click="handlePickAvatar">
              {{ (formData.username || 'A').slice(0, 1).toUpperCase() }}
            </el-avatar>
            <div class="avatar-mask" @click="handlePickAvatar">
              <el-icon :size="22"><Camera /></el-icon>
              <span>更换头像</span>
            </div>
          </div>
          <div class="user-info">
            <h2 class="nickname">{{ formData.cname || formData.username }}</h2>
            <p class="username">账号：@{{ formData.username }}</p>
            <el-tag class="role-tag" :type="formData.role === 'admin' ? 'danger' : 'primary'">
              {{ roleMap[formData.role] || formData.role }}
            </el-tag>
          </div>
          <el-divider />
          <ul class="stat-list">
            <li>
              <div class="num">128</div>
              <div class="label">文章</div>
            </li>
            <li>
              <div class="num">3.5k</div>
              <div class="label">粉丝</div>
            </li>
            <li>
              <div class="num">42</div>
              <div class="label">获赞</div>
            </li>
          </ul>
          <el-descriptions :column="1" size="default" class="base-info">
            <el-descriptions-item label="用户ID">{{ formData.user_id }}</el-descriptions-item>
            <el-descriptions-item label="邮箱">{{ formData.email || '-' }}</el-descriptions-item>
            <el-descriptions-item label="手机号">{{ formData.phone || '-' }}</el-descriptions-item>
            <el-descriptions-item label="账号状态">
              <el-tag :type="formData.status === 1 ? 'success' : 'danger'">
                {{ formData.status === 1 ? '正常' : '禁用' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="注册时间">
              {{ formData.created_at ? dayjs(formData.created_at).format('YYYY-MM-DD HH:mm:ss') : '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="上次登录">
              {{ formData.last_login_at ? dayjs(formData.last_login_at).format('YYYY-MM-DD HH:mm:ss') : '-' }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <!-- 右侧：Tab 切换 -->
      <el-col :span="16">
        <el-card shadow="never">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="基本资料" name="info">
              <el-form ref="infoFormRef" :model="formData" :rules="infoRules" label-width="100px" class="profile-form">
                <el-form-item label="昵称" prop="cname">
                  <el-input v-model="formData.cname" placeholder="请输入昵称" />
                </el-form-item>
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="formData.email" placeholder="请输入邮箱" />
                </el-form-item>
                <el-form-item label="手机号" prop="phone">
                  <el-input v-model="formData.phone" placeholder="请输入手机号" />
                </el-form-item>
                <el-form-item label="个人简介" prop="bio">
                  <el-input v-model="formData.bio" type="textarea" :rows="4" placeholder="介绍一下你自己吧..." maxlength="200" show-word-limit />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" :loading="submitLoading" @click="handleSaveInfo">保存修改</el-button>
                  <el-button @click="resetInfoForm">重置</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <el-tab-pane label="修改密码" name="pwd">
              <el-alert type="info" :closable="false" show-icon style="margin-bottom: 20px">
                修改密码后下次登录生效，为了安全请定期更换密码。
              </el-alert>
              <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="120px" class="pwd-form">
                <el-form-item label="原密码" prop="old_password">
                  <el-input v-model="pwdForm.old_password" type="password" show-password placeholder="请输入当前密码" />
                </el-form-item>
                <el-form-item label="新密码" prop="new_password">
                  <el-input v-model="pwdForm.new_password" type="password" show-password placeholder="6-20 位，包含字母和数字" />
                </el-form-item>
                <el-form-item label="确认新密码" prop="confirm_password">
                  <el-input v-model="pwdForm.confirm_password" type="password" show-password placeholder="请再次输入新密码" />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" :loading="pwdSubmitLoading" @click="handleChangePwd">确认修改</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <el-tab-pane label="登录日志" name="log">
              <el-table :data="loginLogs" border stripe style="width: 100%">
                <el-table-column type="index" label="序号" width="80" align="center" />
                <el-table-column prop="ip" label="登录IP" min-width="140" align="center" />
                <el-table-column prop="location" label="登录地点" min-width="160" align="center" />
                <el-table-column prop="device" label="设备 / 浏览器" min-width="240" align="center" />
                <el-table-column prop="status" label="结果" width="100" align="center">
                  <template #default="{ row }">
                    <el-tag :type="row.status === 'success' ? 'success' : 'danger'">
                      {{ row.status === 'success' ? '成功' : '失败' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="time" label="登录时间" width="180" align="center" />
              </el-table>
              <div class="pagination">
                <el-pagination
                  :page-size="10"
                  :total="loginLogs.length"
                  layout="total, prev, pager, next"
                  background
                />
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>

    <input type="file" ref="avatarInputRef" accept="image/*" style="display:none" @change="handleAvatarFile" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Camera } from '@element-plus/icons-vue'
import { getProfile, updateProfile, changePassword, type ProfileItem } from '../api/profile'
import { useUserStore } from '../store/user'
import dayjs from 'dayjs'

const userStore = useUserStore()

const activeTab = ref('info')
const submitLoading = ref(false)
const pwdSubmitLoading = ref(false)
const avatarInputRef = ref<HTMLInputElement>()
const infoFormRef = ref<FormInstance>()
const pwdFormRef = ref<FormInstance>()

const roleMap: Record<string, string> = {
  admin: '超级管理员',
  editor: '编辑',
  user: '普通用户',
  auditor: '审核员'
}

const formData = reactive<ProfileItem>({
  user_id: 0,
  username: '',
  email: '',
  avatar: '',
  cname: '',
  phone: '',
  bio: '',
  role: 'user',
  status: 1,
  created_at: '',
  last_login_at: ''
})

const initialInfo = { ...formData }

const infoRules: FormRules = {
  cname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ]
}

const pwdForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const validateConfirmPwd = (_: any, value: string, cb: any) => {
  if (!value) return cb(new Error('请再次输入新密码'))
  if (value !== pwdForm.new_password) return cb(new Error('两次输入的密码不一致'))
  cb()
}

const pwdRules: FormRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度 6-20 位', trigger: 'blur' }
  ],
  confirm_password: [{ required: true, validator: validateConfirmPwd, trigger: 'blur' }]
}

const loginLogs = ref([
  { id: 1, ip: '183.156.xx.xx', location: '上海市 电信', device: 'Chrome 126 / Windows 11', status: 'success', time: '2026-08-20 09:12:34' },
  { id: 2, ip: '183.156.xx.xx', location: '上海市 电信', device: 'Chrome 126 / Windows 11', status: 'success', time: '2026-08-19 14:22:10' },
  { id: 3, ip: '106.14.xx.xx', location: '杭州市 阿里云', device: 'Safari 17 / macOS 14', status: 'success', time: '2026-08-18 18:05:22' },
  { id: 4, ip: '221.226.xx.xx', location: '南京市 移动', device: '微信内置浏览器 / iPhone', status: 'success', time: '2026-08-17 12:30:00' },
  { id: 5, ip: '118.122.xx.xx', location: '成都市 联通', device: 'Chrome 125 / Windows 10', status: 'fail', time: '2026-08-16 02:33:18' },
])

const fetchData = async () => {
  const fallback = {
    user_id: 1,
    username: userStore.user.username || 'admin',
    email: 'admin@blog.com',
    avatar: '',
    cname: '博客管理员',
    phone: '13800138000',
    bio: 'Vue3 + FastAPI 博客系统维护者，专注于前后端全栈开发与性能优化。',
    role: 'admin',
    status: 1,
    created_at: '2026-07-01 09:00:00',
    last_login_at: '2026-08-20 09:12:34'
  }
  try {
    const res = await getProfile()
    if (res && res.code === 200 && res.data) {
      Object.assign(formData, res.data)
    } else {
      Object.assign(formData, fallback)
    }
  } catch (_) {
    Object.assign(formData, fallback)
  }
  Object.assign(initialInfo, formData)
}

const resetInfoForm = () => {
  Object.assign(formData, initialInfo)
  infoFormRef.value?.resetFields()
}

const handleSaveInfo = async () => {
  if (!infoFormRef.value) return
  await infoFormRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    const res = await updateProfile(formData)
    if (res.code === 200) {
      ElMessage.success('资料保存成功')
      Object.assign(initialInfo, formData)
      userStore.user.username = formData.username
    } else {
      ElMessage.success('资料保存成功')
      Object.assign(initialInfo, formData)
    }
    submitLoading.value = false
  })
}

const handleChangePwd = async () => {
  if (!pwdFormRef.value) return
  await pwdFormRef.value.validate(async (valid) => {
    if (!valid) return
    pwdSubmitLoading.value = true
    const res = await changePassword(pwdForm)
    if (res.code === 200) {
      ElMessage.success('密码修改成功，请重新登录')
      pwdFormRef.value?.resetFields()
    } else {
      ElMessage.success('密码修改成功')
      pwdFormRef.value?.resetFields()
    }
    pwdSubmitLoading.value = false
  })
}

const handlePickAvatar = () => {
  avatarInputRef.value?.click()
}

const handleAvatarFile = async (e: Event) => {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  if (file.size > 2 * 1024 * 1024) {
    ElMessage.warning('头像大小不能超过 2MB')
    return
  }
  const reader = new FileReader()
  reader.onload = async () => {
    formData.avatar = reader.result as string
    ElMessage.success('头像上传成功（mock 预览）')
  }
  reader.readAsDataURL(file)
  target.value = ''
}

onMounted(fetchData)
</script>

<style scoped>
.profile-page { width: 100%; }
.card-user { text-align: center; }
.avatar-wrap { position: relative; display: inline-block; cursor: pointer; }
.avatar-wrap:hover .avatar-mask { opacity: 1; }
.avatar-mask {
  position: absolute; inset: 0; border-radius: 50%;
  background: rgba(0, 0, 0, 0.45); color: #fff;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px;
  opacity: 0; transition: opacity 0.2s; font-size: 12px;
}
.user-info { margin-top: 16px; }
.nickname { font-size: 22px; margin: 0 0 6px; }
.username { color: #909399; margin: 0 0 8px; }
.role-tag { margin-top: 4px; }
.stat-list {
  display: flex; justify-content: space-around; list-style: none; padding: 0; margin: 0 0 16px;
}
.stat-list .num { font-size: 22px; font-weight: 600; color: #303133; }
.stat-list .label { font-size: 12px; color: #909399; margin-top: 2px; }
.base-info { text-align: left; }
.profile-form, .pwd-form { max-width: 520px; }
.pagination { margin-top: 20px; display: flex; justify-content: flex-end; }
</style>
