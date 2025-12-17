# S-019: Mobile Customer Authentication

**Story Type**: User Story
**Priority**: High
**Estimate**: 4 days
**Sprint**: Epoch 4
**Status**: PENDING

## User Story
**As a** customer
**I want to** log into my account on my phone
**So that** I can manage rentals on the go

## Acceptance Criteria
- [ ] Can register new account on mobile app
- [ ] Can log in with email/password
- [ ] Can use biometric login (Face ID/Touch ID/Fingerprint)
- [ ] Can reset password from mobile
- [ ] Session persists securely on device
- [ ] Can log out and switch accounts
- [ ] Login via PayPal OAuth option

## Definition of Done
- [ ] React Native project setup with Expo
- [ ] Login screen with form validation
- [ ] Registration screen
- [ ] Forgot password flow
- [ ] Biometric authentication integration
- [ ] Secure token storage (Keychain/Keystore)
- [ ] API client for Django backend
- [ ] Tests written and passing (>95% coverage)
- [ ] Documentation updated

## Related Tasks
- T-081: React Native project setup with Expo
- T-082: Authentication screens (login, register, forgot password)
- T-083: Biometric authentication integration
- T-084: Secure token storage (AsyncStorage/Keychain)
- T-085: API client setup for Django backend

## Notes
- Use Expo SecureStore for sensitive data
- JWT tokens with refresh mechanism
- Biometrics optional, can be enabled in settings
- Auto-logout after 30 days of inactivity
- Support both iOS and Android biometrics
