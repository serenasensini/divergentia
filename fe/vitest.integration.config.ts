import { defineConfig } from 'vite';

// Live integration tests: run against a real backend (default http://localhost:5000).
// These are excluded from the default `npm test` run.
export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['src/**/*.integration.test.ts'],
    testTimeout: 30000,
  },
});
