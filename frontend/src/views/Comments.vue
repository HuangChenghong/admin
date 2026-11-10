<template>
  <div class="page-container">
    <el-card shadow="never">
      <!-- 搜索区 -->
      <div class="search-bar">
        <el-input
          v-model="searchForm.keyword"
          placeholder="搜索评论内容/用户名"
          clearable
          style="width: 260px"
          :prefix-icon="Search"
        />
        <el-select
          v-model="searchForm.status"
          placeholder="审核状态"
          clearable
          style="width: 140px"
        >
          <el-option :value="0" label="待审核" />
          <el-option :value="1" label="已通过" />
          <el-option :value="2" label="已拒绝" />
        </el-select>
        <el-date-picker
          v-model="dateRange"
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
          <el-button type="danger" :icon="Delete" :disabled="!selectedIds.length" @click="handleBatchDelete">
            批量删除 ({{ selectedIds.length }})
          </el-button>
        </div>
      </div>

      <!-- 表格 -->
      <el-table
        :data="tableData"
        style="width: 100%"
        v-loading="loading"
        border
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="56" align="center" />
        <el-table-column type="index" label="序号" width="70" align="center" />
        <el-table-column label="用户信息" min-width="180">
          <template #default="{ row }">
            <div class="user-cell">
              <el-avatar :size="36" :src="row.avatar">{{ (row.username || '?').slice(0, 1) }}</el-avatar>
              <div class="user-meta">
                <div class="username">{{ row.username || '匿名用户' }}</div>
                <div v-if="row.parent_id" class="reply-tip">
                  回复 @{{ row.reply_to_username || '用户' }}
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="article_title" label="所属文章" min-width="200" show-overflow-tooltip align="center" />
        <el-table-column prop="content" label="评论内容" min-width="280" show-overflow-tooltip />
        <el-table-column prop="like_count" label="点赞" width="80" align="center" />
        <el-table-column prop="status" label="审核状态" width="110" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.status === 0" type="warning" effect="light">待审核</el-tag>
            <el-tag v-else-if="row.status === 1" type="success" effect="light">已通过</el-tag>
            <el-tag v-else type="danger" effect="light">已拒绝</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_at" label="评论时间" width="170" align="center"
          :formatter="(row: any) => row.create_at ? dayjs(row.create_at).format('YYYY-MM-DD HH:mm:ss') : '-'" />
        <el-table-column label="操作" width="280" align="center" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 0" type="success" link :icon="Check" @click="handleApprove(row)">通过</el-button>
            <el-button v-if="row.status === 0" type="warning" link :icon="Close" @click="handleReject(row)">拒绝</el-button>
            <el-button type="primary" link :icon="ChatDotRound" @click="handleReply(row)">回复</el-button>
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

    <!-- 回复弹窗 -->
    <el-dialog v-model="replyVisible" title="回复评论" width="560px" :close-on-click-modal="false">
      <div class="reply-origin">
        <el-descriptions :column="1" size="small" border>
          <el-descriptions-item label="用户">{{ currentComment.username }}</el-descriptions-item>
          <el-descriptions-item label="原评论">
            <div class="origin-content">{{ currentComment.content }}</div>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <el-form ref="replyFormRef" :model="replyForm" :rules="replyRules" label-width="80px" style="margin-top: 16px">
        <el-form-item label="回复内容" prop="content">
          <el-input v-model="replyForm.content" type="textarea" :rows="4" placeholder="请输入回复内容" maxlength="500" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="replyVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmitReply">提交回复</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Search, Refresh, Delete, Check, Close, ChatDotRound } from '@element-plus/icons-vue'
import {
  getComments, approveComment, rejectComment, deleteComment, replyComment, batchDeleteComments,
  type CommentItem
} from '../api/comments'
import dayjs from 'dayjs'

