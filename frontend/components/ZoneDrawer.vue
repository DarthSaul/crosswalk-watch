<script setup lang="ts">
import type { Point, ZoneDefinition } from '~/types/api'

const props = defineProps<{
  thumbnailUrl: string
  zones: ZoneDefinition[]
}>()

const emit = defineEmits<{
  'update:zones': [zones: ZoneDefinition[]]
}>()

const drawing = useZoneDrawing(props.zones)
watch(drawing.zones, (next) => emit('update:zones', next), { deep: true })

function zonesEqual(a: ZoneDefinition[], b: ZoneDefinition[]): boolean {
  if (a === b) return true
  if (a.length !== b.length) return false
  for (let i = 0; i < a.length; i++) {
    const za = a[i]
    const zb = b[i]
    if (za.name !== zb.name || za.color !== zb.color) return false
    if (za.points.length !== zb.points.length) return false
    for (let j = 0; j < za.points.length; j++) {
      if (za.points[j][0] !== zb.points[j][0] || za.points[j][1] !== zb.points[j][1]) {
        return false
      }
    }
  }
  return true
}

watch(
  () => props.zones,
  (next) => {
    if (!zonesEqual(next, drawing.zones.value)) {
      drawing.zones.value = next.map((z) => ({ ...z, points: z.points.map((p) => [...p] as Point) }))
    }
  },
  { deep: true },
)

const surfaceRef = ref<HTMLElement | null>(null)
const PENDING_ADD_MS = 220
let pendingAdd: ReturnType<typeof setTimeout> | null = null

function toNormalized(event: MouseEvent): Point | null {
  const surface = surfaceRef.value
  if (!surface) return null
  const rect = surface.getBoundingClientRect()
  if (rect.width === 0 || rect.height === 0) return null
  const x = (event.clientX - rect.left) / rect.width
  const y = (event.clientY - rect.top) / rect.height
  return [Math.max(0, Math.min(1, x)), Math.max(0, Math.min(1, y))]
}

function onClick(event: MouseEvent) {
  const point = toNormalized(event)
  if (!point) return
  if (pendingAdd) clearTimeout(pendingAdd)
  pendingAdd = setTimeout(() => {
    drawing.addVertex(point)
    pendingAdd = null
  }, PENDING_ADD_MS)
}

function onDblClick() {
  if (pendingAdd) {
    clearTimeout(pendingAdd)
    pendingAdd = null
  }
  drawing.closeDraft()
}

function onMove(event: MouseEvent) {
  if (!drawing.isDrawing.value) return
  drawing.moveCursor(toNormalized(event))
}

function onLeave() {
  drawing.moveCursor(null)
}

function onKey(event: KeyboardEvent) {
  if (event.key === 'Escape') drawing.cancelDraft()
  else if (event.key === 'Enter' && drawing.canClose.value) drawing.closeDraft()
}

onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
  if (pendingAdd) clearTimeout(pendingAdd)
})

function pointsAttr(points: Point[]): string {
  return points.map(([x, y]) => `${x},${y}`).join(' ')
}

function rubberPath(): string | null {
  if (!drawing.draft.value || !drawing.cursor.value) return null
  const pts = drawing.draft.value.points
  if (pts.length === 0) return null
  const last = pts[pts.length - 1]
  const cur = drawing.cursor.value
  return `M ${last[0]} ${last[1]} L ${cur[0]} ${cur[1]}`
}

function closingPath(): string | null {
  if (!drawing.draft.value || drawing.draft.value.points.length < 2) return null
  if (!drawing.canClose.value) return null
  if (!drawing.cursor.value) return null
  const pts = drawing.draft.value.points
  const first = pts[0]
  const cur = drawing.cursor.value
  return `M ${cur[0]} ${cur[1]} L ${first[0]} ${first[1]}`
}
</script>

<template>
  <div class="zone-drawer">
    <div
      ref="surfaceRef"
      class="surface"
      :class="{ drawing: drawing.isDrawing.value }"
      @click="onClick"
      @dblclick.prevent="onDblClick"
      @mousemove="onMove"
      @mouseleave="onLeave"
    >
      <img :src="thumbnailUrl" alt="frame for drawing zones" class="frame">
      <svg
        class="overlay"
        viewBox="0 0 1 1"
        preserveAspectRatio="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <polygon
          v-for="(zone, i) in drawing.zones.value"
          :key="`zone-${i}`"
          :points="pointsAttr(zone.points)"
          :stroke="zone.color"
          :fill="zone.color"
          fill-opacity="0.15"
          stroke-width="0.004"
          vector-effect="non-scaling-stroke"
        />

        <template v-if="drawing.draft.value && drawing.draft.value.points.length > 0">
          <polyline
            :points="pointsAttr(drawing.draft.value.points)"
            :stroke="drawing.draft.value.color"
            stroke-width="0.004"
            vector-effect="non-scaling-stroke"
            fill="none"
          />
          <path
            v-if="rubberPath()"
            :d="rubberPath()!"
            :stroke="drawing.draft.value.color"
            stroke-width="0.003"
            stroke-dasharray="0.01 0.01"
            vector-effect="non-scaling-stroke"
            fill="none"
          />
          <path
            v-if="closingPath()"
            :d="closingPath()!"
            :stroke="drawing.draft.value.color"
            stroke-width="0.002"
            stroke-dasharray="0.005 0.005"
            stroke-opacity="0.6"
            vector-effect="non-scaling-stroke"
            fill="none"
          />
          <circle
            v-for="(p, i) in drawing.draft.value.points"
            :key="`v-${i}`"
            :cx="p[0]"
            :cy="p[1]"
            r="0.008"
            :fill="drawing.draft.value.color"
          />
        </template>
      </svg>
    </div>

    <p class="hint">
      <span v-if="drawing.isDrawing.value">
        Click to add a vertex · double-click or Enter to close
        ({{ drawing.draft.value?.points.length }} pt{{ drawing.draft.value?.points.length === 1 ? '' : 's' }})
        · Esc cancels
      </span>
      <span v-else>
        Click on the frame to start a zone. Add at least 3 points, then double-click to close.
      </span>
    </p>
  </div>
</template>

<style scoped>
.zone-drawer { display: flex; flex-direction: column; gap: 8px; }
.surface {
  position: relative;
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  background: #000;
  cursor: crosshair;
  user-select: none;
}
.surface.drawing { cursor: crosshair; }
.frame { display: block; width: 100%; height: auto; }
.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}
.hint { margin: 0; color: var(--muted); font-size: 12px; }
</style>
