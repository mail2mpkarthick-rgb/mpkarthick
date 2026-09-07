class HomePage {
  constructor(page) {
    this.page = page;
    this.accountLink = page.locator('[data-testid="account-link"], a:has-text("Account"), button:has-text("Account"), [aria-label*="account"]');
    this.loginModal = page.locator('[data-testid="login-modal"], .login-modal, [role="dialog"]');
    this.loginButton = page.getByRole('button', { name: /log ?in|sign ?in|submit|continue/i });
    this.usernameInput = page.locator('[data-testid="username"], input[name="username"], input[id*="username"], input[placeholder*="User"], input[type="email"]');
    this.passwordInput = page.locator('[data-testid="password"], input[name="password"], input[id*="password"], input[placeholder*="Password"], input[type="password"]');
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

module.exports = { HomePage };