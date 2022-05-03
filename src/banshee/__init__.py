"""
A message bus / command dispatcher implementation.
"""

from banshee.builder import Builder
from banshee.bus import Bus, MessageBus
from banshee.context import Causation, Dispatch, HandleAfter, Identity
from banshee.errors import ConfigurationError, DispatchError, MultipleErrors
from banshee.message import HandleMessage, Message, Middleware, message_for
from banshee.middleware.causation import CausationMiddleware
from banshee.middleware.dispatch import DispatchMiddleware
from banshee.middleware.gate import Gate, GateMiddleware
from banshee.middleware.handle_after import HandleAfterMiddleware
from banshee.middleware.identity import IdentityMiddleware
from banshee.registry import Registry
from banshee.request import (
    Handler,
    HandlerFactory,
    HandlerLocator,
    HandlerReference,
    SimpleHandlerFactory,
)
from banshee.testing import MessageInfo, TraceableBus

__all__ = (
    "Builder",
    "Bus",
    "Causation",
    "CausationMiddleware",
    "ConfigurationError",
    "Dispatch",
    "DispatchError",
    "DispatchMiddleware",
    "Gate",
    "GateMiddleware",
    "HandleAfter",
    "HandleAfterMiddleware",
    "HandleMessage",
    "Handler",
    "HandlerFactory",
    "HandlerLocator",
    "HandlerReference",
    "Identity",
    "IdentityMiddleware",
    "message_for",
    "Message",
    "MessageBus",
    "MessageInfo",
    "Middleware",
    "MultipleErrors",
    "Registry",
    "SimpleHandlerFactory",
    "TraceableBus",
)
