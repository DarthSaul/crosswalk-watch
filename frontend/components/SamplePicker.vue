<script setup lang="ts">
import type { JobResponse, SampleInfo } from '~/types/api'

const emit = defineEmits<{
  selected: [job: JobResponse]
}>()

const { listSamples, createJobFromSample, sampleThumbnailUrl, apiBase } = useJobApi()

const samples = ref<SampleInfo[]>([])
const loading = ref(true)
const loadError = ref<string | null>(null)
const busyFilename = ref<string | null>(null)
const actionError = ref<string | null>(null)

async function refresh() {
  loading.value = true
  loadError.value = null
  try {
    samples.value = await listSamples()
  } catch (e: unknown) {
    loadError.value = e instanceof Error ? e.message : String(e)
  } finally {
    loading.value = false
  }
}

async function pick(sample: SampleInfo) {
  if (busyFilename.value) return
  busyFilename.value = sample.filename
  actionError.value = null
  try {
    const job = await createJobFromSample(sample.filename)
    emit('selected', job)
  } catch (e: unknown) {
    actionError.value = e instanceof Error ? e.message : String(e)
  } finally {
    busyFilename.value = null
  }
}

function formatSize(bytes: number): string {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`
}

function formatDuration(seconds: number | null): string {
  if (seconds === null || !isFinite(seconds)) return '—'
  if (seconds < 60) return `${seconds.toFixed(1)}s`
  const m = Math.floor(seconds / 60)
  const s = Math.round(seconds % 60)
  return `${m}m ${s}s`
}

function fullThumbUrl(sample: SampleInfo): string {
  if (sample.thumbnail_url.startsWith('http')) return sample.thumbnail_url
  if (sample.thumbnail_url.startsWith('/')) return `${apiBase}${sample.thumbnail_url}`
  return sampleThumbnailUrl(sample.filename)
}

onMounted(refresh)
</script>

<template>
  <section class="sample-picker">
    <header>
      <h3>Sample clips</h3>
      <button v-if="!loading" type="button" class="link" @click="refresh">Refresh</button>
    </header>

    <p v-if="loading" class="muted">Loading samples…</p>
    <p v-else-if="loadError" class="error">{{ loadError }}</p>
    <p v-else-if="!samples.length" class="muted">
      No clips in <code>backend/data/samples/</code> yet. Drop a few <code>.mp4</code> files
      there, or run <code>./scripts/fetch_samples.sh</code> from the repo root.
    </p>

    <ul v-else class="grid">
      <li v-for="sample in samples" :key="sample.filename" class="card">
        <button
          type="button"
          class="card-button"
          :disabled="busyFilename !== null"
          :aria-busy="busyFilename === sample.filename"
          @click="pick(sample)"
        >
          <div class="thumb-wrap">
            <img :src="fullThumbUrl(sample)" :alt="`Preview of ${sample.filename}`" loading="lazy">
            <span v-if="busyFilename === sample.filename" class="overlay">Loading…</span>
          </div>
          <div class="meta">
            <p class="filename" :title="sample.filename">{{ sample.filename }}</p>
            <p class="info">
              <span v-if="sample.width && sample.height">{{ sample.width }}×{{ sample.height }}</span>
              <span v-if="sample.fps">· {{ Math.round(sample.fps) }} fps</span>
              <span>· {{ formatDuration(sample.duration_seconds) }}</span>
              <span>· {{ formatSize(sample.size_bytes) }}</span>
            </p>
          </div>
        </button>
      </li>
    </ul>

    <p v-if="actionError" class="error">{{ actionError }}</p>
  </section>
</template>

<style scoped>
.sample-picker { display: flex; flex-direction: column; gap: 12px; }
header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}
h3 {
  margin: 0;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: var(--muted);
}
.link {
  background: none;
  border: none;
  color: var(--accent);
  cursor: pointer;
  font-size: 12px;
  padding: 0;
}
.muted { color: var(--muted); margin: 0; font-size: 13px; }
.error {
  color: var(--danger);
  background: var(--danger-soft);
  border: 1px solid rgba(248, 113, 113, 0.3);
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  margin: 0;
}

.grid {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}
.card { margin: 0; }
.card-button {
  width: 100%;
  text-align: left;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  cursor: pointer;
  padding: 0;
  color: var(--text);
  transition: border-color var(--transition), transform var(--transition);
  display: flex;
  flex-direction: column;
}
.card-button:hover:not(:disabled) {
  border-color: var(--accent);
  transform: translateY(-1px);
}
.card-button:disabled { opacity: 0.6; cursor: progress; }

.thumb-wrap {
  position: relative;
  aspect-ratio: 16 / 9;
  background: #000;
}
.thumb-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.overlay {
  position: absolute;
  inset: 0;
  background: rgba(10, 13, 18, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  color: var(--accent);
}

.meta { padding: 10px 12px; }
.filename {
  margin: 0;
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.info {
  margin: 4px 0 0;
  color: var(--muted);
  font-size: 11px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
</style>
