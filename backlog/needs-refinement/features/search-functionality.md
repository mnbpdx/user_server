# Search Functionality

**Story Points:** 5

## User Story
As a **user**, I want to be able to search for users by username or email, so that I can quickly find specific users.

## Acceptance Criteria
- [ ] GET /api/users/search?q={query} endpoint searches users
- [ ] Searches across username and email fields
- [ ] Case-insensitive search
- [ ] Returns users matching the search query
- [ ] Works with pagination
- [ ] Returns empty list if no matches found

## Technical Notes
- Add search route to users blueprint
- Implement SQL LIKE or full-text search
- Search across username and email fields
- Integrate with existing pagination
- Test with various search terms and edge cases 