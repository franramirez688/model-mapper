"""
    General exceptions
"""


class FormError(Exception):
    pass


class FieldError(Exception):
    pass


class ModelAccessorError(Exception):
    pass


class ModelAccessorAttributeError(ModelAccessorError):
    pass


class ModelAccessorIndexError(ModelAccessorError):
    pass


class ModelAccessorKeyError(ModelAccessorError):
    pass
