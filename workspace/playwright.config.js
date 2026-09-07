const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });

const { defineConfig, devices } = require('@playwright/test');

// Environment configuration
// Set via: $env:BASE_URL="https://uat.ges.store" ; npx playwright test
const TARGET_ENV = process.env.BASE_URL || 'https://dev.ges.store';
const RETRY_COUNT = parseInt(process.env.RETRY_COUNT || '0', 10);
// Headless/Headed mode toggle: set HEADLESS=false for headed mode
const HEADLESS = process.env.HEADLESS !== 'false';

module.exports = defineConfig({
  testDir: './tests',
  timeout: 30 * 1000,
  expect: {
    timeout: 10000
  },
  forbidOnly: false,
  retries: RETRY_COUNT,
  workers: 1,
  reporter: [
    ['html', { outputFolder: 'reports', open: 'never' }],
    ['json', { outputFile: 'reports/test-results.json' }],
    ['line']
  ],
  use: {
    baseURL: TARGET_ENV,
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'retain-on-failure',
    headless: HEADLESS,
    actionTimeout: 15000,
    navigationTimeout: 20000,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    }
  ],
  outputDir: 'test-results/',
});

