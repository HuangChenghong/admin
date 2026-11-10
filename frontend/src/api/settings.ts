import { get, post } from './index'

export type SiteSettings = {
  site_name: string
  site_title: string
  site_logo: string
  site_description: string
  site_keywords: string
  site_url: string
  icp: string
  public_security: string
  contact_email: string
  copyright: string
  theme_color: string
  upload_dir: string
  upload_max_size: number
  upload_allow_exts: string
  article_review: 0 | 1
  comment_review: 0 | 1
  allow_register: 0 | 1
  default_role: string
  close_site: 0 | 1
  close_tip: string
}

export type LinkItem = {
  id: number
  name: string
  url: string
  logo?: string
  description?: string
  sort: number
  status: 0 | 1
  type: 'friend' | 'tool' | 'recommend'
  created_at: string
}

export const getSiteSettings = () => {
  return get<SiteSettings>('/api/settings/site')
}

export const saveSiteSettings = (data: SiteSettings) => {
  return post<string>('/api/settings/site', data)
}

export const getLinks = (params: { type?: string } = {}) => {
  return post<LinkItem[]>('/api/settings/links', params)
}

export const createLink = (data: Partial<LinkItem>) => {
  return post<string>('/api/settings/link', data)
}

export const updateLink = (data: Partial<LinkItem>) => {
  return post<string>('/api/settings/link/update', data)
}

export const deleteLink = (id: number) => {
  return get<void>(`/api/delLink/${id}`)
}
