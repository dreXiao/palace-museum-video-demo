export interface ModelConfig {
  id: string
  name: string
  provider: string
  description: string | null
  apiType: string
  endpoint: string
  apiKeyEnv: string
  modelIds: Record<string, string>
  parameters: Record<string, any>
  pricing: Record<string, any>
  generationConfig: Record<string, any> | null
  isDefault: boolean
  isPreset: boolean
  connectionStatus: string
  lastTestedAt: string | null
}


export interface StyleTag {
  id: string
  name: string
  color: string
  icon: string
  description: string | null
  applicableTypes: string[]
  positivePrompt: string
  negativePrompt: string
  variables: string[]
  defaultParams: Record<string, any>
  isPreset: boolean
  usageCount: number
  createdAt: string
  updatedAt: string
}


export interface ImageAsset {
  id: string
  originalName: string
  width: number
  height: number
  sizeBytes: number
  mimeType: string
  storageUrl: string
  metadata: Record<string, string>
}


export interface GenerationGroup {
  id: string
  imageAssetId: string
  tagId: string
  modelId: string
  userId: string
  bestAttemptId: string | null
  totalAttempts: number
  totalCostYuan: number
  createdAt: string
  updatedAt: string
}
