import '@testing-library/jest-dom/vitest';
import { afterEach, beforeEach, expect } from 'vitest';
import { toHaveNoViolations } from 'jest-axe';
import { installFetchMock, resetFetchMock } from './fetchMock';

expect.extend(toHaveNoViolations);

// jsdom doesn't implement matchMedia; provide a permissive stub so preference
// detection (reduced motion / contrast) doesn't throw during tests.
if (!window.matchMedia) {
  window.matchMedia = (query: string) =>
    ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }) as unknown as MediaQueryList;
}

beforeEach(() => {
  installFetchMock();
});

afterEach(() => {
  resetFetchMock();
  localStorage.clear();
});
