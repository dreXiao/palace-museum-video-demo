<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Upload, Play, X, Loader2, Clock, Coins, AlertCircle } from 'lucide-vue-next'
import { modelsApi, tagsApi, mediaApi, generationApi, ApiError } from '@/api/client'
import { useGenerationStore } from '@/stores/generation'
import type { ModelConfig, StyleTag, ImageAsset } from '@/types/models'

const genStore = useGenerationStore()

// ── State ──
const models = ref<ModelConfig[]>([])
const tags = ref<StyleTag[]>([])
const uploadedImage = ref<ImageAsset | null>(null)
const uploading = ref(false)

const selectedTagIds = ref<string[]>([])
const selectedModelId = ref('')
const duration = ref(10)
const resolution = ref('1080p')
const generating = ref(false)
const errorToast = ref('')
const successToast = ref('')

// ── Computed ──
const presets = computed(() => tags.value.filter(t => t.isPreset))
const customs = computed(() => tags.value.filter(t => !t.isPreset))
const selectedModel = computed(() => models.value.find(m => m.id === selectedModelId.value))
const selectedTags = computed(() => tags.value.filter(t => selectedTagIds.value.includes(t.id)))
const estimatedCost = computed(() => {
  if (!selectedModel.value || !selectedTags.value.length) return 0
  const rate = selectedModel.value.pricing?.rates?.[resolution.value] || 0
  return rate * duration.value * selectedTags.value.length
})
const canGenerate = computed(() =>
  uploadedImage.value && selectedTagIds.value.length > 0 && selectedModelId.value && !generating.value
)

// ── Lifecycle ──
onMounted(async () => {
  try {
    const [modelsRes, tagsRes] = await Promise.all([modelsApi.list(), tagsApi.list()])
    models.value = (modelsRes as any).data || []
    tags.value = (tagsRes as any).data || []
    const def = models.value.find(m => m.isDefault)
    if (def) selectedModelId.value = def.id
  } catch (e) {
    showError('加载配置失败')
  }
})

// ── Methods ──
async function handleFileDrop(e: DragEvent) {
  e.preventDefault()
  const file = e.dataTransfer?.files?.[0]
  if (file) await uploadFile(file)
}

async function handleFileSelect(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) await uploadFile(file)
}

async function handlePaste(e: ClipboardEvent) {
  const file = e.clipboardData?.files?.[0]
  if (file) await uploadFile(file)
}

async function uploadFile(file: File) {
  if (!['image/png', 'image/jpeg', 'image/webp'].includes(file.type)) {
    showError('仅支持 PNG/JPG/WEBP 格式')
    return
  }
  if (file.size > 20 * 1024 * 1024) {
    showError('文件大小不能超过 20MB')
    return
  }
  uploading.value = true
  try {
    const res = await mediaApi.upload(file)
    uploadedImage.value = (res as any).data
  } catch (e) {
    showError('上传失败')
  } finally {
    uploading.value = false
  }
}

function toggleTag(tagId: string) {
  const idx = selectedTagIds.value.indexOf(tagId)
  if (idx >= 0) {
    selectedTagIds.value.splice(idx, 1)
  } else if (selectedTagIds.value.length < 6) {
    selectedTagIds.value.push(tagId)
  }
}

async function startGeneration() {
  if (!canGenerate.value) return
  generating.value = true
  try {
    const res = await generationApi.batchSubmit({
      image_asset_id: uploadedImage.value!.id,
      tag_ids: selectedTagIds.value,
      model_ids: [selectedModelId.value],
      duration: duration.value,
      resolution: resolution.value,
      extended_params: {},
    })
    const data = (res as any).data || []
    data.forEach((task: any) => {
      genStore.addTask({
        id: task.id,
        groupId: task.group_id,
        imageAssetId: task.image_asset_id,
        tagSnapshot: task.tag_snapshot,
        modelSnapshot: task.model_snapshot,
        prompt: task.prompt,
        status: task.status,
        resultVideoUrl: task.result_video_url,
        errorMessage: task.error_message,
        qualityScore: task.quality_score,
        costYuan: task.cost_yuan,
        created: task.created_at,
      })
    })
    showSuccess(`已提交 ${data.length} 个任务`)
  } catch (e) {
    showError(e instanceof ApiError ? e.message : '提交失败')
  } finally {
    generating.value = false
  }
}

