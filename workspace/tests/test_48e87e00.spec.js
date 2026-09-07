const { test, expect } = require('@playwright/test');

test.describe('Login and Search Tests', () => {
  let page;
  let loginPage;
  let showSearchPage;

  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage();
    loginPage = new LoginPage(page);
    showSearchPage = new ShowSearchPage(page);
  });

  test.afterEach(async () => {
    await page.close();
  });

  test('Login with valid credentials', async () => {
    await loginPage.login('muthupandi@arizon.digital', 'Pass@123');
    await expect(page).toHaveURL(/\/dashboard/); // Adjust URL based on expected post-login landing page
  });

  test('Search for a show', async () => {
    await showSearchPage.search('042601434');
    await expect(showSearchPage.showList.locator({ hasText: '042601434' })).toBeVisible();
  });

  test('Search for a non-existent show', async () => {
    await showSearchPage.search('999999');
    await expect(showSearchPage.showList).toHaveCount(0);
  });
});