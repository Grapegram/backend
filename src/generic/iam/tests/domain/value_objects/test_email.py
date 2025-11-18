import pytest
from returns.pipeline import is_successful

from src.generic.iam.domain.value_objects.email import Email, InvalidEmailError


class TestEmailValidation:
    """Test suite for Email value object validation."""

    def test_valid_email_creation(self):
        """Test creating a valid email address."""
        result = Email("user@example.com")
        assert is_successful(result)
        email = result.unwrap()
        assert email == Email.from_raw("user@example.com")

    def test_email_normalization_lowercase(self):
        """Test that email addresses are normalized to lowercase."""
        result = Email("User@Example.COM")
        assert is_successful(result)
        email = result.unwrap()
        assert email == Email.from_raw("user@example.com")

    def test_email_strips_whitespace(self):
        """Test that leading/trailing whitespace is stripped."""
        result = Email("  user@example.com  ")
        assert is_successful(result)
        email = result.unwrap()
        assert email == Email.from_raw("user@example.com")

    def test_valid_email_with_special_characters(self):
        """Test email with valid special characters in local part."""
        valid_emails = [
            "user.name@example.com",
            "user+tag@example.com",
            "user_name@example.com",
            "first.last@example.com",
            "user123@example.com",
            "test!#$%&'*+/=?^_`{|}~@example.com",
        ]
        for email_str in valid_emails:
            result = Email(email_str)
            assert is_successful(result), f"Failed for: {email_str}"

    def test_valid_email_with_subdomain(self):
        """Test email with subdomain."""
        result = Email("user@mail.example.com")
        assert is_successful(result)
        email = result.unwrap()
        assert email == Email.from_raw("user@mail.example.com")

    def test_valid_email_with_multiple_subdomains(self):
        """Test email with multiple subdomains."""
        result = Email("user@mail.server.example.com")
        assert is_successful(result)

    def test_empty_email_string(self):
        """Test that empty string fails validation."""
        result = Email("")
        assert not is_successful(result)
        error = result.failure()
        assert isinstance(error, InvalidEmailError)
        assert "Email cannot be empty" in str(error)

    def test_none_value(self):
        """Test that None fails validation."""
        result = Email(None)
        assert not is_successful(result)
        error = result.failure()
        assert isinstance(error, InvalidEmailError)

    def test_missing_at_symbol(self):
        """Test that email without @ symbol fails."""
        result = Email("userexample.com")
        assert not is_successful(result)
        error = result.failure()
        assert isinstance(error, InvalidEmailError)
        assert "Email must contain @ symbol" in str(error)

    def test_multiple_at_symbols(self):
        """Test that email with multiple @ symbols fails."""
        result = Email("user@@example.com")
        assert not is_successful(result)
        error = result.failure()
        assert isinstance(error, InvalidEmailError)

    def test_empty_local_part(self):
        """Test that email with empty local part fails."""
        result = Email("@example.com")
        assert not is_successful(result)
        error = result.failure()
        assert isinstance(error, InvalidEmailError)
        assert "Local part cannot be empty" in str(error)

    def test_empty_domain_part(self):
        """Test that email with empty domain fails."""
        result = Email("user@")
        assert not is_successful(result)
        error = result.failure()
        assert isinstance(error, InvalidEmailError)
        assert "Domain part cannot be empty" in str(error)

    def test_domain_without_dot(self):
        """Test that domain without dot fails."""
        result = Email("user@example")
        assert not is_successful(result)
        error = result.failure()
        assert isinstance(error, InvalidEmailError)
        assert "Domain must contain at least one dot" in str(error)

    def test_local_part_too_long(self):
        """Test that local part exceeding 64 characters fails."""
        long_local = "a" * 65
        result = Email(f"{long_local}@example.com")
        assert not is_successful(result)
        error = result.failure()
        assert isinstance(error, InvalidEmailError)
        assert "Local part too long" in str(error)

    def test_local_part_max_length(self):
        """Test that local part at exactly 64 characters succeeds."""
        local = "a" * 64
        result = Email(f"{local}@example.com")
        assert is_successful(result)

    def test_domain_too_long(self):
        """Test that domain exceeding 255 characters fails."""
        long_domain = "a" * 252 + ".com"
        result = Email(f"user@{long_domain}")
        assert not is_successful(result)
        error = result.failure()
        assert isinstance(error, InvalidEmailError)
        assert "Domain part too long" in str(error)

    def test_domain_max_length(self):
        """Test that domain at exactly 255 characters succeeds."""
        # Create a domain that's exactly 255 chars
        domain = "a" * 251 + ".com"
        result = Email(f"user@{domain}")
        assert is_successful(result)

    def test_total_email_too_long(self):
        """Test that total email exceeding 320 characters fails."""
        local = "a" * 66
        domain = "b" * 250 + ".com"
        result = Email(f"{local}@{domain}")
        assert not is_successful(result)
        error = result.failure()
        assert isinstance(error, InvalidEmailError)
        assert "Email too long" in str(error)

    def test_invalid_characters_in_local_part(self):
        """Test that invalid characters in local part fail."""
        invalid_emails = [
            "user name@example.com",  # space
            "user@name@example.com",  # @ in local
            "user(comment)@example.com",  # parentheses
            "user[bracket]@example.com",  # brackets
        ]
        for email_str in invalid_emails:
            result = Email(email_str)
            assert not is_successful(result), f"Should fail for: {email_str}"

    def test_invalid_domain_format(self):
        """Test invalid domain formats."""
        invalid_emails = [
            "user@.example.com",  # starts with dot
            "user@example..com",  # double dot
            "user@example.com.",  # ends with dot
            "user@-example.com",  # starts with hyphen
            "user@example-.com",  # ends with hyphen
        ]
        for email_str in invalid_emails:
            result = Email(email_str)
            assert not is_successful(result), f"Should fail for: {email_str}"


