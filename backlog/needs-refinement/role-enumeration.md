# Role Enumeration

**Story Points:** 3

## User Story
As a **user**, I want the system to only accept predefined roles when creating or updating users, so that role values are consistent and valid.

## Acceptance Criteria
- [ ] Role field only accepts "admin", "user", or "manager"
- [ ] Role field rejects invalid values (e.g., "invalid_role", "superuser")
- [ ] Returns clear error message for invalid roles
- [ ] Role validation is case-sensitive

## Technical Notes
- Create RoleEnum class with ADMIN, USER, MANAGER values
- Update UserCreateSchema role field to use RoleEnum
- Add validation to UserUpdateSchema when created
- Test all valid roles and various invalid ones 