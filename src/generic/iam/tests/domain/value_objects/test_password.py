"""
Tests for Password Value Object

Comprehensive test suite covering:
- Basic validation (length, whitespace)
- Strength requirements
- Password strength calculation
- Character type checking
- Security features (masking, representation)
"""

import pytest
from returns.pipeline import is_successful

from seedwork.domain.value_objects import (
    EmptyStringError,
    NotStringError,
    StringTooLong,
    StringTooShort,
)
from src.generic.iam.domain.value_objects.password import (
    InvalidPasswordError,
    Password,
    PasswordStrength,
    WeakPasswordError,
)


class TestPasswordValidation:
    """Test basic password validation rules."""

    def test_valid_password_creation(self):
        """Test creating a valid password."""
        result = Password("SecurePass123!")
        assert is_successful(result)
        password = result.unwrap()
        assert password.value == "SecurePass123!"

    def test_password_too_short(self):
        """Test password shorter than minimum length."""
        result = Password("short")
        assert not is_successful(result)
        error = result.failure()
        assert isinstance(error, StringTooShort)
        assert error.min_length == 8

    def test_password_minimum_length(self):
        """Test password at exact minimum length."""
        result = Password("12345678")
        assert is_successful(result)
        password = result.unwrap()
        assert password.length == 8

    def test_password_too_long(self):
        """Test password exceeding maximum length."""
        long_password = "a" * 129
        result = Password(long_password)
        assert not is_successful(result)
        error = result.failure()
        assert isinstance(error, StringTooLong)
        assert error.max_length == 128

    def test_password_maximum_length(self):
        """Test password at exact maximum length."""
        max_password = "a" * 128
        result = Password(max_password)
        assert is_successful(result)
        password = result.unwrap()
        assert password.length == 128

    def test_password_with_leading_whitespace(self):
        """Test password with leading whitespace is rejected."""
        result = Password(" Password123")
        assert not is_successful(result)
        error = result.failure()
        assert isinstance(error, InvalidPasswordError)
        assert "whitespace" in error.reason.lower()

    def test_password_with_trailing_whitespace(self):
        """Test password with trailing whitespace is rejected."""
        result = Password("Password123 ")
        assert not is_successful(result)
        error = result.failure()
        assert isinstance(error, InvalidPasswordError)
        assert "whitespace" in error.reason.lower()

    def test_password_with_internal_whitespace(self):
        """Test password with internal whitespace is allowed."""
        result = Password("Pass word 123")
        assert is_successful(result)

    def test_password_not_string(self):
        """Test that non-string values are rejected."""
        result = Password(12345678)
        assert not is_successful(result)
        error = result.failure()
        assert isinstance(error, NotStringError)


class TestPasswordStrengthRequirements:
    """Test password strength requirements enforcement."""

    def test_uppercase_requirement(self):
        """Test password with uppercase requirement."""

        class StrictPassword(Password):
            REQUIRE_UPPERCASE = True

        # Should fail without uppercase
        result = StrictPassword("password123!")
        assert not is_successful(result)
        error = result.failure()
        assert isinstance(error, WeakPasswordError)
        assert "uppercase" in error.reason.lower()
        assert "uppercase letter" in error.missing_requirements

        # Should succeed with uppercase
        result = StrictPassword("Password123!")
        assert is_successful(result)

    def test_lowercase_requirement(self):
        """Test password with lowercase requirement."""

        class StrictPassword(Password):
            REQUIRE_LOWERCASE = True

        # Should fail without lowercase
        result = StrictPassword("PASSWORD123!")
        assert not is_successful(result)
        error = result.failure()
        assert isinstance(error, WeakPasswordError)
        assert "lowercase" in error.reason.lower()
        assert "lowercase letter" in error.missing_requirements

        # Should succeed with lowercase
        result = StrictPassword("Password123!")
        assert is_successful(result)

    def test_digit_requirement(self):
        """Test password with digit requirement."""

        class StrictPassword(Password):
            REQUIRE_DIGIT = True

        # Should fail without digit
        result = StrictPassword("Password!")
        assert not is_successful(result)
        error = result.failure()
        assert isinstance(error, WeakPasswordError)
        assert "digit" in error.reason.lower()
        assert "digit" in error.missing_requirements

        # Should succeed with digit
        result = StrictPassword("Password1!")
        assert is_successful(result)

    def test_special_char_requirement(self):
        """Test password with special character requirement."""

        class StrictPassword(Password):
            REQUIRE_SPECIAL = True

        # Should fail without special char
        result = StrictPassword("Password123")
        assert not is_successful(result)
        error = result.failure()
        assert isinstance(error, WeakPasswordError)
        assert "special" in error.reason.lower()
        assert "special character" in error.missing_requirements

        # Should succeed with special char
        result = StrictPassword("Password123!")
        assert is_successful(result)

    def test_all_requirements_combined(self):
        """Test password with all requirements enabled."""

        class VeryStrictPassword(Password):
            REQUIRE_UPPERCASE = True
            REQUIRE_LOWERCASE = True
            REQUIRE_DIGIT = True
            REQUIRE_SPECIAL = True

        # Should fail with missing requirements
        result = VeryStrictPassword("password")
        assert not is_successful(result)
        error = result.failure()
        assert isinstance(error, WeakPasswordError)
        assert len(error.missing_requirements) > 0

        # Should succeed with all requirements met
        result = VeryStrictPassword("Password123!")
        assert is_successful(result)

    def test_multiple_missing_requirements(self):
        """Test error message lists all missing requirements."""

        class StrictPassword(Password):
            REQUIRE_UPPERCASE = True
            REQUIRE_DIGIT = True
            REQUIRE_SPECIAL = True

        result = StrictPassword("password")
        assert not is_successful(result)
        error = result.failure()
        assert isinstance(error, WeakPasswordError)
        assert "uppercase letter" in error.missing_requirements
        assert "digit" in error.missing_requirements
        assert "special character" in error.missing_requirements


