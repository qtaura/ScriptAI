import { test, expect } from '@playwright/test'

// Validate server-side prompt errors appear in the destructive alert

test('dangerous prompt shows validation error in alert', async ({ page }) => {
  await page.goto('/')
  const generator = page.locator('#generator')
  await generator.getByPlaceholder('Describe what you want to create...').fill("<script>alert('x')</script>")
  await generator.getByRole('button', { name: /Generate Code/i }).click()

  const alert = generator.locator('[data-slot="alert"]').first()
  await expect(alert).toBeVisible()
  await expect(alert.locator('[data-slot="alert-title"]').first()).toHaveText(/Generation Error/i)
  await expect(alert.locator('[data-slot="alert-description"]').first()).toContainText(/dangerous/i)
})

test('too long prompt shows length error', async ({ page }) => {
  await page.goto('/')
  const generator = page.locator('#generator')
  const longPrompt = 'a'.repeat(1200)
  await generator.getByPlaceholder('Describe what you want to create...').fill(longPrompt)
  await generator.getByRole('button', { name: /Generate Code/i }).click()

  const desc = generator.locator('[data-slot="alert-description"]').first()
  await expect(desc).toContainText(/too long/i)
})

test('excessive repetition shows repetition error', async ({ page }) => {
  await page.goto('/')
  const generator = page.locator('#generator')
  // Create a prompt with high repetition exceeding 30%
  const repeated = Array(80).fill('repeat').join(' ')
  await generator.getByPlaceholder('Describe what you want to create...').fill(repeated)
  await generator.getByRole('button', { name: /Generate Code/i }).click()

  const desc = generator.locator('[data-slot="alert-description"]').first()
  await expect(desc).toContainText(/repetition/i)
})