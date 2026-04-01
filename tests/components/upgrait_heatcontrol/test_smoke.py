"""Basic smoke tests for the UPGRAIT HeatControl integration overlay."""

from custom_components.upgrait_heatcontrol.const import DEFAULT_PORT, DOMAIN


def test_basic_constants() -> None:
    assert DOMAIN == "upgrait_heatcontrol"
    assert DEFAULT_PORT == 8001
