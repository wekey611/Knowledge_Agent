import http from './http'
import type { TokenResponse, UserRequestInput, UserRequestOutput, InviteTokenInfo, UserRegisterInput, UserRegisterOutput, User, ApproveResponse } from '@/types/api'

export async function login(email: string, password: string): Promise<TokenResponse> {
  const formData = new URLSearchParams()
  formData.append('username', email)
  formData.append('password', password)
  const res = await http.post<TokenResponse>('/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return res.data
}

export async function requestAccount(data: UserRequestInput): Promise<UserRequestOutput> {
  const res = await http.post<UserRequestOutput>('/user/request', data)
  return res.data
}

export async function inviteInfo(token: string): Promise<InviteTokenInfo> {
  const res = await http.get<InviteTokenInfo>('/user/invite-info', { params: { token } })
  return res.data
}

export async function register(data: UserRegisterInput): Promise<UserRegisterOutput> {
  const res = await http.post<UserRegisterOutput>('/user/register', data)
  return res.data
}

export async function fetchMyProfile(): Promise<User> {
  // 后端目前没有 /me 接口，这里用 admin/requests 或其他推断；保留接口待后端补
  const res = await http.get<User>('/me')
  return res.data
}

export async function approveRequest(requestId: number): Promise<ApproveResponse> {
  const res = await http.post<ApproveResponse>(`/user/request/${requestId}/approve`)
  return res.data
}

export async function listRequests(): Promise<UserRequestOutput[]> {
  if ((localStorage.getItem('access_token') || '').startsWith('demo.')) {
    const raw = localStorage.getItem('demo_requests')
    return raw ? JSON.parse(raw) : []
  }
  const res = await http.get<UserRequestOutput[]>('/admin/requests')
  return res.data
}