export default defineBackground(() => {
  const appUrl = import.meta.env.VITE_APP_URL ?? 'http://localhost:5173';

  chrome.runtime.onMessage.addListener((message) => {
    if (message.type === 'DELIVER' && typeof message.jd === 'string') {
      deliverJD(message.jd, appUrl);
    }
  });
});

async function deliverJD(jd: string, appUrl: string) {
  const generateUrl = `${appUrl}/generate`;

  const tabs = await chrome.tabs.query({ url: `${appUrl}/*` });
  const existingTab = tabs.find((t) => t.url?.includes('/generate'));

  let tabId: number;

  if (existingTab?.id) {
    await chrome.tabs.update(existingTab.id, { active: true });
    if (existingTab.windowId) {
      await chrome.windows.update(existingTab.windowId, { focused: true });
    }
    tabId = existingTab.id;
  } else {
    const newTab = await chrome.tabs.create({ url: generateUrl });
    tabId = newTab.id!;
    await waitForTabLoad(tabId);
  }

  await chrome.scripting.executeScript({
    target: { tabId },
    world: 'MAIN',
    func: (jdText: string) => {
      localStorage.setItem(
        'jd_capture',
        JSON.stringify({ jd: jdText, capturedAt: Date.now() }),
      );
      window.dispatchEvent(new StorageEvent('storage', { key: 'jd_capture' }));
    },
    args: [jd],
  });
}

function waitForTabLoad(tabId: number): Promise<void> {
  return new Promise((resolve) => {
    const listener = (
      updatedTabId: number,
      info: chrome.tabs.TabChangeInfo,
    ) => {
      if (updatedTabId === tabId && info.status === 'complete') {
        chrome.tabs.onUpdated.removeListener(listener);
        resolve();
      }
    };
    chrome.tabs.onUpdated.addListener(listener);
  });
}
