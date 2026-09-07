class SecureAccessPage {
  constructor(page) {
    this.page = page;
    this.heading = page.getByRole('heading', { name: /secure access/i });
    this.passwordInput = page.locator('input[type="password"]');
    this.continueButton = page.getByRole('button', { name: /continue/i });
    this.errorMessage = page.getByText(/incorrect password/i);
  }

  async open() {
    await this.page.goto('/');
  }

  async isVisible() {
    return this.heading.isVisible();
  }

  async unlock() {
    if (!process.env.SECURE_PASSWORD) {
      throw new Error('SECURE_PASSWORD environment variable is not configured.');
    }

    await this.passwordInput.fill(process.env.SECURE_PASSWORD);
    await this.continueButton.click();
    await this.heading.waitFor({ state: 'hidden' });
  }

  async submitInvalidPassword() {
    await this.passwordInput.fill('invalid-test-password');
    await this.continueButton.click();
  }
}

module.exports = { SecureAccessPage };
