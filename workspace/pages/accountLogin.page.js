class AccountLoginPage {
  constructor(page) {
    this.page = page;
    this.emailInput = page.locator('input[type="email"][name="email"]');
    this.passwordInput = page.locator('input[type="password"][name="password"]');
    this.loginButton = page.getByRole('button', { name: /log in/i });
    this.createAccountLink = page.getByRole('link', { name: /create an account/i });
    this.forgotPasswordLink = page.getByRole('link', { name: /forgot password/i });
  }

  async isVisible() {
    return this.page.getByRole('heading', { name: /account login/i }).first().isVisible();
  }

  async openRegistration() {
    await this.createAccountLink.click();
  }
}

module.exports = { AccountLoginPage };
