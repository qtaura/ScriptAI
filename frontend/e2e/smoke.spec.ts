import { test, expect } from '@playwright/test'

test('homepage loads and key UI elements are visible', async ({ page }) => {
  await page.goto('/')

  await expect(page.getByRole('heading', { name: /ScriptAI/i })).toBeVisible()
  await expect(page.getByRole('heading', { name: /Try the Code Generator/i })).toBeVisible()
  await expect(page.getByText(/Prompt/i)).toBeVisible()
})