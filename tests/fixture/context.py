"""
Context related fixtures.
"""

import dataclasses


@dataclasses.dataclass(frozen=True)
class Dummy1:
    """
    Dummy context.

    A simple context for use in tests.
    """


@dataclasses.dataclass(frozen=True)
class Dummy2:
    """
    Dummy context.

    A simple context for use in tests.
    """
