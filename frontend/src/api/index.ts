import axios from 'axios'
import { useUserStore } from '../store/user'
import router from '../routes'
import { ElMessage } from 'element-plus'
import type { loginSuccessResponse } from './user'

const server = axios.create({
  baseURL: '',
  timeout: 10000
})

// 请求拦截器：附加 token
server.interceptors.request.use(
  (config) => {
    try {
      const userStore = useUserStore()
      if (userStore.user.access_token) {
        config.headers = config.headers || {}
        config.headers.Authorization = `Bearer ${userStore.user.access_token}`
      }
    } catch (e) {
      // Pinia 可能还未初始化，忽略
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)


// 响应拦截器：处理 401 等情况， TODO: response 类型
server.interceptors.response.use(
  async (response: any) => {
    return response.data
  },
  async (error) => {
    console.error('Request error:4011111-------', error, error.status, error.config)
    if (error && error.status === 401) {
      const refreshToken = useUserStore().user.refresh_token
      if (!refreshToken) {
        const userStore = useUserStore()
        userStore.logout()  
        ElMessage.warning('登录状态已过期，请重新登录')
        router.push('/login')
      }
      // 401 表示未授权，尝试通过refreshToken刷新 access_token, 无感刷新token，自动续期
      const res = (await post('/api/refresh', { refresh_token: refreshToken })) as loginSuccessResponse
      if(res.code === 200) {
        // 刷新成功，更新token
        useUserStore().saveUser({
          access_token: res.access_token,
          username: res.username ?? useUserStore().user.username,
          refresh_token: res.refresh_token
        })
        error.config.headers.Authorization = `Bearer ${res.access_token}`
        return server(error.config)
      }else {
        const userStore = useUserStore()
        userStore.logout()
        ElMessage.warning('登录状态已过期，请重新登录')
        router.push('/login')
      }
    }
  }
)

// 基础响应字段
export type BaseApiResponse = {
  code: number
  msg: string
}

// 泛型 T: 顶层扩展字段（登录接口 access_token 等在顶层，而不是 data 里）
// 泛型 D: data 字段的类型（普通列表/详情接口放在 data 里）
// Partial<T> 表示 T 中的字段都是可选的, T是一个对象类型，而且里面的字段都是可选的
// Extra<T> 兜底：T 不是对象时（如 get<string>、post<void>）退化成 {}，避免约束报错
type Extra<T> = T extends object ? Partial<T> : {}

export type ApiResponse<T = any, D = any> = BaseApiResponse &
  Extra<T> & {
    total?: number
    data?: D
  }

export const get = <T = any, D = any>(url: string,params?: any): Promise<ApiResponse<T, D>> => {
  return server.get(url, { params }) as Promise<ApiResponse<T, D>>
}

export const post = <T = any, D = any>(url: string,data?: any,config?: any): Promise<ApiResponse<T, D>> => {
  return server.post(url, data, config) as Promise<ApiResponse<T, D>>
}



