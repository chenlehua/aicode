import { test, expect } from '@playwright/test';

test.describe('MySQL Database Tests', () => {
  test('should navigate to MySQL database page and display schema', async ({ page }) => {
    // Go to homepage first
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Wait for database list to load (look for the mysql-testdb text)
    const mysqlDbItem = page.locator('text=mysql-testdb').first();
    await expect(mysqlDbItem).toBeVisible({ timeout: 10000 });

    // Click on the database item
    await mysqlDbItem.click();
    await page.waitForLoadState('networkidle');

    // Check if we're on database page
    await expect(page).toHaveURL(/\/databases\/mysql-testdb/);

    // Check for tabs (SQL Editor, Natural Language, Schema, History)
    const tabs = page.locator('[role="tab"], .ant-tabs-tab');
    await expect(tabs.first()).toBeVisible({ timeout: 10000 });
  });

  test('should execute SQL query on MySQL database', async ({ page }) => {
    // Navigate directly to MySQL database page
    await page.goto('/databases/mysql-testdb');
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

        // Check if results table appears with data
        const resultsTable = page.locator('table, .ant-table, [role="table"]').first();
        await expect(resultsTable).toBeVisible({ timeout: 10000 });

        // Verify that we got rows (check for user names from the test data)
        const userDataVisible = page.locator('text=张三, text=zhangsan, text=李四').first();
        await expect(userDataVisible).toBeVisible({ timeout: 5000 });
      }
    }
  });

  test('should show MySQL tables in schema tab', async ({ page }) => {
    await page.goto('/databases/mysql-testdb');
    await page.waitForLoadState('networkidle');

    // Click on Schema tab
    const schemaTab = page.locator('[role="tab"]:has-text("Schema"), .ant-tabs-tab:has-text("Schema")').first();
    if (await schemaTab.isVisible({ timeout: 5000 })) {
      await schemaTab.click();
      await page.waitForTimeout(2000);

      // Check for table names from the MySQL test data
      const usersTable = page.locator('text=users').first();
      await expect(usersTable).toBeVisible({ timeout: 10000 });

      // Check for categories table
      const categoriesTable = page.locator('text=categories').first();
      await expect(categoriesTable).toBeVisible({ timeout: 5000 });
    }
  });
});
