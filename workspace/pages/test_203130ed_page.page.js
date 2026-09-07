const { expect } = require('@playwright/test');

class StorePage {
  constructor(page) {
    this.page = page;
    this.url = 'https://dev.ges.store/';

    // UI Structure Elements
    this.header = page.locator('header, [data-testid="header"]');
    this.logo = page.locator('[data-testid="logo"], .logo, a[href="/"]').first();
    this.navBar = page.locator('nav, [data-testid="nav-bar"]');
    this.heroBanner = page.locator('.hero, [data-testid="hero-banner"], .banner').first();
    this.footer = page.locator('footer, [data-testid="footer"]');

    // Search Elements
    this.searchInput = page.locator('[data-testid="show-search"], [data-testid="search-bar"], input[type="search"], input[name="q"], input[placeholder*="Search"]').first();
    this.searchButton = page.getByRole('button', { name: /search|go|find/i }).or(page.locator('button:has-text("Search")')).first();
    this.productItems = page.locator('.product-item, .show-item, .event-item, [data-testid="product-card"]');
    this.noResultsMessage = page.locator('.no-results, .error-message, text=/no (products|results) found|no results matching/i');

    // Account & Login Elements
    this.accountLink = page.locator('[data-testid="account-link"], a:has-text("Account"), button:has-text("Account"), [aria-label*="account"], a:has-text("Sign In")').first();
    this.loginModal = page.locator('[data-testid="login-modal"], .login-modal, [role="dialog"]');
    this.usernameInput = page.locator('[data-testid="username"], input[name="username"], input[name="email"], input[type="email"]').first();
    this.passwordInput = page.locator('[data-testid="password"], input[name="password"], input[type="password"]').first();
    this.loginButton = page.getByRole('button', { name: /log ?in|sign ?in|submit/i }).first();
    this.errorMessage = page.locator('.error-message, [role="alert"]');

    // Product & Shopping Cart Elements
    this.featuredProduct = page.locator('.featured-product, .product-item, [data-testid="product-card"]').first();
    this.addToCartButton = page.getByRole('button', { name: /add to cart/i }).first();
    this.cartIcon = page.locator('[data-testid="cart-icon"], .cart-icon, a[href*="cart"]').first();
    this.cartBadge = page.locator('[data-testid="cart-badge"], .cart-count, .badge').first();
    this.cartItem = page.locator('.cart-item, [data-testid="cart-item"]');
    this.emptyCartMessage = page.locator('.empty-cart, text=/your cart is empty/i');
    this.checkoutButton = page.getByRole('button', { name: /checkout/i });
  }

  async navigate() {
    await this.page.goto(this.url);
  }

  async searchProduct(keyword) {
    await this.searchInput.fill(keyword);
    await this.searchInput.press('Enter');
  }

  async openAccountModal() {
    await this.accountLink.click();
  }

  async login(username, password) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }

  async selectFeaturedProduct() {
    await this.featuredProduct.click();
  }

  async addToCart() {
    await this.addToCartButton.click();
  }

  async openCart() {
    await this.cartIcon.click();
  }
}

module.exports = { StorePage };