class TestPasswordStrengthCalculation:
    """Test password strength level calculation."""

    def test_weak_password_strength(self):
        """Test weak password identification."""
        result = Password("12345678")
        password = result.unwrap()
        assert password.strength == PasswordStrength.WEAK

    def test_medium_password_strength(self):
        """Test medium password identification."""
        result = Password("password123")
        password = result.unwrap()
        assert password.strength == PasswordStrength.MEDIUM

    def test_strong_password_strength(self):
        """Test strong password identification."""
        result = Password("Password123!")
        password = result.unwrap()
        assert password.strength == PasswordStrength.STRONG

    def test_very_strong_password_strength(self):
        """Test very strong password identification."""
        result = Password("MyVerySecureP@ssw0rd2024!")
        password = result.unwrap()
        assert password.strength == PasswordStrength.VERY_STRONG

    def test_strength_with_length_bonus(self):
        """Test that longer passwords get higher strength."""
        short_result = Password("Pass123!")
        long_result = Password("PassWord123!@#Extra")

        short_password = short_result.unwrap()
        long_password = long_result.unwrap()

        assert long_password.strength.value >= short_password.strength.value


class TestPasswordCharacterChecking:
    """Test password character type checking methods."""

    def test_has_uppercase(self):
        """Test uppercase letter detection."""
        result = Password("Password123")
        password = result.unwrap()
        assert password.has_uppercase() is True

        result = Password("password123")
        password = result.unwrap()
        assert password.has_uppercase() is False

    def test_has_lowercase(self):
        """Test lowercase letter detection."""
        result = Password("Password123")
        password = result.unwrap()
        assert password.has_lowercase() is True

        result = Password("PASSWORD123")
        password = result.unwrap()
        assert password.has_lowercase() is False

    def test_has_digit(self):
        """Test digit detection."""
        result = Password("Password123")
        password = result.unwrap()
        assert password.has_digit() is True

        result = Password("Password")
        password = result.unwrap()
        assert password.has_digit() is False

    def test_has_special_char(self):
        """Test special character detection."""
        result = Password("Password123!")
        password = result.unwrap()
        assert password.has_special_char() is True

        result = Password("Password123")
        password = result.unwrap()
        assert password.has_special_char() is False

    def test_various_special_characters(self):
        """Test detection of various special characters."""
        special_chars = "!@#$%^&*()_+-=[]{}';:\"\\|,.<>/?"
        for char in special_chars:
            result = Password(f"Password{char}")
            password = result.unwrap()
            assert password.has_special_char() is True, f"Failed for character: {char}"

    def test_meets_requirements_default(self):
        """Test meets_requirements with default (no requirements)."""
        result = Password("anypassword123")
        password = result.unwrap()
        assert password.meets_requirements() is True

    def test_meets_requirements_with_strict_policy(self):
        """Test meets_requirements with strict policy."""

        class StrictPassword(Password):
            REQUIRE_UPPERCASE = True
            REQUIRE_LOWERCASE = True
            REQUIRE_DIGIT = True
            REQUIRE_SPECIAL = True

        # This should fail validation, but we can test the logic
        result = StrictPassword("Password123!")
        password = result.unwrap()
        assert password.meets_requirements() is True


