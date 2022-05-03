"""
Tests for :meth:`banshee.message_for`
"""

import banshee

import tests.fixture


def test_it_should_wrap_request() -> None:
    """
    it should wrap request.
    """
    request = object()

    message = banshee.message_for(request)

    assert message.request is request


def test_it_should_wrap_request_and_context() -> None:
    """
    it should wrap request and context.
    """
    request = object()

    context1 = tests.fixture.Dummy1()
    context2 = tests.fixture.Dummy2()

    message = banshee.message_for(request, [context1, context2])

    assert message.request is request
    assert len(message.contexts) == 2
    assert tuple(message.contexts) == (context1, context2)


def test_it_should_not_wrap_message() -> None:
    """
    it should not wrap message.
    """
    message1 = banshee.Message(object())
    # annotation needed to make mypy happy...
    message2: banshee.Message[object] = banshee.message_for(message1)

    assert message2 is message1


def test_it_should_add_contexts_to_message() -> None:
    """
    it should add contexts to message.
    """
    context1 = tests.fixture.Dummy1()
    context2 = tests.fixture.Dummy2()

    message1 = banshee.Message(object(), contexts=(context1, context2))

    context3 = tests.fixture.Dummy1()
    context4 = tests.fixture.Dummy2()

    # annotation needed to make mypy happy...
    message2: banshee.Message[object] = banshee.message_for(
        message1,
        [context3, context4],
    )

    assert message2.request is message1.request
    assert len(message2.contexts) == 4
    assert tuple(message2.contexts) == (context1, context2, context3, context4)
