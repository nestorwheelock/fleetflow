# T-009: Document Upload for Customers

## AI Coding Brief
**Role**: Full-Stack Developer
**Objective**: Implement document upload (license, insurance) for customers
**Related Story**: S-002 (Customer Management)

## Constraints
**Allowed File Paths**:
- /apps/customers/models.py
- /apps/customers/views.py
- /apps/customers/forms.py
- /templates/customers/*

## Deliverables
- [ ] CustomerDocument model
- [ ] Document upload form
- [ ] Document type selection
- [ ] Document viewing/download
- [ ] Document deletion
- [ ] Validation (file type, size)

## Technical Specifications

### CustomerDocument Model
```python
class CustomerDocument(models.Model):
    DOCUMENT_TYPES = [
        ('license_front', "Driver's License (Front)"),
        ('license_back', "Driver's License (Back)"),
        ('insurance', "Insurance Card"),
        ('other', "Other Document"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='customers/documents/%Y/%m/')
    description = models.CharField(max_length=100, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-uploaded_at']
```

### Validation
- Max file size: 10MB
- Allowed types: PDF, JPEG, PNG
- Secure file serving (not directly accessible)

## Definition of Done
- [ ] Documents upload successfully
- [ ] Document types selectable
- [ ] Documents viewable/downloadable
- [ ] Documents can be marked verified
- [ ] Validation prevents wrong file types
- [ ] Tests written and passing (>95% coverage)
