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

#### ✅ GOOD - Docstring Adds Value
```python
def change_password(self, new_hashed_password: str) -> Result[None, Exception]:
    """
    Change user password with business rule validation.
    
    Business Rules:
    - New password must be different from previous password
    - Password change triggers re-authentication requirement
    - Emits UserUpdated event
    
    Example:
        >>> user.change_password("new_hash").unwrap()
        >>> assert user.requires_reauth is True
    """
    password_vo = HashedPassword(new_hashed_password)
    self.check_rule(
        NewPasswordMustBeDifferentFromPreviousPassword(
            prev_password=self.hashed_password, 
            new_password=password_vo
        )
    ).unwrap()
    self.hashed_password = password_vo
    self.requires_reauth = True
    self.register_event(UserUpdated(user_id=self.id, updated_at=self.updated_at))
```

## Code Quality Principles

1. **Type hints are documentation** - Use them instead of docstrings
2. **Clear naming > comments** - Self-documenting code is preferred
3. **DRY for docs too** - Don't repeat type information in docstrings
4. **Document why, not what** - Code shows what, docs should explain why
5. **Business rules deserve docs** - Complex domain logic needs explanation

## When in Doubt

Ask yourself: "Does this docstring tell me something I can't already see from the signature and name?"

If the answer is NO, don't add it.
