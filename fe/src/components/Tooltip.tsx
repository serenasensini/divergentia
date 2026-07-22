import { useId, useState, type ReactNode } from 'react';

interface TooltipProps {
  /** Rich content shown inside the tooltip bubble. */
  content: ReactNode;
  /** Accessible label for the trigger button. */
  label?: string;
}

/**
 * Accessible help tooltip triggered by a small "?" button.
 * - Opens on hover and on keyboard focus; closes on blur / mouse-leave / Esc.
 * - The bubble is linked to the trigger via aria-describedby.
 */
export function Tooltip({ content, label = 'More information' }: TooltipProps) {
  const [open, setOpen] = useState(false);
  const id = useId();

  return (
    <span
      className="tooltip"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
    >
      <button
        type="button"
        className="tooltip__trigger"
        aria-label={label}
        aria-describedby={open ? id : undefined}
        aria-expanded={open}
        onFocus={() => setOpen(true)}
        onBlur={() => setOpen(false)}
        onClick={() => setOpen((v) => !v)}
        onKeyDown={(e) => {
          if (e.key === 'Escape') setOpen(false);
        }}
      >
        ?
      </button>
      {open && (
        <span role="tooltip" id={id} className="tooltip__bubble">
          {content}
        </span>
      )}
    </span>
  );
}

