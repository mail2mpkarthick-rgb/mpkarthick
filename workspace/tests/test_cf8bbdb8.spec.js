const { test, expect } = require('@playwright/test');

const cases = [
  { username: 'muthupandi@arizon.digital', password: 'Pass@123', expected: 'Search results show "042601434"' },
  { username: 'invalid_user@example.com', password: 'Pass@123', expected: 'Error message indicating invalid username' },
  { username: 'muthupandi@arizon.digital', password: '', expected: 'No search results shown' }
];

test.describe('Show Search Test Cases', () => {
  for (const { username, password, expected } of cases) {
    test(`Test valid login and search functionality with ${username} / ${password}`, async ({ page }) => {
      const homePage = new HomePage(page);
      const loginPage = new LoginPage(page);
      const showSearchPage = new ShowSearchPage(page);

      await homePage.navigateToHomePage();
      await homePage.clickAccountLink();

      await loginPage.login('muthupandi@arizon.digital', 'Pass@123');
      await expect(homePage.accountLink).toBeVisible();

      await loginPage.login(username, password);

      if (expected.includes('Search results show')) {
        await showSearchPage.search('042601434');
        const showItem = showSearchPage.showList.filter({ hasText: '042601434' });
        await expect(showItem).toBeVisible();
      } else if (expected.includes('Error message indicating invalid username')) {
        const errorMessage = loginPage.errorMessage;
        await expect(errorMessage).toHaveText('Invalid username');
      } else if (expected.includes('No search results shown')) {
        await showSearchPage.search('');
        const errorMessage = showSearchPage.errorMessage;
        await expect(errorMessage).toHaveText('No search results found');
      }
    });
  }
});

class ShowSearchPage {
  constructor(page) {
    this.page = page;
    this.searchBar = page.locator('[data-testid="show-search"]');
    this.searchButton = page.locator('button:has-text("Search")');
    this.showList = page.locator('.show-item');
    this.errorMessage = page.locator('.error-message');
  }

  async search(keyword) {
    await this.searchBar.fill(keyword);
    await this.searchButton.click();
  }
}

class LoginPage {
  constructor(page) {
    this.page = page;
    this.usernameInput = page.locator('[data-testid="username"]');
    this.passwordInput = page.locator('[data-testid="password"]');
    this.loginButton = page.locator('button:has-text("Log In")');
    this.errorMessage = page.locator('.error-message');
  }

  async login(username, password) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }
}

class HomePage {
  constructor(page) {
    this.page = page;
    this.accountLink = page.locator('[data-testid="account-link"]');
    this.loginModal = page.locator('[data-testid="login-modal"]');
  }

  async navigateToHomePage() {
    await this.page.goto('https://dev.ges.store/');
  }

  async clickAccountLink() {
    await this.accountLink.click();
  }
}