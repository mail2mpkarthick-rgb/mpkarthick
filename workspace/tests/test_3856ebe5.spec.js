const { test, expect } = require('@playwright/test');
const { LoginPage, ShowSearchPage } = require('../pages/test_3856ebe5_page.page.js');

test('Test1', async ({ page }) => {
  const loginPage = new LoginPage(page);
  const showSearchPage = new ShowSearchPage(page);

  // Step 1: Navigate to the home page
  await page.goto('https://dev.ges.store/login');

  // Step 2: Log in with a valid username and password
  await loginPage.login('muthupandi@arizon.digital', 'Pass@123');

  // Step 3: Search for a show
  await showSearchPage.search('042601434');

  // Step 4: Select the show from the search results
  const showItem = showSearchPage.showList.filter({ hasText: '042601434' });
  await showItem.click();
});