import { defineConfig, devices } from '@playwright/test'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'

// Enable strict rate limit mode for e2e runs
process.env.RATELIMIT_STRICT_TEST = process.env.RATELIMIT_STRICT_TEST ?? '1'

// __dirname is not available in ESM; derive it from import.meta.url
const __dirname = dirname(fileURLToPath(import.meta.url))
const isWin = process.platform === 'win32'
const startCommand = isWin ? 'py -3 app.py' : 'python app.py'

export default defineConfig({
  testDir: './e2e',
  timeout: 60_000,
  retries: process.env.CI ? 2 : 1,
  fullyParallel: true,
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  outputDir: 'test-results',
  reporter: [['html', { outputFolder: 'playwright-report' }], ['list']],
  webServer: {
    command: 'npm run dev',
    cwd: __dirname,
    url: 'http://localhost:5173',
    reuseExistingServer: true,
    timeout: 120_000,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
})