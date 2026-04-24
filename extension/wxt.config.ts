import { defineConfig } from 'wxt';
import tailwindcss from '@tailwindcss/vite';

const appUrl = process.env.VITE_APP_URL ?? 'http://localhost:5173';

export default defineConfig({
  srcDir: '.',
  modules: ['@wxt-dev/module-react'],
  vite: () => ({
    plugins: [tailwindcss()],
  }),
  manifest: {
    name: 'R.E.E.D — JD Capture',
    description:
      'Capture job descriptions and send them to R.E.E.D for tailored resume generation.',
    permissions: ['activeTab', 'scripting'],
    host_permissions: [`${appUrl}/*`],
  },
});
