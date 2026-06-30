<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Home, Clock, Tags, Cpu, Settings, LogOut, Menu, X } from 'lucide-vue-next'
import { ref } from 'vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const sidebarCollapsed = ref(false)
const mobileMenuOpen = ref(false)

const navItems = [
  { path: '/', label: '主页', icon: Home },
  { path: '/history', label: '生成历史', icon: Clock },
  { path: '/tags', label: '标签管理', icon: Tags },
  { path: '/models', label: '模型管理', icon: Cpu },
  { path: '/settings', label: '用户设置', icon: Settings },
]

function isActive(path: string): boolean {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

function navigate(path: string) {
  router.push(path)
  mobileMenuOpen.value = false
}

async function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="flex h-screen overflow-hidden bg-background">
    <!-- Desktop Sidebar -->
    <aside
      :class="[
        'hidden lg:flex flex-col border-r border-border bg-sidebar-background transition-all duration-300',
        sidebarCollapsed ? 'w-[60px]' : 'w-[240px]',
      ]"
    >
      <!-- Logo -->
      <div class="flex items-center h-14 px-4 border-b border-sidebar-border shrink-0">
        <span class="text-xl">🏯</span>
        <span v-if="!sidebarCollapsed" class="ml-2 font-semibold text-sidebar-foreground text-sm">
          图生视频平台
        </span>
      </div>

      <!-- Nav -->
      <nav class="flex-1 py-2 overflow-y-auto">
        <button
          v-for="item in navItems"
          :key="item.path"
          @click="navigate(item.path)"
          :class="[
            'w-full flex items-center gap-3 px-3 py-2.5 mx-2 rounded-lg text-sm transition-colors',
            isActive(item.path)
              ? 'bg-sidebar-accent text-sidebar-accent-foreground font-medium'
              : 'text-sidebar-foreground hover:bg-sidebar-accent/50',
          ]"
        >
          <component :is="item.icon" class="h-4 w-4 shrink-0" />
          <span v-if="!sidebarCollapsed">{{ item.label }}</span>
        </button>
      </nav>

      <!-- Footer -->
      <div class="p-3 border-t border-sidebar-border shrink-0">
        <button
          @click="handleLogout"
          class="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-sidebar-foreground hover:bg-sidebar-accent/50 transition-colors"
        >
          <LogOut class="h-4 w-4 shrink-0" />
          <span v-if="!sidebarCollapsed">登出</span>
        </button>
      </div>
    </aside>

    <!-- Mobile overlay -->
    <div
      v-if="mobileMenuOpen"
      class="fixed inset-0 z-50 bg-black/50 lg:hidden"
      @click="mobileMenuOpen = false"
    />
    <div
      :class="[
        'fixed inset-y-0 left-0 z-50 w-[240px] bg-sidebar-background border-r border-sidebar-border transform transition-transform lg:hidden',
        mobileMenuOpen ? 'translate-x-0' : '-translate-x-full',
      ]"
    >
      <div class="flex items-center justify-between h-14 px-4 border-b">
        <span class="font-semibold text-sm">🏯 图生视频平台</span>
        <button @click="mobileMenuOpen = false" class="p-1"><X class="h-5 w-5" /></button>
      </div>
      <nav class="py-2">
        <button
          v-for="item in navItems"
          :key="item.path"
          @click="navigate(item.path)"
          :class="[
            'w-full flex items-center gap-3 px-4 py-3 text-sm',
            isActive(item.path) ? 'bg-sidebar-accent text-sidebar-accent-foreground font-medium' : 'text-sidebar-foreground',
          ]"
        >
          <component :is="item.icon" class="h-4 w-4" />
          {{ item.label }}
        </button>
      </nav>
    </div>

    <!-- Main content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Top bar -->
      <header class="flex items-center justify-between h-14 px-4 border-b border-border bg-background shrink-0">
        <div class="flex items-center gap-3">
          <button @click="mobileMenuOpen = true" class="lg:hidden p-1">
            <Menu class="h-5 w-5" />
          </button>
          <div class="text-sm text-muted-foreground">
            {{ route.meta.title || '首页' }}
          </div>
        </div>
        <div class="flex items-center gap-3">
          <span class="text-xs text-muted-foreground hidden sm:inline">
            {{ auth.user?.username }} ({{ auth.user?.role === 'admin' ? '管理员' : '开发者' }})
          </span>
          <button @click="sidebarCollapsed = !sidebarCollapsed" class="hidden lg:block p-1 text-muted-foreground">
            {{ sidebarCollapsed ? '→' : '←' }}
          </button>
        </div>
      </header>

      <!-- Page content -->
      <main class="flex-1 overflow-y-auto">
        <div class="mx-auto max-w-[1440px] p-4 lg:p-6">
          <router-view />
        </div>
      </main>
    </div>
  </div>
</template>
