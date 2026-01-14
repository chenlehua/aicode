import { test, expect } from '@playwright/test';

test.describe('HomePage', () => {
  test('should load homepage and display database list', async ({ page }) => {
    await page.goto('/');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Check if page title is correct
    await expect(page).toHaveTitle(/DB Query/);
    
    // Check if database list section exists
    const databaseList = page.locator('text=Database').first();
    await expect(databaseList).toBeVisible({ timeout: 10000 });
  });

  test('should add a new database connection', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Fill in database form
    const nameInput = page.locator('input[placeholder*="name" i], input[name="name"]').first();
    const urlInput = page.locator('input[placeholder*="url" i], input[name="url"], input[type="text"]').filter({ hasText: /postgres/i }).first();
    
    // Try to find and fill the form
    const form = page.locator('form').first();
    if (await form.isVisible()) {
      await nameInput.fill('playwright-test');
      await urlInput.fill('postgres://postgres:postgres@localhost:5432/testdb');
      
      // Submit form
      const submitButton = page.locator('button[type="submit"], button:has-text("Add"), button:has-text("Save")').first();
      await submitButton.click();
      
      // Wait for success message or database to appear in list
      await page.waitForTimeout(2000);
    }
  });
});
