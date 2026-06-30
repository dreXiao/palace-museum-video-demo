import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/pages/LoginPage.vue'),
      meta: { title: '登录', requiresAuth: false },
    },
    {
      path: '/',
      name: 'home',
      component: () => import('@/pages/HomePage.vue'),
      meta: { title: '主页', icon: 'Home', requiresAuth: true },
    },
    {
      path: '/history',
      name: 'history',
      component: () => import('@/pages/HistoryPage.vue'),
      meta: { title: '生成历史', icon: 'Clock', requiresAuth: true },
    },
    {
      path: '/history/:id',
      name: 'history-detail',
      component: () => import('@/pages/HistoryDetailPage.vue'),
      meta: { title: '生成详情', parent: 'history', requiresAuth: true },
    },
    {
      path: '/tags',
      name: 'tags',
      component: () => import('@/pages/TagManagePage.vue'),
      meta: { title: '标签管理', icon: 'Tags', requiresAuth: true },
    },
    {
      path: '/models',
      name: 'models',
      component: () => import('@/pages/ModelManagePage.vue'),
      meta: { title: '模型管理', icon: 'Cpu', requiresAuth: true },
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/pages/SettingsPage.vue'),
      meta: { title: '用户设置', icon: 'Settings', requiresAuth: true },
    },
  ],
})

export default router
