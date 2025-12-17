# T-005: Vehicle Image Upload Handling

## AI Coding Brief
**Role**: Full-Stack Developer
**Objective**: Implement multiple image upload per vehicle
**Related Story**: S-001 (Vehicle Fleet Management)

## Constraints
**Allowed File Paths**:
- /apps/vehicles/models.py
- /apps/vehicles/views.py
- /apps/vehicles/forms.py
- /templates/vehicles/*
- /config/settings/*.py

**Forbidden Paths**: None

## Deliverables
- [ ] VehicleImage model
- [ ] Image upload view/form
- [ ] Image validation (size, type)
- [ ] Primary image designation
- [ ] Image deletion
- [ ] Thumbnail generation (optional)
- [ ] AJAX upload (optional enhancement)

## Technical Specifications

### VehicleImage Model
```python
class VehicleImage(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='vehicles/%Y/%m/')
    caption = models.CharField(max_length=100, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-is_primary']

    def save(self, *args, **kwargs):
        # Ensure only one primary image per vehicle
        if self.is_primary:
            VehicleImage.objects.filter(
                vehicle=self.vehicle, is_primary=True
            ).update(is_primary=False)
        super().save(*args, **kwargs)
```

### Image Validation
- Max file size: 5MB
- Allowed types: JPEG, PNG, WebP
- Max images per vehicle: 10
- Recommended dimensions: 1200x800

### Upload Form
```python
class VehicleImageForm(forms.ModelForm):
    class Meta:
        model = VehicleImage
        fields = ['image', 'caption', 'is_primary']

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("Image too large (max 5MB)")
            # Check content type
        return image
```

## Definition of Done
- [ ] Images upload successfully
- [ ] Validation prevents oversized/wrong type files
- [ ] Primary image can be set/changed
- [ ] Images display in gallery on detail page
- [ ] Images can be deleted
- [ ] Tests written and passing (>95% coverage)
