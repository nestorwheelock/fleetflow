# B-004: Customer License Image Upload Missing

**Severity**: High
**Affected Component**: Customers / Profile Management
**Discovered**: December 2025

## Bug Description

The customer form does not allow uploading driver's license images (front and back). While the Customer model has `license_image_front` and `license_image_back` ImageField fields, these are not exposed in the customer create/edit form.

## Steps to Reproduce

1. Log in to FleetFlow
2. Navigate to Customers > Add New Customer
3. Fill out customer information
4. Notice there are no file upload fields for license images
5. Cannot attach license front/back images to customer profile

## Expected Behavior

- Customer form should have file upload fields for license front and back images
- Form should use `enctype="multipart/form-data"` to support file uploads
- Customer detail page should display uploaded license images
- Ability to view combined license image (front on top, back on bottom)

## Actual Behavior

- No file upload fields in customer form
- License images cannot be attached to customer profiles
- Model fields exist but are not exposed in the UI

## Root Cause

The CustomerCreateView and CustomerUpdateView did not include `license_image_front` and `license_image_back` in their `fields` list. The form template also lacked:
1. `enctype="multipart/form-data"` attribute
2. File input fields for license images
3. Preview display for existing images (edit mode)

## Fix Required

1. Add license image fields to CustomerCreateView and CustomerUpdateView
2. Update customer form template with file upload inputs
3. Add `enctype="multipart/form-data"` to form element
4. Update customer detail page to show license images
5. Create combined license view endpoint for printing/viewing

## Technical Details

**Model Fields** (already exist):
```python
license_image_front = models.ImageField(upload_to='customer_licenses/', blank=True, null=True)
license_image_back = models.ImageField(upload_to='customer_licenses/', blank=True, null=True)
```

**Required Changes**:
- `apps/dashboard/views.py` - Add fields to views, add combined license view
- `apps/dashboard/urls.py` - Add URL for combined license view
- `templates/dashboard/customers/form.html` - Add file upload fields
- `templates/dashboard/customers/detail.html` - Show license images

## Environment

- Django: 5.x
- Python: 3.12
- Pillow: 12.0.0

## Related Files

- `apps/customers/models.py` - Customer model (fields exist)
- `apps/dashboard/views.py` - Customer views
- `templates/dashboard/customers/form.html` - Customer form template
- `templates/dashboard/customers/detail.html` - Customer detail template

## Resolution

**Status**: Fixed
**Fixed Date**: December 2025

### Changes Made

1. **Updated `apps/dashboard/views.py`**:
   - Added `license_image_front` and `license_image_back` to CustomerCreateView and CustomerUpdateView fields
   - Added `customer_combined_license` view that combines front and back images into one (front on top, back on bottom)

2. **Updated `apps/dashboard/urls.py`**:
   - Added URL pattern for combined license view: `/dashboard/customers/<pk>/license/`

3. **Updated `templates/dashboard/customers/form.html`**:
   - Added `enctype="multipart/form-data"` to form element
   - Added file input fields for license front and back images
   - Added preview display for existing images in edit mode

4. **Updated `templates/dashboard/customers/detail.html`**:
   - Added section to display license images (front and back side-by-side)
   - Added "View Combined License" button that opens the combined image in a new tab

5. **Tests Added in `tests/test_crud_views.py`**:
   - `test_customer_form_has_license_upload_fields` - Verifies form has upload fields
   - `test_customer_form_accepts_license_images` - Tests file upload functionality
   - `test_customer_detail_shows_license_images` - Verifies images display on detail page
   - `test_combined_license_view_accessible` - Tests combined image generation
   - `test_combined_license_returns_404_without_images` - Tests 404 when images missing

**Tests**: All 215 tests pass at 91% coverage
