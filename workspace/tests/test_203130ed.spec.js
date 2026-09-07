const { test, expect } = require('@playwright/test');
const { StorePage } = require('./store.page');

test.describe('Store Functional Test Suite', () => {
  let storePage;

  test.beforeEach(async ({ page }) => {
    storePage = new StorePage(page);
    await storePage.navigate();
  });

  test('TC_1: Verify Homepage Successful Loading', async ({ page }) => {
    await expect(page).toHaveURL(/ges\.store/);
    await expect(storePage.header).toBeVisible();
    await expect(storePage.logo).toBeVisible();
    await expect(storePage.navBar).toBeVisible();
    await expect(storePage.heroBanner).toBeVisible();
    await expect(storePage.footer).toBeVisible();
  });

  test('TC_2: Search for an Existing Product', async () => {
    await storePage.searchProduct('shirt');
    await expect(storePage.productItems.first()).toBeVisible();
    const count = await storePage.productItems.count();
    expect(count).toBeGreaterThan(0);
  });

  test('TC_3: Search with Invalid / Non-existent Keyword', async () => {
    await storePage.searchProduct('xyz999nonexistent');
    await expect(storePage.noResultsMessage).toBeVisible();
  });

  test('TC_4: Add Product to Shopping Cart', async () => {
    await storePage.selectFeaturedProduct();
    await storePage.addToCart();
    await storePage.openCart();

    await expect(storePage.cartItem.first()).toBeVisible();
    await expect(storePage.cartBadge).toContainText('1');
  });

  test('TC_5: User Login with Invalid Password', async () => {
    await storePage.openAccountModal();
    await storePage.login('user@example.com', 'WrongPassword123');
    await expect(storePage.errorMessage).toBeVisible();
  });

  test('TC_6: Attempt Checkout with Empty Cart', async () => {
    await storePage.openCart();
    await expect(storePage.emptyCartMessage).toBeVisible();
    
    const isCheckoutDisabled = await storePage.checkoutButton.isDisabled().catch(() => true);
    const isCheckoutVisible = await storePage.checkoutButton.isVisible().catch(() => false);
    
    expect(!isCheckoutVisible || isCheckoutDisabled).toBeTruthy();
  });
});