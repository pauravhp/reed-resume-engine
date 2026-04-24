/// <reference types=".wxt/types" />

interface ImportMetaEnv {
  readonly VITE_APP_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
