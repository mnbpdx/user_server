# Role-Based Permissions

**Story Points:** 5

## User Story
As a **system administrator**, I want different user roles to have different permissions, so that access is controlled based on user roles.

## Acceptance Criteria
- [ ] Admin users can perform all CRUD operations
- [ ] Manager users can read and update but not delete
- [ ] Regular users can only read their own data
- [ ] Returns 403 Forbidden for unauthorized actions
- [ ] Role-based access control decorators

## Technical Notes
- Create role-based permission decorators
- Add @require_role decorator for endpoints
- Extract user role from JWT token
- Implement role hierarchy and permissions
- Test access control for different roles 