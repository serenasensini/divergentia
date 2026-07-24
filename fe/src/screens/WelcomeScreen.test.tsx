import { describe, expect, it, vi } from 'vitest';
import { fireEvent, screen } from '@testing-library/react';
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
      screen.getByRole('combobox', { name: /Text size/i }),
      'large',
    );
    await user.click(screen.getByRole('checkbox', { name: /Reduce motion/i }));
    const stored = JSON.parse(
      localStorage.getItem('divergentia.preferences.v1') ?? '{}',
    );
    expect(stored.textSize).toBe('large');
    expect(stored.reduceMotion).toBe(true);
  });

  it('lets the user opt into the playful diamond game theme', async () => {
    const user = userEvent.setup();
    renderWithProviders(<WelcomeScreen onEnter={() => {}} />);
    const toggle = screen.getByRole('checkbox', {
      name: /Playful diamond theme/i,
    });
    expect(toggle).not.toBeChecked();
    await user.click(toggle);
    expect(toggle).toBeChecked();
    const stored = JSON.parse(
      localStorage.getItem('divergentia.preferences.v1') ?? '{}',
    );
    expect(stored.gameTheme).toBe(true);
  });

  it('explains the reading font options via an accessible tooltip', async () => {
    renderWithProviders(<WelcomeScreen onEnter={() => {}} />);
    const trigger = screen.getByRole('button', {
      name: /More information: Reading font/i,
    });
    // The tooltip opens on focus (and hover); assert the explanation appears.
    fireEvent.focus(trigger);
    const tip = await screen.findByRole('tooltip');
    expect(tip).toHaveTextContent(/Atkinson Hyperlegible/i);
  });

  it('resets preferences to defaults after confirmation', async () => {
    const user = userEvent.setup();
    renderWithProviders(<WelcomeScreen onEnter={() => {}} />);

    // Change something away from the default first.
    await user.selectOptions(
      screen.getByRole('combobox', { name: /Text size/i }),
      'x-large',
    );

    // Open the confirmation dialog and confirm.
    await user.click(screen.getByRole('button', { name: /Reset to defaults/i }));
    const dialog = screen.getByRole('alertdialog');
    expect(dialog).toBeInTheDocument();
    await user.click(
      screen.getByRole('button', { name: /^Yes, reset$/i }),
    );

    expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument();
    const stored = JSON.parse(
      localStorage.getItem('divergentia.preferences.v1') ?? '{}',
    );
    expect(stored.textSize).toBe('medium');
  });

  it('cancels a reset without changing preferences', async () => {
    const user = userEvent.setup();
    renderWithProviders(<WelcomeScreen onEnter={() => {}} />);
    await user.selectOptions(
      screen.getByRole('combobox', { name: /Text size/i }),
      'large',
    );
    await user.click(screen.getByRole('button', { name: /Reset to defaults/i }));
    await user.click(screen.getByRole('button', { name: /Cancel/i }));
    expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument();
    const stored = JSON.parse(
      localStorage.getItem('divergentia.preferences.v1') ?? '{}',
    );
    expect(stored.textSize).toBe('large');
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
