"""
    General exceptions
"""


class ModelMapperError(Exception):
    pass


class FieldError(Exception):
    pass


class FieldAccessorError(Exception):
    pass


class FieldAccessorAttributeError(FieldAccessorError):
    pass


class FieldAccessorIndexError(FieldAccessorError):
    pass


class FieldAccessorKeyError(FieldAccessorError):
    pass


class FieldAccessorAssignmentError(FieldAccessorError):
    pass
