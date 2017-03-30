"""
    General exceptions
"""


class ModelMapperError(Exception):
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


class ModelAccessorAssignmentError(ModelAccessorError):
    pass


class FieldAccessorError(Exception):
    pass


class DeclarationError(Exception):
    pass
