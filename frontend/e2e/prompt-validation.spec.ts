import { test, expect } from '@playwright/test'

// Validate server-side prompt errors appear in the destructive alert

test('dangerous prompt shows validation error in alert', async ({ page }) => {
  await page.goto('/')
  const generator = page.locator('#generator')

  // Use a unique client IP to avoid hitting route-level rate limit buckets
  await page.route('**/generate', async (route) => {
    const headers = { ...route.request().headers(), 'X-Forwarded-For': '203.0.113.240' }
    await route.continue({ headers })
  })

  // Ensure using local model to avoid model load errors
  const trigger = generator.locator('[data-slot="select-trigger"]').first()
  await trigger.click()
  await page.getByRole('option', { name: /Local Model(?: \(Placeholder\))?/i }).click()

  await generator.getByPlaceholder('Describe what you want to create...').fill("<script>alert('x')</script>")
  const button = generator.getByRole('button', { name: /Generate Code/i })
  await Promise.all([
    page.waitForResponse((resp) => resp.url().includes('/generate') && resp.request().method() === 'POST'),
    button.click(),
  ])

  // Target the Generation Error alert specifically (not the model load alert)
  const genAlert = generator.getByRole('alert').filter({ hasText: /Generation Error/i }).first()
  await expect(genAlert).toBeVisible()
  await expect(genAlert).toHaveText(/Generation Error/i)
  await expect(genAlert).toContainText(/dangerous/i)
})

test('too long prompt shows length error', async ({ page }) => {
  await page.goto('/')
  const generator = page.locator('#generator')

  // Use a different client IP for this test to avoid 2/min route limit
  await page.route('**/generate', async (route) => {
    const headers = { ...route.request().headers(), 'X-Forwarded-For': '203.0.113.241' }
    await route.continue({ headers })
  })

  // Ensure using local model to avoid model load errors
  const trigger = generator.locator('[data-slot="select-trigger"]').first()
  await trigger.click()
  await page.getByRole('option', { name: /Local Model(?: \(Placeholder\))?/i }).click()

  const longPrompt = 'a'.repeat(1200)
  await generator.getByPlaceholder('Describe what you want to create...').fill(longPrompt)
  const button = generator.getByRole('button', { name: /Generate Code/i })
  await Promise.all([
    page.waitForResponse((resp) => resp.url().includes('/generate') && resp.request().method() === 'POST'),
    button.click(),
  ])

  const genAlert = generator.getByRole('alert').filter({ hasText: /Generation Error/i }).first()
  await expect(genAlert).toBeVisible()
  await expect(genAlert).toContainText(/too long/i)
})

test('excessive repetition shows repetition error', async ({ page }) => {
  await page.goto('/')
  const generator = page.locator('#generator')

  // Use a fresh client IP to avoid rate limit interference from prior tests
  await page.route('**/generate', async (route) => {
    const headers = { ...route.request().headers(), 'X-Forwarded-For': '203.0.113.242' }
    await route.continue({ headers })
  })

  // Ensure using local model to avoid model load errors
  const trigger = generator.locator('[data-slot="select-trigger"]').first()
  await trigger.click()
  await page.getByRole('option', { name: /Local Model(?: \(Placeholder\))?/i }).click()

  // Create a prompt with high repetition exceeding 30%
  const repeated = Array(80).fill('repeat').join(' ')
  await generator.getByPlaceholder('Describe what you want to create...').fill(repeated)
  const button = generator.getByRole('button', { name: /Generate Code/i })
  await Promise.all([
    page.waitForResponse((resp) => resp.url().includes('/generate') && resp.request().method() === 'POST'),
    button.click(),
  ])

  const genAlert = generator.getByRole('alert').filter({ hasText: /Generation Error/i }).first()
  await expect(genAlert).toBeVisible()
  await expect(genAlert).toContainText(/repetition/i)
})