<script setup lang="ts">
</script>

<template>
  <div class="app">
    <header class="app-header">
      <NuxtLink to="/" class="brand">Crosswalk Watch</NuxtLink>
    </header>
    <main class="app-main">
      <NuxtPage />
    </main>
  </div>
</template>

<style>
:root {
  --bg: #0e1116;
  --panel: #161b22;
  --border: #30363d;
  --text: #e6edf3;
  --muted: #8b949e;
  --accent: #58a6ff;
}

* { box-sizing: border-box; }
html, body, #__nuxt { height: 100%; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
  font-size: 14px;
}

.app { min-height: 100vh; display: flex; flex-direction: column; }
.app-header {
  padding: 16px 24px;
  border-bottom: 1px solid var(--border);
  background: var(--panel);
}
.brand {
  color: var(--text);
  text-decoration: none;
  font-weight: 600;
  font-size: 16px;
  letter-spacing: 0.2px;
}
.brand:hover { color: var(--accent); }
.app-main { flex: 1; padding: 24px; max-width: 960px; margin: 0 auto; width: 100%; }
</style>
