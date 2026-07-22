"""
Unit tests for color palette utilities.
"""
import pytest

from app.utils.color_utils import (
    complementary,
    generate_palette,
    hex_to_rgb,
    is_valid_hex,
    rgb_to_hex,
)


class TestColorUtils:
    """Test cases for color_utils."""

    def test_is_valid_hex(self):
        assert is_valid_hex("#FF0000")
        assert is_valid_hex("FF0000")
        assert not is_valid_hex("#FFF")
        assert not is_valid_hex("#GGGGGG")
        assert not is_valid_hex("")

    def test_hex_rgb_roundtrip(self):
        assert hex_to_rgb("#FF0000") == (255, 0, 0)
        assert hex_to_rgb("00FF00") == (0, 255, 0)
        assert rgb_to_hex((0, 0, 255)) == "#0000FF"
        assert hex_to_rgb("nope") is None

    def test_complementary(self):
        # Complementary of pure red is cyan; of green is magenta.
        assert complementary("#FF0000") == "#00FFFF"
        assert complementary("#00FF00") == "#FF00FF"

    def test_palette_uses_explicit_seeds_first(self):
        palette = generate_palette(["#FF0000", "#0000FF"], 2, "even")
        assert palette == ["#FF0000", "#0000FF"]

    def test_palette_single_color(self):
        assert generate_palette(["#FF0000"], 1, "even") == ["#FF0000"]

    def test_palette_zero_or_negative(self):
        assert generate_palette(["#FF0000"], 0, "even") == []
        assert generate_palette(["#FF0000"], -3, "even") == []

    def test_palette_derives_extra_colors_distinct(self):
        palette = generate_palette(["#FF0000", "#0000FF"], 4, "even")
        assert len(palette) == 4
        # All colors distinct so every role is visually separated.
        assert len(set(palette)) == 4

    def test_palette_all_schemes_distinct(self):
        for scheme in ("complementary", "triadic", "tetradic", "even", "analogous"):
            palette = generate_palette(["#3366CC", "#CC6633"], 5, scheme)
            assert len(palette) == 5, scheme
            assert len(set(palette)) == 5, scheme

    def test_palette_invalid_seed_falls_back(self):
        palette = generate_palette([None, "bad"], 3, "even")
        assert len(palette) == 3
        assert all(is_valid_hex(c) for c in palette)

    def test_palette_unknown_scheme_falls_back(self):
        palette = generate_palette(["#FF0000"], 3, "not-a-scheme")
        assert len(palette) == 3
