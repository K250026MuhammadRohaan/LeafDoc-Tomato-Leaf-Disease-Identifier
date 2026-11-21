# ======================================================================
# exceptions.py
# LeafDoc - our own custom exception (error) class.
# ======================================================================


class InvalidImageError(Exception):
    """Raised when an image file is missing, is not an image, or is damaged.

    It inherits from Exception, so we can catch it with
    `except InvalidImageError` and show a friendly message instead of crashing.
    """
    pass
