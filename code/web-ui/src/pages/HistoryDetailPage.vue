<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { historyApi, generationApi } from '@/api/client'
import { ArrowLeft, Play, RefreshCw, Star } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const groupId = route.params.id as string
const detail = ref<Record<string, any>>({})
const attempts = ref<any[]>([])
const loading = ref(true)
const regenerating = ref(false)
const regenPrompt = ref('')
const regenModel = ref('')
const regenDuration = ref(10)

onMounted(async () => {
  try {
    const res = await historyApi.getGroupDetail(groupId)
    const data = (res as any).data
    detail.value = data.group || {}
    attempts.value = data.attempts || []
    if (attempts.value.length > 0) {
      regenPrompt.value = attempts.value[0].prompt || ''
    }
  } catch (e) {
    console.error('Failed to load detail', e)
  } finally {
    loading.value = false
  }
})

async function handleRegenerate() {
  regenerating.value = true
  try {
    await generationApi.submit({
      image_asset_id: detail.value.imageAssetId,
      tag_ids: [detail.value.tagId],
      model_id: detail.value.modelId,
      duration: regenDuration.value,
      resolution: '1080p',
      extended_params: {},
    })
    alert('已提交重新生成任务')
  } catch (e) {
    console.error(e)
  } finally {
    regenerating.value = false
  }
}

function renderStars(score: number | null): string {
  return score ? '⭐'.repeat(score) : '—'
}
</script>

<template>
  <div class="space-y-6" v-if="!loading">
    <!-- Header -->
    <div class="flex items-center gap-3">
      <button @click="router.push('/history')" class="p-1 rounded hover:bg-muted"><ArrowLeft class="h-5 w-5" /></button>
      <div class="text-sm text-muted-foreground">返回历史列表</div>
    </div>

    <div class="text-lg font-semibold">
      {{ detail.imageAssetId?.slice(0, 12) || '...' }}
    </div>

    <!-- Comparison View -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="border border-border rounded-lg p-4">
        <h4 class="text-sm font-medium mb-3">原图 vs 生成视频</h4>
        <div class="flex items-center justify-center gap-4">
          <div class="w-1/2 aspect-square bg-muted rounded-lg flex items-center justify-center text-muted-foreground text-sm">
            原图
          </div>
          <span class="text-muted-foreground">→</span>
          <div class="w-1/2 aspect-square bg-muted rounded-lg flex items-center justify-center text-muted-foreground text-sm">
            <Play class="h-8 w-8" />
          </div>
        </div>
      </div>

      <!-- Attempt Timeline -->
      <div class="border border-border rounded-lg p-4">
        <h4 class="text-sm font-medium mb-3">生成尝试时间线</h4>
        <div class="space-y-3 max-h-[400px] overflow-y-auto">
          <div
            v-for="(attempt, i) in attempts" :key="attempt.id"
            :class="[
              'border rounded-lg p-3 text-sm',
              attempt.is_best_attempt ? 'border-emerald-500/30 bg-emerald-500/5' : 'border-border',
            ]"
          >
            <div class="flex items-center gap-2 mb-1">
              <span class="font-medium">尝试 #{{ attempt.attempt_number }}</span>
              <span class="text-muted-foreground">· {{ attempt.model_snapshot?.name || '未知' }}</span>
              <span class="text-muted-foreground">· {{ renderStars(attempt.quality_score) }}</span>
              <span class="text-muted-foreground">· ¥{{ attempt.cost_yuan || 0 }}</span>
              <span v-if="attempt.is_best_attempt" class="text-xs text-emerald-600 font-medium">✅ 最佳</span>
            </div>
            <div class="text-xs text-muted-foreground mb-1">提示词: {{ attempt.prompt?.slice(0, 80) }}...</div>
            <div class="flex gap-2">
              <button class="text-xs text-primary hover:underline">▶ 播放视频</button>
              <button class="text-xs text-primary hover:underline">下载</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Regenerate Panel -->
    <div class="border border-border rounded-lg p-4">
      <h4 class="text-sm font-medium mb-3 flex items-center gap-2"><RefreshCw class="h-4 w-4" /> 重新生成</h4>
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-3 items-end">
        <div class="lg:col-span-2">
          <label class="text-xs text-muted-foreground block mb-1">修改提示词</label>
          <textarea v-model="regenPrompt" rows="2" class="w-full rounded-md border border-input bg-background px-3 py-2 text-xs" />
        </div>
        <div>
          <label class="text-xs text-muted-foreground block mb-1">时长</label>
          <select v-model.number="regenDuration" class="w-full rounded-md border border-input bg-background px-3 py-1.5 text-xs">
            <option :value="6">6s</option>
            <option :value="10">10s</option>
            <option :value="15">15s</option>
          </select>
        </div>
        <div>
          <button
            @click="handleRegenerate"
            :disabled="regenerating"
            class="w-full rounded-md bg-primary text-primary-foreground px-4 py-2 text-sm font-medium hover:opacity-90 disabled:opacity-50"
          >
            {{ regenerating ? '提交中...' : '🎬 重新生成' }}
          </button>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="space-y-4 animate-pulse">
    <div class="h-6 bg-muted rounded w-32" />
    <div class="h-64 bg-muted rounded-lg" />
    <div class="h-32 bg-muted rounded-lg" />
  </div>
</template>
