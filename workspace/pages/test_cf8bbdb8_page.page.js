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
    this.usernameInput = page.locator('[data-testid="username"]');
    this.passwordInput = page.locator('[data-testid="password"]');
    this.loginButton = page.locator('button:has-text("Log In")');
  }

  async navigateToHomePage() {
    await this.page.goto('https://dev.ges.store/');
  }

  async clickAccountLink() {
    await this.accountLink.click();
  }

  async login(username, password) {
    if (await this.loginModal.isVisible()) {
      await this.usernameInput.fill(username);
      await this.passwordInput.fill(password);
      await this.loginButton.click();
    }
  }
}

module.exports = { ShowSearchPage, LoginPage, HomePage };