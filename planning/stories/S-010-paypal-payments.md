# S-010: PayPal Payment Integration

**Story Type**: User Story
**Priority**: High
**Estimate**: 4 days
**Sprint**: Epoch 2
**Status**: PENDING

## User Story
**As a** customer
**I want to** pay for my rental online with PayPal
**So that** I can complete my booking securely

## Acceptance Criteria
- [ ] Can pay rental amount via PayPal checkout
- [ ] Can authorize security deposit hold (not charged)
- [ ] Receive payment confirmation email
- [ ] Payment recorded in system with transaction ID
- [ ] Can view payment history in my account
- [ ] Refunds processed automatically for cancellations
- [ ] Can pay with PayPal balance or linked card

## Definition of Done
- [ ] PayPal SDK integrated
- [ ] Checkout flow with PayPal button
- [ ] Deposit authorization implemented
- [ ] Payment model storing transaction details
- [ ] Payment confirmation emails
- [ ] Refund processing logic
- [ ] Payment history page for customers
- [ ] Tests written and passing (>95% coverage)
- [ ] Documentation updated

## Related Tasks
- T-041: PayPal SDK integration
- T-042: Payment checkout flow
- T-043: Deposit authorization
- T-044: Payment recording and receipts
- T-045: Refund processing

## Notes
- PayPal Business account required
- Sandbox testing before production
- Deposit hold released after successful return
- Support both PayPal and Debit/Credit via PayPal
- Store PayPal transaction IDs for reconciliation
