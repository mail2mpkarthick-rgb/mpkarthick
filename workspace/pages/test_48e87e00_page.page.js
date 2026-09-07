class LoginPage {
  constructor(page) {
    this.page = page;
    this.usernameInput = page.locator('[data-testid="username"], input[name="username"], input[id*="username"], input[placeholder*="User"], input[type="email"]');
    this.passwordInput = page.locator('[data-testid="password"], input[name="password"], input[id*="password"], input[placeholder*="Password"], input[type="password"]');
    this.loginButton = page.getByRole('button', { name: /log ?in|sign ?in|submit|continue/i });
  }

  async login(username, password) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }
}

class ShowSearchPage {
  constructor(page) {
    this.page = page;
    this.searchBar = page.locator('[data-testid="show-search"]');
    this.searchButton = page.getByRole('button', { name: /search|go|find/i });
    this.showList = page.locator('.show-item');
  }

  async search(keyword) {
    await this.searchBar.fill(keyword);
    await this.searchButton.click();
  }
}

class EventSearchPage {
  constructor(page) {
    this.page = page;
    this.searchBar = page.locator('[data-testid="search-bar"], input[name="q"], input[placeholder*="Search"], input[type="search"], [aria-label*="search"]');
    this.searchButton = page.getByRole('button', { name: /search|go|find/i });
  }

  async search(keyword) {
    await this.searchBar.fill(keyword);
    await this.searchButton.click();
  }
}

module.exports = { LoginPage, ShowSearchPage, EventSearchPage };