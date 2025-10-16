import { test, expect } from '@playwright/test'

test('homepage loads and key UI elements are visible', async ({ page }) => {
  await page.goto('/')

  // Hero tagline heading
  await expect(page.getByRole('heading', { name: /Production Code/i })).toBeVisible()
  // Generator section heading
  await expect(page.getByRole('heading', { name: /Try the Code Generator/i })).toBeVisible()
  // Prompt label in the generator form (scope to generator section to avoid duplicates)
  const generator = page.locator('#generator')
  await expect(generator.getByText(/^Prompt$/i)).toBeVisible()
})