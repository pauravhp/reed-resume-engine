export function scrapeJD(): string | null {
  const selectors = ['main', 'article', '[role="main"]'];
  for (const selector of selectors) {
    const el = document.querySelector(selector);
    if (el instanceof HTMLElement && el.innerText.trim().length > 200) {
      return el.innerText.trim();
    }
  }

  const selection = window.getSelection()?.toString().trim();
  if (selection && selection.length > 100) {
    return selection;
  }

  return null;
}
