const { test, expect } = require('@playwright/test');
const { SecureAccessPage, ShowSearchPage, LoginPage, HomePage } = require('../pages/test_92c2d331_page.page.js');

test('Test_1', async ({ page }) => {
  const secureAccessPage = new SecureAccessPage(page);
  const showSearchPage = new ShowSearchPage(page);
  const loginPage = new LoginPage(page);
  const homePage = new HomePage(page);

  await homePage.navigateToHomePage();

  // Step 2: If the Secure Access page is displayed, enter the valid secure access password and click Submit.
  if (await homePage.isSecureAccessPageDisplayed()) {
    await secureAccessPage.enterSecureAccessPassword('valid-password');
  }

  // Step 3: Verify that the application is redirected to the Show Search page.
  expect(await showSearchPage.showList.count()).toBeGreaterThan(0);

  // Step 4: Search for the required show.
  await showSearchPage.search('required-show');

  // Step 5: Select the required show from the search results.
  await showSearchPage.selectShow('required-show');

  // Step 6: Verify that the Login page is displayed.
  expect(await loginPage.loginButton.isVisible()).toBe(true);

  // Step 7: Enter a valid Username.
  await loginPage.login('valid-username', 'valid-password');

  // Step 10: Verify that the user is successfully logged in and redirected to the application home page.
  expect(await homePage.accountLink.isVisible()).toBe(true);
});