class SecureAccessPage {
  constructor(page) {
    this.page = page;
    this.passwordInput = page.locator('[data-testid="secure-access-password"]');
    this.submitButton = page.locator('button:has-text("Submit")');
  }

  async enterSecureAccessPassword(password) {
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}

class ShowSearchPage {
  constructor(page) {
    this.page = page;
    this.showList = page.locator('.show-item');
    this.errorMessage = page.locator('.error-message');
  }

  async selectShow(showName) {
    const showItem = this.showList.filter({ hasText: showName });
    await showItem.click();
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
    this.passwordInput = page.locator('[data-testid="secure-access-password"]');
    this.errorMessage = page.locator('.error-message');
  }

  async navigateToHomePage() {
    await this.page.goto('https://dev.ges.store/');
  }

  async clickAccountLink() {
    await this.accountLink.click();
  }

  async isSecureAccessPageDisplayed() {
    return this.passwordInput.isVisible();
  }
}

module.exports = { SecureAccessPage, ShowSearchPage, LoginPage, HomePage }; 