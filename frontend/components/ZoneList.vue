<script setup lang="ts">
import type { ZoneDefinition } from '~/types/api'

const props = defineProps<{
  zones: ZoneDefinition[]
  readonly?: boolean
}>()

const emit = defineEmits<{
  remove: [index: number]
  rename: [index: number, name: string]
  clear: []
}>()

function onRename(i: number, event: Event) {
  const input = event.target as HTMLInputElement
  emit('rename', i, input.value)
}
</script>

<template>
  <aside class="zone-list">
    <header>
      <h2>Zones</h2>
      <button
        v-if="!readonly && zones.length"
        class="link"
        type="button"
        @click="emit('clear')"
      >
        Clear all
      </button>
    </header>
    <p v-if="!zones.length" class="empty">
      No zones yet. {{ readonly ? '' : 'Draw one on the frame.' }}
    </p>
    <ul v-else>
      <li v-for="(zone, i) in zones" :key="i">
        <span class="swatch" :style="{ background: zone.color }" />
        <input
          v-if="!readonly"
          class="name"
          :value="zone.name"
          :aria-label="`Rename ${zone.name}`"
          @change="onRename(i, $event)"
        >
        <span v-else class="name-static">{{ zone.name }}</span>
        <span class="meta">{{ zone.points.length }} pts</span>
        <button
          v-if="!readonly"
          class="remove"
          type="button"
          :aria-label="`Remove ${zone.name}`"
          @click="emit('remove', i)"
        >
          ×
        </button>
      </li>
    </ul>
  </aside>
</template>

<style scoped>
.zone-list {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px;
  min-width: 220px;
}
header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 8px;
}
h2 { margin: 0; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--muted); }
.link {
  background: none;
  border: none;
  color: var(--accent);
  cursor: pointer;
  font-size: 12px;
  padding: 0;
}
.empty { margin: 0; color: var(--muted); font-size: 13px; }
ul { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 6px; }
li {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.03);
}
.swatch {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  flex-shrink: 0;
}
.name {
  flex: 1;
  background: transparent;
  border: 1px solid transparent;
  color: var(--text);
  font-size: 13px;
  padding: 2px 4px;
  border-radius: 4px;
  min-width: 0;
}
.name:hover { border-color: var(--border); }
.name:focus { outline: none; border-color: var(--accent); }
.name-static { flex: 1; font-size: 13px; }
.meta { color: var(--muted); font-size: 11px; }
.remove {
  background: transparent;
  border: 0;
  color: var(--muted);
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
  padding: 0 4px;
}
.remove:hover { color: #f85149; }
</style>
