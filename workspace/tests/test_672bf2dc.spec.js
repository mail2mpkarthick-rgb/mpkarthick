const { test, expect } = require('@playwright/test');
const { PasswordPage, EventSearchPage, EventDetailsPage } = require('../pages/test_672bf2dc_page.page.js');

test.describe('Password Page', () => {
  let passwordPage;

  test.beforeEach(async ({ page }) => {
    await page.goto('https://dev.ges.store/password');
    passwordPage = new PasswordPage(page);
  });

  test('Positive Login', async () => {
    await passwordPage.login('validUser', 'validPass');
    await expect(passwordPage.errorMessage).toBeHidden();
  });

  test('Negative Login', async () => {
    await passwordPage.login('invalidUser', 'invalidPass');
    await expect(passwordPage.errorMessage).toBeVisible();
  });
});

test.describe('Event Search Page', () => {
  let eventSearchPage;

  test.beforeEach(async ({ page }) => {
    await page.goto('https://dev.ges.store/events');
    eventSearchPage = new EventSearchPage(page);
  });

  test('Positive Search', async () => {
    await eventSearchPage.search('ValidKeyword');
    await expect(eventSearchPage.eventList).toHaveCount(5); // Assuming 5 events are displayed
  });

  test('Negative Search', async () => {
    await eventSearchPage.search('InvalidKeyword');
    await expect(eventSearchPage.errorMessage).toBeVisible();
  });
});

test.describe('Event Details Page', () => {
  let eventDetailsPage;

  test.beforeEach(async ({ page }) => {
    await page.goto('https://dev.ges.store/events/1'); // Assuming the URL for event details
    eventDetailsPage = new EventDetailsPage(page);
  });

  test('Positive Navigation', async () => {
    const title = await eventDetailsPage.getTitle();
    expect(title).toBe('Event Title');
  });

  test('Negative Navigation', async ({ page }) => {
    await page.goto('https://dev.ges.store/events/999'); // Assuming a non-existent event ID
    await expect(eventDetailsPage.errorMessage).toBeVisible();
  });
});