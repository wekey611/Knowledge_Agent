import http from './http'
import type { TokenResponse } from '@/types/api'

export async function login(email: string, password: string): Promise<TokenResponse> {
  const formData = new URLSearchParams()
  formData.append('username', email)
  formData.append('password', password)

  const res = await http.post<TokenResponse>('/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return res.data
}
