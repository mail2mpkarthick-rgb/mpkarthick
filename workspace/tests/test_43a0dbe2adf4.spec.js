const { test, expect } = require('@playwright/test');
const { ShowSearchPage } = require('./show_search.page');

test.describe('Website Navigation and Show Search', () => {
  test('TC_1 - Naviagate the website and search show', async ({ page }) => {
    const showSearchPage = new ShowSearchPage(page);

    // Step 1: Go to website "https://dev.ges.store/"
    await showSearchPage.navigate();

    // Step 2: Search the show under "Type show name, nickname, date, location, or acronym to begin." box
    const searchQuery = 'CES';
    await showSearchPage.searchShow(searchQuery);

    // Verification
    await expect(showSearchPage.searchInput).toHaveValue(searchQuery);
  });
});