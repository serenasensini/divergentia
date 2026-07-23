import { describe, expect, it } from 'vitest';
import { axe } from 'jest-axe';
import { render } from '@testing-library/react';
import { DiamondStepTracker } from './DiamondStepTracker';

const steps = [
  { id: 'format', label: 'Colour & style' },
  { id: 'spacing', label: 'Breathing room' },
  { id: 'framing', label: 'Frames & borders' },
];

describe('DiamondStepTracker', () => {
  it('has no detectable accessibility violations', async () => {
    const { container } = render(
      <DiamondStepTracker
        steps={steps}
        completedIds={new Set(['format'])}
        aria-label="Applied so far"
      />,
    );
    expect(await axe(container)).toHaveNoViolations();
  });

  it('marks completed, current and upcoming diamonds correctly', () => {
    const { getByLabelText } = render(
      <DiamondStepTracker
        steps={steps}
        completedIds={new Set(['format'])}
        aria-label="Applied so far"
      />,
    );
    expect(getByLabelText('Colour & style: completed')).toBeInTheDocument();
    expect(getByLabelText('Breathing room: current step')).toBeInTheDocument();
    expect(
      getByLabelText('Frames & borders: not started yet'),
    ).toBeInTheDocument();
  });

  it('renders a diamond per step, in order', () => {
    const { container } = render(
      <DiamondStepTracker
        steps={steps}
        completedIds={new Set()}
        aria-label="Applied so far"
      />,
    );
    const items = container.querySelectorAll('.diamond-tracker__item');
    expect(items).toHaveLength(3);
  });

  it('only applies the celebrate animation to the given celebratingId', () => {
    const { container } = render(
      <DiamondStepTracker
        steps={steps}
        completedIds={new Set(['format'])}
        celebratingId="format"
        aria-label="Applied so far"
      />,
    );
    const celebrating = container.querySelectorAll('.plumbob--celebrate');
    expect(celebrating).toHaveLength(1);
  });
});

