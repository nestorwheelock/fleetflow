# S-023: Trip Sharing for Safety

**Story Type**: User Story
**Priority**: Medium
**Estimate**: 4 days
**Sprint**: Epoch 4
**Status**: PENDING

## User Story
**As a** customer
**I want to** share my trip with family members
**So that** they know where I am for safety

## Acceptance Criteria
- [ ] Can create shareable trip link
- [ ] Family can view live location without installing app
- [ ] Can set trip sharing to auto-expire (1hr, 4hr, 8hr, custom)
- [ ] Can revoke sharing at any time
- [ ] Shared view shows vehicle location, speed, ETA
- [ ] Can share via SMS, email, or messaging apps
- [ ] Privacy: Only shares during active sharing session

## Definition of Done
- [ ] Trip sharing backend API
- [ ] Unique shareable link generation
- [ ] Web-based shared trip viewer
- [ ] Sharing controls in mobile app
- [ ] Expiration and revocation logic
- [ ] Native share sheet integration
- [ ] Tests written and passing (>95% coverage)
- [ ] Documentation updated

## Related Tasks
- T-103: Trip sharing backend API
- T-104: Share link generation
- T-105: Web-based shared trip viewer
- T-106: Sharing controls in app
- T-107: Expiration and revocation logic
- T-108: Native share sheet integration

## Notes
- Share links are unique tokens (not guessable)
- Web viewer works without login
- Shows: Map, vehicle marker, speed, last update time
- Auto-expires to protect privacy
- Viewer shows app download prompt
