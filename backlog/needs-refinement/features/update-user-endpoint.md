# Update User Endpoint

**Story Points:** 5

## User Story
As a **user**, I want to be able to update existing user information, so that user data can be modified without creating new records.

## Acceptance Criteria
- [ ] PUT /api/users/{id} endpoint updates entire user record
- [ ] PATCH /api/users/{id} endpoint updates partial user record  
- [ ] Returns 200 OK with updated user data
- [ ] Returns 404 Not Found for non-existent user IDs
- [ ] Validates updated data using existing validation rules
- [ ] Respects unique constraints (email, username)

## Technical Notes
- Create UserUpdateSchema for validation
- Add PUT/PATCH routes to users blueprint
- Handle partial updates for PATCH requests
- Test full and partial update scenarios
- Ensure validation works for updates 