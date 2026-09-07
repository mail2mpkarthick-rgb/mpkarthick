const { test, expect } = require('@playwright/test');
const { HomePage } = require('../pages/test_ada2977a_page.page.js');

test('Test the flow from home page to account login', async ({ page }) => {
  const homePage = new HomePage(page);

  // Step 1: Navigate to home page
  await homePage.navigateToHomePage();

  // Step 2: Click on account link
  await homePage.clickAccountLink();

  // Step 3: Verify that the login modal is visible
  expect(await homePage.loginModal.isVisible()).toBe(true);

  // Step 4: Login with provided credentials (this should be replaced with actual credentials)
  await homePage.login('username', 'password');

  // Step 5: Verify that the account login page is displayed
  const accountLoginTitle = page.locator('[data-testid="account-login-title"]');
  expect(await accountLoginTitle.isVisible()).toBe(true);
});