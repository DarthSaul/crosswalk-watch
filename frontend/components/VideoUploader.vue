<script setup lang="ts">
import type { JobResponse } from '~/types/api'

const emit = defineEmits<{ uploaded: [job: JobResponse] }>()

const { uploadVideo } = useJobApi()

const isDragging = ref(false)
const isUploading = ref(false)
const error = ref<string | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)

async function handleFile(file: File) {
  error.value = null
  if (!file.type.startsWith('video/')) {
    error.value = `Expected a video file, got "${file.type || 'unknown'}".`
    return
  }
  isUploading.value = true
  try {
    const job = await uploadVideo(file)
    emit('uploaded', job)
  } catch (e: unknown) {
    const message = e instanceof Error ? e.message : String(e)
    error.value = `Upload failed: ${message}`
  } finally {
    isUploading.value = false
  }
}

function onDrop(event: DragEvent) {
  event.preventDefault()
  isDragging.value = false
  const file = event.dataTransfer?.files?.[0]
  if (file) handleFile(file)
}

function onChange(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) handleFile(file)
  target.value = ''
}

function openPicker() {
  fileInput.value?.click()
}
</script>

<template>
  <div
    class="uploader"
    :class="{ dragging: isDragging, uploading: isUploading }"
    @dragover.prevent="isDragging = true"
    @dragenter.prevent="isDragging = true"
    @dragleave.prevent="isDragging = false"
    @drop="onDrop"
    @click="openPicker"
  >
    <input
      ref="fileInput"
      type="file"
      accept="video/*"
      class="hidden-input"
      @change="onChange"
    >
    <div v-if="isUploading" class="status">Uploading…</div>
    <div v-else class="prompt">
      <p class="title">Drop a video here</p>
      <p class="sub">or click to choose a file</p>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<style scoped>
.uploader {
  border: 2px dashed var(--border);
  border-radius: var(--radius);
  padding: 36px 20px;
  text-align: center;
  cursor: pointer;
  background: var(--bg-soft);
  transition: border-color var(--transition), background-color var(--transition);
}
.uploader.dragging { border-color: var(--accent); background: var(--accent-soft); }
.uploader.uploading { cursor: progress; opacity: 0.75; }
.title { font-size: 15px; font-weight: 600; margin: 0 0 4px; }
.sub { color: var(--muted); margin: 0; font-size: 13px; }
.status { font-size: 14px; color: var(--accent); }
.error { color: var(--danger); margin-top: 10px; font-size: 13px; }
.hidden-input { display: none; }
</style>
