import { test, expect } from '@playwright/test'

// Validate strict rate limit shows UI error after exceeding limit

test('shows rate limit error after multiple generates', async ({ page }) => {
  await page.goto('/')
  const generator = page.locator('#generator')
  await generator.getByPlaceholder('Describe what you want to create...').fill('Generate a simple function')
  const button = generator.getByRole('button', { name: /Generate Code/i })

  const waitGenerate = async () => {
    await page.waitForResponse((resp) => resp.url().includes('/generate') && resp.request().method() === 'POST')
  }

  // First generate
  await button.click()
  await waitGenerate()

  // Second generate
  await button.click()
  await waitGenerate()

  // Third generate should hit route-level limiter (2/min in strict mode)
  await button.click()
  const alert = generator.locator('[data-slot="alert"]').first()
  await expect(alert).toBeVisible()
  await expect(alert.locator('[data-slot="alert-description"]').first()).toContainText(/Rate limit exceeded/i)
})