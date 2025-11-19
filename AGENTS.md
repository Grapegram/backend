# Guidelines for LLM Agents Working on This Codebase

## Documentation Standards

### Docstrings - When to Use

**❌ DO NOT add docstrings that simply duplicate information already clear from:**

- Function/method names
- Parameter names and type hints
- Return type annotations

**✅ DO add docstrings when you need to explain:**

- Complex business rules
- Non-obvious behavior or side effects
- Complex algorithms or logic
- Usage examples for complicated APIs
- Important constraints or preconditions
- Domain-specific concepts

### Examples

#### ❌ BAD - Redundant Docstring

```python
def get_user_by_id(user_id: UserId) -> User | None:
    """
    Get a user by their ID.

    Args:
        user_id: The user ID

    Returns:
        User if found, None otherwise
    """
    return self.repository.find_by_id(user_id)
```

#### ✅ GOOD - No Docstring Needed

```python
def get_user_by_id(user_id: UserId) -> User | None:
    return self.repository.find_by_id(user_id)
```

## Code Quality Principles

1. **Type hints are documentation** - Use them instead of docstrings
2. **Clear naming > comments** - Self-documenting code is preferred
3. **DRY for docs too** - Don't repeat type information in docstrings
4. **Document why, not what** - Code shows what, docs should explain why
5. **Business rules deserve docs** - Complex domain logic needs explanation

## Error Handling with Result Containers

### ❌ DO NOT raise exceptions in domain layer

```python
def change_email(self, new_email: str) -> None:
    email_vo = Email(new_email)
    if self.email == email_vo:
        raise ValueError("New email must be different from previous email")
    self.email = email_vo
```

### ✅ DO use Result containers

```python
from returns.result import Result
from seedwork.returns import catch_unwrap

@catch_unwrap
def change_email(
    self, new_email: str
) -> Result[None, NewEmailMustBeDifferentFromPreviousEmail | VOValidationException]:
    email_vo = Email(new_email).unwrap()
    self.check_rule(
        NewEmailMustBeDifferentFromPreviousEmail(prev_email=self.email, new_email=email_vo)
    ).unwrap()
    self.email = email_vo
    self.is_verified = False  # Require re-verification

    self.register_event(
        UserUpdated(
            user_id=self.id,
            updated_at=self.updated_at,
        )
    )
```

### Key Points

1. **Always return `Result[T, E]`** for operations that can fail in domain layer
2. **Use `@catch_unwrap` decorator** to automatically wrap exceptions into Result
3. **Use `.unwrap()`** to extract values from Result (will be caught by decorator)
4. **Use union types in return annotation** to specify all possible error types: `Result[None, ErrorType1 | ErrorType2]`
5. **Factory methods return Result**: `Result[Self, VOValidationException]`
6. **Business operations return Result**: `Result[None, BusinessRuleException | VOValidationException]`

### Pattern Examples

#### Create Factory Method

```python
@classmethod
def create(
    cls,
    email: str,
    username: str,
    hashed_password: str,
) -> Result[Self, VOValidationException]:
    user_id = UserId.next_id()
    email_vo = Email(email).unwrap()
    hashed_password_vo = HashedPassword(hashed_password).unwrap()
    now = utcnow()

    user = cls(
        id=user_id,
        email=email_vo,
        username=username,
        hashed_password=hashed_password_vo,
    )

    user.register_event(
        UserCreated(
            user_id=user_id,
            email=email,
            username=username,
            created_at=now,
        )
    )

    return user
```

#### Business Operation with Rule Checking

```python
@catch_unwrap
def change_password(
    self, new_hashed_password: str
) -> Result[None, NewPasswordMustBeDifferentFromPreviousPassword | VOValidationException]:
    password_vo = HashedPassword(new_hashed_password)
    self.check_rule(
        NewPasswordMustBeDifferentFromPreviousPassword(
            prev_password=self.hashed_password, new_password=password_vo
        )
    ).unwrap()
    self.hashed_password = password_vo

    self.register_event(
        UserUpdated(
            user_id=self.id,
            updated_at=self.updated_at,
        )
    )
```

#### Simple State Changes (No Result Needed)

```python
def deactivate(self) -> None:
    if not self.is_active:
        return

    self.is_active = False

    self.register_event(
        UserDeactivated(
            user_id=self.id,
            deactivated_at=self.updated_at,
        )
    )
```

## When in Doubt

Ask yourself: "Does this docstring tell me something I can't already see from the signature and name?"

If the answer is NO, don't add it.
