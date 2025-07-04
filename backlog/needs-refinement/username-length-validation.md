# Username Length Validation

**Story Points:** 2

## User Story
As a **user**, I want the system to validate username length when creating or updating users, so that usernames meet minimum requirements.

## Acceptance Criteria
- [ ] Username field rejects empty strings
- [ ] Username field rejects usernames shorter than 3 characters
- [ ] Username field accepts usernames 3-50 characters
- [ ] Returns clear error message for invalid username lengths

## Technical Notes
- Update UserCreateSchema username field with Field(min_length=3, max_length=50)
- Add validation to UserUpdateSchema when created
- Test empty string, 2-char, 3-char, 50-char, 51-char usernames 