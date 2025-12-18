# B-008: Photo Thumbnails Are Square, Cutting Off Vehicle Images

**Severity**: Medium
**Affected Component**: Vehicle Photo Gallery / Thumbnails
**Discovered**: 2025-12-18

## Bug Description

Vehicle photo thumbnails are displayed as squares, which cuts off portions of the vehicle images. Since vehicle photos are typically landscape orientation (wider than tall), square thumbnails crop important parts of the image.

## Steps to Reproduce

1. Navigate to a vehicle detail page
2. View the photo gallery/thumbnails
3. Observe that thumbnails are square, cutting off sides of vehicles

## Expected Behavior

Photo thumbnails should be rectangular (landscape orientation, e.g., 16:9 or 4:3 aspect ratio) to properly display vehicle photos without cutting off important content.

## Actual Behavior

Thumbnails are square (1:1 aspect ratio), causing horizontal cropping of vehicle images.

## Proposed Fix

Update CSS for thumbnail containers to use a landscape aspect ratio:
- Change from `aspect-ratio: 1/1` or `padding-bottom: 100%` to `aspect-ratio: 16/9` or `aspect-ratio: 4/3`
- Use `object-fit: cover` to maintain proper scaling
- Ensure responsive behavior is maintained

## Files to Investigate

- `templates/dashboard/vehicles/detail.html` - Vehicle detail page
- `templates/dashboard/vehicles/list.html` - Vehicle list thumbnails
- `static/css/` - Any custom thumbnail styles
- Tailwind classes used for image containers

## Acceptance Criteria

- [ ] Thumbnails display in landscape aspect ratio (16:9 or 4:3)
- [ ] Vehicle images are not cut off horizontally
- [ ] Thumbnails scale properly on different screen sizes
- [ ] List view and detail view both use consistent thumbnail style
- [ ] Image quality is maintained
