# Delete User Endpoint

**Story Points:** 3

## User Story
As a **user**, I want to be able to delete users from the system, so that unused accounts can be removed.

## Acceptance Criteria
- [ ] DELETE /api/users/{id} endpoint removes user
- [ ] Returns 204 No Content on successful deletion
- [ ] Returns 404 Not Found for non-existent user IDs
- [ ] User is completely removed from database
- [ ] Cannot retrieve deleted user via GET requests

## Technical Notes
- Add DELETE route to users blueprint
- Implement hard delete (remove from database)
- Add proper error handling for non-existent users
- Test deletion and subsequent GET requests