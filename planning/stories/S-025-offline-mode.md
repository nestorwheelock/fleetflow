# S-025: Offline Mode & Sync

**Story Type**: User Story
**Priority**: Medium
**Estimate**: 3 days
**Sprint**: Epoch 4
**Status**: PENDING

## User Story
**As a** customer
**I want to** access my rental info without internet
**So that** I can see my booking details anywhere

## Acceptance Criteria
- [ ] Current rental details available offline
- [ ] Contract PDF downloadable and viewable offline
- [ ] Last known vehicle location shown offline
- [ ] Syncs automatically when back online
- [ ] Clear indicator when viewing cached data
- [ ] Offline access to emergency contact numbers

## Definition of Done
- [ ] Offline data persistence with AsyncStorage
- [ ] Contract PDF download and local storage
- [ ] Offline indicator UI component
- [ ] Background sync when connectivity restored
- [ ] Conflict resolution for any offline changes
- [ ] Emergency info always cached
- [ ] Tests written and passing (>95% coverage)
- [ ] Documentation updated

## Related Tasks
- T-115: Offline data persistence (AsyncStorage)
- T-116: Contract PDF download and storage
- T-117: Offline indicator UI
- T-118: Background sync when online
- T-119: Conflict resolution for synced data

## Notes
- Cache current and next upcoming rental
- PDF stored in app documents directory
- Banner shows "Viewing cached data" when offline
- Sync on app foreground if stale (>5 minutes)
- Emergency numbers: Roadside assist, rental office
