"""Domain types, units, time and identifiers shared by every package (pure, no I/O)."""

from importlib.metadata import version

__all__ = ["__version__"]

__version__ = version("helder-core")
