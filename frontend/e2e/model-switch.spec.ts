import { test, expect } from '@playwright/test'

// Verify model selection dropdown shows providers and local generation produces a stub
test('model selection shows providers and local generates code', async ({ page }) => {
  await page.goto('/')

  const generator = page.locator('#generator')

  // Open the model select
  const trigger = generator.locator('[data-slot="select-trigger"]').first()
  await trigger.click()

  const listbox = page.getByRole('listbox')
  await expect(listbox).toBeVisible()

  // Provider options should be visible
  await expect(page.getByRole('option', { name: /Local Model \(Placeholder\)/i })).toBeVisible()
  await expect(page.getByRole('option', { name: /OpenAI GPT-3\.5/i })).toBeVisible()
  await expect(page.getByRole('option', { name: /Anthropic Claude/i })).toBeVisible()
  await expect(page.getByRole('option', { name: /Google Gemini/i })).toBeVisible()
  await expect(page.getByRole('option', { name: /HuggingFace StarCoder/i })).toBeVisible()

  // Close dropdown
  await page.keyboard.press('Escape')

  // Enter a prompt and generate
  await generator.getByPlaceholder('Describe what you want to create...').fill('Write a Python function that prints "Hello World"')
  await generator.getByRole('button', { name: /Generate Code/i }).click()

  const codeBlock = generator.locator('pre code').first()
  await expect(codeBlock).toBeVisible()
  await expect(codeBlock).toContainText(/Generated locally based on prompt/i)
})