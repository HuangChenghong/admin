import { defineStore } from 'pinia'
import { login, logout, register, type loginData } from '../api/user'

export type loginResponse = {
  access_token: string
  username: string
  refresh_token: string
  // role: string
  // status: number
}

// 从 localStorage 恢复用户状态
const getStoredUser = (): loginResponse => {
  try {
    const stored = localStorage.getItem('blog_user')
    if (stored) return JSON.parse(stored)
  } catch (e) {
    console.error('Failed to parse stored user', e)
  }
  return {
    access_token: '',
    username: '',
    refresh_token: '',
    // role: '',
    // status: ''
  }
}

export const useUserStore = defineStore('user', {
  state: () => ({
    user: getStoredUser()
  }),
  actions: {
    async login(data: loginData) {
      const res = await login(data)
      return res
    },

    async logout() {
      this.user.access_token = ''
      this.user.username = ''
      this.user.refresh_token = ''
      localStorage.removeItem('blog_user')
      localStorage.clear()
      try {
        return await logout()
      } catch (e) {
        return null
      }
    },

    async register(data: any) {
      return await register(data)
    },

    // 保存用户信息到 localStorage
    saveUser(user: { access_token: string; username: string, refresh_token: string }) {
      this.user.access_token = user.access_token
      this.user.username = user.username
      this.user.refresh_token = user.refresh_token
      // this.user.role = user.role
      // this.user.status = user.status
      localStorage.setItem('blog_user', JSON.stringify(this.user))
    }
  }
})
