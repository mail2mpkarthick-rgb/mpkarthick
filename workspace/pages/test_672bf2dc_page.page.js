const { Page } = require('@playwright/test');

class PasswordPage {
  constructor(page) {
    this.page = page;
    this.usernameInput = page.locator('[data-testid="username"], input[name="username"], input[id*="username"], input[placeholder*="User"], input[type="email"]');
    this.passwordInput = page.locator('[data-testid="password"], input[name="password"], input[id*="password"], input[placeholder*="Password"], input[type="password"]');
    this.loginButton = page.getByRole('button', { name: /log ?in|sign ?in|submit|continue/i });
    this.errorMessage = page.locator('.error-message');
  }

  async login(username, password) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }
}

class EventSearchPage {
  constructor(page) {
    this.page = page;
    this.searchBar = page.locator('[data-testid="search-bar"], input[name="q"], input[placeholder*="Search"], input[type="search"], [aria-label*="search"]');
    this.searchButton = page.getByRole('button', { name: /search|go|find/i });
    this.eventList = page.locator('.event-item, .search-item, .result-item');
    this.errorMessage = page.locator('.error-message');
  }

  async search(keyword) {
    await this.searchBar.fill(keyword);
    await this.searchButton.click();
  }
}

class EventDetailsPage {
  constructor(page) {
    this.page = page;
    this.eventTitle = page.locator('[data-testid="event-title"]');
    this.errorMessage = page.locator('.error-message');
  }

  async getTitle() {
    return this.eventTitle.textContent();
  }
}

module.exports = { PasswordPage, EventSearchPage, EventDetailsPage };