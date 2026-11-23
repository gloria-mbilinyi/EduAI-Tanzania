import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./e2e",
  workers: 1,
  fullyParallel: false,
  timeout: 60000,
  reporter: [
    ["list"],
    ["junit", { outputFile: "../docs/testing/playwright-results.xml" }],
  ],
  use: {
    baseURL: "http://127.0.0.1:5173",
    channel: process.env.PLAYWRIGHT_BROWSER_CHANNEL === 'chromium' ? undefined : 'chrome',
    headless: true,
    viewport: { width: 1440, height: 1000 },
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
  },
});