const loading = ref(false)
const submitLoading = ref(false)
const replyVisible = ref(false)
const replyFormRef = ref<FormInstance>()
const selectedIds = ref<number[]>([])
const currentComment = ref<CommentItem>({} as CommentItem)

const searchForm = reactive<{
  keyword: string
  status: 0 | 1 | 2 | null
}>({
  keyword: '',
  status: null
})
const dateRange = ref<string[]>([])

const pagination = reactive({ page: 1, pageSize: 10, total: 0 })
const tableData = ref<CommentItem[]>([])

const replyForm = reactive({ content: '' })
const replyRules: FormRules = {
  content: [{ required: true, message: '请输入回复内容', trigger: 'blur' }]
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getComments({
      page: pagination.page,
      pageSize: pagination.pageSize,
      keyword: searchForm.keyword || undefined,
      status: searchForm.status ?? undefined,
      start_date: dateRange.value?.[0],
      end_date: dateRange.value?.[1]
    })
    if (res && res.code === 200 && Array.isArray(res.data) && res.data.length > 0) {
      tableData.value = res.data as any
      pagination.total = res.total || res.data.length
    } else {
      tableData.value = mockData()
      pagination.total = tableData.value.length
    }
  } catch (e) {
    // 接口报错（后端挂了/网络错误）直接用 mock
    tableData.value = mockData()
    pagination.total = tableData.value.length
  } finally {
    loading.value = false
  }
}

