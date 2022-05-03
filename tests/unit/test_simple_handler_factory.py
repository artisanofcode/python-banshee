"""
Tests for :class:`banshee.SimpleHandlerFactory`
"""
import typing

import banshee


def test_it_should_return_functions_untouched() -> None:
    """
    it should return functions untouched
    """

    def _foo(_: typing.Any, /) -> None:
        pass

    reference: banshee.HandlerReference[typing.Any] = banshee.HandlerReference(
        name="test",
        handler=_foo,
    )

    factory = banshee.SimpleHandlerFactory()

    result = factory(reference)

    assert result is typing.cast(banshee.Handler[typing.Any], _foo)


def test_it_should_return_classes_instantiated() -> None:
    """
    it should return classes instantiated
    """

    class _Foo:  # pylint: disable=too-few-public-methods
        def __call__(self, _: typing.Any, /) -> typing.Any:
            pass

    reference: banshee.HandlerReference[typing.Any] = banshee.HandlerReference(
        name="test",
        handler=_Foo,
    )

    factory = banshee.SimpleHandlerFactory()

    result = factory(reference)

    assert isinstance(result, _Foo)
