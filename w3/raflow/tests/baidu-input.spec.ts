import { test, expect } from '@playwright/test';

/**
 * This test opens Baidu and focuses on the search input,
 * allowing manual testing of Raflow's text insertion feature.
 *
 * To test:
 * 1. Run `npm run tauri dev` in another terminal
 * 2. Run this test: `npx playwright test tests/baidu-input.spec.ts --headed`
 * 3. When Baidu opens with cursor in search box, press Cmd+Shift+\ to start recording
 * 4. Speak into the microphone
 * 5. The transcribed text should appear in the search box
 */
test.describe('Raflow Text Insertion Test', () => {
  test('should open Baidu with cursor in search input', async ({ page }) => {
    // Navigate to Baidu
    await page.goto('https://www.baidu.com');

    // Wait for the search input to be visible
    const searchInput = page.locator('#kw');
    await expect(searchInput).toBeVisible();

    // Click to focus the search input
    await searchInput.click();

    // Verify the input is focused
    await expect(searchInput).toBeFocused();

    console.log('\n=================================================');
    console.log('✅ Baidu is ready for testing!');
    console.log('');
    console.log('Now test Raflow:');
    console.log('1. Make sure Raflow is running (npm run tauri dev)');
    console.log('2. Press Cmd+Shift+\\ to start recording');
    console.log('3. Speak clearly into your microphone');
    console.log('4. Watch for text to appear in the search box');
    console.log('5. Press Cmd+Shift+\\ again to stop recording');
    console.log('=================================================\n');

    // Keep the page open for 60 seconds for manual testing
    await page.waitForTimeout(60000);

    // Check if any text was entered
    const inputValue = await searchInput.inputValue();
    if (inputValue) {
      console.log(`✅ Text was entered: "${inputValue}"`);
    } else {
      console.log('⚠️ No text was entered during the test period');
    }
  });

  test('should continuously monitor input for text insertion', async ({ page }) => {
    // Navigate to Baidu
    await page.goto('https://www.baidu.com');

    const searchInput = page.locator('#kw');
    await expect(searchInput).toBeVisible();
    await searchInput.click();

    console.log('\n🎤 Monitoring for text insertion...');
    console.log('Press Ctrl+C to stop the test\n');

    let lastValue = '';
    let checkCount = 0;

    // Monitor input for 120 seconds
    while (checkCount < 240) {
      const currentValue = await searchInput.inputValue();
      if (currentValue !== lastValue) {
        console.log(`📝 Text changed: "${currentValue}"`);
        lastValue = currentValue;
      }
      await page.waitForTimeout(500);
      checkCount++;
    }
  });
});