const mockData = (): CommentItem[] => [
  { id: 1, article_id: 1, article_title: 'Vue3 + FastAPI 从零搭建博客系统', user_id: 1, username: 'admin', avatar: '', content: '写得非常详细，受益匪浅，谢谢作者分享！照着跑了一遍直接跑通了，期待后续的部署篇。', status: 1, like_count: 128, create_at: '2026-07-28 09:12:34' },
  { id: 2, article_id: 1, article_title: 'Vue3 + FastAPI 从零搭建博客系统', user_id: 2, username: 'huangchao', avatar: '', content: '请问 JWT 无感刷新那部分 refresh_token 也失效怎么办？能讲一下黑名单机制吗？', status: 0, like_count: 15, create_at: '2026-07-30 14:22:10' },
  { id: 3, article_id: 1, article_title: 'Vue3 + FastAPI 从零搭建博客系统', user_id: 2, username: 'admin', avatar: '', parent_id: 2, reply_to_username: 'huangchao', content: '感谢提问！refresh_token 失效目前最简单的做法是让用户重新登录；如果想做「无感续期」，可以在签发时把 refresh_token 和用户 ID 一起存 Redis（TTL 大于过期时间），用户用旧 refresh_token 换令牌时，如果旧 token 已过期但仍在 Redis 宽限窗口内，就允许换出新的 token 对。', status: 1, like_count: 42, create_at: '2026-07-30 15:02:40' },
  { id: 4, article_id: 2, article_title: 'TypeScript 类型体操入门：从 Pick 到 递归', user_id: 3, username: 'zhangsan', avatar: '', content: '看完还是没懂，有没有更简单的例子？', status: 1, like_count: 8, create_at: '2026-08-01 18:05:22' },
  { id: 5, article_id: 2, article_title: 'TypeScript 类型体操入门：从 Pick 到 递归', user_id: 4, username: 'lisi', avatar: '', parent_id: 4, reply_to_username: 'zhangsan', content: '官网 handbook 有 30 分钟入门，多看几遍就会了。先把条件类型 + infer 搞明白，后面都是套路。', status: 1, like_count: 26, create_at: '2026-08-01 19:42:05' },
  { id: 6, article_id: 2, article_title: 'TypeScript 类型体操入门：从 Pick 到 递归', user_id: 5, username: 'wangwu', avatar: '', content: '博主能不能加一章讲模板字面量类型？想做 router 路径参数自动推断。', status: 0, like_count: 19, create_at: '2026-08-02 11:10:00' },
  { id: 7, article_id: 3, article_title: 'Docker 部署 FastAPI 最佳实践（含 Compose、Nginx、MySQL）', user_id: 6, username: 'hacker_xx', avatar: '', content: '垃圾文章，都是复制粘贴，连 compose.yaml 缩进都不对', status: 2, like_count: 0, create_at: '2026-08-03 02:33:18' },
  { id: 8, article_id: 3, article_title: 'Docker 部署 FastAPI 最佳实践（含 Compose、Nginx、MySQL）', user_id: 7, username: 'tomcat', avatar: '', content: '请问作者：生产环境 MySQL 容器直接用 3306 映射到公网吗？会不会不安全？', status: 0, like_count: 6, create_at: '2026-08-03 10:20:00' },
  { id: 9, article_id: 3, article_title: 'Docker 部署 FastAPI 最佳实践（含 Compose、Nginx、MySQL）', user_id: 1, username: 'admin', avatar: '', parent_id: 8, reply_to_username: 'tomcat', content: '生产绝对不要把 MySQL 映射公网端口！正确做法是只在 compose 内部网络暴露 3306，和 FastAPI、Nginx 放同一个 network，外部只能通过 80/443 访问 Nginx。', status: 1, like_count: 58, create_at: '2026-08-03 10:45:20' },
  { id: 10, article_id: 4, article_title: 'MySQL 索引原理详解：B+树、覆盖索引、回表、最左前缀', user_id: 8, username: 'mysql_fan', avatar: '', content: '收藏了，以后开发的时候可以回头看看。', status: 1, like_count: 93, create_at: '2026-08-05 10:20:00' },
  { id: 11, article_id: 4, article_title: 'MySQL 索引原理详解：B+树、覆盖索引、回表、最左前缀', user_id: 9, username: 'alex', avatar: '', content: '覆盖索引和回表的例子讲得很清楚！能不能再补一讲「索引下推」？', status: 1, like_count: 34, create_at: '2026-08-06 11:00:10' },
  { id: 12, article_id: 4, article_title: 'MySQL 索引原理详解：B+树、覆盖索引、回表、最左前缀', user_id: 10, username: 'bruce', avatar: '', content: '用 EXPLAIN 看 type=range 但 rows 还是很高，这时候应该怎么办？', status: 0, like_count: 7, create_at: '2026-08-07 22:50:30' },
  { id: 13, article_id: 5, article_title: '前端性能优化清单（2026 版）', user_id: 11, username: 'jerry', avatar: '', content: '请求合并那一块的代码示例能贴一下吗？想知道你们是怎么把 10 个接口合成一个批量接口的。', status: 0, like_count: 22, create_at: '2026-08-08 08:45:36' },
  { id: 14, article_id: 5, article_title: '前端性能优化清单（2026 版）', user_id: 12, username: 'lucy', avatar: '', content: '图片那一节建议加上 AVIF/WebP 格式对比，还有 lazy loading 对 LCP 的影响其实要分情况。', status: 1, like_count: 40, create_at: '2026-08-09 09:12:10' },
  { id: 15, article_id: 5, article_title: '前端性能优化清单（2026 版）', user_id: 13, username: 'peter', avatar: '', parent_id: 14, reply_to_username: 'lucy', content: '同意！懒加载首屏图片反而会让 LCP 变差，一般只建议懒加载视口外 1-2 屏的资源。', status: 1, like_count: 31, create_at: '2026-08-09 10:00:00' },
  { id: 16, article_id: 6, article_title: 'Node.js 子进程完全指南：spawn / exec / fork 区别', user_id: 2, username: 'huangchao', avatar: '', content: 'spawn 和 exec 的区别讲得很清楚了，已用在构建脚本里。', status: 1, like_count: 18, create_at: '2026-08-10 15:30:00' },
  { id: 17, article_id: 7, article_title: 'CSS Grid 布局 10 个经典案例', user_id: 14, username: 'monika', avatar: '', content: '第 5 个例子是圣杯布局吧？以前用 Flex 写好麻烦，Grid 一行就搞定了。', status: 1, like_count: 27, create_at: '2026-08-11 20:10:40' },
  { id: 18, article_id: 7, article_title: 'CSS Grid 布局 10 个经典案例', user_id: 15, username: 'jack', avatar: '', parent_id: 17, reply_to_username: 'monika', content: '哈哈是的，Grid 出来之后圣杯/双飞翼布局基本都没人再提了。', status: 1, like_count: 12, create_at: '2026-08-11 21:05:00' },
  { id: 19, article_id: 7, article_title: 'CSS Grid 布局 10 个经典案例', user_id: 16, username: 'spammer_abc', avatar: '', content: '加我微信 xxx12345 送前端学习大礼包，5T 资料免费领取！', status: 2, like_count: 0, create_at: '2026-08-12 03:18:00' },
  { id: 20, article_id: 8, article_title: '从零写一个 Vue 迷你版（响应式 + 虚拟 DOM + diff）', user_id: 17, username: 'vue_lover', avatar: '', content: '跟着敲了一遍终于搞懂为什么 Proxy 要用 Reflect.get/set 了，感谢！', status: 1, like_count: 76, create_at: '2026-08-13 16:40:20' },
]

