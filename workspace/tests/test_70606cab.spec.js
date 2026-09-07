const { test, expect } = require('@playwright/test');
const { SecureAccessPage, ShowSearchPage } = require('../pages/test_70606cab_page.page.js');

test.describe('Security and Navigation Tests', () => {
  let page;

  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage();
  });

  test.afterEach(async () => {
    await page.close();
  });

  test('TC_1: Secure Application Access with Correct Password', async () => {
    const secureAccessPage = new SecureAccessPage(page);
    const showSearchPage = new ShowSearchPage(page);

    expect(process.env.SECURE_PASSWORD).toBeTruthy();
    await secureAccessPage.navigateToHomePage();
    await secureAccessPage.enterSecureAccessPassword(process.env.SECURE_PASSWORD);

    expect(await showSearchPage.isSecureAccessPageDisplayed()).toBe(false);
  });

  test('TC_2: Invalid Password Test', async () => {
    const secureAccessPage = new SecureAccessPage(page);

    await secureAccessPage.navigateToHomePage();
    await secureAccessPage.enterSecureAccessPassword('wrongpass');

    expect(await secureAccessPage.errorMessage.isVisible()).toBe(true);
  });

  test('TC_3: Account Login Page Test', async () => {
    const showSearchPage = new ShowSearchPage(page);

    await showSearchPage.navigateToHomePage();
    await showSearchPage.clickAccountLink();

    const accountLoginModal = page.locator('[data-testid="login-modal"]');
    expect(await accountLoginModal.isVisible()).toBe(true);
  });
});