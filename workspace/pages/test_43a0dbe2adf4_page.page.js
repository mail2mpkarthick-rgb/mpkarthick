const { expect } = require('@playwright/test');

class ShowSearchPage {
  constructor(page) {
    this.page = page;
    this.url = 'https://dev.ges.store/';
    this.searchInput = page.locator('[data-testid="show-search"], input[placeholder*="Type show name"], input[placeholder*="nickname"], input[placeholder*="acronym"], input[type="search"]').first();
    this.searchButton = page.getByRole('button', { name: /search|go|find/i }).or(page.locator('button:has-text("Search")')).first();
    this.showList = page.locator('.show-item, .product-item, .event-item, [data-testid="product-card"]');
  }

  async navigate() {
    await this.page.goto(this.url);
  }

  async searchShow(keyword) {
    await this.searchInput.fill(keyword);
    if (await this.searchButton.isVisible()) {
      await this.searchButton.click();
    } else {
      await this.searchInput.press('Enter');
    }
  }
}

module.exports = { ShowSearchPage };