class TestPasswordSecurity:
    """Test security-related features of Password."""

    def test_password_string_is_masked(self):
        """Test that str(password) returns masked value."""
        result = Password("SecurePass123!")
        password = result.unwrap()
        assert str(password) == "********"

    def test_password_repr_is_safe(self):
        """Test that repr(password) doesn't expose password."""
        result = Password("SecurePass123!")
        password = result.unwrap()
        repr_str = repr(password)
        assert "SecurePass123!" not in repr_str
        assert "Password(" in repr_str
        assert "length=" in repr_str
        assert "strength=" in repr_str

    def test_password_value_property(self):
        """Test that .value property returns actual password."""
        result = Password("SecurePass123!")
        password = result.unwrap()
        # Direct access should work for internal use
        assert password.value == "SecurePass123!"

    def test_password_equality(self):
        """Test password equality comparison."""
        result1 = Password("SamePassword123")
        result2 = Password("SamePassword123")
        result3 = Password("DifferentPass123")

        password1 = result1.unwrap()
        password2 = result2.unwrap()
        password3 = result3.unwrap()

        assert password1 == password2
        assert password1 != password3

    def test_password_equality_with_non_password(self):
        """Test password equality with non-Password objects."""
        result = Password("SecurePass123!")
        password = result.unwrap()
        assert password != "SecurePass123!"
        assert password != 123
        assert password != None

    def test_password_hashable(self):
        """Test that passwords can be used in sets and dicts."""
        result1 = Password("Password123!")
        result2 = Password("Password456!")

        password1 = result1.unwrap()
        password2 = result2.unwrap()

        # Should be usable in sets
        password_set = {password1, password2}
        assert len(password_set) == 2

        # Should be usable as dict keys
        password_dict = {password1: "user1", password2: "user2"}
        assert len(password_dict) == 2

    def test_password_length_property(self):
        """Test password length property."""
        result = Password("12345678")
        password = result.unwrap()
        assert password.length == 8

        result = Password("VeryLongPassword123!")
        password = result.unwrap()
        assert password.length == 20


class TestPasswordEdgeCases:
    """Test edge cases and special scenarios."""

    def test_password_with_unicode(self):
        """Test password with unicode characters."""
        result = Password("Pässwörd123!")
        assert is_successful(result)
        password = result.unwrap()
        assert "ä" in password.value

    def test_password_with_emoji(self):
        """Test password with emoji characters."""
        result = Password("Password123!😀")
        assert is_successful(result)

    def test_password_all_same_character(self):
        """Test password with all same characters."""
        result = Password("aaaaaaaa")
        assert is_successful(result)
        password = result.unwrap()
        assert password.strength == PasswordStrength.WEAK

    def test_from_raw_bypasses_validation(self):
        """Test that from_raw creates password without validation."""
        # This would normally fail validation (too short)
        password = Password.from_raw("abc")
        assert password.value == "abc"
        assert password.length == 3

    def test_from_raw_with_whitespace(self):
        """Test from_raw allows whitespace that would normally be rejected."""
        password = Password.from_raw(" password ")
        assert password.value == " password "

    def test_password_with_only_spaces(self):
        """Test password with only spaces."""
        result = Password("        ")
        # Should fail due to whitespace trimming
        assert not is_successful(result)

    def test_empty_string_password(self):
        """Test empty string password."""
        result = Password("")
        assert not is_successful(result)
        error = result.failure()
        assert isinstance(error, EmptyStringError)


class TestPasswordCustomSubclasses:
    """Test creating custom password subclasses with different policies."""

    def test_custom_length_requirements(self):
        """Test custom password with different length requirements."""

        class LongPassword(Password):
            MIN_LENGTH = 16
            MAX_LENGTH = 64

        # Should fail with default length
        result = LongPassword("Password123!")
        assert not is_successful(result)

        # Should succeed with longer password
        result = LongPassword("VeryLongPassword123!Extra")
        assert is_successful(result)

    def test_custom_policy_password(self):
        """Test custom password with specific policy."""

        class CorporatePassword(Password):
            MIN_LENGTH = 12
            REQUIRE_UPPERCASE = True
            REQUIRE_LOWERCASE = True
            REQUIRE_DIGIT = True
            REQUIRE_SPECIAL = True

        # Should fail policy
        result = CorporatePassword("password")
        assert not is_successful(result)

        # Should pass policy
        result = CorporatePassword("Corp0rate!Pass")
        assert is_successful(result)

    def test_relaxed_policy_password(self):
        """Test password with relaxed requirements."""

        class RelaxedPassword(Password):
            MIN_LENGTH = 4
            MAX_LENGTH = 256

        result = RelaxedPassword("pass")
        assert is_successful(result)
