import { get, post } from './index'

export type ProfileItem = {
  user_id: number
  username: string
  email: string
  avatar: string
  cname: string
  phone?: string
  bio?: string
  role: string
  role_name?: string
  status: 0 | 1
  created_at: string
  last_login_at?: string
}

export type ChangePasswordData = {
  old_password: string
  new_password: string
  confirm_password: string
}

export const getProfile = () => {
  return get<ProfileItem>('/api/profile')
}

export const updateProfile = (data: Partial<ProfileItem>) => {
  return post<string>('/api/profile', data)
}

export const changePassword = (data: ChangePasswordData) => {
  return post<string>('/api/profile/changePassword', data)
}

export const uploadAvatar = (formData: FormData) => {
  return post<string>('/api/profile/avatar', formData)
}
