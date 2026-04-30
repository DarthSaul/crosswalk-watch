import type { Point, ZoneDefinition } from '~/types/api'

export const ZONE_PALETTE: readonly string[] = [
  '#ff6b6b',
  '#4ecdc4',
  '#ffe66d',
  '#a8e6cf',
  '#c084fc',
  '#fb923c',
  '#60a5fa',
  '#f472b6',
] as const

export function nextPaletteColor(usedCount: number): string {
  return ZONE_PALETTE[usedCount % ZONE_PALETTE.length]
}

export interface DraftZone {
  points: Point[]
  color: string
}

export function useZoneDrawing(initial: ZoneDefinition[] = []) {
  const zones = ref<ZoneDefinition[]>([...initial])
  const draft = ref<DraftZone | null>(null)
  const cursor = ref<Point | null>(null)

  const isDrawing = computed(() => draft.value !== null)
  const canClose = computed(() => (draft.value?.points.length ?? 0) >= 3)

  function startDraft() {
    draft.value = { points: [], color: nextPaletteColor(zones.value.length) }
  }

  function addVertex(point: Point) {
    if (!draft.value) startDraft()
    draft.value!.points.push(point)
  }

  function moveCursor(point: Point | null) {
    cursor.value = point
  }

  function cancelDraft() {
    draft.value = null
    cursor.value = null
  }

  function closeDraft(): boolean {
    if (!draft.value || draft.value.points.length < 3) return false
    const name = `Zone ${zones.value.length + 1}`
    zones.value.push({
      name,
      color: draft.value.color,
      points: [...draft.value.points],
    })
    draft.value = null
    cursor.value = null
    return true
  }

  function removeZone(index: number) {
    zones.value.splice(index, 1)
  }

  function renameZone(index: number, name: string) {
    const trimmed = name.trim()
    if (!trimmed) return
    zones.value[index] = { ...zones.value[index], name: trimmed }
  }

  function clearAll() {
    zones.value = []
    cancelDraft()
  }

  return {
    zones,
    draft,
    cursor,
    isDrawing,
    canClose,
    startDraft,
    addVertex,
    moveCursor,
    cancelDraft,
    closeDraft,
    removeZone,
    renameZone,
    clearAll,
  }
}
