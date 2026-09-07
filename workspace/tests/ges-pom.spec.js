const { test, expect } = require('@playwright/test');
const { SecureAccessPage } = require('../pages/secureAccess.page.js');
const { ShowHomePage } = require('../pages/showHome.page.js');
const { AccountLoginPage } = require('../pages/accountLogin.page.js');
const { RegistrationPage } = require('../pages/registration.page.js');

async function openAuthenticatedHome(page) {
  const secureAccess = new SecureAccessPage(page);
  await secureAccess.open();

  if (await secureAccess.isVisible()) {
    await secureAccess.unlock();
  }

  await expect(page.getByPlaceholder('Show text search')).toBeVisible();
}

test.describe('GES customer portal', () => {
  test('allows secure access with configured environment password', async ({ page }) => {
    await openAuthenticatedHome(page);
    await expect(page.getByText('Find Your Show Here')).toBeVisible();
  });

  test('filters shows from the home search field', async ({ page }) => {
    await openAuthenticatedHome(page);
    const home = new ShowHomePage(page);

    await home.searchForShow('TESOL');

    await expect(page.getByText('TESOL International Convention & Expo')).toBeVisible();
  });

  test('opens the account login page from the home page', async ({ page }) => {
    await openAuthenticatedHome(page);
    const home = new ShowHomePage(page);

    await home.openAccount();

    const accountLogin = new AccountLoginPage(page);
    await expect(page).toHaveURL(/\/login$/);
    await expect(accountLogin.emailInput).toBeVisible();
    await expect(accountLogin.passwordInput).toBeVisible();
    await expect(accountLogin.loginButton).toBeVisible();
  });

  test('opens registration from account login', async ({ page }) => {
    await openAuthenticatedHome(page);
    const home = new ShowHomePage(page);
    await home.openAccount();

    const accountLogin = new AccountLoginPage(page);
    await accountLogin.openRegistration();

    const registration = new RegistrationPage(page);
    await expect(page).toHaveURL(/\/findcompany$/);
    await expect(registration.form).toBeVisible();
  });

  test('redirects unauthenticated cart access to account login', async ({ page }) => {
    await openAuthenticatedHome(page);
    const home = new ShowHomePage(page);

    await home.openCart();

    await expect(page).toHaveURL(/\/login$/);
    await expect(new AccountLoginPage(page).emailInput).toBeVisible();
  });
});
