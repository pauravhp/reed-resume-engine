import { useState } from 'react';
import { scrapeJD } from '../../lib/scraper';

type PopupState = 'idle' | 'capturing' | 'success' | 'error';

export default function App() {
  const [state, setState] = useState<PopupState>('idle');
  const [preview, setPreview] = useState('');
  const appUrl = import.meta.env.VITE_APP_URL ?? 'http://localhost:5173';

  async function handleCapture() {
    setState('capturing');

    try {
      const [tab] = await chrome.tabs.query({
        active: true,
        currentWindow: true,
      });
      if (!tab?.id) {
        setState('error');
        return;
      }

      const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: scrapeJD,
      });

      const jdText = results?.[0]?.result;
      if (!jdText) {
        setState('error');
        return;
      }

      setPreview(jdText.slice(0, 100));
      setState('success');

      chrome.runtime.sendMessage({ type: 'DELIVER', jd: jdText });
    } catch {
      setState('error');
    }
  }

  return (
    <div className="min-w-[280px] max-w-[360px]">
      <div className="flex h-10 items-center bg-sage px-4">
        <span className="font-display text-sm font-semibold tracking-[0.08em] text-header-text">
          R.E.E.D
        </span>
      </div>

      <div className="flex flex-col items-center gap-3 bg-oat px-4 py-6">
        {state === 'idle' && (
          <>
            <p className="font-body text-[11px] text-text-secondary">
              Grab the JD from this page
            </p>
            <button
              onClick={handleCapture}
              className="w-full rounded-[7px] bg-sage-accent px-5 py-2.5 font-body text-[13px] font-medium text-white transition-colors duration-150 hover:bg-sage-accent-hover"
            >
              Capture Job Description
            </button>
          </>
        )}

        {state === 'capturing' && (
          <button
            disabled
            className="flex w-full items-center justify-center gap-2 rounded-[7px] bg-sage-accent px-5 py-2.5 font-body text-[13px] font-medium text-white opacity-70"
          >
            <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
            Capturing
          </button>
        )}

        {state === 'success' && (
          <>
            <div className="flex items-center gap-2">
              <svg
                className="h-4 w-4 text-success"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2.5}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M5 13l4 4L19 7"
                />
              </svg>
              <span className="font-body text-[13px] font-semibold text-success">
                Captured
              </span>
            </div>
            <div className="w-full rounded-[9px] border border-border bg-oat-card p-3">
              <p className="line-clamp-2 font-body text-[11px] text-text-secondary">
                {preview}
              </p>
            </div>
            <p className="font-body text-[11px] text-text-secondary">
              Opening app
            </p>
            <a
              href={`${appUrl}/generate`}
              target="_blank"
              rel="noopener noreferrer"
              className="font-body text-[11px] text-sage-accent hover:underline"
            >
              Open manually
            </a>
          </>
        )}

        {state === 'error' && (
          <>
            <p className="text-center font-body text-xs font-medium text-text-primary">
              Couldn't find a job description on this page.
            </p>
            <p className="font-body text-[11px] text-text-secondary">
              Select the text and try again.
            </p>
            <button
              onClick={handleCapture}
              className="w-full rounded-[7px] bg-sage-accent px-5 py-2.5 font-body text-[13px] font-medium text-white transition-colors duration-150 hover:bg-sage-accent-hover"
            >
              Capture Job Description
            </button>
          </>
        )}
      </div>
    </div>
  );
}
