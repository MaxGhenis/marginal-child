"""Tests for chart transformation utilities."""

import pytest
from marginal_child.chart_utils import clip_mtr_value, transform_data_for_chart


class TestClipMTRValue:
    """Test MTR value clipping."""

    def test_clip_extreme_positive(self):
        """Extreme positive values should be clipped to 1."""
        assert clip_mtr_value(10.79) == 1.0
        assert clip_mtr_value(2.5) == 1.0
        assert clip_mtr_value(1.5) == 1.0

    def test_clip_extreme_negative(self):
        """Extreme negative values should be clipped to -1."""
        assert clip_mtr_value(-28.37) == -1.0
        assert clip_mtr_value(-2.5) == -1.0
        assert clip_mtr_value(-1.5) == -1.0

    def test_normal_range_unchanged(self):
        """Values in [-1, 1] should pass through unchanged."""
        assert clip_mtr_value(0.0) == 0.0
        assert clip_mtr_value(0.5) == 0.5
        assert clip_mtr_value(-0.5) == -0.5
        assert clip_mtr_value(0.676) == 0.676

    def test_boundary_values(self):
        """Boundary values should be exact."""
        assert clip_mtr_value(1.0) == 1.0
        assert clip_mtr_value(-1.0) == -1.0


class TestTransformDataForChart:
    """Test data transformation for Recharts."""

    def test_basic_transformation(self):
        """Should transform basic data correctly."""
        data = [
            {"income": 0, "num_children": 0, "mtr": 0.0},
            {"income": 10000, "num_children": 0, "mtr": 0.28},
            {"income": 0, "num_children": 1, "mtr": 0.0},
            {"income": 10000, "num_children": 1, "mtr": 0.55},
        ]

        result = transform_data_for_chart(data, "mtr", "absolute")

        assert len(result) == 2  # 2 income points
        assert result[0]["income"] == 0
        assert result[0]["0_children"] == 0.0
        assert result[0]["1_children"] == 0.0
        assert result[1]["income"] == 10000
        assert result[1]["0_children"] == 0.28
        assert result[1]["1_children"] == 0.55

    def test_clip_extreme_mtr_values(self):
        """Should clip extreme MTR values to [-1, 1]."""
        data = [
            {"income": 0, "num_children": 0, "mtr": -28.37},  # Extreme negative
            {"income": 10000, "num_children": 0, "mtr": 10.79},  # Extreme positive
        ]

        result = transform_data_for_chart(data, "mtr", "absolute", clip_mtr=True)

        assert result[0]["0_children"] == -1.0
        assert result[1]["0_children"] == 1.0

    def test_no_clipping_when_disabled(self):
        """Should not clip when clip_mtr=False."""
        data = [
            {"income": 0, "num_children": 0, "mtr": -28.37},
            {"income": 10000, "num_children": 0, "mtr": 10.79},
        ]

        result = transform_data_for_chart(data, "mtr", "absolute", clip_mtr=False)

        assert result[0]["0_children"] == -28.37
        assert result[1]["0_children"] == 10.79

    def test_net_income_not_clipped(self):
        """Net income values should never be clipped."""
        data = [
            {"income": 0, "num_children": 0, "net_income": 50000},
            {"income": 10000, "num_children": 0, "net_income": 100000},
        ]

        result = transform_data_for_chart(data, "net_income", "absolute")

        assert result[0]["0_children"] == 50000
        assert result[1]["0_children"] == 100000

    def test_marginal_benefit_transformation(self):
        """Should handle marginal benefit data."""
        data = [
            {"income": 0, "num_children": 1, "marginal_benefit": 1000},
            {"income": 10000, "num_children": 1, "marginal_benefit": 1500},
        ]

        result = transform_data_for_chart(data, "net_income", "marginal")

        assert result[0]["1_children"] == 1000
        assert result[1]["1_children"] == 1500

    def test_empty_data(self):
        """Should handle empty data gracefully."""
        result = transform_data_for_chart([], "mtr", "absolute")
        assert result == []

    def test_multiple_children(self):
        """Should handle multiple children counts."""
        data = []
        for income in [0, 10000, 20000]:
            for num_children in [0, 1, 2, 3]:
                data.append({
                    "income": income,
                    "num_children": num_children,
                    "mtr": 0.2 + num_children * 0.1
                })

        result = transform_data_for_chart(data, "mtr", "absolute")

        assert len(result) == 3  # 3 income points
        assert all(f"{i}_children" in result[0] for i in range(4))
        assert result[0]["0_children"] == 0.2
        assert result[0]["3_children"] == 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
