"""Monitoring metric extraction and braille sparkline tests."""

import pytest

from dokli.monitoring import (
    METRIC_SCALE,
    format_duo_total_label,
    metric_duo,
    metric_value,
    metric_value_text,
    render_dual_sparkline,
    render_sparkline,
)

_SAMPLE = {
    "cpu": {"value": "2.50%", "time": 0},
    "memory": {"value": {"used": "1.108GiB", "total": "62.4GiB"}, "time": 0},
    "network": {"value": {"inputMb": "7.59", "outputMb": "0.14"}, "time": 0},
    "block": {"value": {"readMb": "786", "writeMb": "1.31"}, "time": 0},
    "disk": {"value": {"diskUsedPercentage": "42.0%", "total": "1024GB"}, "time": 0},
}


class TestMetricValue:
    """Numeric sample extraction."""

    def test_cpu_percentage(self):
        assert metric_value(_SAMPLE, "cpu") == 2.5

    def test_memory_ratio_percent(self):
        assert metric_value(_SAMPLE, "memory") == pytest.approx(1.7756, abs=1e-3)

    def test_memory_mixed_units_percent(self):
        sample = {"memory": {"value": {"used": "252.4MiB", "total": "8GiB"}, "time": 0}}
        # 252.4 MiB / 8 GiB (8192 MiB) ~= 3.08%, not 3155%.
        assert metric_value(sample, "memory") == pytest.approx(3.081, abs=1e-2)

    def test_network_sum(self):
        assert metric_value(_SAMPLE, "network") == pytest.approx(7.73)

    def test_block_sum(self):
        assert metric_value(_SAMPLE, "block") == pytest.approx(787.31)

    def test_disk_percentage(self):
        assert metric_value(_SAMPLE, "disk") == pytest.approx(42.0)

    def test_missing_metric_returns_none(self):
        assert metric_value({}, "cpu") is None
        assert metric_value({"cpu": {}}, "cpu") is None


class TestMetricValueText:
    """Short current-value labels."""

    def test_cpu_label(self):
        assert metric_value_text(_SAMPLE, "cpu") == "2.50%"

    def test_memory_label(self):
        assert metric_value_text(_SAMPLE, "memory") == "1.108GiB/62.4GiB"

    def test_network_label(self):
        assert metric_value_text(_SAMPLE, "network") == "7.59MB\u2193 0.14MB\u2191"

    def test_block_label(self):
        assert metric_value_text(_SAMPLE, "block") == "786MB\u2193 1.31MB\u2191"

    def test_disk_label(self):
        assert metric_value_text(_SAMPLE, "disk") == "42.0%"

    def test_missing_metric_label_dash(self):
        assert metric_value_text({}, "cpu") == "-"


class TestRenderSparkline:
    """Braille bar sparkline rendering."""

    def test_empty_values_blank_lines(self):
        assert render_sparkline([], height=3) == "\n\n"

    def test_zero_top_blank_lines(self):
        assert render_sparkline([0, 0], height=2) == "\n"

    def test_single_sample_fills_one_column(self):
        spark = render_sparkline([5, 0], height=1)
        assert spark != ""

    def test_max_value_fills_full_height(self):
        spark = render_sparkline([10, 0], height=2, vmax=10)
        lines = spark.splitlines()
        assert len(lines) == 2
        assert all(line for line in lines)

    def test_partial_value_bottom_aligns(self):
        spark = render_sparkline([5, 0], height=3, vmax=10)
        # 5/10*12 = 6 units -> one full row + one partial row, on the baseline.
        lines = spark.splitlines()
        assert len(lines) == 3
        assert not lines[0]
        assert lines[-1]

    def test_window_max_scale_when_no_vmax(self):
        spark = render_sparkline([4, 8], height=2)
        lines = spark.splitlines()
        # The tallest bar spans both rows; the shorter sits on the baseline.
        assert len(lines) == 2
        assert lines[0] and lines[-1]

    def test_small_percentage_stays_visible(self):
        # 0.2% on a fixed 0-100 scale would round to 0 units; keep 1 dot.
        spark = render_sparkline([0.2], height=3, vmax=100)
        assert spark

    def test_low_bar_aligns_to_bottom_row(self):
        # A 1-unit bar on a 3-row graph must sit on the last (baseline) row.
        spark = render_sparkline([0.2], height=3, vmax=100)
        lines = spark.splitlines()
        assert len(lines) == 3
        assert not lines[0] and not lines[1]
        assert lines[2]

    def test_over_scale_value_never_grows_past_height(self):
        # docker CPUPerc can exceed 100% (measured on a single core); the chart
        # must stay exactly `height` rows instead of spiking taller.
        for value in (100.0, 150.0, 168.2, 250.0):
            assert len(render_sparkline([value], height=3, vmax=100).splitlines()) == 3

    def test_dual_over_scale_stays_at_two_height(self):
        spark = render_dual_sparkline([1000], [5], height=2)
        assert len(spark.splitlines()) == 4


class TestMetricDuo:
    """Two-direction (down/up) sample extraction."""

    def test_network_down_up(self):
        assert metric_duo(_SAMPLE, "network") == (7.59, 0.14)

    def test_block_down_up(self):
        assert metric_duo(_SAMPLE, "block") == (786, 1.31)

    def test_single_direction_metric_returns_none(self):
        assert metric_duo(_SAMPLE, "cpu") is None

    def test_missing_metric_returns_none(self):
        assert metric_duo({}, "network") is None


class TestRenderDualSparkline:
    """Mirrored two-direction braille sparkline."""

    def test_empty_returns_two_height_blank_lines(self):
        assert render_dual_sparkline([], [], height=3) == "\n".join([""] * 6)

    def test_returns_two_times_height_rows(self):
        spark = render_dual_sparkline([10], [5], height=2)
        assert len(spark.split("\n")) == 4

    def test_up_only_fills_top_half(self):
        spark = render_dual_sparkline([0], [10], height=2)
        lines = spark.split("\n")
        assert len(lines) == 4
        assert lines[0] and lines[1]
        assert not lines[2] and not lines[3]

    def test_down_only_fills_bottom_half(self):
        spark = render_dual_sparkline([10], [0], height=2)
        lines = spark.split("\n")
        assert len(lines) == 4
        assert not lines[0] and not lines[1]
        assert lines[2] and lines[3]

    def test_shared_scale_keeps_ratio(self):
        # Down dominates (10 vs 0.5); the up side keeps a 1-unit floor.
        spark = render_dual_sparkline([10], [0.5], height=2)
        lines = spark.split("\n")
        assert len(lines) == 4
        assert not lines[0]
        assert lines[1]
        assert lines[2] and lines[3]


class TestTotalLabel:
    """Cumulative down/up total formatting."""

    def test_gb_totals(self):
        assert format_duo_total_label(61400, 14200) == "60.0GB\u2193/13.9GB\u2191"

    def test_mb_and_kb_totals(self):
        assert format_duo_total_label(7.59, 0.14) == "8MB\u2193/143KB\u2191"


class TestMetricScale:
    """Per-metric sparkline scale caps."""

    def test_percentage_metrics_use_fixed_scale(self):
        assert METRIC_SCALE["cpu"] == 100
        assert METRIC_SCALE["memory"] == 100
        assert METRIC_SCALE["disk"] == 100

    def test_absolute_metrics_use_relative_scale(self):
        assert METRIC_SCALE["network"] is None
        assert METRIC_SCALE["block"] is None
