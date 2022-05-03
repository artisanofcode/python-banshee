"""
Tests for :class:`banshee.Builder`
"""

import pytest

import banshee
import banshee.bus

import tests.fixture


def test_with_middleware_should_add_middleware() -> None:
    """
    with_middleware() should add middleware.
    """
    builder1 = banshee.Builder()

    middleware1 = tests.fixture.mock_middleware()
    middleware2 = tests.fixture.mock_middleware()

    builder2 = builder1.with_middleware(middleware1)
    builder3 = builder2.with_middleware(middleware2)

    assert len(builder1.middleware) == 0
    assert len(builder2.middleware) == 1
    assert len(builder3.middleware) == 2
    assert builder2.middleware[0] is middleware1
    assert builder3.middleware[0] is middleware1
    assert builder3.middleware[1] is middleware2


def test_with_factory_should_set_factory() -> None:
    """
    with_factory() should set factory.
    """
    builder1 = banshee.Builder()

    factory = tests.fixture.mock_factory()

    builder2 = builder1.with_factory(factory)

    assert builder1.factory is None
    assert builder2.factory is factory


def test_with_locator_should_set_locator() -> None:
    """
    with_locator() should set locator.
    """
    builder1 = banshee.Builder()

    locator = tests.fixture.mock_locator()

    builder2 = builder1.with_locator(locator)

    assert builder1.locator is None
    assert builder2.locator is locator


def test_build_should_construct_message_bus_instance_with_dispatch_middleware() -> None:
    """
    build() should construct message bus instance with DispatchMiddleware .
    """
    builder = banshee.Builder(
        middleware=(tests.fixture.mock_middleware(), tests.fixture.mock_middleware()),
        factory=tests.fixture.mock_factory(),
        locator=tests.fixture.mock_locator(),
    )

    bus = builder.build()

    assert isinstance(bus, banshee.bus.MessageBus)
    assert len(bus.middleware) == 3
    assert bus.middleware[0] == builder.middleware[0]
    assert bus.middleware[1] == builder.middleware[1]
    assert isinstance(bus.middleware[2], banshee.DispatchMiddleware)
    assert bus.middleware[2].factory == builder.factory
    assert bus.middleware[2].locator == builder.locator


def test_build_should_default_to_simple_handler_factory() -> None:
    """
    build() should default to SimpleHandlerFactory
    """
    builder = banshee.Builder(locator=tests.fixture.mock_locator())

    bus = builder.build()

    assert isinstance(bus, banshee.bus.MessageBus)
    assert isinstance(bus.middleware[0], banshee.DispatchMiddleware)
    assert isinstance(bus.middleware[0].factory, banshee.SimpleHandlerFactory)


def test_build_should_error_when_locator_is_not_provided() -> None:
    """
    build() should error when locator is not provided
    """
    builder = banshee.Builder()

    with pytest.raises(banshee.ConfigurationError, match="No locator provided."):
        builder.build()
