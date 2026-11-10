import { createRouter, createWebHashHistory } from 'vue-router'
import { useUserStore } from '../store/user'
import Layout from '../layout/Layout.vue'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/Register.vue'),
    meta: { title: '注册' }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '首页统计', requiresAuth: true }
      },
      {
        path: 'articles',
        name: 'articles',
        component: () => import('../views/Articles.vue'),
        meta: { title: '文章管理', requiresAuth: true }
      },
      {
        path: 'categories',
        name: 'categories',
        component: () => import('../views/Categories.vue'),
        meta: { title: '分类管理', requiresAuth: true }
      },
      {
        path: 'comments',
        name: 'comments',
        component: () => import('../views/Comments.vue'),
        meta: { title: '评论管理', requiresAuth: true }
      },
      {
        path: 'users',
        name: 'users',
        component: () => import('../views/Users.vue'),
        meta: { title: '用户管理', requiresAuth: true }
      },
      {
        path: 'roles',
        name: 'roles',
        component: () => import('../views/Roles.vue'),
        meta: { title: '角色管理', requiresAuth: true }
      },
      {
        path: 'permissions',
        name: 'permissions',
        component: () => import('../views/Permissions.vue'),
        meta: { title: '菜单/权限管理', requiresAuth: true }
      },
      {
        path: 'settings',
        name: 'settings',
        component: () => import('../views/Settings.vue'),
        meta: { title: '系统设置', requiresAuth: true }
      },
      {
        path: 'profile',
        name: 'profile',
        component: () => import('../views/Profile.vue'),
        meta: { title: '个人中心', requiresAuth: true }
      },
      {
        path: 'logs',
        name: 'logs',
        component: () => import('../views/Logs.vue'),
        meta: { title: '日志管理', requiresAuth: true }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('../views/Login.vue')
  }
]

const router = createRouter({
  routes,
  history: createWebHashHistory()
})

/**
 * 路由守卫
 * @param to 目标路由
 * @param from 来源路由
 * @param next 路由守卫函数
 */
router.beforeEach((to, _from, next) => {
  const userStore = useUserStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (requiresAuth && !userStore.user.access_token) {
    // 需要登录但未登录，跳转到登录页
    next({ name: 'login' })
  } else if ((to.name === 'login' || to.name === 'register') && userStore.user.access_token) {  
    // 已登录访问登录/注册页，跳转到首页
    next({ name: 'dashboard' })
  } else {
    next()
  }
})

export default router
