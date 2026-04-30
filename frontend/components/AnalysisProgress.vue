<script setup lang="ts">
const props = defineProps<{ progress: number }>()

const pct = computed(() => Math.max(0, Math.min(100, Math.round(props.progress * 100))))
</script>

<template>
  <div class="progress">
    <div class="bar">
      <div class="fill" :style="{ width: `${pct}%` }" />
    </div>
    <p class="meta">
      <span class="dot" />
      Analyzing… {{ pct }}%
    </p>
  </div>
</template>

<style scoped>
.progress { margin: 16px 0; }
.bar {
  width: 100%;
  height: 8px;
  background: var(--border);
  border-radius: 999px;
  overflow: hidden;
}
.fill {
  height: 100%;
  background: var(--accent);
  transition: width 0.4s ease-out;
}
.meta {
  margin: 8px 0 0;
  color: var(--muted);
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent);
  animation: pulse 1.2s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 1; }
}
</style>
