class SecureAccessPage {
  constructor(page) {
    this.page = page;
    this.passwordInput = page.locator('input[type="password"], input[name="password"], input[placeholder*="•"], [aria-label*="password"]');
    this.continueButton = page.getByRole('button', { name: /continue|submit|enter|access/i });
    this.secureAccessHeading = page.locator('h2', { hasText: /secure access/i });
    this.instructions = page.locator('p', { hasText: /enter the password to continue/i });
    this.errorMessage = page.locator('text=/incorrect password/i');
  }

  async goto() {
    await this.page.goto('/');
  }

  async isDisplayed() {
    return this.secureAccessHeading.isVisible();
  }

  async enterPassword(password) {
    await this.passwordInput.fill(password);
    await this.continueButton.click();
  }
}

module.exports = { SecureAccessPage };