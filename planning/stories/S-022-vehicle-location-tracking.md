# S-022: Real-Time Vehicle Location Tracking

**Story Type**: User Story
**Priority**: High
**Estimate**: 5 days
**Sprint**: Epoch 4
**Status**: PENDING

## User Story
**As a** customer
**I want to** see where my rented vehicle is on a map
**So that** I can find it in a parking lot or if it's stolen

## Acceptance Criteria
- [ ] Can see vehicle location on map in real-time
- [ ] Can see vehicle's last known location if offline
- [ ] Can get directions to vehicle location
- [ ] Map updates automatically every 30 seconds
- [ ] Can see vehicle heading/direction indicator
- [ ] Can view location history for current rental period
- [ ] Works even when app is backgrounded

## Definition of Done
- [ ] Map screen with MapBox or Google Maps
- [ ] Real-time location updates via WebSocket
- [ ] Vehicle marker with direction arrow
- [ ] "Get Directions" integration with Maps app
- [ ] Location history timeline view
- [ ] Offline caching of last known location
- [ ] Background location refresh
- [ ] Tests written and passing (>95% coverage)
- [ ] Documentation updated

## Related Tasks
- T-097: Map screen with MapBox/Google Maps
- T-098: Real-time location via WebSocket
- T-099: Vehicle marker with direction indicator
- T-100: Navigation/directions integration
- T-101: Location history timeline
- T-102: Offline location caching

## Notes
- WebSocket connection for real-time updates
- Fallback to polling if WebSocket fails
- Direction indicator shows vehicle heading
- Open native Maps app for turn-by-turn directions
- Location history stored locally for offline viewing
