import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  // Backward-compatible redirects
  { path: '/login', redirect: '/auth/login' },
  { path: '/register', redirect: '/auth/register' },

  {
    path: '/auth',
    component: () => import('@/layouts/AuthLayout.vue'),
    children: [
      {
        path: 'login',
        name: 'Login',
        component: () => import('@/pages/login/index.vue'),
        meta: { requiresAuth: false },
      },
      {
        path: 'request',
        name: 'Request',
        component: () => import('@/pages/request/index.vue'),
        meta: { requiresAuth: false },
      },
      {
        path: 'register',
        name: 'Register',
        component: () => import('@/pages/register/index.vue'),
        meta: { requiresAuth: false },
      },
    ],
  },
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/pages/dashboard/index.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'admin/requests',
        name: 'AdminRequests',
        component: () => import('@/pages/admin/requests.vue'),
        meta: { requiresAuth: true, requiresAdmin: true },
      },
      {
        path: 'organizations',
        meta: { requiresAuth: true },
        children: [
          {
            path: '',
            name: 'Organizations',
            component: () => import('@/pages/organizations/index.vue'),
          },
          {
            path: ':id',
            name: 'OrganizationDetail',
            component: () => import('@/pages/organizations/[id].vue'),
          },
        ],
      },
      {
        path: 'knowledge',
        meta: { requiresAuth: true },
        component: () => import('@/pages/knowledge/index.vue'),
      },
      {
        path: 'knowledge/:id(\\d+)',
        component: () => import('@/layouts/KnowledgeLayout.vue'),
        meta: { requiresAuth: true },
        children: [
          {
            path: '',
            name: 'KnowledgeChat',
            component: () => import('@/pages/knowledge/[id]/index.vue'),
          },
          {
            path: 'documents',
            name: 'KnowledgeDocuments',
            component: () => import('@/pages/knowledge/[id]/documents.vue'),
          },
          {
            path: 'settings',
            name: 'KnowledgeSettings',
            component: () => import('@/pages/knowledge/[id]/settings.vue'),
          },
        ],
      },
    ],
  },
  // 全局 catch-all：兜底未匹配路径（放最后）
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const auth = useAuthStore()

  // /knowledge/<非数字> 这种乱敲的 URL，统一跳回 KB 列表
  // 比如 /knowledge/documents、/knowledge/settings 等
  const kmMatch = to.path.match(/^\/knowledge\/([^\/]+)$/)
  if (kmMatch) {
    const seg = kmMatch[1]
    if (!/^\d+$/.test(seg) && !['documents', 'settings'].includes(seg)) {
      next({ path: '/knowledge' })
      return
    }
  }

  // 需要登录但未登录 → 跳转登录页
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  // 需要管理员但非管理员 → 跳转首页
  if (to.meta.requiresAdmin && !auth.isAdmin) {
    next({ name: 'Dashboard' })
    return
  }

  // 已登录用户访问登录页 / 申请页 → 跳转首页
  if ((to.name === 'Login' || to.name === 'Request') && auth.isLoggedIn) {
    next({ name: 'Dashboard' })
    return
  }

  next()
})

export default router
