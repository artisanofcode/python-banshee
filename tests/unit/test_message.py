"""
Tests for :class:`banshee.Message`
"""

import dataclasses

import pytest

import banshee

import tests.fixture


def test_it_should_allow_access_to_request() -> None:
    """
    it should allow access to request.
    """
    request = object()

    message = banshee.Message(request)

    assert message.request is request


def test_it_should_be_immutable() -> None:
    """
    it should be immutable.
    """
    context = tests.fixture.Dummy1()

    message = banshee.Message(object(), contexts=(context,))

    with pytest.raises(dataclasses.FrozenInstanceError):
        message.request = object()  # type: ignore

    with pytest.raises(dataclasses.FrozenInstanceError):
        message.contexts = (context,)  # type: ignore

    print(message.contexts.__class__)
    with pytest.raises(TypeError):
        # pylint: disable=unsupported-assignment-operation
        message.contexts[0] = context  # type: ignore


def test_it_should_default_to_empty_sequence_for_contexts() -> None:
    """
    it should allow access to request.
    """
    message = banshee.Message(object())

    assert len(message.contexts) == 0


def test_it_should_allow_access_to_contexts() -> None:
    """
    it should allow access to request.
    """
    context1 = tests.fixture.Dummy1()
    context2 = tests.fixture.Dummy2()

    message = banshee.Message(
        object(),
        contexts=(
            context1,
            context2,
        ),
    )

    assert len(message.contexts) == 2
    assert message.contexts[0] == context1
    assert message.contexts[1] == context2


def test_get_should_return_matching_context() -> None:
    """
    get() should return matching context.
    """
    context = tests.fixture.Dummy1()

    message = banshee.Message(
        object(),
        contexts=(
            tests.fixture.Dummy2(),
            context,
            tests.fixture.Dummy2(),
        ),
    )

    assert message.get(tests.fixture.Dummy1) is context


def test_get_should_return_none_for_unknown_context() -> None:
    """
    get() should return none for unknown context.
    """
    message = banshee.Message(object(), contexts=(tests.fixture.Dummy2(),))

    assert message.get(tests.fixture.Dummy1) is None


def test_get_should_return_most_recent_matching_context() -> None:
    """
    get() should return most recent matching context.
    """
    context1 = tests.fixture.Dummy1()
    context2 = tests.fixture.Dummy1()

    message = banshee.Message(
        object(),
        contexts=(
            tests.fixture.Dummy2(),
            context1,
            tests.fixture.Dummy2(),
            context2,
        ),
    )

    assert message.get(tests.fixture.Dummy1) is context2


def test_get_should_return_default_for_unknown_context() -> None:
    """
    get() should return matching context.
    """
    context = tests.fixture.Dummy1()

    message = banshee.Message(object(), contexts=(tests.fixture.Dummy2(),))

    assert message.get(tests.fixture.Dummy1, context) is context


def test_all_should_return_matching_contexts() -> None:
    """
    get() should return matching context.
    """
    context1 = tests.fixture.Dummy1()
    context2 = tests.fixture.Dummy1()

    message = banshee.Message(
        object(),
        contexts=(
            tests.fixture.Dummy2(),
            context1,
            tests.fixture.Dummy2(),
            context2,
        ),
    )

    result = tuple(message.all(tests.fixture.Dummy1))

    assert len(result) == 2
    assert result[0] == context1
    assert result[1] == context2


def test_all_should_return_empty_sequence_for_unknown_context() -> None:
    """
    get() should return empty sequence for unknown context.
    """
    message = banshee.Message(
        object(),
        contexts=(
            tests.fixture.Dummy2(),
            tests.fixture.Dummy2(),
        ),
    )

    result = tuple(message.all(tests.fixture.Dummy1))

    assert len(result) == 0


def test_has_should_return_true_for_matching_context() -> None:
    """
    has() should return True for matching context.
    """
    context = tests.fixture.Dummy1()

    message = banshee.Message(
        object(),
        contexts=(
            tests.fixture.Dummy2(),
            context,
            tests.fixture.Dummy2(),
        ),
    )

    assert message.has(tests.fixture.Dummy1) is True


def test_has_should_return_false_for_unknown_context() -> None:
    """
    has() should return False for unknown context.
    """
    message = banshee.Message(object(), contexts=(tests.fixture.Dummy2(),))

    assert message.has(tests.fixture.Dummy1) is False


