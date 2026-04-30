<script setup lang="ts">
import type { JobResponse } from '~/types/api'

const route = useRoute()
const jobId = computed(() => String(route.params.id))
const { getJob, analyzeJob, thumbnailUrl, resultUrl } = useJobApi()

const { data: job, error, pending, refresh } = await useAsyncData<JobResponse>(
  () => `job-${jobId.value}`,
  () => getJob(jobId.value),
  { watch: [jobId] },
)

const analyzeError = ref<string | null>(null)
const isAnalyzing = ref(false)

async function startAnalyze() {
  if (!job.value) return
  analyzeError.value = null
  isAnalyzing.value = true
  try {
    await analyzeJob(job.value.id)
    await refresh()
  } catch (e: unknown) {
    analyzeError.value = e instanceof Error ? e.message : String(e)
  } finally {
    isAnalyzing.value = false
  }
}

let pollTimer: ReturnType<typeof setInterval> | null = null

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

watch(
  () => job.value?.status,
  (status) => {
    if (status === 'processing') {
      if (!pollTimer) pollTimer = setInterval(() => refresh(), 1000)
    } else {
      stopPolling()
    }
  },
  { immediate: true },
)

onBeforeUnmount(stopPolling)

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString()
}
</script>

<template>
  <section>
    <div v-if="pending && !job" class="state">Loading job…</div>

    <div v-else-if="error" class="state error-state">
      <h1>Job not found</h1>
      <p class="muted">No job with id <code>{{ jobId }}</code>.</p>
      <NuxtLink to="/" class="back">← Back to upload</NuxtLink>
    </div>

    <div v-else-if="job" class="job">
      <header class="job-header">
        <div>
          <h1 class="title">{{ job.original_filename }}</h1>
          <p class="meta">
            <span class="badge" :data-status="job.status">{{ job.status }}</span>
            <span class="muted">· {{ formatDate(job.created_at) }}</span>
            <span class="muted">· id {{ job.id.slice(0, 8) }}</span>
          </p>
        </div>
        <button
          v-if="job.status === 'uploaded' || job.status === 'failed' || job.status === 'complete'"
          class="primary"
          :disabled="isAnalyzing"
          @click="startAnalyze"
        >
          {{ job.status === 'complete' ? 'Re-analyze' : 'Analyze' }}
        </button>
      </header>

      <p v-if="job.error" class="error-banner">
        Pipeline failed: {{ job.error }}
      </p>
      <p v-if="analyzeError" class="error-banner">
        {{ analyzeError }}
      </p>

      <AnalysisProgress
        v-if="job.status === 'processing'"
        :progress="job.progress"
      />

      <ResultPlayer
        v-if="job.status === 'complete' && job.result_url"
        :src="resultUrl(job.id)"
        :stats="job.stats"
      />

      <figure
        v-else-if="job.thumbnail_url"
        class="thumb"
      >
        <img :src="thumbnailUrl(job.id)" :alt="`Thumbnail for ${job.original_filename}`">
        <figcaption class="muted">Frame at t≈1.0s</figcaption>
      </figure>
      <p v-else class="muted">Thumbnail not available.</p>
    </div>
  </section>
</template>

<style scoped>
.state { padding: 48px 0; text-align: center; color: var(--muted); }
.error-state h1 { color: var(--text); margin: 0 0 8px; }
.muted { color: var(--muted); }
.back { color: var(--accent); }

.job-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}
.title { margin: 0 0 6px; font-size: 20px; word-break: break-all; }
.meta { margin: 0; display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  background: var(--border);
  color: var(--text);
  text-transform: lowercase;
}
.badge[data-status="uploaded"] { background: #1f6feb33; color: #58a6ff; }
.badge[data-status="processing"] { background: #d4a72c33; color: #e3b341; }
.badge[data-status="complete"] { background: #2ea04333; color: #3fb950; }
.badge[data-status="failed"] { background: #f8514933; color: #f85149; }

.primary {
  background: var(--accent);
  color: #0d1117;
  border: 0;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
}
.primary:hover { filter: brightness(1.1); }
.primary:disabled { opacity: 0.5; cursor: progress; }

.error-banner {
  background: #f8514922;
  border: 1px solid #f8514955;
  color: #ffb4ad;
  padding: 10px 14px;
  border-radius: 8px;
  margin: 0 0 16px;
  font-size: 13px;
}

.thumb {
  margin: 0;
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  background: #000;
}
.thumb img { display: block; width: 100%; height: auto; }
.thumb figcaption { padding: 8px 12px; font-size: 12px; background: var(--panel); }
</style>
