# Enhanced Health Check

**Story Points:** 3

## User Story
As a **system administrator**, I want a comprehensive health check endpoint, so that I can monitor system health and dependencies.

## Acceptance Criteria
- [ ] Returns JSON instead of plain text
- [ ] Includes database connectivity status
- [ ] Includes system information (version, uptime)
- [ ] Includes dependency status checks
- [ ] Returns appropriate HTTP status codes
- [ ] Includes performance metrics

## Technical Notes
- Update /health endpoint to return JSON
- Add database connection health check
- Include application version and build info
- Add dependency health checks (Redis, etc.)
- Return 200 OK when healthy, 503 when unhealthy
- Include response time and system metrics 