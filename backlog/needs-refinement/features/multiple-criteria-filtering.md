# Multiple Criteria Filtering

**Story Points:** 5

## User Story
As a **user**, I want to be able to filter users by multiple criteria (role, age range, etc.), so that I can find users meeting specific conditions.

## Acceptance Criteria
- [ ] GET /api/users supports multiple query parameters
- [ ] Filter by role: ?role={role}
- [ ] Filter by age range: ?age_min={min}&age_max={max}
- [ ] Combine multiple filters (role + age range)
- [ ] Works with pagination and search
- [ ] Returns filtered results matching all criteria

## Technical Notes
- Add query parameter parsing to GET /api/users
- Implement SQL WHERE clauses for each filter
- Handle combination of multiple filters
- Integrate with existing pagination
- Test various filter combinations 