# Code Quality and Bloat Reduction

**Story Points:** 5

## User Story
As a **developer**, I want to reduce code bloat and improve maintainability, so that the codebase is cleaner, more consistent, and easier to work with.

## Acceptance Criteria
- [ ] Remove unused legacy code (`database.py`)
- [ ] Eliminate duplicate validation logic (service-layer vs database constraints)
- [ ] Extract common error handling patterns to reduce repetition
- [ ] Refactor `UserService` static methods for better design
- [ ] Add database unique constraints for username/email fields
- [ ] Create reusable validation utilities
- [ ] Verify all changes don't break existing functionality

## Technical Notes

### High Priority (Critical Issues)
1. **Remove `database.py`** - This file contains fake data that's completely unused
2. **Simplify constraint validation** - Currently checking uniqueness in both service layer AND catching database IntegrityError
3. **Add proper database constraints** - User model should have `unique=True` on username/email fields

### Medium Priority (Design Improvements)
4. **Refactor UserService** - Consider:
   - Making it a proper class with dependency injection
   - OR convert to standalone functions
   - Current static method pattern is awkward
5. **Extract error handling decorator** - The try/catch blocks in UserService are verbose and repetitive

### Low Priority (Nice to Have)
6. **Consolidate validation helpers** - The `_parse_json_body()` helper could be extracted to shared utilities
7. **Add database indexes** - For performance on username/email lookups (already in backlog)

## Implementation Strategy
1. **Start with removals** - Delete `database.py` and duplicate validation checks
2. **Add database constraints** - Update User model with `unique=True`
3. **Refactor service layer** - Decide on static methods vs instance methods vs functions
4. **Extract common patterns** - Create error handling decorator/utility
5. **Test thoroughly** - Ensure no regression in existing functionality

## Risk Assessment
- **Low risk** - Most changes are removals of unused code
- **Medium risk** - Database constraint changes need migration consideration
- **Testing required** - Full test suite must pass after changes

## Definition of Done
- [ ] All unused code removed
- [ ] Database constraints properly implemented
- [ ] Service layer simplified and consistent
- [ ] Error handling patterns consolidated
- [ ] All existing tests pass
- [ ] Code review completed
- [ ] No regression in API functionality