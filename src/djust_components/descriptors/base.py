"""
Re-exports for descriptor-based component development.

No new base class needed — djust's LiveComponent IS the base.
TypedState is re-exported for convenience.
"""

from djust.components.base import LiveComponent
from djust_components.mixins.base import TypedState

__all__ = ["LiveComponent", "TypedState"]
