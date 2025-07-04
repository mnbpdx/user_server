# Proper HTTP Status Codes

**Story Points:** 3

## User Story
As a **developer**, I want the API to return proper HTTP status codes, so that client applications can handle errors appropriately.

## Acceptance Criteria
- [ ] Returns 422 Unprocessable Entity for validation errors
- [ ] Returns 409 Conflict for duplicate resource errors
- [ ] Returns 404 Not Found for non-existent resources
- [ ] Returns 400 Bad Request for malformed requests
- [ ] Returns 500 Internal Server Error only for actual server errors

## Technical Notes
- Update error handling in routes to use proper status codes
- Change validation errors from 400 to 422
- Add 409 handling for unique constraint violations
- Review and update all error responses
- Test error scenarios with correct status codes 