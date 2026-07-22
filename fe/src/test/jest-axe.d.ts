// Ambient module types for jest-axe (ships no types of its own).
declare module 'jest-axe' {
  export function axe(
    html: Element | string,
    options?: Record<string, unknown>,
  ): Promise<unknown>;
  export function configureAxe(
    options?: Record<string, unknown>,
  ): typeof axe;
  export const toHaveNoViolations: {
    toHaveNoViolations(received: unknown): {
      pass: boolean;
      message: () => string;
    };
  };
}
