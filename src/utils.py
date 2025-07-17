"""Utility functions for Aza Man financial assistant.

This module provides helper functions for parsing and processing configuration data.
"""


def split_model_and_provider(fully_specified_name: str) -> dict:
    """Split a fully specified model name into provider and model components.

    Args:
        fully_specified_name: The full model name (e.g., "provider/model").

    Returns:
        dict: Dictionary with "model" and "provider" keys.
    """
    if "/" in fully_specified_name:
        provider, model = fully_specified_name.split("/", maxsplit=1)
    else:
        provider = None
        model = fully_specified_name
    return {"model": model, "provider": provider}