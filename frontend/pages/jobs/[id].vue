<script setup lang="ts">
import type { JobResponse } from '~/types/api'

const route = useRoute()
const jobId = computed(() => String(route.params.id))
const { getJob, thumbnailUrl } = useJobApi()

const { data: job, error, pending, refresh } = await useAsyncData<JobResponse>(
  () => `job-${jobId.value}`,
  () => getJob(jobId.value),
  { watch: [jobId] },
)

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString()
}
</script>

<template>
  <section>
    <div v-if="pending" class="state">Loading job…</div>

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
        <button class="refresh" @click="refresh()">Refresh</button>
      </header>

      <figure v-if="job.thumbnail_url" class="thumb">
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

.refresh {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text);
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
}
.refresh:hover { border-color: var(--accent); color: var(--accent); }

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
