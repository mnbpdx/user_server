# Pagination for User Lists

**Story Points:** 5

## User Story
As a **user**, I want to be able to paginate through user lists, so that large datasets don't slow down the application.

## Acceptance Criteria
- [ ] GET /api/users supports ?page={page}&limit={limit} parameters
- [ ] Default page size is 20 users
- [ ] Maximum page size is 100 users
- [ ] Returns pagination metadata (total, pages, current_page, etc.)
- [ ] Works with existing role filtering
- [ ] Returns 400 Bad Request for invalid pagination parameters

## Technical Notes
- Add pagination parameters to GET /api/users route
- Update UserResponseSchema to include pagination metadata
- Implement SQL LIMIT/OFFSET for pagination
- Test with various page sizes and edge cases
- Ensure pagination works with role filtering 