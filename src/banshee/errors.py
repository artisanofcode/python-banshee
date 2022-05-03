"""
Errors raised by banshee.
"""

import exceptiongroup


class MultipleErrors(exceptiongroup.ExceptionGroup[Exception]):
    """
    Multiple errors.

    Multiple errors were produced.
    """


class DispatchError(MultipleErrors):
    """
    Dispatch error.

    There was an error while handling a request.
    """


class ConfigurationError(RuntimeError):
    """
    Configuration error.

    There was an error in how banshee was configured.
    """
