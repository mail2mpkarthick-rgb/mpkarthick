class SecureAccessPage {
  constructor(page) {
    this.page = page;
    this.passwordInput = page.locator('[data-testid="secure-access-password"], input[name="password"], input[id*="password"], input[placeholder*="Password"], input[type="password"]');
    this.submitButton = page.getByRole('button', { name: /submit|continue|access|login|sign ?in/i });
    this.errorMessage = page.locator('.error-message');
  }

  async navigateToHomePage() {
    await this.page.goto('https://dev.ges.store/');
  }

  async enterSecureAccessPassword(password) {
    await this.passwordInput.first().fill(password);
    await this.submitButton.first().click();
  }
}

class ShowSearchPage {
  constructor(page) {
    this.page = page;
    this.passwordInput = page.locator('[data-testid="secure-access-password"], input[type="password"], input[placeholder*="Password"], input[name="password"], input[id*="password"]');
    this.showList = page.locator('.show-item, .search-item, .result-item');
    this.errorMessage = page.locator('.error-message');
  }

  async navigateToHomePage() {
    await this.page.goto('https://dev.ges.store/');
  }

  async clickAccountLink() {
    const accountLink = this.page.locator('[data-testid="account-link"]');
    if (await accountLink.isVisible()) {
      await accountLink.click();
    }
  }

  async isSecureAccessPageDisplayed() {
    return this.passwordInput.isVisible();
  }
}

module.exports = { SecureAccessPage, ShowSearchPage }; 