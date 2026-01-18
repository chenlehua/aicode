<script lang="ts">
  import { onMount } from 'svelte';
  import { listen } from '@tauri-apps/api/event';
  import { invoke } from '@tauri-apps/api/core';
  import { appState, isRecording } from './lib/stores/appState';
  import { settings } from './lib/stores/settings';
  import StatusBar from './lib/components/StatusBar.svelte';
  import TranscriptPreview from './lib/components/TranscriptPreview.svelte';
  import SettingsPanel from './lib/components/SettingsPanel.svelte';
  import HotkeyHint from './lib/components/HotkeyHint.svelte';

  let showSettings = false;
  let recording = false;
  let errorMessage = '';
  let hasAccessibility = true;

  isRecording.subscribe(value => {
    recording = value;
  });

  async function checkAccessibility() {
    try {
      hasAccessibility = await invoke<boolean>('check_accessibility');
      if (!hasAccessibility) {
        console.warn('Accessibility permission not granted');
      }
    } catch (e) {
      console.error('Failed to check accessibility:', e);
    }
  }

  async function requestAccessibility() {
    try {
      await invoke('request_accessibility');
      // Check again after a short delay
      setTimeout(checkAccessibility, 1000);
    } catch (e) {
      console.error('Failed to request accessibility:', e);
    }
  }

  onMount(async () => {
    // Load settings
    await settings.load();

    // Refresh app state
    await appState.refresh();

    // Check accessibility permission
    await checkAccessibility();

    // Listen for toggle-recording events from backend
    await listen('toggle-recording', async () => {
      try {
        errorMessage = '';
        await appState.toggleRecording();
      } catch (e: any) {
        errorMessage = e.toString();
        console.error('Toggle recording error:', e);
      }
    });
  });

  async function handleToggleClick() {
    try {
      errorMessage = '';
      await appState.toggleRecording();
    } catch (e: any) {
      errorMessage = e.toString();
      console.error('Toggle recording error:', e);
    }
  }

  function toggleSettings() {
    showSettings = !showSettings;
  }
</script>

<main>
  <div class="container">
    {#if !hasAccessibility}
      <div class="permission-warning">
        <span class="warning-icon">⚠️</span>
        <div class="warning-content">
          <strong>Accessibility Permission Required</strong>
          <p>Raflow needs accessibility permission to type text into other apps.</p>
          <button class="grant-button" on:click={requestAccessibility}>
            Grant Permission
          </button>
        </div>
      </div>
    {/if}

    <StatusBar />

    <TranscriptPreview />

    {#if errorMessage}
      <div class="error-message">
        {errorMessage}
      </div>
    {/if}

    <HotkeyHint />

    <div class="actions">
      <button
        class="record-button"
        class:recording={recording}
        on:click={handleToggleClick}
      >
        {recording ? 'Stop Recording' : 'Start Recording'}
      </button>

      <button class="settings-toggle" on:click={toggleSettings}>
        {showSettings ? 'Hide Settings' : 'Settings'}
      </button>
    </div>

    {#if showSettings}
      <SettingsPanel />
    {/if}
  </div>
</main>

<style>
  :global(:root) {
    /* Light theme */
    --bg-primary: #ffffff;
    --bg-secondary: #f5f5f7;
    --text-primary: #1d1d1f;
    --text-secondary: #86868b;
    --text-tertiary: #aeaeb2;
    --border-color: #d2d2d7;
    --border-accent: #007aff;
    --color-primary: #007aff;
    --color-recording: #ff3b30;
    --color-idle: #34c759;
    --color-error: #ff3b30;
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

  @media (prefers-color-scheme: dark) {
    :global(:root) {
      --bg-primary: #1c1c1e;
      --bg-secondary: #2c2c2e;
      --text-primary: #f5f5f7;
      --text-secondary: #aeaeb2;
      --text-tertiary: #636366;
      --border-color: #38383a;
      --border-accent: #0a84ff;
      --color-primary: #0a84ff;
    }
  }

  :global(*) {
    box-sizing: border-box;
  }

  :global(body) {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
      'Helvetica Neue', Arial, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  /* Scrollbar styling */
  :global(::-webkit-scrollbar) {
    width: 8px;
  }

  :global(::-webkit-scrollbar-track) {
    background: transparent;
  }

  :global(::-webkit-scrollbar-thumb) {
    background: var(--border-color);
    border-radius: 4px;
  }

  :global(::-webkit-scrollbar-thumb:hover) {
    background: var(--text-tertiary);
  }

  main {
    min-height: 100vh;
    padding: 20px;
    box-sizing: border-box;
  }

  .container {
    display: flex;
    flex-direction: column;
    gap: 16px;
    max-width: 400px;
    margin: 0 auto;
  }

  .error-message {
    padding: 12px 16px;
    background: rgba(255, 59, 48, 0.1);
    border: 1px solid var(--color-error);
    border-radius: 8px;
    color: var(--color-error);
    font-size: 13px;
  }

  .actions {
    display: flex;
    gap: 10px;
  }

  .record-button {
    flex: 1;
    padding: 12px 20px;
    background: var(--color-primary);
    border: none;
    border-radius: 10px;
    color: white;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .record-button:hover {
    filter: brightness(1.1);
  }

  .record-button:active {
    transform: scale(0.98);
  }

  .record-button.recording {
    background: var(--color-recording);
  }

  .settings-toggle {
    padding: 12px 20px;
    background: transparent;
    border: 1px solid var(--border-color);
    border-radius: 10px;
    color: var(--text-secondary);
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .settings-toggle:hover {
    background: var(--bg-secondary);
    color: var(--text-primary);
  }

  .permission-warning {
    display: flex;
    gap: 12px;
    padding: 14px 16px;
    background: rgba(255, 149, 0, 0.1);
    border: 1px solid #ff9500;
    border-radius: 10px;
  }

  .warning-icon {
    font-size: 20px;
    line-height: 1;
  }

  .warning-content {
    flex: 1;
  }

  .warning-content strong {
    display: block;
    color: #ff9500;
    font-size: 14px;
    margin-bottom: 4px;
  }

  .warning-content p {
    margin: 0 0 10px 0;
    font-size: 12px;
    color: var(--text-secondary);
    line-height: 1.4;
  }

  .grant-button {
    padding: 6px 12px;
    background: #ff9500;
    border: none;
    border-radius: 6px;
    color: white;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .grant-button:hover {
    filter: brightness(1.1);
  }
</style>
