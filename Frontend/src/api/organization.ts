// ========================================
// Organization API — 真实后端接口
// ========================================
import http from './http'
import type {
  Organization,
  OrganizationCreate,
  OrganizationMember,
  OrganizationOut,
  OrganizationUpdate,
  OrgRole,
} from '@/types/knowledge'

/** 我的组织列表（GET /organization） */
export async function fetchOrganizations(): Promise<Organization[]> {
  const res = await http.get<Organization[]>('/organization')
  return res.data
}

/** 组织详情（GET /organization/{org_id}） */
export async function fetchOrganization(orgId: number): Promise<Organization> {
  const res = await http.get<Organization>(`/organization/${orgId}`)
  return res.data
}

/** 创建组织（POST /organization） */
export async function createOrganization(data: OrganizationCreate): Promise<OrganizationOut> {
  const res = await http.post<OrganizationOut>('/organization', data)
  return res.data
}

/** 更新组织（PATCH /organization/{org_id}） */
export async function updateOrganization(
  orgId: number,
  data: OrganizationUpdate
): Promise<Organization> {
  const res = await http.patch<Organization>(`/organization/${orgId}`, data)
  return res.data
}

/** 删除组织（DELETE /organization/{org_id}） */
export async function deleteOrganization(orgId: number): Promise<unknown> {
  const res = await http.delete(`/organization/${orgId}`)
  return res.data
}

/** 成员列表（GET /organization/{org_id}/members） */
export async function fetchMembers(orgId: number): Promise<OrganizationMember[]> {
  const res = await http.get<OrganizationMember[]>(`/organization/${orgId}/members`)
  return res.data
}

/** 添加成员（POST /organization/{org_id}/members，后端以 query 参数接收） */
export async function addMember(
  orgId: number,
  userId: number,
  role: OrgRole
): Promise<OrganizationMember> {
  const res = await http.post<OrganizationMember>(`/organization/${orgId}/members`, null, {
    params: { user_id: userId, role },
  })
  return res.data
}

/** 修改成员角色（PATCH /organization/{org_id}/members/{user_id}） */
export async function updateMemberRole(
  orgId: number,
  userId: number,
  role: OrgRole
): Promise<OrganizationMember> {
  const res = await http.patch<OrganizationMember>(`/organization/${orgId}/members/${userId}`, {
    role,
  })
  return res.data
}

/** 退出组织（DELETE /organization/{org_id}/members/me） */
export async function quitOrganization(orgId: number): Promise<unknown> {
  const res = await http.delete(`/organization/${orgId}/members/me`)
  return res.data
}

/** 移除成员（DELETE /organization/{org_id}/members/{user_id}） */
export async function removeMember(orgId: number, userId: number): Promise<unknown> {
  const res = await http.delete(`/organization/${orgId}/members/${userId}`)
  return res.data
}
