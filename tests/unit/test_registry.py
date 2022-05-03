"""
Tests for :class:`banshee.Registry`
"""
import collections.abc
import typing

import banshee

import tests.fixture


class _Foo:  # pylint: disable=too-few-public-methods
    pass


class _Bar:  # pylint: disable=too-few-public-methods
    pass


class _Handler:  # pylint: disable=too-few-public-methods
    pass


def _handler(_: _Foo, /) -> None:
    pass


def name_for(handler: type | collections.abc.Callable[..., typing.Any]) -> str:
    """
    Name for handler

    Helper to get the name the registry would automatically generate for a handler.

    :param handler: the handler callable or type

    :returns: the auto generated name
    """

    registry = banshee.Registry()

    registry.subscribe(handler, to=_Foo)

    references = tuple(registry.subscribers_for(banshee.message_for(_Foo())))

    assert references
    return references[0].name


def test_subscribe_should_register_handler() -> None:
    """
    subscribe() should register handler
    """
    registry = banshee.Registry()

    handler1 = tests.fixture.mock_handler()
    handler2 = tests.fixture.mock_handler()

    registry.subscribe(handler1, to=_Foo)
    registry.subscribe(handler2, to=_Foo)

    references = tuple(registry.subscribers_for(banshee.message_for(_Foo())))

    assert [ref.handler for ref in references] == [handler1, handler2]
    assert not tuple(registry.subscribers_for(banshee.message_for(_Bar())))


def test_subscribe_should_accept_handler_name() -> None:
    """
    subscribe() should accept handler name
    """
    registry = banshee.Registry()

    handler = tests.fixture.mock_handler()

    registry.subscribe(handler, to=_Foo, name="test-name")

    references = tuple(registry.subscribers_for(banshee.message_for(_Foo())))

    assert len(references) == 1
    assert references[0].name == "test-name"


def test_subscribe_should_generate_handler_name_when_absent() -> None:
    """
    subscribe() should generate handler name when absent
    """
    registry = banshee.Registry()

    registry.subscribe(_handler, to=_Foo)

    references = tuple(registry.subscribers_for(banshee.message_for(_Foo())))

    assert len(references) == 1
    assert references[0].name == f"{__name__}._handler"


def test_subscribe_to_should_register_handler() -> None:
    """
    subscribe_to() should register handler
    """
    registry = banshee.Registry()

    handler1 = tests.fixture.mock_handler()
    handler2 = tests.fixture.mock_handler()

    registry.subscribe_to(_Foo)(handler1)
    registry.subscribe_to(_Foo)(handler2)

    references = tuple(registry.subscribers_for(banshee.message_for(_Foo())))

    assert [ref.handler for ref in references] == [handler1, handler2]
    assert not tuple(registry.subscribers_for(banshee.message_for(_Bar())))


def test_subscribe_to_should_accept_handler_name() -> None:
    """
    subscribe_to() should accept handler name
    """
    registry = banshee.Registry()

    handler = tests.fixture.mock_handler()

    registry.subscribe_to(_Foo, name="test-name")(handler)

    references = tuple(registry.subscribers_for(banshee.message_for(_Foo())))

    assert len(references) == 1
    assert references[0].name == "test-name"


def test_subscribe_to_should_generate_handler_name_when_absent() -> None:
    """
    subscribe_to() should generate handler name when absent
    """
    registry = banshee.Registry()

    registry.subscribe_to(_Foo)(_handler)

    references = tuple(registry.subscribers_for(banshee.message_for(_Foo())))

    assert len(references) == 1
    assert references[0].name == f"{__name__}._handler"


def test_subscribe_should_generate_handler_name_for_functions() -> None:
    """
    subscribe() should generate handler name for functions
    """

    assert name_for(_handler) == f"{__name__}._handler"


def test_subscribe_should_generate_handler_name_for_classes() -> None:
    """
    subscribe() should generate handler name for classes
    """

    assert name_for(_Handler) == f"{__name__}._Handler"


def test_subscribe_should_generate_handler_name_for_generics() -> None:
    """
    subscribe() should generate handler name for generics
    """

    T = typing.TypeVar("T")

    class _GenericHandler(typing.Generic[T]):  # pylint: disable=too-few-public-methods
        pass

    Foo = typing.TypeVar("Foo")

    name = name_for(_GenericHandler[Foo])

    assert name == f"{__name__}._GenericHandler[Foo]", name

    name = name_for(_GenericHandler[_Bar])

    assert name == f"{__name__}._GenericHandler[{__name__}._Bar]", name

    name = name_for(_GenericHandler[str])

    assert name == f"{__name__}._GenericHandler[str]", name

    name = name_for(_GenericHandler[tuple[str, ...]])

    assert name == f"{__name__}._GenericHandler[tuple[str, ...]]", name

    name = name_for(_GenericHandler[None])

    assert name == f"{__name__}._GenericHandler[None]", name


def test_subscribe_should_generate_handler_name_for_annotated_types() -> None:
    """
    subscribe() should generate handler name for Annotated types
    """

    name = name_for(typing.Annotated[_Handler, "foo"])  # type: ignore

    assert name == f"typing.Annotated[{__name__}._Handler, {repr('foo')}]", name

    name = name_for(typing.Annotated[_Handler, 123])  # type: ignore

    assert name == f"typing.Annotated[{__name__}._Handler, {repr(123)}]", name
