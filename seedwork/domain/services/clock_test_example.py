"""
Example test file demonstrating how to use the Clock abstraction for testing.

This file shows how to use FixedClock to control time in tests,
making them deterministic and easier to write.
"""

from datetime import datetime, timedelta

from seedwork.domain.services import FixedClock, reset_clock, set_clock, utcnow


def test_example_with_fixed_clock():
    """Example test showing how to use FixedClock for deterministic tests."""

    # Arrange: Set up a fixed time for testing
    fixed_time = datetime(2024, 1, 15, 12, 0, 0)
    test_clock = FixedClock(fixed_time)
    set_clock(test_clock)

    try:
        # Act: Use utcnow() in your code - it will return the fixed time
        current_time = utcnow()

        # Assert: Time is predictable
        assert current_time == fixed_time

        # You can advance time in tests
        future_time = fixed_time + timedelta(hours=1)
        test_clock.set_time(future_time)

        new_time = utcnow()
        assert new_time == future_time

    finally:
        # Cleanup: Always reset the clock after tests
        reset_clock()


def test_user_creation_with_fixed_clock():
    """
    Example showing how to test User entity with controlled time.

    This would be used in actual tests like:

    from generic.iam.domain.entities.user import User
    from seedwork.domain.services import FixedClock, set_clock, reset_clock

    def test_user_timestamps():
        # Arrange
        fixed_time = datetime(2024, 1, 15, 10, 30, 0)
        set_clock(FixedClock(fixed_time))

        try:
            # Act
            user = User.create(
                email="test@example.com",
                username="testuser",
                hashed_password="hashed_password_here"
            )

            # Assert - timestamps are predictable
            assert user.created_at == fixed_time
            assert user.updated_at == fixed_time

            # Simulate time passing
            new_time = fixed_time + timedelta(days=1)
            get_clock().set_time(new_time)

            # Update user
            user.change_email("newemail@example.com")

            # Assert - updated_at changed, created_at didn't
            assert user.created_at == fixed_time
            assert user.updated_at == new_time

        finally:
            reset_clock()
    """
    pass


def test_multiple_operations_with_time_control():
    """Example showing multiple operations with time control."""

    # Start at a known time
    start_time = datetime(2024, 1, 1, 0, 0, 0)
    test_clock = FixedClock(start_time)
    set_clock(test_clock)

    try:
        # Simulate a sequence of events over time
        times = []

        # Event 1: Initial action
        times.append(utcnow())

        # Advance 1 hour
        test_clock.set_time(start_time + timedelta(hours=1))
        times.append(utcnow())

        # Advance 1 day
        test_clock.set_time(start_time + timedelta(days=1))
        times.append(utcnow())

        # Verify the timeline
        assert times[0] == start_time
        assert times[1] == start_time + timedelta(hours=1)
        assert times[2] == start_time + timedelta(days=1)

    finally:
        reset_clock()


if __name__ == "__main__":
    print("Running clock test examples...")

    test_example_with_fixed_clock()
    print("✓ test_example_with_fixed_clock passed")

    test_user_creation_with_fixed_clock()
    print("✓ test_user_creation_with_fixed_clock passed")

    test_multiple_operations_with_time_control()
    print("✓ test_multiple_operations_with_time_control passed")

    print("\nAll examples passed! You can now use these patterns in your tests.")