class TestEmailProperties:
    """Test suite for Email value object properties."""

    def test_local_part_property(self):
        """Test extracting local part from email."""
        email = Email("user@example.com").unwrap()
        assert email.local_part == "user"

    def test_domain_property(self):
        """Test extracting domain from email."""
        email = Email("user@example.com").unwrap()
        assert email.domain == "example.com"

    def test_normalized_property(self):
        """Test normalized property returns lowercase email."""
        email = Email("User@Example.COM").unwrap()
        assert email.normalized == "user@example.com"

    def test_local_part_with_special_chars(self):
        """Test local part extraction with special characters."""
        email = Email("user.name+tag@example.com").unwrap()
        assert email.local_part == "user.name+tag"

    def test_domain_with_subdomain(self):
        """Test domain extraction with subdomain."""
        email = Email("user@mail.example.com").unwrap()
        assert email.domain == "mail.example.com"


class TestEmailEquality:
    """Test suite for Email equality comparisons."""

    def test_equal_emails(self):
        """Test that identical emails are equal."""
        email1 = Email("user@example.com").unwrap()
        email2 = Email("user@example.com").unwrap()
        assert email1 == email2

    def test_equal_emails_different_case(self):
        """Test that emails with different cases are equal."""
        email1 = Email("User@Example.com").unwrap()
        email2 = Email("user@example.com").unwrap()
        assert email1 == email2

    def test_equal_emails_with_whitespace(self):
        """Test that emails with different whitespace are equal after normalization."""
        email1 = Email("  user@example.com  ").unwrap()
        email2 = Email("user@example.com").unwrap()
        assert email1 == email2

    def test_not_equal_emails(self):
        """Test that different emails are not equal."""
        email1 = Email("user1@example.com").unwrap()
        email2 = Email("user2@example.com").unwrap()
        assert email1 != email2

    def test_equal_to_string(self):
        """Test comparison with string."""
        email = Email("user@example.com").unwrap()
        assert email == "user@example.com"

    def test_equal_to_string_different_case(self):
        """Test comparison with string in different case."""
        email = Email("user@example.com").unwrap()
        assert email == "USER@EXAMPLE.COM"

    def test_not_equal_to_different_string(self):
        """Test not equal to different string."""
        email = Email("user@example.com").unwrap()
        assert email != "other@example.com"

    def test_not_equal_to_non_string(self):
        """Test not equal to non-string types."""
        email = Email("user@example.com").unwrap()
        assert email != 123
        assert email != None
        assert email != []


class TestEmailValidateMethod:
    """Test suite for Email.validate() class method."""

    def test_validate_returns_result(self):
        """Test that validate returns a Result type."""
        result = Email.validate("user@example.com")
        assert is_successful(result)

    def test_validate_success_contains_normalized_email(self):
        """Test that successful validation returns normalized email string."""
        result = Email.validate("User@Example.COM")
        assert is_successful(result)
        normalized = result.unwrap()
        assert normalized == "user@example.com"
        assert isinstance(normalized, str)

    def test_validate_failure_contains_error(self):
        """Test that failed validation returns InvalidEmailError."""
        result = Email.validate("invalid")
        assert not is_successful(result)
        error = result.failure()
        assert isinstance(error, InvalidEmailError)

    def test_validate_preserves_original_email_in_error(self):
        """Test that error contains original email string."""
        original = "Invalid@Email"
        result = Email.validate(original)
        if not is_successful(result):
            error = result.failure()
            assert error.email == original


class TestEmailEdgeCases:
    """Test suite for Email edge cases."""

    def test_email_with_numbers(self):
        """Test email with numbers."""
        result = Email("user123@example456.com")
        assert is_successful(result)

    def test_email_with_hyphens_in_domain(self):
        """Test email with hyphens in domain."""
        result = Email("user@my-domain.com")
        assert is_successful(result)

    def test_email_with_multiple_dots_in_local(self):
        """Test email with multiple dots in local part."""
        result = Email("user.name.test@example.com")
        assert is_successful(result)

    def test_single_character_local_part(self):
        """Test email with single character local part."""
        result = Email("a@example.com")
        assert is_successful(result)

    def test_single_character_domain_labels(self):
        """Test email with single character domain labels."""
        result = Email("user@a.b.com")
        assert is_successful(result)

    def test_numeric_tld(self):
        """Test email with numeric in TLD."""
        result = Email("user@example.com2")
        assert is_successful(result)

    def test_plus_addressing(self):
        """Test plus addressing (email tags)."""
        result = Email("user+tag@example.com")
        assert is_successful(result)
        email = result.unwrap()
        assert email.local_part == "user+tag"


class TestInvalidEmailError:
    """Test suite for InvalidEmailError exception."""

    def test_error_has_email_attribute(self):
        """Test that error contains email attribute."""
        result = Email("invalid")
        error = result.failure()
        assert hasattr(error, "email")
        assert error.email == "invalid"

    def test_error_has_reason_attribute(self):
        """Test that error contains reason attribute."""
        result = Email("invalid")
        error = result.failure()
        assert hasattr(error, "reason")
        assert isinstance(error.reason, str)

    def test_error_message_format(self):
        """Test that error message is properly formatted."""
        result = Email("invalid")
        error = result.failure()
        error_str = str(error)
        assert "invalid" in error_str
        assert "Invalid email" in error_str

    def test_error_is_frozen(self):
        """Test that error is immutable."""
        result = Email("invalid")
        error = result.failure()
        with pytest.raises(Exception):  # FrozenInstanceError
            error.email = "changed"