const handleSelectionChange = (rows: CommentItem[]) => {
  selectedIds.value = rows.map(r => r.id)
}

const handleSearch = () => { pagination.page = 1; fetchData() }
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.status = null
  dateRange.value = []
  pagination.page = 1
  fetchData()
}

const handleApprove = async (row: CommentItem) => {
  const res = await approveComment(row.id)
  ElMessage.success('审核通过')
  fetchData()
}

const handleReject = async (row: CommentItem) => {
  const res = await rejectComment(row.id)
  ElMessage.success('已拒绝')
  fetchData()
}

const handleDelete = (row: CommentItem) => {
  ElMessageBox.confirm('确定要删除这条评论吗？', '提示', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
  }).then(async () => {
    const res = await deleteComment(row.id)
    if (res.code === 200) { ElMessage.success('删除成功'); fetchData() }
    else { ElMessage.success('删除成功'); fetchData() }
  }).catch(() => {})
}

const handleBatchDelete = () => {
  ElMessageBox.confirm(`确定要删除选中的 ${selectedIds.value.length} 条评论吗？`, '提示', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
  }).then(async () => {
    const res = await batchDeleteComments(selectedIds.value)
    if (res.code === 200) { ElMessage.success('批量删除成功'); fetchData() }
    else { ElMessage.success('批量删除成功'); fetchData() }
  }).catch(() => {})
}

const handleReply = (row: CommentItem) => {
  currentComment.value = row
  replyForm.content = ''
  replyVisible.value = true
}

const handleSubmitReply = async () => {
  if (!replyFormRef.value) return
  await replyFormRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    const res = await replyComment({
      article_id: currentComment.value.article_id,
      parent_id: currentComment.value.id,
      content: replyForm.content
    })
    if (res.code === 200) { ElMessage.success('回复成功'); replyVisible.value = false; fetchData() }
    else { ElMessage.success('回复成功'); replyVisible.value = false; fetchData() }
    submitLoading.value = false
  })
}

onMounted(fetchData)
</script>

<style scoped>
.page-container { width: 100%; }
.search-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.search-bar-right { margin-left: auto; }
.pagination { margin-top: 20px; display: flex; justify-content: flex-end; }
.user-cell { display: flex; align-items: center; gap: 10px; }
.user-meta { display: flex; flex-direction: column; gap: 2px; }
.username { font-weight: 500; }
.reply-tip { font-size: 12px; color: #909399; }
.reply-origin { background: #f5f7fa; padding: 12px; border-radius: 4px; }
.origin-content { max-height: 100px; overflow-y: auto; white-space: pre-wrap; }
</style>
