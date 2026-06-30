<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { tagsApi, ApiError } from '@/api/client'
import type { StyleTag } from '@/types/models'
import { Plus, Download, Upload, RotateCcw, Edit, Copy, Trash2 } from 'lucide-vue-next'

const tags = ref<StyleTag[]>([])
const loading = ref(true)
const editingTag = ref<StyleTag | null>(null)
const showEditor = ref(false)
const showCustom = ref(false)  // toggle to show/hide custom tags section
const editorMode = ref<'create' | 'edit'>('create')

// Editor form state
const editForm = ref({
  name: '', color: '#6366F1', icon: '🎨', description: '',
  positive_prompt: '', negative_prompt: '', variables: [] as string[],
  applicable_types: [] as string[], default_params: {} as Record<string, any>,
})

const presets = computed(() => tags.value.filter(t => t.isPreset))
const customs = computed(() => tags.value.filter(t => !t.isPreset))

onMounted(async () => {
  await loadTags()
})

async function loadTags() {
  try {
    const res = await tagsApi.list()
    tags.value = (res as any).data || []
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editorMode.value = 'create'
  editForm.value = { name: '', color: '#6366F1', icon: '🎨', description: '', positive_prompt: '', negative_prompt: '', variables: [], applicable_types: [], default_params: {} }
  showEditor.value = true
}

function openEdit(tag: StyleTag) {
  editorMode.value = 'edit'
  editingTag.value = tag
  editForm.value = {
    name: tag.name, color: tag.color, icon: tag.icon,
    description: tag.description || '', positive_prompt: tag.positivePrompt,
    negative_prompt: tag.negativePrompt || '', variables: tag.variables || [],
    applicable_types: tag.applicableTypes || [], default_params: tag.defaultParams || {},
  }
  showEditor.value = true
}

async function saveTag() {
  try {
    if (editorMode.value === 'create') {
      const res = await tagsApi.create(editForm.value)
      tags.value.push((res as any).data)
    } else if (editingTag.value) {
      await tagsApi.update(editingTag.value.id, { ...editForm.value, change_note: '编辑标签' })
      await loadTags()
    }
    showEditor.value = false
  } catch (e) {
    alert(e instanceof ApiError ? e.message : '保存失败')
  }
}

async function handleDelete(tag: StyleTag) {
  if (!confirm(`确定删除标签"${tag.name}"？`)) return
  try {
    await tagsApi.delete(tag.id)
    tags.value = tags.value.filter(t => t.id !== tag.id)
  } catch (e) {
    alert(e instanceof ApiError ? e.message : '删除失败')
  }
}

async function handleCopy(tag: StyleTag) {
  try {
    await tagsApi.copy(tag.id)
    await loadTags()
  } catch (e) {
    alert('复制失败')
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Toolbar -->
    <div class="flex flex-wrap items-center gap-3">
      <h2 class="text-lg font-semibold">标签管理</h2>
      <div class="flex-1" />
      <button @click="openCreate" class="inline-flex items-center gap-1.5 rounded-md bg-primary text-primary-foreground px-3 py-1.5 text-xs hover:opacity-90">
        <Plus class="h-3.5 w-3.5" /> 新建标签
      </button>
      <button class="inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 text-xs hover:bg-muted">
        <Upload class="h-3.5 w-3.5" /> 导入
      </button>
      <button class="inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 text-xs hover:bg-muted">
        <Download class="h-3.5 w-3.5" /> 导出
      </button>
      <button class="inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 text-xs hover:bg-muted">
        <RotateCcw class="h-3.5 w-3.5" /> 恢复预设
      </button>
    </div>

    <!-- Presets -->
    <div>
      <h3 class="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-3">预设标签组 (5组)</h3>
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-3">
        <div
          v-for="tag in presets" :key="tag.id"
          class="border border-border rounded-lg p-4 space-y-2 hover:border-primary/20 transition-colors"
        >
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-2">
              <span class="text-xl">{{ tag.icon }}</span>
              <span class="font-medium text-sm">{{ tag.name }}</span>
              <span class="text-[10px] bg-muted px-1.5 py-0.5 rounded text-muted-foreground">系统预设</span>
            </div>
          </div>
          <p class="text-xs text-muted-foreground">{{ tag.description || '无描述' }}</p>
          <div class="text-[11px] text-muted-foreground truncate">
            正向: {{ tag.positivePrompt?.slice(0, 60) }}...
          </div>
          <div class="flex items-center justify-between text-[11px] text-muted-foreground">
            <span>使用: {{ tag.usageCount || 0 }}次</span>
            <div class="flex gap-2">
              <button @click="openEdit(tag)" class="text-primary hover:underline">编辑</button>
              <button @click="handleCopy(tag)" class="text-primary hover:underline">复制</button>
              <button @click="handleDelete(tag)" class="text-destructive hover:underline">删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Customs -->
    <div v-if="customs.length">
      <h3 class="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-3">自定义标签</h3>
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-3">
        <div
          v-for="tag in customs" :key="tag.id"
          class="border border-dashed border-border rounded-lg p-4 space-y-2 hover:border-primary/20 transition-colors"
        >
          <div class="flex items-center gap-2">
            <span class="text-xl">{{ tag.icon }}</span>
            <span class="font-medium text-sm">{{ tag.name }}</span>
          </div>
          <p class="text-xs text-muted-foreground">{{ tag.description || '无描述' }}</p>
          <div class="flex items-center justify-between text-[11px] text-muted-foreground">
            <span>使用: {{ tag.usageCount || 0 }}次</span>
            <div class="flex gap-2">
              <button @click="openEdit(tag)" class="text-primary hover:underline">编辑</button>
              <button @click="handleCopy(tag)" class="text-primary hover:underline">复制</button>
              <button @click="handleDelete(tag)" class="text-destructive hover:underline">删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Editor Modal -->
    <div v-if="showEditor" class="fixed inset-0 z-50 flex items-start justify-center pt-[10vh] bg-black/50" @click.self="showEditor = false">
      <div class="w-full max-w-2xl bg-card border border-border rounded-xl shadow-2xl mx-4 max-h-[85vh] overflow-y-auto" @click.stop>
        <div class="flex items-center justify-between p-4 border-b border-border">
          <h3 class="font-semibold">{{ editorMode === 'create' ? '新建标签' : '编辑标签' }}</h3>
          <button @click="showEditor = false" class="p-1 hover:bg-muted rounded">✕</button>
        </div>
        <div class="p-6 space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-xs font-medium">标签名称</label>
              <input v-model="editForm.name" class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm mt-1" />
            </div>
            <div>
              <label class="text-xs font-medium">颜色</label>
              <input v-model="editForm.color" type="color" class="w-full h-9 rounded-md border border-input mt-1" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-xs font-medium">图标 (Emoji)</label>
              <input v-model="editForm.icon" class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm mt-1" />
            </div>
            <div>
              <label class="text-xs font-medium">适用类型 (逗号分隔)</label>
              <input v-model="editForm.applicable_types" class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm mt-1" />
            </div>
          </div>
          <div>
            <label class="text-xs font-medium">描述</label>
            <input v-model="editForm.description" class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm mt-1" />
          </div>
          <div>
            <label class="text-xs font-medium">正向提示词</label>
            <textarea v-model="editForm.positive_prompt" rows="4" class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm mt-1 font-mono" />
          </div>
          <div>
            <label class="text-xs font-medium">负向提示词</label>
            <textarea v-model="editForm.negative_prompt" rows="2" class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm mt-1 font-mono" />
          </div>
        </div>
        <div class="flex justify-end gap-2 p-4 border-t border-border">
          <button @click="showEditor = false" class="px-4 py-2 rounded-md border border-border text-sm hover:bg-muted">取消</button>
          <button @click="saveTag" class="px-4 py-2 rounded-md bg-primary text-primary-foreground text-sm hover:opacity-90">保存标签</button>
        </div>
      </div>
    </div>
  </div>
</template>
