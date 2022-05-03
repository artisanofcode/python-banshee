"""
Additional context for requests.
"""

import dataclasses
import typing
import uuid


@dataclasses.dataclass(frozen=True, slots=True)
class HandleAfter:
    """
    Handle after context.

    Presence of this context marks that processing of the message should be postponed
    until after the current message has been handled.
    """


@dataclasses.dataclass(frozen=True, slots=True)
class Dispatch:
    """
    Dispatch context.

    Marks a message as having had its request processed by a specific handler
    and contains the result of that execution.

    :param name: handler name
    :param result: result of handler
    """

    #: handler name
    name: str
    #: result of handler
    result: typing.Any | None


@dataclasses.dataclass(frozen=True, slots=True)
class Identity:
    """
    Identity context.

    Attaches a unique identifier to the event.

    :param unique_id: unique identifier
    """

    #: unique identifier
    unique_id: uuid.UUID


@dataclasses.dataclass(frozen=True, slots=True)
class Causation:
    """
    Causation context.

    Holds the identity of the request that created this request, and the root request
    for correlating related events.

    :param causation_id: parent identifier
    :param correlation_id: root identifier
    """

    #: parent identifier
    causation_id: uuid.UUID
    #: root identifier
    correlation_id: uuid.UUID
