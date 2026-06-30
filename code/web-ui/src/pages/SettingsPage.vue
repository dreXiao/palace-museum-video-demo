<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { settingsApi } from '@/api/client'

const prefs = ref<Record<string, any>>({
  default_resolution: '1080p',
  default_duration: 10,
  history_view: 'grid',
  page_size: 20,
  language: 'zh-CN',
  theme: 'system',
})
const saved = ref(false)

onMounted(async () => {
  try {
    const res = await settingsApi.getPreferences()
    if ((res as any).data) {
      prefs.value = { ...prefs.value, ...(res as any).data }
    }
  } catch {}
})

async function savePrefs() {
  try {
    await settingsApi.updatePreferences(prefs.value)
    saved.value = true
    setTimeout(() => saved.value = false, 3000)
  } catch {
    alert('保存失败')
  }
}
</script>

<template>
  <div class="space-y-6 max-w-4xl">
    <h2 class="text-lg font-semibold">用户设置</h2>

    <!-- API Key Status -->
    <div class="border border-border rounded-lg p-6 space-y-4">
      <h3 class="text-sm font-medium">API Key 状态</h3>
      <p class="text-xs text-muted-foreground">API Key 在服务端环境变量管理，此处仅显示状态。修改后需重启服务端。</p>
      <div class="space-y-2">
        <div class="flex items-center gap-2 text-sm">
          <span class="w-2 h-2 rounded-full bg-emerald-500" />
          <span class="font-mono text-xs">DASHSCOPE_API_KEY</span>
          <span class="text-emerald-600 text-xs">✅ 已配置</span>
        </div>
        <div class="flex items-center gap-2 text-sm">
          <span class="w-2 h-2 rounded-full bg-emerald-500" />
          <span class="font-mono text-xs">SEEDANCE_API_KEY</span>
          <span class="text-emerald-600 text-xs">✅ 已配置</span>
        </div>
        <div class="flex items-center gap-2 text-sm">
          <span class="w-2 h-2 rounded-full bg-red-500" />
          <span class="font-mono text-xs">KLING_API_KEY</span>
          <span class="text-red-500 text-xs">❌ 未配置</span>
        </div>
      </div>
    </div>

    <!-- Preferences -->
    <div class="border border-border rounded-lg p-6 space-y-4">
      <h3 class="text-sm font-medium">偏好设置</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="text-xs text-muted-foreground">默认分辨率</label>
          <select v-model="prefs.default_resolution" class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm mt-1">
            <option value="720p">720p</option>
            <option value="1080p">1080p</option>
          </select>
        </div>
        <div>
          <label class="text-xs text-muted-foreground">默认时长(秒)</label>
          <select v-model.number="prefs.default_duration" class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm mt-1">
            <option :value="6">6s</option>
            <option :value="8">8s</option>
            <option :value="10">10s</option>
            <option :value="15">15s</option>
          </select>
        </div>
        <div>
          <label class="text-xs text-muted-foreground">历史默认视图</label>
          <select v-model="prefs.history_view" class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm mt-1">
            <option value="grid">网格</option>
            <option value="list">列表</option>
          </select>
        </div>
        <div>
          <label class="text-xs text-muted-foreground">每页条数</label>
          <select v-model.number="prefs.page_size" class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm mt-1">
            <option :value="10">10条</option>
            <option :value="20">20条</option>
            <option :value="50">50条</option>
          </select>
        </div>
        <div>
          <label class="text-xs text-muted-foreground">主题</label>
          <select v-model="prefs.theme" class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm mt-1">
            <option value="light">浅色</option>
            <option value="dark">深色</option>
            <option value="system">跟随系统</option>
          </select>
        </div>
        <div>
          <label class="text-xs text-muted-foreground">语言</label>
          <select v-model="prefs.language" class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm mt-1">
            <option value="zh-CN">简体中文</option>
            <option value="en">English</option>
          </select>
        </div>
      </div>
      <button @click="savePrefs" class="mt-4 rounded-md bg-primary text-primary-foreground px-4 py-2 text-sm hover:opacity-90">
        {{ saved ? '已保存 ✓' : '保存设置' }}
      </button>
    </div>

    <!-- Storage -->
    <div class="border border-border rounded-lg p-6 space-y-3">
      <h3 class="text-sm font-medium">存储用量</h3>
      <div class="flex gap-8 text-sm">
        <div><span class="text-muted-foreground">原图:</span> 12 张 / 45.2 MB</div>
        <div><span class="text-muted-foreground">视频:</span> 48 条 / 1.2 GB</div>
      </div>
      <div class="h-2 bg-muted rounded-full overflow-hidden">
        <div class="h-full bg-primary rounded-full transition-all" style="width: 12.5%" />
      </div>
      <div class="text-xs text-muted-foreground">已用 1.25 GB / 总计 10 GB (12.5%)</div>
    </div>

    <!-- About -->
    <div class="border border-border rounded-lg p-6">
      <h3 class="text-sm font-medium mb-2">关于</h3>
      <div class="text-xs text-muted-foreground space-y-1">
        <div>版本: v1.0.0</div>
        <div>构建: 2026-07-01</div>
        <div>API 版本: v1</div>
      </div>
    </div>
  </div>
</template>
