import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  // Backward-compatible redirects
  { path: '/login', redirect: '/auth/login' },
  { path: '/request', redirect: '/auth/request' },
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
        path: 'knowledge',
        meta: { requiresAuth: true },
        redirect: '/dashboard',
        children: [
          {
            path: ':id',
            component: () => import('@/layouts/KnowledgeLayout.vue'),
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
            ],
          },
        ],
      },
    ],
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const auth = useAuthStore()

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

  // 已登录用户访问登录页 → 跳转首页
  if (to.name === 'Login' && auth.isLoggedIn) {
    next({ name: 'Dashboard' })
    return
  }

  next()
})

export default router
