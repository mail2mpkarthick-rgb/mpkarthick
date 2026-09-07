class ShowHomePage {
  constructor(page) {
    this.page = page;
    this.searchInput = page.getByPlaceholder('Show text search');
    this.regionSelector = page.getByRole('button', { name: /GES US/i });
    this.accountLink = page.getByRole('link', { name: 'Account' });
    this.cartLink = page.locator('a[href="/cart"]:visible');
    this.showCards = page.locator('a[href="/login"]');
  }

  async searchForShow(searchText) {
    await this.searchInput.fill(searchText);
  }

  async openAccount() {
    await this.accountLink.click();
  }

  async openCart() {
    await this.page.goto('/cart');
  }
}

module.exports = { ShowHomePage };
