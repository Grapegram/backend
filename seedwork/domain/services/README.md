# Domain Services

This directory contains domain services that support domain logic without being entities or value objects themselves.

## Clock Service

The Clock service provides an abstraction for datetime operations, making your domain entities testable and time-independent.

### Why Use Clock Abstraction?

When domain entities use `datetime.utcnow()` directly, tests become:
- **Non-deterministic**: Tests that depend on current time may fail at different times
- **Hard to control**: You can't easily test time-dependent business logic
- **Difficult to debug**: Time-based bugs are hard to reproduce

The Clock abstraction solves these problems by allowing you to control time in tests.

### Usage in Domain Entities

Instead of using `datetime.utcnow()` directly:

```python
# ❌ Don't do this
from datetime import datetime

class User:
    def __init__(self):
        self.created_at = datetime.utcnow()  # Hard to test!
```

Use the `utcnow()` function from the clock service:

```python
# ✅ Do this
from seedwork.domain.services import utcnow

class User:
    def __init__(self):
        self.created_at = utcnow()  # Testable!
```

### Clock Implementations

#### SystemClock (Production)

The default implementation that uses real system time:

```python
from seedwork.domain.services import SystemClock

clock = SystemClock()
now = clock.now()  # Returns datetime.utcnow()
```

#### FixedClock (Testing)

A clock that returns a fixed time, perfect for testing:

```python
from datetime import datetime
from seedwork.domain.services import FixedClock

# Create a clock frozen at a specific time
clock = FixedClock(datetime(2024, 1, 15, 10, 30, 0))
now = clock.now()  # Always returns 2024-01-15 10:30:00

# Advance time in tests
clock.set_time(datetime(2024, 1, 15, 11, 30, 0))
now = clock.now()  # Now returns 2024-01-15 11:30:00
```

### Global Clock Configuration

The module provides a global clock instance that can be configured:

```python
from seedwork.domain.services import set_clock, get_clock, reset_clock, FixedClock
from datetime import datetime

# Set a custom clock (e.g., in test setup)
test_clock = FixedClock(datetime(2024, 1, 1, 0, 0, 0))
set_clock(test_clock)

# Use the global clock through utcnow()
from seedwork.domain.services import utcnow
current_time = utcnow()  # Returns 2024-01-01 00:00:00

# Reset to SystemClock (e.g., in test teardown)
reset_clock()
```

### Testing Examples

#### Basic Test with Fixed Time

```python
from datetime import datetime
from seedwork.domain.services import FixedClock, set_clock, reset_clock

def test_user_creation():
    # Arrange: Set up fixed time
    fixed_time = datetime(2024, 1, 15, 10, 30, 0)
    set_clock(FixedClock(fixed_time))
    
    try:
        # Act: Create user (internally uses utcnow())
        user = User.create(email="test@example.com", username="testuser")
        
        # Assert: Time is predictable
        assert user.created_at == fixed_time
        assert user.updated_at == fixed_time
    finally:
        # Cleanup: Always reset clock
        reset_clock()
```

#### Testing Time-Dependent Logic

```python
from datetime import datetime, timedelta
from seedwork.domain.services import FixedClock, set_clock, reset_clock, get_clock

def test_user_login_tracking():
    # Start at a known time
    start_time = datetime(2024, 1, 1, 10, 0, 0)
    clock = FixedClock(start_time)
    set_clock(clock)
    
    try:
        # Create user
        user = User.create(email="test@example.com", username="testuser")
        assert user.last_login_at is None
        
        # Simulate first login
        user.record_login()
        assert user.last_login_at == start_time
        
        # Advance time by 1 hour
        new_time = start_time + timedelta(hours=1)
        clock.set_time(new_time)
        
        # Simulate second login
        user.record_login()
        assert user.last_login_at == new_time
    finally:
        reset_clock()
```

#### Pytest Fixture

Create a reusable pytest fixture:

```python
import pytest
from datetime import datetime
from seedwork.domain.services import FixedClock, set_clock, reset_clock

@pytest.fixture
def fixed_clock():
    """Provides a FixedClock for testing."""
    clock = FixedClock(datetime(2024, 1, 1, 0, 0, 0))
    set_clock(clock)
    yield clock
    reset_clock()

# Use in tests
def test_with_fixture(fixed_clock):
    user = User.create(email="test@example.com", username="testuser")
    assert user.created_at == datetime(2024, 1, 1, 0, 0, 0)
    
    # Advance time
    fixed_clock.set_time(datetime(2024, 1, 2, 0, 0, 0))
    user.record_login()
    assert user.last_login_at == datetime(2024, 1, 2, 0, 0, 0)
```

### Best Practices

1. **Always use `utcnow()` in domain entities**: Never use `datetime.utcnow()` directly
2. **Reset clock in tests**: Use `reset_clock()` in teardown or `finally` blocks
3. **Use UTC**: All times should be in UTC to avoid timezone issues
4. **Consider fixtures**: Create reusable test fixtures for clock management
5. **Document time dependencies**: If business logic depends on time, document it clearly

### API Reference

#### Functions

- `utcnow() -> datetime`: Get current UTC datetime from the configured clock
- `get_clock() -> Clock`: Get the current global clock instance
- `set_clock(clock: Clock) -> None`: Set the global clock instance
- `reset_clock() -> None`: Reset to SystemClock

#### Classes

- `Clock`: Abstract base class for clock implementations
- `SystemClock`: Production clock using real system time
- `FixedClock`: Test clock with controllable fixed time

### Migration Guide

If you have existing code using `datetime.utcnow()`:

1. Import the clock service:
   ```python
   from seedwork.domain.services import utcnow
   ```

2. Replace all `datetime.utcnow()` calls:
   ```python
   # Before
   self.created_at = datetime.utcnow()
   
   # After
   self.created_at = utcnow()
   ```

3. Update your tests to use `FixedClock`:
   ```python
   from seedwork.domain.services import FixedClock, set_clock, reset_clock
   
   def test_something():
       set_clock(FixedClock(datetime(2024, 1, 1)))
       try:
           # Your test code
           pass
       finally:
           reset_clock()
   ```

That's it! Your code is now fully testable with controllable time.
