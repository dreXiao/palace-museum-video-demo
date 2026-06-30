<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ApiError } from '@/api/client'

const router = useRouter()
const auth = useAuthStore()

const username = ref('admin')
const password = ref('')
const errorMsg = ref('')
const loading = ref(false)

async function handleLogin() {
  errorMsg.value = ''
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    router.push('/')
  } catch (e) {
    errorMsg.value = e instanceof ApiError ? e.message : '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-muted/30 p-4">
    <div class="w-full max-w-sm">
      <div class="text-center mb-8">
        <div class="text-4xl mb-2">🏯</div>
        <h1 class="text-xl font-semibold">故宫日历·图生视频管理平台</h1>
        <p class="text-sm text-muted-foreground mt-1">请登录以继续</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-4 bg-card border border-border rounded-lg p-6">
        <div>
          <label class="block text-sm font-medium mb-1">用户名</label>
          <input
            v-model="username"
            type="text"
            class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder="管理员用户名"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">密码</label>
          <input
            v-model="password"
            type="password"
            class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder="请输入密码"
          />
        </div>

        <div v-if="errorMsg" class="text-sm text-destructive">{{ errorMsg }}</div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full rounded-md bg-primary text-primary-foreground px-4 py-2.5 text-sm font-medium hover:opacity-90 disabled:opacity-50 transition-opacity"
        >
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
    </div>
  </div>
</template>
