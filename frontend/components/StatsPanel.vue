<script setup lang="ts">
import {
  Chart,
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import type { ChartConfiguration } from 'chart.js'

import type { ProcessingStats, ZoneStats } from '~/types/api'

Chart.register(
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend,
  Filler,
)

const props = defineProps<{ stats: ProcessingStats }>()

const canvas = ref<HTMLCanvasElement | null>(null)
let chart: Chart<'line'> | null = null

function formatDwell(seconds: number): string {
  if (seconds < 1) return `${Math.round(seconds * 1000)} ms`
  if (seconds < 60) return `${seconds.toFixed(1)} s`
  const m = Math.floor(seconds / 60)
  const s = Math.round(seconds % 60)
  return `${m}m ${s}s`
}

function buildConfig(stats: ProcessingStats): ChartConfiguration<'line'> {
  const fps = stats.fps || 30
  const longest = stats.zones.reduce(
    (n, z) => Math.max(n, z.occupancy_series.length),
    0,
  )
  const labels = Array.from({ length: longest }, (_, i) => (i / fps).toFixed(1))

  return {
    type: 'line',
    data: {
      labels,
      datasets: stats.zones.map((zone) => ({
        label: zone.name,
        data: zone.occupancy_series,
        borderColor: zone.color,
        backgroundColor: hexToRgba(zone.color, 0.18),
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.25,
        fill: true,
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { labels: { color: '#e6edf3' } },
        tooltip: { callbacks: { title: (items) => `t=${items[0]?.label}s` } },
      },
      scales: {
        x: {
          title: { display: true, text: 'time (s)', color: '#8b949e' },
          ticks: {
            color: '#8b949e',
            maxTicksLimit: 8,
            autoSkip: true,
          },
          grid: { color: '#30363d33' },
        },
        y: {
          title: { display: true, text: 'objects in zone', color: '#8b949e' },
          ticks: { color: '#8b949e', precision: 0, stepSize: 1 },
          grid: { color: '#30363d33' },
          beginAtZero: true,
        },
      },
    },
  }
}

function hexToRgba(hex: string, alpha: number): string {
  const fallback = `rgba(125, 125, 125, ${alpha})`
  let m = hex.trim().replace(/^#/, '')
  if (/^[0-9a-fA-F]{3}$/.test(m)) {
    m = m[0] + m[0] + m[1] + m[1] + m[2] + m[2]
  }
  if (!/^[0-9a-fA-F]{6}$/.test(m)) return fallback
  const r = parseInt(m.slice(0, 2), 16)
  const g = parseInt(m.slice(2, 4), 16)
  const b = parseInt(m.slice(4, 6), 16)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

function render() {
  if (!canvas.value) return
  if (chart) {
    chart.destroy()
    chart = null
  }
  if (!props.stats.zones.length) return
  chart = new Chart(canvas.value, buildConfig(props.stats))
}

onMounted(render)
watch(() => props.stats, render, { deep: true })
onBeforeUnmount(() => {
  chart?.destroy()
  chart = null
})

const zonesSorted = computed<ZoneStats[]>(() =>
  [...props.stats.zones].sort((a, b) => b.entries - a.entries),
)
</script>

<template>
  <section class="stats-panel">
    <h2>Zone analytics</h2>

    <div v-if="!stats.zones.length" class="empty">
      No zones were defined for this analysis.
    </div>

    <template v-else>
      <div class="chart-wrap">
        <canvas ref="canvas" />
      </div>

      <table class="zone-table">
        <thead>
          <tr>
            <th>Zone</th>
            <th>Entries</th>
            <th>Avg dwell</th>
            <th>Peak concurrent</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="zone in zonesSorted" :key="zone.name">
            <td>
              <span class="swatch" :style="{ background: zone.color }" />
              {{ zone.name }}
            </td>
            <td>{{ zone.entries }}</td>
            <td>{{ formatDwell(zone.avg_dwell_seconds) }}</td>
            <td>{{ zone.max_concurrent }}</td>
          </tr>
        </tbody>
      </table>
    </template>
  </section>
</template>

<style scoped>
.stats-panel {
  margin-top: 24px;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
}
h2 {
  margin: 0 0 16px;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--muted);
}
.empty { color: var(--muted); font-size: 13px; }
.chart-wrap {
  position: relative;
  height: 240px;
  margin-bottom: 20px;
}
.zone-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
.zone-table th,
.zone-table td {
  text-align: left;
  padding: 8px 10px;
  border-bottom: 1px solid var(--border);
}
.zone-table th {
  color: var(--muted);
  font-weight: 500;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}
.zone-table tr:last-child td { border-bottom: 0; }
.swatch {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 2px;
  margin-right: 8px;
  vertical-align: middle;
}
</style>
