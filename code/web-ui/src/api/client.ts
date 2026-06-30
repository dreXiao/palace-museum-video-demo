import { ofetch, type FetchContext, type FetchResponse } from 'ofetch'

const API_BASE = '/api/v1'

const rawFetch = ofetch.create({
  baseURL: API_BASE,
  async onRequest({ options }: FetchContext) {
    const token = localStorage.getItem('access_token')
    if (token) {
      const headers = new Headers(options.headers)
      headers.set('Authorization', `Bearer ${token}`)
      options.headers = headers
    }
  },
  async onResponseError({ response }: FetchContext & { response: FetchResponse<any> }) {
    if (response.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    const body = response._data as Record<string, any> | undefined
    throw new ApiError(body?.message || body?.detail || '请求失败', response.status)
  },
})

// Typed wrapper — ofetch's $Fetch type doesn't expose .get/.post convenience methods,
// but they work at runtime via Proxy; this wrapper restores type-safe method helpers.
export const apiClient = {
  get: <T = any>(path: string, opts?: { params?: Record<string, any> }) =>
    rawFetch(path, { method: 'GET', query: opts?.params }) as Promise<T>,
  post: <T = any>(path: string, body?: any) =>
    rawFetch(path, { method: 'POST', body }) as Promise<T>,
  put: <T = any>(path: string, body?: any) =>
    rawFetch(path, { method: 'PUT', body }) as Promise<T>,
  delete: <T = any>(path: string) =>
    rawFetch(path, { method: 'DELETE' }) as Promise<T>,
}

export class ApiError extends Error {
  status: number
  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

// ── Auth ──
export const authApi = {
  login: (username: string, password: string) =>
    apiClient.post<{ success: boolean; data: { access_token: string; refresh_token: string } }>('/auth/login', { username, password }),
  me: () => apiClient.get<{ success: boolean; data: { id: string; username: string; role: string } }>('/auth/me'),
}

// ── Generation ──
export const generationApi = {
  submit: (data: Record<string, any>) =>
    apiClient.post('/generation/submit', data),
  batchSubmit: (data: Record<string, any>) =>
    apiClient.post('/generation/batch-submit', data),
  getStatus: (taskId: string) =>
    apiClient.get(`/generation/${taskId}/status`),
  rateTask: (taskId: string, data: { quality_score: number; quality_notes?: string }) =>
    apiClient.post(`/generation/${taskId}/rate`, data),
}

// ── History ──
export const historyApi = {
  listGroups: (params: Record<string, any> = {}) =>
    apiClient.get('/history/groups', { params }),
  getGroupDetail: (groupId: string) =>
    apiClient.get(`/history/groups/${groupId}`),
  deleteGroup: (groupId: string) =>
    apiClient.delete(`/history/groups/${groupId}`),
}

// ── Tags ──
export const tagsApi = {
  list: () => apiClient.get('/tags'),
  create: (data: Record<string, any>) => apiClient.post('/tags', data),
  update: (tagId: string, data: Record<string, any>) => apiClient.put(`/tags/${tagId}`, data),
  delete: (tagId: string) => apiClient.delete(`/tags/${tagId}`),
  copy: (tagId: string) => apiClient.post(`/tags/${tagId}/copy`),
  getVersions: (tagId: string) => apiClient.get(`/tags/${tagId}/versions`),
}

// ── Models ──
export const modelsApi = {
  list: () => apiClient.get('/models'),
  create: (data: Record<string, any>) => apiClient.post('/models', data),
  update: (modelId: string, data: Record<string, any>) => apiClient.put(`/models/${modelId}`, data),
  delete: (modelId: string) => apiClient.delete(`/models/${modelId}`),
  testConnection: (modelId: string) => apiClient.post(`/models/${modelId}/test`),
  setDefault: (modelId: string) => apiClient.post(`/models/${modelId}/set-default`),
}

// ── Media ──
export const mediaApi = {
  upload: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return apiClient.post('/media/upload', form)
  },
  getImage: (assetId: string) => apiClient.get(`/media/image/${assetId}`),
}

// ── Settings ──
export const settingsApi = {
  getPreferences: () => apiClient.get('/settings/preferences'),
  updatePreferences: (data: Record<string, any>) => apiClient.put('/settings/preferences', data),
}
