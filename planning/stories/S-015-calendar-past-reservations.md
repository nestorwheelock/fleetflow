# S-015: Optional Past Reservations View in Calendar

**Story Type**: User Story
**Priority**: Medium
**Estimate**: 1 day
**Status**: Pending

## User Story

**As a** rental agent
**I want to** optionally view past reservations in the calendar
**So that** I can review historical booking patterns and reference past rentals

## Acceptance Criteria

- [ ] By default, calendar shows current and future reservations only
- [ ] Toggle/checkbox to "Show Past Reservations" is available
- [ ] When enabled, past reservations appear with distinct styling (faded/different color)
- [ ] Past reservations are clearly distinguishable from current/future ones
- [ ] Toggle preference is remembered (localStorage or user preference)
- [ ] Performance is maintained when showing past reservations (pagination/limit)

## UI/UX Requirements

- Toggle should be in calendar header/toolbar area
- Past reservations should be visually muted (lower opacity, gray border, etc.)
- Status colors should still be visible but less prominent
- Clicking past reservation shows read-only details

## Technical Notes

- Add `include_past` query parameter to calendar API
- Add filter to reservation query based on parameter
- Update JavaScript to handle toggle state
- Consider limiting past reservations to last 6 months for performance

## Definition of Done

- [ ] Toggle UI implemented
- [ ] API supports include_past parameter
- [ ] Past reservations styled distinctly
- [ ] Preference persisted in localStorage
- [ ] Tests written and passing
- [ ] Documentation updated
