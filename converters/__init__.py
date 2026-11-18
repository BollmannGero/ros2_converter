"""Register the supported data converters."""

from .images import IMAGE_CONVERTERS

MESSAGE_CONVERTERS = {**IMAGE_CONVERTERS}