def test_get_item_should_return_matching_context() -> None:
    """
    it[key] should return matching context.
    """
    context = tests.fixture.Dummy1()

    message = banshee.Message(
        object(),
        contexts=(
            tests.fixture.Dummy2(),
            context,
            tests.fixture.Dummy2(),
        ),
    )

    assert message[tests.fixture.Dummy1] is context


def test_get_item_should_raise_key_error_for_unknown_context() -> None:
    """
    it[key] should raise KeyError for unknown context.
    """
    message = banshee.Message(object(), contexts=(tests.fixture.Dummy2(),))

    with pytest.raises(KeyError):
        message[tests.fixture.Dummy1]  # pylint: disable=pointless-statement


def test_get_item_should_return_most_recent_matching_context() -> None:
    """
    it[key] should return most recent matching context.
    """
    context1 = tests.fixture.Dummy1()
    context2 = tests.fixture.Dummy1()

    message = banshee.Message(
        object(),
        contexts=(
            tests.fixture.Dummy2(),
            context1,
            tests.fixture.Dummy2(),
            context2,
        ),
    )

    assert message[tests.fixture.Dummy1] is context2


def test_contains_should_return_true_for_matching_context() -> None:
    """
    (key in it) should return True for matching context.
    """
    context = tests.fixture.Dummy1()

    message = banshee.Message(
        object(),
        contexts=(
            tests.fixture.Dummy2(),
            context,
            tests.fixture.Dummy2(),
        ),
    )

    assert (tests.fixture.Dummy1 in message) is True


def test_contains_should_return_false_for_unknown_context() -> None:
    """
    (key in it) should return False for unknown context.
    """
    message = banshee.Message(object(), contexts=(tests.fixture.Dummy2(),))

    assert (tests.fixture.Dummy1 in message) is False


def test_including_creates_a_new_instance_with_same_request() -> None:
    """
    including() creates a new instance with same request.
    """
    message1 = banshee.Message(object())

    message2 = message1.including(tests.fixture.Dummy1())

    assert message1 is not message2
    assert message1.request is message2.request


def test_including_returns_same_instance_when_no_change() -> None:
    """
    including() returns same instance when no change.
    """
    message1 = banshee.Message(object())

    message2 = message1.including()

    assert message1 is message2


def test_including_adds_contexts_to_returned_instance() -> None:
    """
    including() adds contexts to returned instance.
    """
    context1 = tests.fixture.Dummy1()
    context2 = tests.fixture.Dummy1()
    context3 = tests.fixture.Dummy1()
    context4 = tests.fixture.Dummy1()

    message1 = banshee.Message(object(), contexts=(context1, context2))

    message2 = message1.including(context3, context4)

    message3 = message1.including(context3)

    assert len(message1.contexts) == 2
    assert len(message2.contexts) == 4
    assert len(message3.contexts) == 3

    assert message1.contexts[0] == message2.contexts[0] == message3.contexts[0]
    assert message1.contexts[1] == message2.contexts[1] == message3.contexts[1]

    assert message2.contexts[2] == context3
    assert message2.contexts[3] == context4

    assert message3.contexts[2] == context3


def test_excluding_creates_a_new_instance_with_same_request() -> None:
    """
    excluding() creates a new instance with same request.
    """
    message1 = banshee.Message(
        object(),
        contexts=(
            tests.fixture.Dummy2(),
            tests.fixture.Dummy1(),
            tests.fixture.Dummy2(),
        ),
    )

    message2 = message1.excluding(tests.fixture.Dummy2)

    assert message1 is not message2
    assert message1.request is message2.request


def test_excluding_returns_same_instance_when_no_change() -> None:
    """
    excluding() returns same instance when no change.
    """
    message1 = banshee.Message(
        object(),
        contexts=(tests.fixture.Dummy1(),),
    )

    message2 = message1.excluding(tests.fixture.Dummy2)

    assert message1 is message2


def test_excluding_removes_contexts_from_returned_instance() -> None:
    """
    including() removes contexts from returned instance.
    """
    context = tests.fixture.Dummy1()

    message1 = banshee.Message(
        object(),
        contexts=(
            tests.fixture.Dummy2(),
            context,
            tests.fixture.Dummy2(),
        ),
    )

    message2 = message1.excluding(tests.fixture.Dummy2)

    assert len(message1.contexts) == 3
    assert len(message2.contexts) == 1

    assert message2.contexts[0] == context
