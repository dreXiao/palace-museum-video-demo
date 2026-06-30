<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { modelsApi, ApiError } from '@/api/client'
import type { ModelConfig } from '@/types/models'
import { Plus, Upload, RotateCcw, Edit, Wifi, Trash2 } from 'lucide-vue-next'

const models = ref<ModelConfig[]>([])
const loading = ref(true)
const showEditor = ref(false)
const editingModel = ref<ModelConfig | null>(null)
const editorMode = ref<'create' | 'edit'>('create')
const testingModels = ref<Set<string>>(new Set())

const editForm = ref({
  name: '', provider: '', description: '',
  api_type: 'custom', endpoint: '', api_key_env: '',
  model_ids: {} as Record<string, string>,
  parameters: {} as Record<string, any>,
  pricing: {} as Record<string, any>,
  generation_config: {} as Record<string, any>,
})

onMounted(async () => {
  await loadModels()
})

async function loadModels() {
  try {
    const res = await modelsApi.list()
    models.value = (res as any).data || []
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editorMode.value = 'create'
  editForm.value = {
    name: '', provider: '', description: '',
    api_type: 'dashscope', endpoint: '', api_key_env: '',
    model_ids: {}, parameters: { duration: { min: 4, max: 15, default: 10 }, resolutions: { options: ['720p', '1080p'], default: '1080p' }, audio: { supported: false, default: false }, frameControl: { supported: false }, extended: {} },
    pricing: { mode: 'per_second', currency: 'CNY', rates: {} },
    generation_config: { maxConcurrent: 2, pollIntervalMs: 3000, timeoutMs: 300000, retryCount: 2 },
  }
  showEditor.value = true
}

function openEdit(model: ModelConfig) {
  editorMode.value = 'edit'
  editingModel.value = model
  editForm.value = {
    name: model.name, provider: model.provider, description: model.description || '',
    api_type: model.apiType, endpoint: model.endpoint, api_key_env: model.apiKeyEnv,
    model_ids: { ...model.modelIds }, parameters: { ...model.parameters },
    pricing: { ...model.pricing }, generation_config: { ...(model.generationConfig || {}) },
  }
  showEditor.value = true
}

async function saveModel() {
  try {
    if (editorMode.value === 'create') {
      await modelsApi.create(editForm.value)
    } else if (editingModel.value) {
      await modelsApi.update(editingModel.value.id, editForm.value)
    }
    showEditor.value = false
    await loadModels()
  } catch (e) {
    alert(e instanceof ApiError ? e.message : '保存失败')
  }
}

async function handleDelete(model: ModelConfig) {
  if (!confirm(`确定删除模型"${model.name}"？`)) return
  try {
    await modelsApi.delete(model.id)
    models.value = models.value.filter(m => m.id !== model.id)
  } catch (e) {
    alert(e instanceof ApiError ? e.message : '删除失败')
  }
}

async function handleTest(model: ModelConfig) {
  testingModels.value.add(model.id)
  try {
    const res = await modelsApi.testConnection(model.id)
    await loadModels()
  } catch (e) {
    alert('测试失败')
  } finally {
    testingModels.value.delete(model.id)
  }
}

async function handleSetDefault(model: ModelConfig) {
  try {
    await modelsApi.setDefault(model.id)
    await loadModels()
  } catch (e) {
    alert('设置失败')
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Toolbar -->
    <div class="flex flex-wrap items-center gap-3">
      <h2 class="text-lg font-semibold">模型管理</h2>
      <div class="flex-1" />
      <div class="text-xs text-muted-foreground">
        共 {{ models.length }} 个 | 🟢 {{ models.filter(m => m.connectionStatus === 'connected').length }} 连通 | 🔴 {{ models.filter(m => m.connectionStatus !== 'connected').length }} 未连通
      </div>
      <button @click="openCreate" class="inline-flex items-center gap-1.5 rounded-md bg-primary text-primary-foreground px-3 py-1.5 text-xs hover:opacity-90">
        <Plus class="h-3.5 w-3.5" /> 添加模型
      </button>
      <button class="inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 text-xs hover:bg-muted">
        <Upload class="h-3.5 w-3.5" /> 导入
      </button>
      <button @click="loadModels" class="inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 text-xs hover:bg-muted">
        <RotateCcw class="h-3.5 w-3.5" /> 刷新状态
      </button>
    </div>

    <!-- Model List -->
    <div class="space-y-3">
      <div
        v-for="model in models" :key="model.id"
        :class="[
          'border rounded-lg p-4 space-y-2 transition-colors',
          model.isDefault ? 'border-primary/30 bg-primary/[0.02]' : 'border-border',
        ]"
      >
        <div class="flex items-start justify-between">
          <div class="flex items-center gap-2">
            <span
              :class="['w-2.5 h-2.5 rounded-full shrink-0 mt-1',
                model.connectionStatus === 'connected' ? 'bg-emerald-500' :
                model.connectionStatus === 'failed' ? 'bg-red-500' : 'bg-yellow-500',
              ]"
            />
            <div>
              <div class="flex items-center gap-2">
                <span class="font-medium">{{ model.name }}</span>
                <span v-if="model.isDefault" class="text-[10px] bg-primary/10 text-primary px-1.5 py-0.5 rounded">默认</span>
                <span v-if="model.isPreset" class="text-[10px] bg-muted text-muted-foreground px-1.5 py-0.5 rounded">系统预设</span>
              </div>
              <div class="text-xs text-muted-foreground mt-0.5">
                {{ model.provider }} · {{ model.apiType }} · {{ model.endpoint }}
              </div>
            </div>
          </div>
          <div class="flex items-center gap-1">
            <button @click="handleSetDefault(model)" v-if="!model.isDefault" class="text-xs text-muted-foreground hover:text-foreground px-2 py-1 rounded hover:bg-muted">设为默认</button>
            <button @click="openEdit(model)" class="p-1.5 rounded hover:bg-muted"><Edit class="h-3.5 w-3.5" /></button>
            <button @click="handleTest(model)" :disabled="testingModels.has(model.id)" class="p-1.5 rounded hover:bg-muted">
              <Wifi :class="['h-3.5 w-3.5', testingModels.has(model.id) ? 'animate-pulse' : '']" />
            </button>
            <button @click="handleDelete(model)" v-if="!model.isPreset" class="p-1.5 rounded hover:bg-muted text-destructive"><Trash2 class="h-3.5 w-3.5" /></button>
          </div>
        </div>
        <div class="grid grid-cols-2 lg:grid-cols-5 gap-2 text-xs text-muted-foreground">
          <div>💰 ¥{{ model.pricing?.rates?.['1080p'] || '?' }}/秒</div>
          <div>⏱ {{ model.parameters?.duration?.min || 4 }}-{{ model.parameters?.duration?.max || 15 }}秒</div>
          <div>🖥 {{ (model.parameters?.resolutions?.options || ['1080p']).join('/') }}</div>
          <div>🔄 并发{{ model.generationConfig?.maxConcurrent || 2 }}</div>
          <div v-if="model.lastTestedAt">最后测试: {{ new Date(model.lastTestedAt).toLocaleString('zh-CN') }}</div>
        </div>
      </div>
    </div>

    <!-- Editor Modal -->
    <div v-if="showEditor" class="fixed inset-0 z-50 flex items-start justify-center pt-[5vh] bg-black/50" @click.self="showEditor = false">
      <div class="w-full max-w-3xl bg-card border border-border rounded-xl shadow-2xl mx-4 max-h-[90vh] overflow-y-auto" @click.stop>
        <div class="flex items-center justify-between p-4 border-b border-border">
          <h3 class="font-semibold">{{ editorMode === 'create' ? '新建模型' : '编辑模型' }}</h3>
          <button @click="showEditor = false" class="p-1 hover:bg-muted rounded">✕</button>
        </div>
        <div class="p-6 space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-xs font-medium">模型名称</label>
              <input v-model="editForm.name" class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm mt-1" />
            </div>
            <div>
              <label class="text-xs font-medium">厂商</label>
              <input v-model="editForm.provider" class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm mt-1" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-xs font-medium">API 类型</label>
              <select v-model="editForm.api_type" class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm mt-1">
                <option value="dashscope">DashScope (通义万相)</option>
                <option value="volcengine-ark">火山引擎 ARK (Seedance)</option>
                <option value="kling">Kling 开放平台</option>
                <option value="custom">自定义</option>
              </select>
            </div>
            <div>
              <label class="text-xs font-medium">API 端点</label>
              <input v-model="editForm.endpoint" class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm mt-1" />
            </div>
          </div>
          <div>
            <label class="text-xs font-medium">API Key 环境变量名</label>
            <input v-model="editForm.api_key_env" placeholder="例如: DASHSCOPE_API_KEY" class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm mt-1" />
          </div>
          <div>
            <label class="text-xs font-medium">模型ID映射 (JSON)</label>
            <textarea v-model="editForm.model_ids" class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm mt-1 font-mono h-20" />
          </div>
          <details class="border border-border rounded-lg p-4">
            <summary class="text-sm font-medium cursor-pointer">高级: 参数 / 计费 / 生成行为 (JSON)</summary>
            <div class="mt-4 space-y-3">
              <div>
                <label class="text-xs font-medium">参数配置 (JSON)</label>
                <textarea v-model="editForm.parameters" class="w-full rounded-md border border-input bg-background px-3 py-2 text-xs font-mono h-32" />
              </div>
              <div>
                <label class="text-xs font-medium">计费配置 (JSON)</label>
                <textarea v-model="editForm.pricing" class="w-full rounded-md border border-input bg-background px-3 py-2 text-xs font-mono h-24" />
              </div>
              <div>
                <label class="text-xs font-medium">生成行为配置 (JSON)</label>
                <textarea v-model="editForm.generation_config" class="w-full rounded-md border border-input bg-background px-3 py-2 text-xs font-mono h-20" />
              </div>
            </div>
          </details>
        </div>
        <div class="flex justify-end gap-2 p-4 border-t border-border">
          <button @click="showEditor = false" class="px-4 py-2 rounded-md border border-border text-sm hover:bg-muted">取消</button>
          <button @click="saveModel" class="px-4 py-2 rounded-md bg-primary text-primary-foreground text-sm hover:opacity-90">保存模型</button>
        </div>
      </div>
    </div>
  </div>
</template>
