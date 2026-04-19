import { expect, test } from '@playwright/test';

const storyIds = [
  '__STORYBOOK_ID__--default',
  '__STORYBOOK_ID__--brand',
];

for (const storyId of storyIds) {
  test(`visual diff ${storyId}`, async ({ page }) => {
    await page.goto(`${process.env.STORYBOOK_URL}/iframe.html?id=${storyId}&viewMode=story`);
    await page.setViewportSize({ width: 1200, height: 900 });
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveScreenshot(`${storyId}.png`, {
      animations: 'disabled',
    });
  });
}
