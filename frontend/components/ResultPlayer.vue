<script setup lang="ts">
import type { ProcessingStats } from '~/types/api'

defineProps<{ src: string; stats: ProcessingStats | null }>()

function formatDuration(seconds: number): string {
  if (seconds < 1) return `${Math.round(seconds * 1000)} ms`
  if (seconds < 60) return `${seconds.toFixed(1)} s`
  const m = Math.floor(seconds / 60)
  const s = Math.round(seconds % 60)
  return `${m}m ${s}s`
}
</script>

<template>
  <div class="result">
    <video :src="src" controls preload="metadata" class="player" />
    <dl v-if="stats" class="stats">
      <div>
        <dt>Frames</dt>
        <dd>{{ stats.processed_frames }} / {{ stats.total_frames }}</dd>
      </div>
      <div>
        <dt>Unique tracks</dt>
        <dd>{{ stats.unique_tracks }}</dd>
      </div>
      <div>
        <dt>Pipeline time</dt>
        <dd>{{ formatDuration(stats.duration_seconds) }}</dd>
      </div>
    </dl>
  </div>
</template>

<style scoped>
.result { margin-top: 16px; }
.player {
  width: 100%;
  background: #000;
  border: 1px solid var(--border);
  border-radius: 12px;
  display: block;
}
.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
  margin: 16px 0 0;
  padding: 0;
}
.stats > div {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 14px;
}
.stats dt {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--muted);
  margin-bottom: 4px;
}
.stats dd { margin: 0; font-size: 18px; font-weight: 600; }
</style>
