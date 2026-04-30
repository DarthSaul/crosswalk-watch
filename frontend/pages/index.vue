<script setup lang="ts">
import type { JobResponse } from '~/types/api';

async function onJobReady(job: JobResponse) {
	await navigateTo(`/jobs/${job.id}`);
}

const tools = [
	{ name: 'FastAPI', label: 'API server', href: 'https://fastapi.tiangolo.com' },
	{ name: 'Nuxt 3', label: 'Frontend', href: 'https://nuxt.com' },
	{ name: 'YOLO11n (Ultralytics)', label: 'Detection', href: 'https://docs.ultralytics.com' },
	{ name: 'ByteTrack', label: 'Tracking', href: 'https://github.com/ifzhang/ByteTrack' },
	{ name: 'supervision', label: 'CV utilities', href: 'https://supervision.roboflow.com' },
	{ name: 'OpenCV', label: 'Video I/O', href: 'https://opencv.org' },
	{ name: 'ffmpeg', label: 'Transcode', href: 'https://ffmpeg.org' },
	{ name: 'Chart.js', label: 'Plotting', href: 'https://www.chartjs.org' },
] as const;

const steps = [
	{
		n: 1,
		title: 'Pick or upload a clip',
		body: 'Choose a sample below or drop in your own video. We extract a single frame so you have something to draw on.',
	},
	{
		n: 2,
		title: 'Draw zones (optional)',
		body: 'Click points around an area of interest — a crosswalk, a turn lane, a curb. Double-click to close. Skip this for a quick whole-frame run.',
	},
	{
		n: 3,
		title: 'Analyze, then review',
		body: 'YOLO finds people and vehicles, ByteTrack stitches them across frames, and you get back an annotated video plus per-zone entries, dwell time, and occupancy over time.',
	},
] as const;
</script>

<template>
	<section class="home">
		<header class="hero">
			<p class="kicker">Computer-Vision Playground</p>
			<h1>Turn any intersection clip into measurable insights.</h1>
			<p class="lede">
				Crosswalk Watch is a fullstack demo that turns a video clip into something you can
				actually measure: tracked people and vehicles, named polygon zones, and per-zone stats —
				entries, dwell, occupancy over time.
			</p>
			<p class="kicker">Tooling</p>
			<ul class="tools" aria-label="Built with">
				<li v-for="t in tools" :key="t.name">
					<a :href="t.href" target="_blank" rel="noopener">
						<span class="tool-name">{{ t.name }}</span>
						<span class="tool-label">{{ t.label }}</span>
					</a>
				</li>
			</ul>
		</header>

		<section class="how">
			<h2 class="section-title">How it works</h2>
			<ol class="steps">
				<li v-for="step in steps" :key="step.n">
					<span class="step-num">{{ step.n }}</span>
					<div>
						<h3>{{ step.title }}</h3>
						<p>{{ step.body }}</p>
					</div>
				</li>
			</ol>
		</section>

		<section class="try">
			<h2 class="section-title">Try it</h2>

			<div class="try-grid">
				<div class="card try-card">
					<h3>Upload your own</h3>
					<p class="muted">
						Drop in any <code>.mp4</code> up to 200&nbsp;MB. We extract a thumbnail
						at t≈1.0s so you can draw zones before analysis kicks off.
					</p>
					<VideoUploader @uploaded="onJobReady" />
				</div>

				<div class="card try-card">
					<h3>Use a sample</h3>
					<p class="muted">
						Pre-loaded crosswalk clips. Click one to get a job in seconds.
					</p>
					<SamplePicker @selected="onJobReady" />
				</div>
			</div>
		</section>
	</section>
</template>

<style scoped>
.home {
	display: flex;
	flex-direction: column;
	gap: 56px;
}

.hero {
	display: flex;
	flex-direction: column;
	gap: 14px;
}
.kicker {
	margin: 0;
	text-transform: uppercase;
	letter-spacing: 1.2px;
	font-size: 11px;
	color: var(--accent);
	font-weight: 600;
}
.hero h1 {
	margin: 0;
	font-size: clamp(28px, 4vw, 40px);
	line-height: 1.15;
	font-weight: 700;
	letter-spacing: -0.5px;
	background: linear-gradient(180deg, var(--text) 0%, var(--muted-strong) 130%);
	-webkit-background-clip: text;
	background-clip: text;
	color: transparent;
}
.lede {
	margin: 0;
	margin-bottom: 1.5rem;
	color: var(--muted-strong);
	font-size: 16px;
	max-width: 64ch;
	line-height: 1.55;
}
.tools {
	list-style: none;
	margin: 8px 0 0;
	padding: 0;
	display: flex;
	flex-wrap: wrap;
	gap: 8px;
}
.tools a {
	display: inline-flex;
	align-items: baseline;
	gap: 6px;
	padding: 6px 10px;
	background: var(--panel);
	border: 1px solid var(--border);
	border-radius: var(--radius-pill);
	color: var(--text);
	font-size: 12px;
	text-decoration: none;
	transition: border-color var(--transition);
}
.tools a:hover {
	border-color: var(--accent);
	text-decoration: none;
}
.tool-name {
	font-weight: 600;
}
.tool-label {
	color: var(--muted);
	font-size: 11px;
}

.section-title {
	font-size: 13px;
	text-transform: uppercase;
	letter-spacing: 0.8px;
	color: var(--muted);
	margin: 0 0 16px;
}

.steps {
	list-style: none;
	margin: 0;
	padding: 0;
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
	gap: 16px;
}
.steps li {
	display: flex;
	gap: 14px;
	background: var(--panel);
	border: 1px solid var(--border);
	border-radius: var(--radius);
	padding: 18px;
}
.step-num {
	flex: 0 0 auto;
	width: 28px;
	height: 28px;
	border-radius: var(--radius-sm);
	background: var(--accent-soft);
	color: var(--accent);
	display: inline-flex;
	align-items: center;
	justify-content: center;
	font-weight: 700;
	font-size: 13px;
}
.steps h3 {
	margin: 0 0 6px;
	font-size: 15px;
}
.steps p {
	margin: 0;
	color: var(--muted-strong);
	font-size: 13px;
	line-height: 1.5;
}

.try-grid {
	display: grid;
	grid-template-columns: minmax(0, 2fr) minmax(0, 1fr);
	gap: 20px;
	align-items: stretch;
}
@media (max-width: 760px) {
	.try-grid {
		grid-template-columns: 1fr;
		align-items: start;
	}
}
.card {
	background: var(--panel);
	border: 1px solid var(--border);
	border-radius: var(--radius);
	padding: 20px;
	display: flex;
	flex-direction: column;
	gap: 12px;
}
.try-card h3 {
	margin: 0;
	font-size: 16px;
}
.try-card > :last-child {
	flex: 1;
	min-height: 0;
}
.muted {
	color: var(--muted);
	margin: 0;
	font-size: 13px;
}
</style>
