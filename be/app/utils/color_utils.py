"""
Color utilities for deriving harmonized palettes from user-provided seeds.

The document formatting endpoint lets users pick one or two "seed" colors
(``positive`` / ``negative``). When several document roles (titles, section
titles, paragraph titles, body text, captions) are colored at once, two seeds
are not enough. This module derives additional, visually related colors using
classic color-wheel harmonies (complementary, triadic, tetradic, evenly
spaced) so every enabled role gets a distinct color.

Only the Python standard library is used (``colorsys``); no extra dependency.
"""
import colorsys
import logging
import re
from typing import List, Optional, Sequence

logger = logging.getLogger(__name__)

_HEX_RE = re.compile(r'^#?[0-9A-Fa-f]{6}$')

# Supported palette schemes.
SCHEMES = ('complementary', 'triadic', 'tetradic', 'even', 'analogous')
DEFAULT_SCHEME = 'even'

# Lightness clamp keeps derived colors legible (avoid near-white / near-black).
_MIN_LIGHTNESS = 0.15
_MAX_LIGHTNESS = 0.85


def is_valid_hex(color: str) -> bool:
    """Return True if ``color`` is a valid 6-digit hex string (with/without #)."""
    return bool(color) and bool(_HEX_RE.match(color))


def hex_to_rgb(hex_color: str) -> Optional[tuple]:
    """Convert a hex color (``#RRGGBB`` or ``RRGGBB``) to an ``(r, g, b)`` tuple."""
    if not is_valid_hex(hex_color):
        return None
    value = hex_color.lstrip('#')
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: Sequence[float]) -> str:
    """Convert an ``(r, g, b)`` tuple (0-255) to an upper-case ``#RRGGBB`` string."""
    r, g, b = (max(0, min(255, round(c))) for c in rgb)
    return '#{:02X}{:02X}{:02X}'.format(r, g, b)


def _rotate_hue(hex_color: str, degrees: float, clamp_lightness: bool = False) -> str:
    """Return ``hex_color`` with its hue rotated by ``degrees`` on the color wheel."""
    rgb = hex_to_rgb(hex_color)
    if rgb is None:
        raise ValueError(f"Invalid hex color: {hex_color}")
    r, g, b = (c / 255 for c in rgb)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    h = (h + degrees / 360.0) % 1.0
    if clamp_lightness:
        l = max(_MIN_LIGHTNESS, min(_MAX_LIGHTNESS, l))
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return rgb_to_hex((r * 255, g * 255, b * 255))


def complementary(hex_color: str) -> str:
    """Return the complementary color (hue rotated by 180 degrees)."""
    return _rotate_hue(hex_color, 180.0)


def _scheme_offsets(scheme: str, count: int) -> List[float]:
    """Return the list of hue offsets (in degrees) for ``count`` colors."""
    if count <= 1:
        return [0.0]
    if scheme == 'complementary':
        # Alternate base / complement, then spread extras around the wheel.
        offsets = [0.0, 180.0]
        extra = count - 2
        for i in range(extra):
            offsets.append((i + 1) * (360.0 / (extra + 1)))
        return offsets[:count]
    if scheme == 'triadic':
        base = [0.0, 120.0, 240.0]
        return [base[i % 3] + (i // 3) * 40.0 for i in range(count)]
    if scheme == 'tetradic':
        base = [0.0, 90.0, 180.0, 270.0]
        return [base[i % 4] + (i // 4) * 30.0 for i in range(count)]
    if scheme == 'analogous':
        # Fan out around the base hue in +/-30 degree steps.
        return [((i + 1) // 2) * 30.0 * (-1 if i % 2 else 1) for i in range(count)]
    # 'even' (default): spread hues uniformly around the wheel.
    return [i * (360.0 / count) for i in range(count)]


def generate_palette(
    seeds: Sequence[Optional[str]],
    count: int,
    scheme: str = DEFAULT_SCHEME,
) -> List[str]:
    """
    Build a palette of ``count`` distinct hex colors derived from ``seeds``.

    Args:
        seeds: One or more seed colors (hex). ``None``/invalid entries are
            ignored. If no valid seed is given, a default red base is used.
        count: Number of colors required (typically the number of enabled
            roles). Values <= 0 yield an empty list.
        scheme: One of :data:`SCHEMES`. Defaults to ``'even'``.

    Returns:
        A list of ``count`` upper-case ``#RRGGBB`` strings. Colors are made
        unique where the scheme would otherwise collide.
    """
    if count <= 0:
        return []

    valid_seeds = [s for s in seeds if s and is_valid_hex(s)]
    if not valid_seeds:
        logger.warning("No valid seed colors provided; falling back to default base")
        valid_seeds = ['#FF0000']

    if scheme not in SCHEMES:
        logger.warning(f"Unknown scheme '{scheme}'; falling back to '{DEFAULT_SCHEME}'")
        scheme = DEFAULT_SCHEME

    base = valid_seeds[0]

    # If the caller supplied enough explicit seeds, honor them first and only
    # derive the remainder from the base hue.
    palette: List[str] = []
    for seed in valid_seeds[:count]:
        palette.append(seed if seed.startswith('#') else f'#{seed.upper()}')

    remaining = count - len(palette)
    if remaining > 0:
        offsets = _scheme_offsets(scheme, count)
        # Skip the offsets already covered by explicit seeds.
        for offset in offsets[len(palette):count]:
            palette.append(_rotate_hue(base, offset, clamp_lightness=True))

    return _dedupe(palette, base)


def _dedupe(palette: List[str], base: str) -> List[str]:
    """Ensure palette entries are unique by nudging duplicates' hue."""
    seen = set()
    result: List[str] = []
    for color in palette:
        candidate = color.upper()
        nudge = 12.0
        while candidate in seen:
            candidate = _rotate_hue(candidate, nudge, clamp_lightness=True)
            nudge += 12.0
        seen.add(candidate)
        result.append(candidate)
    return result
