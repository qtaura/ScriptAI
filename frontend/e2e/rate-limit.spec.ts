import { test, expect } from '@playwright/test'

// Validate strict rate limit shows UI error after exceeding limit

test('shows rate limit error after multiple generates', async ({ page }) => {
  await page.goto('/')
  const generator = page.locator('#generator')

  // Use a stable client IP for this test to deterministically hit the limiter
  await page.route('**/generate', async (route) => {
    const headers = { ...route.request().headers(), 'X-Forwarded-For': '203.0.113.250' }
    await route.continue({ headers })
  })

  // Ensure using local model to avoid model load errors affecting rate limit test
  const trigger = generator.locator('[data-slot="select-trigger"]').first()
  await trigger.click()
  await page.getByRole('option', { name: /Local Model(?: \(Placeholder\))?/i }).click()

  await generator.getByPlaceholder('Describe what you want to create...').fill('Generate a simple function')
  const button = generator.getByRole('button', { name: /Generate Code/i })
  const predicate = (resp: any) => resp.url().includes('/generate') && resp.request().method() === 'POST'

  // First generate
  await Promise.all([
    page.waitForResponse(predicate),
    button.click(),
  ])

  // Second generate
  await Promise.all([
    page.waitForResponse(predicate),
    button.click(),
  ])

  // Third generate should hit route-level limiter (2/min in strict mode)
  await Promise.all([
    page.waitForResponse(predicate),
    button.click(),
  ])

  // Target the Generation Error alert specifically
  const genAlert = generator.getByRole('alert').filter({ hasText: /Generation Error/i }).first()
  await expect(genAlert).toBeVisible()
  await expect(genAlert).toContainText(/Rate limit exceeded/i)
})