function showError(msg: string) { errorToast.value = msg; setTimeout(() => errorToast.value = '', 4000) }
function showSuccess(msg: string) { successToast.value = msg; setTimeout(() => successToast.value = '', 3000) }
function triggerFileInput() { (document.getElementById('file-input') as HTMLInputElement)?.click() }
</script>

<template>
  <div class="space-y-6" @paste="handlePaste">
    <!-- Toast -->
    <div v-if="errorToast" class="bg-destructive/10 border border-destructive/30 text-destructive rounded-lg px-4 py-3 text-sm">{{ errorToast }}</div>
    <div v-if="successToast" class="bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 rounded-lg px-4 py-3 text-sm">{{ successToast }}</div>

    <!-- Main 3-column Layout -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Left: Upload -->
      <div class="space-y-4">
        <h3 class="text-sm font-medium text-muted-foreground uppercase tracking-wider">📷 上传古画图片</h3>
        <div
          @dragover.prevent
          @drop.prevent="handleFileDrop"
          @click="triggerFileInput"
          class="border-2 border-dashed border-border rounded-xl p-8 text-center cursor-pointer hover:border-primary/50 hover:bg-muted/30 transition-colors min-h-[200px] flex flex-col items-center justify-center"
        >
          <input id="file-input" type="file" accept="image/png,image/jpeg,image/webp" class="hidden" @change="handleFileSelect" />
          <template v-if="!uploadedImage && !uploading">
            <Upload class="h-10 w-10 text-muted-foreground mb-3" />
            <p class="text-sm text-muted-foreground">拖拽或点击上传古画</p>
            <p class="text-xs text-muted-foreground mt-1">PNG / JPG / WEBP · 最大 20MB</p>
          </template>
          <template v-else-if="uploading">
            <Loader2 class="h-10 w-10 text-primary animate-spin mb-3" />
            <p class="text-sm text-muted-foreground">上传中...</p>
          </template>
          <template v-else-if="uploadedImage">
            <img :src="uploadedImage.storageUrl" class="max-h-[160px] max-w-full rounded-lg object-contain mb-2" />
            <p class="text-xs text-muted-foreground">{{ uploadedImage.originalName }} ({{ uploadedImage.width }}×{{ uploadedImage.height }})</p>
            <button @click.stop="uploadedImage = null" class="text-xs text-destructive mt-1 hover:underline">移除</button>
          </template>
        </div>

        <!-- Metadata form -->
        <div v-if="uploadedImage" class="border border-border rounded-lg p-4 space-y-2">
          <p class="text-xs font-medium text-muted-foreground uppercase">📝 古画元数据（可选）</p>
          <div class="grid grid-cols-2 gap-2">
            <input type="text" placeholder="朝代" class="rounded-md border border-input bg-background px-3 py-1.5 text-xs" />
            <input type="text" placeholder="作者" class="rounded-md border border-input bg-background px-3 py-1.5 text-xs" />
            <input type="text" placeholder="类别" class="rounded-md border border-input bg-background px-3 py-1.5 text-xs" />
            <input type="text" placeholder="材质" class="rounded-md border border-input bg-background px-3 py-1.5 text-xs" />
          </div>
        </div>
      </div>

      <!-- Center: Style + Model -->
      <div class="space-y-6">
        <!-- Style Tags -->
        <div>
          <h3 class="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-3">🎨 选择风格标签 ({{ selectedTagIds.length }}/6)</h3>
          <div class="space-y-3">
            <div v-if="presets.length" class="grid grid-cols-3 gap-2">
              <button
                v-for="tag in presets" :key="tag.id"
                @click="toggleTag(tag.id)"
                :class="[
                  'flex flex-col items-center gap-1 p-3 rounded-lg border text-xs transition-all',
                  selectedTagIds.includes(tag.id)
                    ? 'border-primary bg-primary/5 text-primary font-medium'
                    : 'border-border hover:border-primary/30 hover:bg-muted/20',
                ]"
              >
                <span class="text-lg">{{ tag.icon }}</span>
                <span>{{ tag.name }}</span>
              </button>
            </div>
            <div v-if="customs.length" class="grid grid-cols-3 gap-2">
              <button
                v-for="tag in customs" :key="tag.id"
                @click="toggleTag(tag.id)"
                :class="[
                  'flex flex-col items-center gap-1 p-3 rounded-lg border text-xs transition-all',
                  selectedTagIds.includes(tag.id)
                    ? 'border-primary bg-primary/5 text-primary font-medium'
                    : 'border-border hover:border-primary/30 hover:bg-muted/20 border-dashed',
                ]"
              >
                <span class="text-lg">{{ tag.icon }}</span>
                <span>{{ tag.name }}</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Model Selection -->
        <div>
          <h3 class="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-3">🖥️ 选择模型</h3>
          <div class="grid grid-cols-3 gap-2">
            <button
              v-for="model in models" :key="model.id"
              @click="selectedModelId = model.id"
              :class="[
                'p-3 rounded-lg border text-left text-xs transition-all',
                selectedModelId === model.id
                  ? 'border-primary bg-primary/5'
                  : model.connectionStatus === 'connected'
                    ? 'border-border hover:border-primary/30 cursor-pointer'
                    : 'border-border opacity-50 cursor-not-allowed',
              ]"
              :disabled="model.connectionStatus !== 'connected'"
            >
              <div class="flex items-center gap-1.5 mb-1">
                <span :class="['w-2 h-2 rounded-full', model.connectionStatus === 'connected' ? 'bg-emerald-500' : model.connectionStatus === 'failed' ? 'bg-red-500' : 'bg-yellow-500']" />
                <span class="font-medium">{{ model.name }}</span>
              </div>
              <div class="text-muted-foreground">
                {{ model.provider }} · ¥{{ model.pricing?.rates?.[resolution] || '?' }}/秒
              </div>
            </button>
          </div>
        </div>
      </div>

      <!-- Right: Generation Queue -->
      <div class="space-y-4">
        <h3 class="text-sm font-medium text-muted-foreground uppercase tracking-wider">📋 生成队列</h3>
        <div v-if="genStore.activeTasks.length === 0" class="border border-border rounded-lg p-8 text-center">
          <p class="text-sm text-muted-foreground">暂无任务，去左侧选择和生成吧</p>
        </div>
        <div v-else class="space-y-2 max-h-[400px] overflow-y-auto">
          <div
            v-for="task in genStore.activeTasks" :key="task.id"
            :class="[
              'border rounded-lg p-3 text-xs space-y-1',
              task.status === 'completed' ? 'border-emerald-500/30 bg-emerald-500/5' :
              task.status === 'failed' ? 'border-red-500/30 bg-red-500/5' :
              'border-border',
            ]"
          >
            <div class="flex items-center justify-between">
              <span class="font-medium">{{ task.tagSnapshot?.name || '未知风格' }}</span>
              <span :class="[
                'px-1.5 py-0.5 rounded text-[10px] font-medium',
                task.status === 'completed' ? 'bg-emerald-500/10 text-emerald-600' :
                task.status === 'generating' ? 'bg-blue-500/10 text-blue-600' :
                task.status === 'failed' ? 'bg-red-500/10 text-red-600' :
                task.status === 'queued' ? 'bg-muted text-muted-foreground' : 'bg-muted'
              ]">
                {{ task.status === 'completed' ? '✅ 完成' : task.status === 'generating' ? '⏳ 生成中' : task.status === 'failed' ? '❌ 失败' : '📋 排队' }}
              </span>
            </div>
            <div class="text-muted-foreground">{{ task.modelSnapshot?.name || '' }}</div>
            <div v-if="task.costYuan" class="text-muted-foreground">
              <Coins class="h-3 w-3 inline" /> ¥{{ task.costYuan }}
            </div>
            <div v-if="task.errorMessage" class="text-red-500 flex items-center gap-1">
              <AlertCircle class="h-3 w-3" /> {{ task.errorMessage }}
            </div>
            <button
              v-if="task.status === 'completed'"
              class="text-primary text-xs hover:underline"
            >
              ▶ 预览
            </button>
            <button
              v-if="task.status === 'completed' || task.status === 'failed' || task.status === 'cancelled'"
              @click="genStore.removeTask(task.id)"
              class="text-muted-foreground hover:text-foreground ml-2"
            ><X class="h-3 w-3 inline" /></button>
          </div>
        </div>
        <div v-if="genStore.activeTasks.length > 0" class="flex gap-2">
          <button @click="genStore.clearCompleted()" class="text-xs text-muted-foreground hover:text-foreground">清空已完成</button>
        </div>
      </div>
    </div>

    <!-- Parameters Bar -->
    <div class="border border-border rounded-lg p-4">
      <h3 class="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-3">⚙ 参数设置</h3>
      <div class="flex flex-wrap gap-6 items-center">
        <div class="flex items-center gap-2">
          <label class="text-xs text-muted-foreground">时长</label>
          <select v-model.number="duration" class="rounded-md border border-input bg-background px-3 py-1.5 text-xs">
            <option :value="4">4s</option>
            <option :value="6">6s</option>
            <option :value="8">8s</option>
            <option :value="10">10s</option>
            <option :value="12">12s</option>
            <option :value="15">15s</option>
          </select>
        </div>
        <div class="flex items-center gap-2">
          <label class="text-xs text-muted-foreground">分辨率</label>
          <select v-model="resolution" class="rounded-md border border-input bg-background px-3 py-1.5 text-xs">
            <option value="720p">720p</option>
            <option value="1080p">1080p</option>
          </select>
        </div>
        <div v-for="(param, key) in selectedModel?.parameters?.extended || {}" :key="key" class="flex items-center gap-2">
          <template v-if="param.expose && param.type === 'boolean'">
            <label class="text-xs text-muted-foreground">{{ param.label }}</label>
            <input type="checkbox" class="rounded" />
          </template>
          <template v-else-if="param.expose && param.type === 'slider'">
            <label class="text-xs text-muted-foreground">{{ param.label }}</label>
            <input type="range" :min="param.min" :max="param.max" :step="param.step" :value="param.default" class="w-24" />
            <span class="text-xs">{{ param.default }}</span>
          </template>
        </div>
      </div>
    </div>

    <!-- Generate Button -->
    <div class="border border-border rounded-lg p-4 text-center">
      <button
        @click="startGeneration"
        :disabled="!canGenerate"
        class="inline-flex items-center gap-2 rounded-lg bg-primary text-primary-foreground px-8 py-3 text-sm font-medium hover:opacity-90 disabled:opacity-40 transition-opacity"
      >
        <Play class="h-4 w-4" /> 🎬 开始生成视频
      </button>
      <p v-if="estimatedCost > 0" class="text-xs text-muted-foreground mt-2">
        选中 {{ selectedTags.length }} 个标签 × {{ duration }}s × ¥{{ selectedModel?.pricing?.rates?.[resolution] || '?' }}/s = 合计 ¥{{ estimatedCost.toFixed(2) }}
        <span class="text-muted-foreground/60"> | 预计 {{ selectedTags.length }} 个任务</span>
      </p>
    </div>
  </div>
</template>
