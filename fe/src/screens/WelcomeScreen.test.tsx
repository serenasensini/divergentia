import { describe, expect, it, vi } from 'vitest';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe } from 'jest-axe';
import { WelcomeScreen } from './WelcomeScreen';
import { renderWithProviders } from '../test/renderWithProviders';

describe('WelcomeScreen (Step 1)', () => {
  it('has no detectable accessibility violations', async () => {
    const { container } = renderWithProviders(<WelcomeScreen onEnter={() => {}} />);
    expect(await axe(container)).toHaveNoViolations();
  });

  it('lets the user pick a companion', async () => {
    const user = userEvent.setup();
    renderWithProviders(<WelcomeScreen onEnter={() => {}} />);
    const pip = screen.getByRole('radio', { name: /Pip/i });
    await user.click(pip);
    expect(pip).toBeChecked();
  });

  it('persists preferences to localStorage', async () => {
    const user = userEvent.setup();
    renderWithProviders(<WelcomeScreen onEnter={() => {}} />);
    await user.selectOptions(
      screen.getByLabelText(/Text size/i),
      'large',
    );
    await user.click(screen.getByLabelText(/Reduce motion/i));
    const stored = JSON.parse(
      localStorage.getItem('divergentia.preferences.v1') ?? '{}',
    );
    expect(stored.textSize).toBe('large');
    expect(stored.reduceMotion).toBe(true);
  });

  it('calls onEnter and marks onboarding complete', async () => {
    const user = userEvent.setup();
    const onEnter = vi.fn();
    renderWithProviders(<WelcomeScreen onEnter={onEnter} />);
    await user.click(screen.getByRole('button', { name: /Enter the workshop/i }));
    expect(onEnter).toHaveBeenCalledOnce();
    const stored = JSON.parse(
      localStorage.getItem('divergentia.preferences.v1') ?? '{}',
    );
    expect(stored.onboarded).toBe(true);
  });
});
