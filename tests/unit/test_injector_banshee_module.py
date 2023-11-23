"""
Tests for :class:`banshee.extra.injector.BansheeModule`
"""

import injector

import banshee
import banshee.extra.injector


def test_it_should_build_bus_instance() -> None:
    """
    it should build bus instance.
    """
    registry = banshee.Registry()
    container = injector.Injector(banshee.extra.injector.BansheeModule(registry))
    bus = container.get(banshee.Bus)  # type: ignore

    assert isinstance(bus, banshee.Bus)


def test_it_should_allow_multiple_uses() -> None:
    """
    it should allow multiple uses.
    """
    registry = banshee.Registry()
    container = injector.Injector(banshee.extra.injector.BansheeModule(registry))
    bus1 = container.get(banshee.Bus)  # type: ignore

    container = injector.Injector(banshee.extra.injector.BansheeModule(registry))
    bus2 = container.get(banshee.Bus)  # type: ignore

    assert bus1 is not bus2
