<script setup lang="ts">
import type { JobResponse } from '~/types/api'

async function onUploaded(job: JobResponse) {
  await navigateTo(`/jobs/${job.id}`)
}
</script>

<template>
  <section>
    <h1 class="title">Upload a video</h1>
    <p class="lede">
      Drop in a clip of an intersection — we'll extract a thumbnail and stash it
      against a job ID. Analysis lands in Phase 2.
    </p>
    <VideoUploader @uploaded="onUploaded" />
  </section>
</template>

<style scoped>
.title { margin: 0 0 8px; font-size: 22px; }
.lede { color: var(--muted); margin: 0 0 24px; max-width: 60ch; }
</style>
