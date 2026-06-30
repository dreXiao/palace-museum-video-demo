import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface GenerationTask {
  id: string
  groupId: string
  imageAssetId: string
  tagSnapshot: Record<string, any>
  modelSnapshot: Record<string, any>
  prompt: string
  status: 'queued' | 'generating' | 'completed' | 'failed' | 'cancelled'
  resultVideoUrl: string | null
  errorMessage: string | null
  qualityScore: number | null
  costYuan: number
  created: string
}

export const useGenerationStore = defineStore('generation', () => {
  const activeTasks = ref<GenerationTask[]>([])

  function addTask(task: GenerationTask) {
    activeTasks.value.unshift(task)
  }

  function updateTask(taskId: string, update: Partial<GenerationTask>) {
    const idx = activeTasks.value.findIndex(t => t.id === taskId)
    if (idx >= 0) {
      activeTasks.value[idx] = { ...activeTasks.value[idx], ...update }
    }
  }

  function removeTask(taskId: string) {
    activeTasks.value = activeTasks.value.filter(t => t.id !== taskId)
  }

  function clearCompleted() {
    activeTasks.value = activeTasks.value.filter(t => t.status === 'generating' || t.status === 'queued')
  }

  return { activeTasks, addTask, updateTask, removeTask, clearCompleted }
})
