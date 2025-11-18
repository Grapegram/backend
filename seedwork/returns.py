from functools import wraps

from returns.primitives.exceptions import UnwrapFailedError


def catch_unwrap(func):
    """
    Decorator that catches UnwrapFailedError exceptions and converts them to Failure results.

    This is useful when you want to unwrap Result values inside a function and automatically
    catch any unwrap failures, converting them back to Failure results.

    The decorator works by wrapping the function with @safe, which catches UnwrapFailedError.
    When an unwrap fails, it extracts the original Failure from the UnwrapFailedError's
    halted_container attribute and returns it.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except UnwrapFailedError as exc:
            return exc.halted_container

    return wrapper
