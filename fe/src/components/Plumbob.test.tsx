import { describe, expect, it, vi } from 'vitest';
import { axe } from 'jest-axe';
import { render } from '@testing-library/react';
import { Plumbob } from './Plumbob';

describe('Plumbob', () => {
  it('has no detectable accessibility violations when decorative', async () => {
    const { container } = render(<Plumbob />);
    expect(await axe(container)).toHaveNoViolations();
  });

  it('has no detectable accessibility violations when labelled', async () => {
    const { container } = render(
      <Plumbob state="current" label="Step 2: current step" />,
    );
    expect(await axe(container)).toHaveNoViolations();
  });

  it('is hidden from assistive tech when purely decorative', () => {
    const { container } = render(<Plumbob />);
    expect(container.firstChild).toHaveAttribute('aria-hidden', 'true');
  });

  it('exposes an accessible label instead of aria-hidden when provided', () => {
    const { getByLabelText } = render(
      <Plumbob label="Step 1: completed" state="completed" />,
    );
    const el = getByLabelText('Step 1: completed');
    expect(el).not.toHaveAttribute('aria-hidden');
    expect(el).toHaveAttribute('role', 'img');
  });

  it('only relies on CSS animation for the pulsing "current" state, so it is automatically muted by the app-wide reduced-motion rules', () => {
    // The pulse comes from the .plumbob--current CSS animation, which is
    // disabled globally by html[data-reduce-motion='true'] and the OS
    // prefers-reduced-motion media query (see styles/global.css). No
    // component-level JS animation exists to independently guard here.
    const { container } = render(<Plumbob state="current" />);
    expect(container.querySelector('.plumbob--current')).toBeInTheDocument();
  });

  it('applies the celebrate class only when requested', () => {
    const { container, rerender } = render(<Plumbob state="completed" />);
    expect(container.querySelector('.plumbob--celebrate')).toBeNull();

    rerender(<Plumbob state="completed" celebrate />);
    expect(container.querySelector('.plumbob--celebrate')).toBeInTheDocument();
  });

  it('calls onCelebrateEnd when the celebrate animation finishes', () => {
    const onCelebrateEnd = vi.fn();
    const { container } = render(
      <Plumbob state="completed" celebrate onCelebrateEnd={onCelebrateEnd} />,
    );
    const el = container.firstChild as HTMLElement;
    el.dispatchEvent(
      new Event('animationend', { bubbles: true, cancelable: true }),
    );
    expect(onCelebrateEnd).toHaveBeenCalledOnce();
  });
});

