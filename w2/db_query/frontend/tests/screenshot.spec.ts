import { test, expect } from '@playwright/test';

test('Screenshot: Execute SQL query on DBQUERY_TEST', async ({ page }) => {
  // Navigate to the app
  await page.goto('http://localhost:5173/');
  
  // Wait for the page to load
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(2000);
  
  // Find and click the database in the sidebar (case-insensitive search)
  const dbItem = page.locator('[class*="cursor-pointer"]').filter({ hasText: /dbquery_test/i }).first();
  
  try {
    await dbItem.waitFor({ state: 'visible', timeout: 10000 });
    await dbItem.click();
  } catch (e) {
    // If not found, try clicking on any database item
    console.log('DBQUERY_TEST not found, looking for alternatives...');
    const anyDbItem = page.locator('[class*="rounded-lg"][class*="cursor-pointer"]').first();
    await anyDbItem.waitFor({ state: 'visible', timeout: 5000 });
    await anyDbItem.click();
  }
  
  // Wait for the database page to load
  await page.waitForTimeout(3000);
  
  // Make sure we're on the MANUAL SQL tab
  const manualSqlTab = page.locator('span:has-text("MANUAL SQL")').first();
  await manualSqlTab.click();
  await page.waitForTimeout(1000);
  
  // Wait for Monaco editor to be ready - try different selectors
  await page.waitForTimeout(2000);
  
  // Click inside the Monaco editor area to focus it
  const monacoContainer = page.locator('.monaco-editor').first();
  await monacoContainer.waitFor({ state: 'visible', timeout: 15000 });
  await monacoContainer.click();
  
  // Wait for editor to be focused
  await page.waitForTimeout(500);
  
  // Select all and type the SQL query
  await page.keyboard.press('Meta+A');
  await page.keyboard.press('Control+A');
  await page.keyboard.type('SELECT * FROM order_items LIMIT 100;', { delay: 20 });
  
  // Wait a moment for the editor to update
  await page.waitForTimeout(1000);
  
  // Click the EXECUTE button
  const executeButton = page.locator('button:has-text("EXECUTE")');
  await executeButton.click();
  
  // Wait for query results to load
  await page.waitForTimeout(4000);
  
  // Take final screenshot
  await page.screenshot({ 
    path: '../images/query_result_order_items.png',
    fullPage: false 
  });
  
  console.log('Screenshot saved to ./w2/db_query/images/query_result_order_items.png');
});
