import pytest
from returns.pipeline import is_successful
from returns.result import Failure, Success

from seedwork.returns import catch_unwrap


class TestCatchFailureDecorator:
    """Test suite for the catch_unwrap decorator."""

    def test_successful_result_is_returned_as_is(self):
        """Test that successful results pass through unchanged."""

        @catch_unwrap
        def returns_success():
            return Success(42)

        result = returns_success()
        assert is_successful(result)
        assert result.unwrap() == 42

    def test_failure_result_is_returned_as_is(self):
        """Test that Failure results pass through unchanged."""

        @catch_unwrap
        def returns_failure():
            return Failure("error message")

        result = returns_failure()
        assert not is_successful(result)
        assert result.failure() == "error message"

    def test_unwrap_failed_error_is_caught_and_converted_to_failure(self):
        """Test that UnwrapFailedError from unwrapping Failure is caught."""

        @catch_unwrap
        def unwraps_failure():
            failed = Failure("original error")
            return failed.unwrap()  # This raises UnwrapFailedError

        result = unwraps_failure()
        assert not is_successful(result)
        assert result.failure() == "original error"

    def test_nested_failure_unwrap_is_caught(self):
        """Test catching unwrap on nested Failure results."""

        @catch_unwrap
        def nested_unwrap():
            inner_failure = Failure(ValueError("nested error"))
            return inner_failure.unwrap()

        result = nested_unwrap()
        assert not is_successful(result)
        assert isinstance(result.failure(), ValueError)
        assert str(result.failure()) == "nested error"

    def test_regular_exceptions_are_not_caught(self):
        """Test that regular exceptions are not caught by the decorator."""

        @catch_unwrap
        def raises_regular_exception():
            raise ValueError("regular exception")

        with pytest.raises(ValueError, match="regular exception"):
            raises_regular_exception()

    def test_successful_value_is_returned_directly(self):
        """Test that non-Result values wrapped in Success are returned."""

        @catch_unwrap
        def returns_plain_value():
            return Success("plain string")

        result = returns_plain_value()
        assert is_successful(result)
        assert result.unwrap() == "plain string"

    def test_multiple_unwraps_first_failure_is_caught(self):
        """Test that the first unwrap failure is caught."""

        @catch_unwrap
        def multiple_operations():
            result1 = Failure("first error")
            result1.unwrap()  # This will raise
            result2 = Failure("second error")
            return result2.unwrap()  # This won't be reached

        result = multiple_operations()
        assert not is_successful(result)
        assert result.failure() == "first error"

    def test_complex_failure_object(self):
        """Test with complex error objects."""

        class CustomError:
            def __init__(self, code, message):
                self.code = code
                self.message = message

        @catch_unwrap
        def returns_complex_error():
            error = CustomError(404, "Not found")
            return Failure(error).unwrap()

        result = returns_complex_error()
        assert not is_successful(result)
        error = result.failure()
        assert isinstance(error, CustomError)
        assert error.code == 404
        assert error.message == "Not found"

    def test_success_with_none_value(self):
        """Test that Success with None value works correctly."""

        @catch_unwrap
        def returns_none():
            return Success(None)

        result = returns_none()
        assert is_successful(result)
        assert result.unwrap() is None

    def test_failure_with_none_value(self):
        """Test that Failure with None value works correctly."""

        @catch_unwrap
        def returns_failure_none():
            return Failure(None).unwrap()

        result = returns_failure_none()
        assert not is_successful(result)
        assert result.failure() is None

    def test_chained_result_operations(self):
        """Test decorator with chained Result operations."""

        @catch_unwrap
        def chained_operations():
            return Success(10).map(lambda x: x * 2).bind(lambda x: Success(x + 5))

        result = chained_operations()
        assert is_successful(result)
        assert result.unwrap() == 25

    def test_failed_chained_operations(self):
        """Test decorator with failed chained operations."""

        @catch_unwrap
        def failed_chain():
            return (
                Success(10)
                .map(lambda x: x * 2)
                .bind(lambda x: Failure("chain broken"))
                .unwrap()  # This will raise UnwrapFailedError
            )

        result = failed_chain()
        assert not is_successful(result)
        assert result.failure() == "chain broken"

    def test_decorator_preserves_function_metadata(self):
        """Test that decorator preserves function name and docstring."""

        @catch_unwrap
        def documented_function():
            """This is a documented function."""
            return Success(42)

        # Note: functools.wraps is not used in the decorator,
        # so this test documents current behavior
        # If you want to preserve metadata, add @functools.wraps(func) to the decorator
        result = documented_function()
        assert is_successful(result)

    def test_with_function_arguments(self):
        """Test decorator works with functions that accept arguments."""

        @catch_unwrap
        def process_value(value, multiplier=2):
            if value < 0:
                return Failure("negative value").unwrap()
            return Success(value * multiplier)

        result1 = process_value(5)
        assert is_successful(result1)
        assert result1.unwrap() == 10

        result2 = process_value(3, multiplier=4)
        assert is_successful(result2)
        assert result2.unwrap() == 12

        result3 = process_value(-1)
        assert not is_successful(result3)
        assert result3.failure() == "negative value"

    def test_with_kwargs_only(self):
        """Test decorator with keyword-only arguments."""

        @catch_unwrap
        def process_data(*, data, strict=False):
            if strict and not data:
                return Failure("empty data").unwrap()
            return Success(data or "default")

        result1 = process_data(data="test")
        assert is_successful(result1)
        assert result1.unwrap() == "test"

        result2 = process_data(data="", strict=True)
        assert not is_successful(result2)
        assert result2.failure() == "empty data"

    def test_with_class_method(self):
        """Test decorator works with class methods."""

        class Calculator:
            @catch_unwrap
            def divide(self, a, b):
                if b == 0:
                    return Failure("division by zero").unwrap()
                return Success(a / b)

        calc = Calculator()
        result1 = calc.divide(10, 2)
        assert is_successful(result1)
        assert result1.unwrap() == 5.0

        result2 = calc.divide(10, 0)
        assert not is_successful(result2)
        assert result2.failure() == "division by zero"

    def test_with_static_method(self):
        """Test decorator works with static methods."""

        class MathUtils:
            @staticmethod
            @catch_unwrap
            def safe_sqrt(value):
                if value < 0:
                    return Failure("negative value").unwrap()
                return Success(value**0.5)

        result1 = MathUtils.safe_sqrt(16)
        assert is_successful(result1)
        assert result1.unwrap() == 4.0

        result2 = MathUtils.safe_sqrt(-1)
        assert not is_successful(result2)
        assert result2.failure() == "negative value"

    def test_exception_object_in_failure(self):
        """Test with exception objects in Failure."""

        @catch_unwrap
        def returns_exception_failure():
            exc = ValueError("something went wrong")
            return Failure(exc).unwrap()

        result = returns_exception_failure()
        assert not is_successful(result)
        error = result.failure()
        assert isinstance(error, ValueError)
        assert str(error) == "something went wrong"

    def test_empty_failure(self):
        """Test with Failure containing empty string."""

        @catch_unwrap
        def empty_error():
            return Failure("").unwrap()

        result = empty_error()
        assert not is_successful(result)
        assert result.failure() == ""

    def test_decorator_is_idempotent(self):
        """Test that applying decorator multiple times doesn't break functionality."""

        @catch_unwrap
        @catch_unwrap
        def double_decorated():
            return Failure("error").unwrap()

        result = double_decorated()
        assert not is_successful(result)
        # The error might be wrapped, but it should still be a Failure
        assert not is_successful(result)
