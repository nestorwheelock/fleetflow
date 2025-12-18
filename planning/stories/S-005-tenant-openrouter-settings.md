# S-005: Tenant Settings for OpenRouter API Key

**Story Type**: User Story
**Priority**: High
**Estimate**: 2 days
**Sprint**: Sprint 2
**Status**: Pending

## User Story
**As a** tenant owner
**I want to** configure my OpenRouter API key in the settings
**So that** I can enable AI-powered automation features for my rental business

## Acceptance Criteria
- [ ] Tenant settings page accessible from dashboard navigation
- [ ] OpenRouter API key input field (password/hidden type)
- [ ] "Test API Key" button to verify key is valid
- [ ] Enable/disable toggle for auto-parsing features
- [ ] Model selection dropdown (Claude 3.5 Sonnet, GPT-4 Vision, etc.)
- [ ] API key encrypted at rest (Fernet encryption)
- [ ] API key never exposed in API responses or logs
- [ ] Settings only accessible to tenant owners (not managers/staff)

## Definition of Done
- [ ] TenantSettings model created with encrypted API key field
- [ ] Settings API endpoint (GET/PATCH) implemented
- [ ] API key test endpoint working
- [ ] Settings UI template created
- [ ] Navigation link added for tenant owners
- [ ] Unit tests for encryption (>95% coverage)
- [ ] Integration tests for settings API
- [ ] Documentation updated

## Technical Notes
- Use `cryptography` library for Fernet encryption
- Store `FIELD_ENCRYPTION_KEY` in environment variables
- TenantSettings is OneToOne with Tenant model
- Feature check utility for plan-based access control

## Related Tasks
- T-010: Create automation app and models
- T-011: Implement encryption utilities
- T-013: Tenant settings API
- T-015: Settings UI
