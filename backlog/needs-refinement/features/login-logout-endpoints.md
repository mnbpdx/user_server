# Login/Logout Endpoints

**Story Points:** 3

## User Story
As a **user**, I want to be able to login and logout, so that I can authenticate and manage my session.

## Acceptance Criteria
- [ ] POST /api/auth/login endpoint for authentication
- [ ] POST /api/auth/logout endpoint for session termination
- [ ] Returns JWT token on successful login
- [ ] Validates username/email and password
- [ ] Handles invalid credentials gracefully

## Technical Notes
- Add authentication routes blueprint
- Implement password hashing and verification
- Generate JWT tokens on successful login
- Add token blacklisting for logout (optional)
- Test login/logout flow and error cases 