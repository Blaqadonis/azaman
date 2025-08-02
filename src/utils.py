"""Utility functions for Aza Man financial assistant."""

def split_model_and_provider(fully_specified_name: str) -> dict:
    """Split a fully specified model name into provider and model components.

    Args:
        fully_specified_name (str): The full model name (e.g., "provider/model").

    Returns:
        dict: Dictionary with "model" and "provider" keys. Provider may be None if not specified.
    """
    if "/" in fully_specified_name:
        provider, model = fully_specified_name.split("/", maxsplit=1)
    else:
        provider = None
        model = fully_specified_name
    return {"model": model, "provider": provider}