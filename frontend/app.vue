<script setup lang="ts">
const githubUrl = 'https://github.com/DarthSaul/crosswalk-watch'
</script>

<template>
  <div class="app">
    <header class="app-header">
      <div class="container header-inner">
        <NuxtLink to="/" class="brand">
          <span class="brand-mark" aria-hidden="true">
            <svg viewBox="0 0 20 20" width="20" height="20">
              <rect x="2" y="3" width="3" height="14" rx="1" fill="currentColor" />
              <rect x="8.5" y="3" width="3" height="14" rx="1" fill="currentColor" />
              <rect x="15" y="3" width="3" height="14" rx="1" fill="currentColor" />
            </svg>
          </span>
          <span class="brand-text">Crosswalk Watch</span>
        </NuxtLink>
        <nav class="nav-links">
          <a
            :href="githubUrl"
            target="_blank"
            rel="noopener"
            class="nav-link"
            aria-label="GitHub repository"
          >
            <svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true">
              <path
                fill="currentColor"
                d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"
              />
            </svg>
            <span>GitHub</span>
          </a>
        </nav>
      </div>
    </header>
    <main class="app-main">
      <div class="container">
        <NuxtPage />
      </div>
    </main>
  </div>
</template>

<style>
:root {
  --bg: #0a0d12;
  --bg-soft: #0e1218;
  --panel: #131720;
  --panel-2: #1a1f2a;
  --border: #252b36;
  --border-strong: #364050;
  --text: #e7ecf3;
  --muted: #8a94a3;
  --muted-strong: #a5afbe;
  --accent: #2dd4bf;
  --accent-strong: #14b8a6;
  --accent-soft: rgba(45, 212, 191, 0.14);
  --accent-ring: rgba(45, 212, 191, 0.45);
  --danger: #f87171;
  --danger-soft: rgba(248, 113, 113, 0.16);
  --warning: #fbbf24;
  --success: #34d399;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.4);
  --shadow-md: 0 6px 24px rgba(0, 0, 0, 0.35);
  --radius: 12px;
  --radius-sm: 8px;
  --radius-pill: 999px;
  --transition: 0.15s ease;
  --container-max: 1024px;
  --container-pad: 24px;
  --header-pad-y: 14px;
}

* { box-sizing: border-box; }
html, body, #__nuxt { height: 100%; }
html { color-scheme: dark; }
body {
  margin: 0;
  background:
    radial-gradient(1200px 600px at 80% -10%, rgba(45, 212, 191, 0.06), transparent 60%),
    radial-gradient(800px 500px at -10% 0%, rgba(96, 165, 250, 0.05), transparent 60%),
    var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", system-ui, sans-serif;
  font-size: 14px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
::selection { background: var(--accent-soft); color: var(--text); }

button {
  font-family: inherit;
}

:focus-visible {
  outline: 2px solid var(--accent-ring);
  outline-offset: 2px;
  border-radius: 4px;
}

code {
  background: var(--panel-2);
  border: 1px solid var(--border);
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 12px;
  font-family: ui-monospace, "SF Mono", Menlo, Monaco, monospace;
}

.container {
  max-width: var(--container-max);
  margin: 0 auto;
  padding-left: var(--container-pad);
  padding-right: var(--container-pad);
  width: 100%;
}

.app { min-height: 100vh; display: flex; flex-direction: column; }
.app-header {
  border-bottom: 1px solid var(--border);
  background: rgba(10, 13, 18, 0.85);
  backdrop-filter: saturate(140%) blur(8px);
  position: sticky;
  top: 0;
  z-index: 10;
}
.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: var(--header-pad-y);
  padding-bottom: var(--header-pad-y);
}
.brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: var(--text);
  text-decoration: none;
  font-weight: 600;
  font-size: 15px;
  letter-spacing: 0.2px;
}
.brand:hover { text-decoration: none; color: var(--text); }
.brand-mark {
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: var(--accent-soft);
  color: var(--accent);
}
.nav-links {
  display: flex;
  align-items: center;
  gap: 8px;
}
.nav-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--muted-strong);
  font-size: 13px;
  padding: 6px 10px;
  border-radius: var(--radius-sm);
  transition: color var(--transition), background var(--transition);
  text-decoration: none;
}
.nav-link:hover { color: var(--text); background: var(--panel-2); text-decoration: none; }

.app-main {
  flex: 1;
  padding: 32px 0 64px;
}
</style>
