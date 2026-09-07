class RegistrationPage {
  constructor(page) {
    this.page = page;
    this.form = page.locator('form');
  }

  async isVisible() {
    return this.form.isVisible();
  }
}

module.exports = { RegistrationPage };
