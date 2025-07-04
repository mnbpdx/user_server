# Email Format Validation

**Story Points:** 3

## User Story
As a **user**, I want the system to validate email addresses when I create or update a user account, so that only valid email formats are accepted.

## Acceptance Criteria
- [ ] Email field rejects invalid formats (e.g., "invalid_email", "test@", "@example.com")
- [ ] Email field accepts valid formats (e.g., "user@example.com", "test+tag@domain.co.uk")
- [ ] Returns clear error message for invalid email formats
- [ ] Uses Pydantic EmailStr type for validation

## Technical Notes
- Update UserCreateSchema to use EmailStr instead of str
- Add email validation to UserUpdateSchema when created
- Test with various valid/invalid email formats 