<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { historyApi, ApiError } from '@/api/client'
import { Search, Download, Grid3X3, List, Star } from 'lucide-vue-next'
import type { GenerationGroup } from '@/types/models'

const router = useRouter()
const groups = ref<GenerationGroup[]>([])
const loading = ref(true)
const viewMode = ref<'grid' | 'list'>('grid')
const searchQuery = ref('')

onMounted(async () => {
  try {
    const res = await historyApi.listGroups({ limit: 20 })
    groups.value = (res as any).data || []
  } catch (e) {
    console.error('Failed to load history', e)
  } finally {
    loading.value = false
  }
})

function viewDetail(id: string) {
  router.push(`/history/${id}`)
}

function renderStars(score: number | null): string {
  return score ? '⭐'.repeat(score) : '—'
}
</script>

<template>
  <div class="space-y-4">
    <!-- Toolbar -->
    <div class="flex flex-wrap items-center gap-3">
      <h2 class="text-lg font-semibold">生成历史</h2>
      <div class="flex-1" />
      <div class="flex items-center gap-2">
        <div class="relative">
          <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
          <input v-model="searchQuery" type="text" placeholder="搜索原图/风格..." class="pl-8 pr-3 py-1.5 rounded-md border border-input bg-background text-xs w-48" />
        </div>
        <button @click="viewMode = 'grid'" :class="['p-1.5 rounded', viewMode === 'grid' ? 'bg-muted' : '']"><Grid3X3 class="h-4 w-4" /></button>
        <button @click="viewMode = 'list'" :class="['p-1.5 rounded', viewMode === 'list' ? 'bg-muted' : '']"><List class="h-4 w-4" /></button>
        <button class="inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 text-xs hover:bg-muted transition-colors">
          <Download class="h-3.5 w-3.5" /> 批量导出
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <div v-for="i in 8" :key="i" class="border border-border rounded-lg p-4 animate-pulse">
        <div class="h-32 bg-muted rounded mb-3" />
        <div class="h-3 bg-muted rounded w-2/3 mb-2" />
        <div class="h-3 bg-muted rounded w-1/2" />
      </div>
    </div>

    <!-- Empty -->
    <div v-else-if="groups.length === 0" class="border border-border rounded-xl p-16 text-center">
      <div class="text-4xl mb-4">🖼️</div>
      <p class="text-muted-foreground">还没有生成记录</p>
      <router-link to="/" class="text-sm text-primary hover:underline mt-2 inline-block">去主页试试吧 →</router-link>
    </div>

    <!-- Grid View -->
    <div v-else-if="viewMode === 'grid'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <div
        v-for="group in groups" :key="group.id"
        class="border border-border rounded-lg overflow-hidden hover:border-primary/30 transition-colors cursor-pointer group"
        @click="viewDetail(group.id)"
      >
        <div class="aspect-[16/9] bg-muted flex items-center justify-center text-muted-foreground text-sm">
          <!-- Placeholder — real impl shows thumbnail -->
          原图预览
        </div>
        <div class="p-3 space-y-1.5">
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium truncate">{{ group.tagId?.slice(0, 8) || '...' }}</span>
            <span class="text-xs text-muted-foreground">{{ renderStars(null) }}</span>
          </div>
          <div class="flex items-center gap-2 text-xs text-muted-foreground">
            <span>{{ group.modelId?.slice(0, 8) || '...' }}</span>
            <span>·</span>
            <span>第{{ group.totalAttempts }}次</span>
          </div>
          <div class="flex items-center justify-between text-xs text-muted-foreground">
            <span>¥{{ group.totalCostYuan || 0 }}</span>
            <span>{{ new Date(group.createdAt).toLocaleDateString('zh-CN') }}</span>
          </div>
          <div class="pt-2 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <button class="flex-1 text-xs py-1 rounded bg-muted hover:bg-muted/80">详情</button>
            <button class="flex-1 text-xs py-1 rounded bg-primary/10 text-primary hover:bg-primary/20">重新生成</button>
          </div>
        </div>
      </div>
    </div>

    <!-- List View -->
    <div v-else class="border border-border rounded-lg overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-muted/50">
          <tr>
            <th class="text-left p-3 text-xs font-medium text-muted-foreground">原图</th>
            <th class="text-left p-3 text-xs font-medium text-muted-foreground">风格</th>
            <th class="text-left p-3 text-xs font-medium text-muted-foreground">模型</th>
            <th class="text-left p-3 text-xs font-medium text-muted-foreground">评分</th>
            <th class="text-left p-3 text-xs font-medium text-muted-foreground">尝试</th>
            <th class="text-left p-3 text-xs font-medium text-muted-foreground">费用</th>
            <th class="text-left p-3 text-xs font-medium text-muted-foreground">时间</th>
            <th class="text-right p-3 text-xs font-medium text-muted-foreground">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="group in groups" :key="group.id" class="border-t border-border hover:bg-muted/20 cursor-pointer" @click="viewDetail(group.id)">
            <td class="p-3 text-xs">🖼️</td>
            <td class="p-3 text-xs">{{ group.tagId?.slice(0, 10) || '...' }}</td>
            <td class="p-3 text-xs">{{ group.modelId?.slice(0, 10) || '...' }}</td>
            <td class="p-3 text-xs">{{ renderStars(null) }}</td>
            <td class="p-3 text-xs">{{ group.totalAttempts }}</td>
            <td class="p-3 text-xs">¥{{ group.totalCostYuan || 0 }}</td>
            <td class="p-3 text-xs">{{ new Date(group.createdAt).toLocaleDateString('zh-CN') }}</td>
            <td class="p-3 text-xs text-right">
              <button class="text-primary hover:underline">详情</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
