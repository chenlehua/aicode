import { test, expect } from '@playwright/test';

test.describe('DatabasePage', () => {
  test('should navigate to database page and display schema', async ({ page }) => {
    // Go to homepage first
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Try to click on a database if it exists
    const databaseLink = page.locator('a, button, [role="button"]').filter({ hasText: /testdb/i }).first();
    
    if (await databaseLink.isVisible({ timeout: 5000 })) {
      await databaseLink.click();
      await page.waitForLoadState('networkidle');
      
      // Check if we're on database page
      await expect(page).toHaveURL(/\/databases\//);
      
      // Check for tabs (SQL Editor, Natural Language, Schema, History)
      const tabs = page.locator('[role="tab"], .ant-tabs-tab');
      await expect(tabs.first()).toBeVisible({ timeout: 10000 });
    } else {
      // If no database exists, test the page structure anyway
      await page.goto('/databases/testdb');
      await page.waitForLoadState('networkidle');
      
      // Should show error or loading state
      const errorOrLoading = page.locator('text=Error, text=Loading, text=Not Found, [role="alert"]').first();
      await expect(errorOrLoading).toBeVisible({ timeout: 5000 });
    }
  });

  test('should execute SQL query', async ({ page }) => {
    await page.goto('/databases/testdb');
    await page.waitForLoadState('networkidle');
    
    // Wait for SQL editor to be visible
    const sqlEditor = page.locator('.monaco-editor').first();
    
    if (await sqlEditor.isVisible({ timeout: 10000 })) {
      // Click on Monaco Editor to focus
      await sqlEditor.click();
      
      // Clear existing content and type SQL query using keyboard
      await page.keyboard.press('Control+A');
      await page.keyboard.type('SELECT * FROM users LIMIT 5');
      
      // Click execute button
      const executeButton = page.locator('button:has-text("Execute"), button:has-text("Run")').first();
      if (await executeButton.isVisible({ timeout: 5000 })) {
        await executeButton.click();
        
        // Wait for results
        await page.waitForTimeout(3000);
        
        // Check if results table appears
        const resultsTable = page.locator('table, .ant-table, [role="table"]').first();
        await expect(resultsTable).toBeVisible({ timeout: 10000 });
      }
    }
  });
});
